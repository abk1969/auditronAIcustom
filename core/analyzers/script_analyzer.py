"""Analyseur de sécurité pour les scripts."""
import re
import os
import stat
from typing import Dict, Any, List, Optional
from pathlib import Path

from .base_analyzer import BaseAnalyzer
from .interfaces import AnalyzerType
from ..logger import logger
from ..error_handling import SecurityError, ErrorSeverity

class ScriptAnalyzer(BaseAnalyzer):
    """Analyseur de sécurité spécialisé pour les scripts."""

    @property
    def analyzer_type(self) -> AnalyzerType:
        """Retourne le type d'analyseur."""
        return AnalyzerType.SCRIPT

    async def _setup(self) -> None:
        """Configure l'analyseur."""
        self.dangerous_commands = {
            'rm -rf /',
            'chmod 777',
            '> /dev/sda',
            'mkfs',
            'dd if=/dev/zero',
            ':(){:|:&};:',
            'wget http|curl http',
            'eval',
            'sudo',
            'sudo su'
        }
        
        self.network_commands = {
            'wget',
            'curl',
            'nc',
            'netcat',
            'telnet',
            'ftp',
            'ssh',
            'nmap'
        }
        
        self.file_operations = {
            'rm',
            'mv',
            'cp',
            'dd',
            'chmod',
            'chown',
            'touch',
            'mkdir',
            'rmdir'
        }

    async def _analyze_impl(self) -> Dict[str, Any]:
        """
        Effectue l'analyse du script.
        
        Returns:
            Dict contenant les résultats de l'analyse
        """
        try:
            # Détecter le type de script
            script_type = self._detect_script_type()
            if not script_type:
                return {
                    'is_script': False
                }
            
            # Analyser les permissions si c'est un fichier
            permissions_issues = []
            if os.path.isfile(self.context.filename):
                permissions_issues = self._check_permissions()
            
            # Analyser le contenu
            security_issues = []
            security_issues.extend(self._check_dangerous_commands())
            security_issues.extend(self._check_network_access())
            security_issues.extend(self._check_file_operations())
            security_issues.extend(self._check_input_validation())
            security_issues.extend(permissions_issues)
            
            return {
                'is_script': True,
                'script_type': script_type,
                'issues': security_issues
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse du script: {str(e)}")
            raise SecurityError(
                message=f"Erreur lors de l'analyse du script: {str(e)}",
                vulnerability_type="script_analysis_error",
                severity=ErrorSeverity.ERROR
            )

    def _detect_script_type(self) -> Optional[str]:
        """
        Détecte le type de script.
        
        Returns:
            Type de script ou None
        """
        # Vérifier le shebang
        first_line = self.context.code.splitlines()[0] if self.context.code else ""
        if first_line.startswith('#!'):
            if '/bin/bash' in first_line or '/bin/sh' in first_line:
                return 'shell'
            elif '/bin/python' in first_line:
                return 'python'
            elif '/bin/node' in first_line:
                return 'node'
                
        # Vérifier l'extension
        ext = Path(self.context.filename).suffix.lower()
        if ext in {'.sh', '.bash'}:
            return 'shell'
        elif ext == '.py':
            return 'python'
        elif ext in {'.js', '.ts'}:
            return 'node'
            
        # Analyse heuristique du contenu
        content = self.context.code.lower()
        if any(kw in content for kw in {'#!/bin/bash', 'echo', 'export'}):
            return 'shell'
        elif any(kw in content for kw in {'import', 'def', 'class', 'print'}):
            return 'python'
        elif any(kw in content for kw in {'require(', 'module.exports', 'console.log'}):
            return 'node'
            
        return None

    def _check_permissions(self) -> List[Dict[str, Any]]:
        """
        Vérifie les permissions du script.
        
        Returns:
            Liste des problèmes de permissions
        """
        issues = []
        try:
            st = os.stat(self.context.filename)
            mode = st.st_mode
            
            # Vérifier les permissions world-writable
            if mode & stat.S_IWOTH:
                issues.append({
                    'severity': 'high',
                    'type': 'unsafe_permissions',
                    'description': 'Le script est modifiable par tous les utilisateurs',
                    'line_number': 0,
                    'code': f"chmod {oct(mode)[-3:]} {self.context.filename}",
                    'cwe': ['CWE-732']
                })
                
            # Vérifier SUID/SGID
            if mode & (stat.S_ISUID | stat.S_ISGID):
                issues.append({
                    'severity': 'high',
                    'type': 'unsafe_permissions',
                    'description': 'Le script a des bits SUID/SGID activés',
                    'line_number': 0,
                    'code': f"chmod {oct(mode)[-3:]} {self.context.filename}",
                    'cwe': ['CWE-732']
                })
                
        except Exception as e:
            logger.warning(f"Impossible de vérifier les permissions: {str(e)}")
            
        return issues

    def _check_dangerous_commands(self) -> List[Dict[str, Any]]:
        """
        Vérifie la présence de commandes dangereuses.
        
        Returns:
            Liste des problèmes de sécurité
        """
        issues = []
        lines = self.context.code.splitlines()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line.startswith('#'):
                continue
                
            for cmd in self.dangerous_commands:
                if re.search(rf'\b{cmd}\b', line):
                    issues.append({
                        'severity': 'critical',
                        'type': 'dangerous_command',
                        'description': f'Commande dangereuse détectée: {cmd}',
                        'line_number': i,
                        'code': line,
                        'cwe': ['CWE-78']
                    })
                    
        return issues

    def _check_network_access(self) -> List[Dict[str, Any]]:
        """
        Vérifie les accès réseau.
        
        Returns:
            Liste des problèmes de sécurité
        """
        issues = []
        lines = self.context.code.splitlines()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line.startswith('#'):
                continue
                
            for cmd in self.network_commands:
                if re.search(rf'\b{cmd}\b', line):
                    # Vérifier si HTTPS est utilisé
                    if 'http://' in line and not 'https://' in line:
                        issues.append({
                            'severity': 'high',
                            'type': 'insecure_network',
                            'description': 'Communication non chiffrée détectée',
                            'line_number': i,
                            'code': line,
                            'cwe': ['CWE-319']
                        })
                    else:
                        issues.append({
                            'severity': 'medium',
                            'type': 'network_access',
                            'description': f'Accès réseau détecté: {cmd}',
                            'line_number': i,
                            'code': line,
                            'cwe': ['CWE-918']
                        })
                    
        return issues

    def _check_file_operations(self) -> List[Dict[str, Any]]:
        """
        Vérifie les opérations sur les fichiers.
        
        Returns:
            Liste des problèmes de sécurité
        """
        issues = []
        lines = self.context.code.splitlines()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line.startswith('#'):
                continue
                
            for cmd in self.file_operations:
                if re.search(rf'\b{cmd}\b', line):
                    # Vérifier les chemins absolus
                    if re.search(r'\b/(?:etc|usr|bin|sbin|lib|var)\b', line):
                        issues.append({
                            'severity': 'high',
                            'type': 'file_operation',
                            'description': f'Opération sur fichier système: {cmd}',
                            'line_number': i,
                            'code': line,
                            'cwe': ['CWE-73']
                        })
                    else:
                        issues.append({
                            'severity': 'medium',
                            'type': 'file_operation',
                            'description': f'Opération sur fichier: {cmd}',
                            'line_number': i,
                            'code': line,
                            'cwe': ['CWE-73']
                        })
                    
        return issues

    def _check_input_validation(self) -> List[Dict[str, Any]]:
        """
        Vérifie la validation des entrées.
        
        Returns:
            Liste des problèmes de sécurité
        """
        issues = []
        lines = self.context.code.splitlines()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line.startswith('#'):
                continue
                
            # Vérifier l'utilisation de variables non échappées
            if re.search(r'\$\{?\w+\}?', line):
                if not re.search(r'"\$\{?\w+\}?"', line):
                    issues.append({
                        'severity': 'medium',
                        'type': 'input_validation',
                        'description': 'Variable non échappée',
                        'line_number': i,
                        'code': line,
                        'cwe': ['CWE-78']
                    })
                    
            # Vérifier l'injection de commandes
            if re.search(r'`.*\$.*`|\$(.*\(.*\))', line):
                issues.append({
                    'severity': 'high',
                    'type': 'command_injection',
                    'description': 'Possible injection de commande',
                    'line_number': i,
                    'code': line,
                    'cwe': ['CWE-78']
                })
                
        return issues
