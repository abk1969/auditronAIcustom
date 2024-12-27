"""Repository de patterns pour l'analyse TypeScript."""
from typing import Dict, List, Pattern
import re

class TypeScriptPatternsRepository:
    """Repository contenant les patterns d'analyse pour TypeScript."""

    def __init__(self):
        """Initialise les patterns de sécurité et qualité."""
        self.security_patterns: Dict[str, Pattern] = {
            'eval_usage': re.compile(r'eval\s*\('),
            'function_constructor': re.compile(r'new\s+Function\s*\('),
            'dangerous_innerHTML': re.compile(r'\.innerHTML\s*='),
            'sql_injection': re.compile(r'execute(?:Sql|Query|Statement)|raw(?:Query|Statement)'),
            'command_injection': re.compile(r'exec\s*\(|execSync\s*\(|spawn\s*\('),
            'sensitive_data': re.compile(r'password|secret|key|token|credential', re.IGNORECASE),
            'insecure_random': re.compile(r'Math\.random\s*\('),
            'prototype_pollution': re.compile(r'Object\.assign|Object\.prototype|__proto__'),
            'xss_vulnerable': re.compile(r'document\.write|\.outerHTML\s*='),
            'unsafe_regex': re.compile(r'new\s+RegExp\s*\('),
        }
        
        self.quality_patterns: Dict[str, Pattern] = {
            'console_log': re.compile(r'console\.(log|debug|info)'),
            'any_type': re.compile(r':\s*any\b'),
            'empty_catch': re.compile(r'catch\s*\([^)]*\)\s*{}'),
            'magic_numbers': re.compile(r'\b\d{4,}\b'),
            'long_function': re.compile(r'function\s+\w+\s*\([^)]*\)\s*{[^}]{200,}}'),
            'complex_condition': re.compile(r'if\s*\([^)]{100,}\)'),
            'nested_callbacks': re.compile(r'callback.*callback.*callback'),
            'todo_comment': re.compile(r'//\s*TODO|/\*\s*TODO'),
            'unused_import': re.compile(r'import.*from.*\n(?!.*\1)'),
            'deprecated_api': re.compile(r'@deprecated|@obsolete'),
        }

    def get_security_patterns(self) -> Dict[str, Pattern]:
        """Retourne les patterns de sécurité."""
        return self.security_patterns

    def get_quality_patterns(self) -> Dict[str, Pattern]:
        """Retourne les patterns de qualité."""
        return self.quality_patterns

    def get_all_patterns(self) -> Dict[str, Pattern]:
        """Retourne tous les patterns."""
        return {**self.security_patterns, **self.quality_patterns}
