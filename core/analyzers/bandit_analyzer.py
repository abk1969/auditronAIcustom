"""Analyseur de sécurité Python utilisant Bandit."""
import subprocess
import json
import tempfile
from typing import Dict, Any, List, Optional
from pathlib import Path

from .base_analyzer import BaseAnalyzer
from .interfaces import AnalyzerType
from ..logger import logger
from ..error_handling import SecurityError, ErrorSeverity

class BanditAnalyzer(BaseAnalyzer):
    """Analyseur de sécurité Python utilisant l'outil Bandit."""

    def __init__(self, config=None):
        """
        Initialise l'analyseur Bandit.
        
        Args:
            config: Configuration optionnelle
        """
        super().__init__(config)
        self.bandit_config = self._config.get_analyzer_settings('bandit') if self._config else None

    @property
    def analyzer_type(self) -> AnalyzerType:
        """Retourne le type d'analyseur."""
        return AnalyzerType.SECURITY

    async def _setup(self) -> None:
        """Configure l'analyseur."""
        try:
            # Vérifier que Bandit est installé
            subprocess.run(
                ["bandit", "--version"],
                capture_output=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            logger.error("Bandit n'est pas installé ou accessible")
            raise RuntimeError("Bandit n'est pas disponible") from e
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de Bandit: {str(e)}")
            raise

    async def _analyze_impl(self) -> Dict[str, Any]:
        """
        Effectue l'analyse de sécurité.
        
        Returns:
            Dict contenant les résultats de l'analyse
        """
        try:
            # Créer un fichier temporaire avec le code
            temp_file = self._create_temp_file(self.context.code, '.py')
            
            # Exécuter Bandit avec sortie JSON
            process = subprocess.run(
                [
                    "bandit",
                    "-f", "json",
                    "-ll",  # Log level
                    "-i",  # Include more info
                    "-v",  # Verbose
                    "-n", "3",  # Number of processes
                    temp_file
                ],
                capture_output=True,
                text=True,
                check=False
            )
            
            # Analyser la sortie
            if process.stdout:
                try:
                    results = json.loads(process.stdout)
                    return self._process_results(results)
                except json.JSONDecodeError:
                    logger.error("Erreur lors du parsing des résultats Bandit")
                    return self._create_empty_results()
            
            # Gérer les erreurs
            if process.returncode != 0 and process.stderr:
                logger.error(f"Erreur Bandit: {process.stderr}")
                return {
                    "error": True,
                    "message": process.stderr
                }
            
            return self._create_empty_results()
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse Bandit: {str(e)}")
            raise SecurityError(
                message=f"Erreur lors de l'analyse de sécurité: {str(e)}",
                vulnerability_type="security_analysis_error",
                severity=ErrorSeverity.ERROR
            )

    def _process_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traite les résultats bruts de Bandit.
        
        Args:
            results: Résultats JSON de Bandit
            
        Returns:
            Dict contenant les résultats formatés
        """
        security_issues = []
        metrics = {
            'total_issues': len(results.get('results', [])),
            'by_severity': {},
            'by_confidence': {},
            'by_test_id': {}
        }
        
        # Traiter chaque problème
        for issue in results.get('results', []):
            formatted_issue = self._format_issue(issue)
            security_issues.append(formatted_issue)
            
            # Mettre à jour les métriques
            severity = issue.get('issue_severity', 'unknown')
            confidence = issue.get('issue_confidence', 'unknown')
            test_id = issue.get('test_id', 'unknown')
            
            metrics['by_severity'][severity] = metrics['by_severity'].get(severity, 0) + 1
            metrics['by_confidence'][confidence] = metrics['by_confidence'].get(confidence, 0) + 1
            metrics['by_test_id'][test_id] = metrics['by_test_id'].get(test_id, 0) + 1
            
        return {
            'security_issues': security_issues,
            'metrics': metrics,
            'generated_at': results.get('generated_at', ''),
            'scan_info': {
                'python_version': results.get('scan_info', {}).get('python_version', ''),
                'bandit_version': results.get('scan_info', {}).get('bandit_version', ''),
                'tools': results.get('scan_info', {}).get('tools', [])
            }
        }

    def _format_issue(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formate un problème de sécurité.
        
        Args:
            issue: Problème à formater
            
        Returns:
            Dict contenant le problème formaté
        """
        return {
            'severity': issue.get('issue_severity', ''),
            'confidence': issue.get('issue_confidence', ''),
            'test_id': issue.get('test_id', ''),
            'test_name': issue.get('test_name', ''),
            'issue_text': issue.get('issue_text', ''),
            'line_number': issue.get('line_number', 0),
            'line_range': issue.get('line_range', []),
            'code': issue.get('code', ''),
            'filename': issue.get('filename', ''),
            'more_info': issue.get('more_info', ''),
            'cwe': self._get_cwe_for_test(issue.get('test_id', '')),
            'fix_suggestion': self._get_fix_suggestion(issue)
        }

    def _create_empty_results(self) -> Dict[str, Any]:
        """
        Crée des résultats vides.
        
        Returns:
            Dict contenant des résultats vides
        """
        return {
            'security_issues': [],
            'metrics': {
                'total_issues': 0,
                'by_severity': {},
                'by_confidence': {},
                'by_test_id': {}
            },
            'generated_at': '',
            'scan_info': {
                'python_version': '',
                'bandit_version': '',
                'tools': []
            }
        }

    def _get_cwe_for_test(self, test_id: str) -> List[str]:
        """
        Retourne les CWE associés à un test.
        
        Args:
            test_id: ID du test
            
        Returns:
            Liste des CWE
        """
        cwe_mapping = {
            'B101': ['CWE-676'],  # assert
            'B102': ['CWE-78'],   # exec
            'B103': ['CWE-78'],   # subprocess
            'B104': ['CWE-78'],   # subprocess_shell
            'B105': ['CWE-78'],   # hardcoded_password_string
            'B106': ['CWE-259'],  # hardcoded_password_funcarg
            'B107': ['CWE-259'],  # hardcoded_password_default
            'B108': ['CWE-78'],   # hardcoded_tmp_directory
            'B109': ['CWE-78'],   # password_config_option_not_marked_secret
            'B110': ['CWE-78'],   # try_except_pass
            'B111': ['CWE-78'],   # execute_with_run_as_root_equals_true
            'B112': ['CWE-78'],   # try_except_continue
            'B201': ['CWE-78'],   # flask_debug_true
            'B301': ['CWE-78'],   # pickle
            'B302': ['CWE-78'],   # marshal
            'B303': ['CWE-78'],   # md5
            'B304': ['CWE-78'],   # ciphers
            'B305': ['CWE-78'],   # cipher_modes
            'B306': ['CWE-78'],   # mktemp_q
            'B307': ['CWE-78'],   # eval
            'B308': ['CWE-78'],   # mark_safe
            'B309': ['CWE-78'],   # httpsconnection
            'B310': ['CWE-78'],   # urllib_urlopen
            'B311': ['CWE-78'],   # random
            'B312': ['CWE-78'],   # telnetlib
            'B313': ['CWE-78'],   # xml_bad_cElementTree
            'B314': ['CWE-78'],   # xml_bad_ElementTree
            'B315': ['CWE-78'],   # xml_bad_expatreader
            'B316': ['CWE-78'],   # xml_bad_expatbuilder
            'B317': ['CWE-78'],   # xml_bad_sax
            'B318': ['CWE-78'],   # xml_bad_minidom
            'B319': ['CWE-78'],   # xml_bad_pulldom
            'B320': ['CWE-78'],   # xml_bad_etree
            'B321': ['CWE-78'],   # ftplib
            'B322': ['CWE-78'],   # input
            'B323': ['CWE-78'],   # unverified_context
            'B324': ['CWE-78'],   # hashlib_new_insecure_functions
            'B325': ['CWE-78'],   # tempnam
            'B401': ['CWE-78'],   # import_telnetlib
            'B402': ['CWE-78'],   # import_ftplib
            'B403': ['CWE-78'],   # import_pickle
            'B404': ['CWE-78'],   # import_subprocess
            'B405': ['CWE-78'],   # import_xml_etree
            'B406': ['CWE-78'],   # import_xml_sax
            'B407': ['CWE-78'],   # import_xml_expat
            'B408': ['CWE-78'],   # import_xml_minidom
            'B409': ['CWE-78'],   # import_xml_pulldom
            'B410': ['CWE-78'],   # import_lxml
            'B411': ['CWE-78'],   # import_xmlrpclib
            'B412': ['CWE-78'],   # import_httplib
            'B413': ['CWE-78'],   # import_urllib_urlopen
            'B414': ['CWE-78'],   # import_pycrypto
            'B415': ['CWE-78'],   # import_cryptography
            'B416': ['CWE-78'],   # import_hashlib
            'B417': ['CWE-78'],   # import_pyghmi
            'B501': ['CWE-78'],   # request_with_no_cert_validation
            'B502': ['CWE-78'],   # ssl_with_bad_version
            'B503': ['CWE-78'],   # ssl_with_bad_defaults
            'B504': ['CWE-78'],   # ssl_with_no_version
            'B505': ['CWE-78'],   # weak_cryptographic_key
            'B506': ['CWE-78'],   # yaml_load
            'B507': ['CWE-78'],   # ssh_no_host_key_verification
            'B601': ['CWE-78'],   # paramiko_calls
            'B602': ['CWE-78'],   # subprocess_popen_with_shell_equals_true
            'B603': ['CWE-78'],   # subprocess_without_shell_equals_true
            'B604': ['CWE-78'],   # any_other_function_with_shell_equals_true
            'B605': ['CWE-78'],   # start_process_with_a_shell
            'B606': ['CWE-78'],   # start_process_with_no_shell
            'B607': ['CWE-78'],   # start_process_with_partial_path
            'B608': ['CWE-78'],   # hardcoded_sql_expressions
            'B609': ['CWE-78'],   # linux_commands_wildcard_injection
            'B610': ['CWE-78'],   # django_extra_used
            'B611': ['CWE-78'],   # django_rawsql_used
            'B701': ['CWE-78'],   # jinja2_autoescape_false
            'B702': ['CWE-78'],   # use_of_mako_templates
            'B703': ['CWE-78']    # django_mark_safe
        }
        
        return cwe_mapping.get(test_id, ['CWE-0'])

    def _get_fix_suggestion(self, issue: Dict[str, Any]) -> str:
        """
        Génère une suggestion de correction.
        
        Args:
            issue: Problème à corriger
            
        Returns:
            Suggestion de correction
        """
        test_id = issue.get('test_id', '')
        
        suggestions = {
            'B101': "Éviter d'utiliser assert en production",
            'B102': "Ne pas utiliser exec() avec des entrées non fiables",
            'B103': "Utiliser subprocess.run() avec shell=False",
            'B104': "Éviter shell=True avec subprocess",
            'B105': "Ne pas coder en dur les mots de passe",
            'B106': "Utiliser des variables d'environnement pour les secrets",
            'B107': "Ne pas utiliser de mots de passe par défaut",
            'B108': "Utiliser tempfile.mkstemp() pour les fichiers temporaires",
            'B109': "Marquer les options de mot de passe comme secrètes",
            'B110': "Gérer explicitement les exceptions",
            'B111': "Éviter run_as_root=True",
            'B112': "Gérer explicitement les exceptions",
            'B201': "Désactiver le mode debug en production",
            'B301': "Utiliser json à la place de pickle",
            'B302': "Utiliser json à la place de marshal",
            'B303': "Utiliser hashlib.sha256() ou plus récent",
            'B304': "Utiliser des algorithmes de chiffrement forts",
            'B305': "Utiliser des modes de chiffrement sécurisés",
            'B306': "Utiliser tempfile.mkstemp()",
            'B307': "Ne pas utiliser eval() avec des entrées non fiables",
            'B308': "Valider le HTML avant mark_safe()",
            'B309': "Utiliser des connexions HTTPS",
            'B310': "Utiliser requests à la place de urllib",
            'B311': "Utiliser secrets pour la cryptographie",
            'B312': "Ne pas utiliser telnetlib",
            'B313': "Utiliser defusedxml",
            'B314': "Utiliser defusedxml",
            'B315': "Utiliser defusedxml",
            'B316': "Utiliser defusedxml",
            'B317': "Utiliser defusedxml",
            'B318': "Utiliser defusedxml",
            'B319': "Utiliser defusedxml",
            'B320': "Utiliser defusedxml",
            'B321': "Utiliser SFTP à la place de FTP",
            'B322': "Utiliser input() avec précaution",
            'B323': "Vérifier les certificats SSL",
            'B324': "Utiliser des fonctions de hachage sécurisées",
            'B325': "Utiliser tempfile.mkstemp()",
            'B401': "Ne pas utiliser telnetlib",
            'B402': "Utiliser SFTP à la place de FTP",
            'B403': "Utiliser json à la place de pickle",
            'B404': "Utiliser subprocess avec précaution",
            'B405': "Utiliser defusedxml",
            'B406': "Utiliser defusedxml",
            'B407': "Utiliser defusedxml",
            'B408': "Utiliser defusedxml",
            'B409': "Utiliser defusedxml",
            'B410': "Utiliser defusedxml",
            'B411': "Utiliser des alternatives modernes",
            'B412': "Utiliser requests",
            'B413': "Utiliser requests",
            'B414': "Utiliser cryptography",
            'B415': "Utiliser cryptography correctement",
            'B416': "Utiliser des algorithmes sécurisés",
            'B417': "Mettre à jour pyghmi",
            'B501': "Valider les certificats SSL",
            'B502': "Utiliser TLS 1.2 ou plus récent",
            'B503': "Configurer SSL correctement",
            'B504': "Spécifier la version SSL/TLS",
            'B505': "Utiliser des clés cryptographiques fortes",
            'B506': "Utiliser yaml.safe_load()",
            'B507': "Vérifier les clés d'hôte SSH",
            'B601': "Configurer paramiko de manière sécurisée",
            'B602': "Éviter shell=True",
            'B603': "Utiliser shell=False",
            'B604': "Éviter l'exécution de shell",
            'B605': "Éviter l'exécution de shell",
            'B606': "Utiliser des chemins absolus",
            'B607': "Utiliser des chemins absolus",
            'B608': "Utiliser des requêtes paramétrées",
            'B609': "Échapper les caractères spéciaux",
            'B610': "Éviter django.extra",
            'B611': "Utiliser l'ORM Django",
            'B701': "Activer l'autoescape Jinja2",
            'B702': "Valider les templates Mako",
            'B703': "Valider avant mark_safe()"
        }
        
        return suggestions.get(test_id, "Revoir le code pour la sécurité")
