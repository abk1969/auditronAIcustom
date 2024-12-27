"""Analyseur de sécurité pour TypeScript."""
import subprocess
import json
import tempfile
from typing import Dict, Any, List, Optional
from pathlib import Path

from .base_analyzer import BaseAnalyzer
from .interfaces import AnalyzerType
from ..logger import logger
from ..error_handling import SecurityError, ErrorSeverity

class TypeScriptAnalyzer(BaseAnalyzer):
    """Analyseur de sécurité spécialisé pour TypeScript."""

    @property
    def analyzer_type(self) -> AnalyzerType:
        """Retourne le type d'analyseur."""
        return AnalyzerType.TYPESCRIPT

    async def _setup(self) -> None:
        """Configure l'analyseur."""
        try:
            # Vérifier que les outils TypeScript sont installés
            subprocess.run(
                ["tsc", "--version"],
                capture_output=True,
                check=True
            )
            subprocess.run(
                ["eslint", "--version"],
                capture_output=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            logger.error("TypeScript ou ESLint n'est pas installé")
            raise RuntimeError("Outils TypeScript non disponibles") from e
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des outils: {str(e)}")
            raise

    async def _analyze_impl(self) -> Dict[str, Any]:
        """
        Effectue l'analyse TypeScript.
        
        Returns:
            Dict contenant les résultats de l'analyse
        """
        try:
            # Créer un fichier temporaire avec le code
            temp_file = self._create_temp_file(self.context.code, '.ts')
            
            # Créer un tsconfig temporaire
            tsconfig = self._create_tsconfig()
            tsconfig_file = self._create_temp_file(json.dumps(tsconfig), '.json')
            
            # Créer un eslintrc temporaire
            eslintrc = self._create_eslintrc()
            eslintrc_file = self._create_temp_file(json.dumps(eslintrc), '.json')
            
            # Analyser avec TypeScript
            ts_issues = self._analyze_typescript(temp_file, tsconfig_file)
            
            # Analyser avec ESLint
            eslint_issues = self._analyze_eslint(temp_file, eslintrc_file)
            
            # Combiner et traiter les résultats
            return self._process_results(ts_issues, eslint_issues)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse TypeScript: {str(e)}")
            raise SecurityError(
                message=f"Erreur lors de l'analyse TypeScript: {str(e)}",
                vulnerability_type="typescript_analysis_error",
                severity=ErrorSeverity.ERROR
            )

    def _create_tsconfig(self) -> Dict[str, Any]:
        """
        Crée une configuration TypeScript.
        
        Returns:
            Dict contenant la configuration
        """
        return {
            "compilerOptions": {
                "target": "ES2020",
                "module": "commonjs",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True,
                "noImplicitAny": True,
                "strictNullChecks": True,
                "strictFunctionTypes": True,
                "noImplicitThis": True,
                "noUnusedLocals": True,
                "noUnusedParameters": True,
                "noImplicitReturns": True,
                "noFallthroughCasesInSwitch": True
            }
        }

    def _create_eslintrc(self) -> Dict[str, Any]:
        """
        Crée une configuration ESLint.
        
        Returns:
            Dict contenant la configuration
        """
        return {
            "env": {
                "browser": True,
                "es2021": True,
                "node": True
            },
            "extends": [
                "eslint:recommended",
                "plugin:@typescript-eslint/recommended",
                "plugin:security/recommended"
            ],
            "parser": "@typescript-eslint/parser",
            "parserOptions": {
                "ecmaVersion": 12,
                "sourceType": "module"
            },
            "plugins": [
                "@typescript-eslint",
                "security"
            ],
            "rules": {
                "security/detect-object-injection": "error",
                "security/detect-non-literal-regexp": "error",
                "security/detect-non-literal-require": "error",
                "security/detect-eval-with-expression": "error",
                "security/detect-no-csrf-before-method-override": "error",
                "security/detect-buffer-noassert": "error",
                "security/detect-child-process": "error",
                "security/detect-disable-mustache-escape": "error",
                "security/detect-new-buffer": "error",
                "security/detect-possible-timing-attacks": "error",
                "security/detect-pseudoRandomBytes": "error",
                "security/detect-unsafe-regex": "error"
            }
        }

    def _analyze_typescript(
        self,
        file_path: str,
        config_path: str
    ) -> List[Dict[str, Any]]:
        """
        Analyse avec TypeScript.
        
        Args:
            file_path: Chemin du fichier à analyser
            config_path: Chemin du fichier de configuration
            
        Returns:
            Liste des problèmes trouvés
        """
        process = subprocess.run(
            [
                "tsc",
                "--project", config_path,
                "--noEmit",
                "--pretty", "false",
                file_path
            ],
            capture_output=True,
            text=True,
            check=False
        )
        
        issues = []
        if process.stderr:
            # Parser la sortie d'erreur de TypeScript
            for line in process.stderr.splitlines():
                if '(' in line and ')' in line:
                    issue = self._parse_typescript_error(line)
                    if issue:
                        issues.append(issue)
                        
        return issues

    def _analyze_eslint(
        self,
        file_path: str,
        config_path: str
    ) -> List[Dict[str, Any]]:
        """
        Analyse avec ESLint.
        
        Args:
            file_path: Chemin du fichier à analyser
            config_path: Chemin du fichier de configuration
            
        Returns:
            Liste des problèmes trouvés
        """
        process = subprocess.run(
            [
                "eslint",
                "--config", config_path,
                "--format", "json",
                file_path
            ],
            capture_output=True,
            text=True,
            check=False
        )
        
        if process.stdout:
            try:
                results = json.loads(process.stdout)
                if results and isinstance(results, list):
                    return self._parse_eslint_results(results[0])
            except json.JSONDecodeError:
                logger.error("Erreur lors du parsing des résultats ESLint")
                
        return []

    def _parse_typescript_error(self, error_line: str) -> Optional[Dict[str, Any]]:
        """
        Parse une ligne d'erreur TypeScript.
        
        Args:
            error_line: Ligne d'erreur à parser
            
        Returns:
            Dict contenant l'erreur parsée ou None
        """
        try:
            # Format: file(line,col): error TS2551: message
            parts = error_line.split(':', 3)
            if len(parts) >= 3:
                location = parts[0]
                error_type = parts[1].strip()
                code = parts[2].strip().split(' ')[0]
                message = parts[2].strip()
                
                # Extraire ligne et colonne
                loc_parts = location[location.find('(')+1:location.find(')')].split(',')
                line = int(loc_parts[0])
                col = int(loc_parts[1]) if len(loc_parts) > 1 else 0
                
                return {
                    'type': 'typescript',
                    'code': code,
                    'message': message,
                    'line_number': line,
                    'column': col,
                    'severity': 'error' if 'error' in error_type else 'warning'
                }
        except Exception as e:
            logger.debug(f"Erreur lors du parsing d'une erreur TypeScript: {str(e)}")
            
        return None

    def _parse_eslint_results(self, file_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse les résultats ESLint.
        
        Args:
            file_result: Résultats pour un fichier
            
        Returns:
            Liste des problèmes trouvés
        """
        issues = []
        for message in file_result.get('messages', []):
            issues.append({
                'type': 'eslint',
                'code': message.get('ruleId', ''),
                'message': message.get('message', ''),
                'line_number': message.get('line', 0),
                'column': message.get('column', 0),
                'severity': 'error' if message.get('severity') == 2 else 'warning'
            })
        return issues

    def _process_results(
        self,
        ts_issues: List[Dict[str, Any]],
        eslint_issues: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Traite les résultats combinés.
        
        Args:
            ts_issues: Problèmes TypeScript
            eslint_issues: Problèmes ESLint
            
        Returns:
            Dict contenant les résultats formatés
        """
        security_issues = []
        code_quality = {
            'complexity': 0,
            'functions': [],
            'unused_code': {
                'variables': [],
                'functions': [],
                'imports': []
            }
        }
        
        # Traiter les problèmes TypeScript
        for issue in ts_issues:
            if self._is_security_issue(issue):
                security_issues.append(self._format_security_issue(issue))
            else:
                self._update_code_quality(code_quality, issue)
                
        # Traiter les problèmes ESLint
        for issue in eslint_issues:
            if self._is_security_issue(issue):
                security_issues.append(self._format_security_issue(issue))
            else:
                self._update_code_quality(code_quality, issue)
                
        return {
            'security_issues': security_issues,
            'code_quality': code_quality
        }

    def _is_security_issue(self, issue: Dict[str, Any]) -> bool:
        """
        Détermine si un problème est lié à la sécurité.
        
        Args:
            issue: Problème à vérifier
            
        Returns:
            True si c'est un problème de sécurité
        """
        security_patterns = {
            'security/',  # Règles ESLint security
            'detect-eval',
            'detect-non-literal-require',
            'detect-buffer-noassert',
            'detect-child-process',
            'detect-disable-mustache-escape',
            'detect-new-buffer',
            'detect-no-csrf-before-method-override',
            'detect-object-injection',
            'detect-possible-timing-attacks',
            'detect-pseudoRandomBytes',
            'detect-unsafe-regex'
        }
        
        return any(
            pattern in issue.get('code', '').lower()
            for pattern in security_patterns
        )

    def _format_security_issue(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formate un problème de sécurité.
        
        Args:
            issue: Problème à formater
            
        Returns:
            Dict contenant le problème formaté
        """
        return {
            'severity': 'high' if issue.get('severity') == 'error' else 'medium',
            'type': 'security_typescript',
            'code': issue.get('code', ''),
            'message': issue.get('message', ''),
            'line_number': issue.get('line_number', 0),
            'column': issue.get('column', 0),
            'file': self.context.filename
        }

    def _update_code_quality(
        self,
        quality: Dict[str, Any],
        issue: Dict[str, Any]
    ) -> None:
        """
        Met à jour les métriques de qualité.
        
        Args:
            quality: Métriques à mettre à jour
            issue: Problème à analyser
        """
        code = issue.get('code', '').lower()
        
        if 'complexity' in code:
            quality['complexity'] += 1
        elif 'unused' in code:
            if 'variable' in code:
                quality['unused_code']['variables'].append(issue)
            elif 'function' in code:
                quality['unused_code']['functions'].append(issue)
            elif 'import' in code:
                quality['unused_code']['imports'].append(issue)
