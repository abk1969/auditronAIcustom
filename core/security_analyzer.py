"""Module principal d'analyse de sécurité pour AuditronAI."""
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor

from .analyzers import (
    BanditAnalyzer,
    RadonAnalyzer,
    VultureAnalyzer,
    ProspectorAnalyzer,
    ScriptAnalyzer,
    TypeScriptAnalyzer
)
from .config.analyzer_config import AnalyzerConfig
from .logger import logger
from .analysis_progress import ProgressHandler, DefaultProgressHandler
from .scoring import SecurityScorer
from .analysis_results import AnalysisResults, CodeQuality, SecurityIssue

class SecurityAnalyzer:
    """Classe principale pour l'analyse de sécurité du code."""
    
    def __init__(self, progress_handler: Optional[ProgressHandler] = None, max_workers: int = 4):
        """
        Initialise l'analyseur de sécurité.
        
        Args:
            progress_handler: Gestionnaire de progression optionnel
            max_workers: Nombre maximum de workers pour l'exécution parallèle
        """
        self.config = AnalyzerConfig.from_env()
        self.progress_handler = progress_handler or DefaultProgressHandler()
        self.scorer = SecurityScorer(self.config.thresholds)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Initialisation lazy des analyseurs
        self._analyzers = {}

    def _get_analyzer(self, name: str):
        """Récupère ou crée un analyseur de manière lazy."""
        if name not in self._analyzers:
            analyzer_map = {
                'bandit': BanditAnalyzer,
                'radon': RadonAnalyzer,
                'vulture': VultureAnalyzer,
                'prospector': ProspectorAnalyzer,
                'script': ScriptAnalyzer,
                'typescript': TypeScriptAnalyzer
            }
            self._analyzers[name] = analyzer_map[name](self.config)
        return self._analyzers[name]

    async def analyze(self, code: str, filename: str = "code.py") -> AnalysisResults:
        """Analyse complète du code source de manière asynchrone."""
        try:
            self._setup_analysis()
            results = AnalysisResults(filename)
            results.set_code(code)
            
            if filename.endswith('.ts'):
                await self._analyze_typescript(code, filename, results)
            else:
                # Vérifier si c'est un script
                is_script = await self._analyze_script(code, filename, results)
                if is_script:
                    return results
                
                # Analyse Python standard en parallèle
                await self._analyze_python(code, filename, results)
            
            # Calculer le score final
            self._calculate_score(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse : {str(e)}")
            return AnalysisResults.create_default()
            
        finally:
            await self._cleanup()

    def _setup_analysis(self):
        """Configure l'interface pour l'analyse."""
        self.progress_handler.setup_ui()
        self.progress_handler.update_status("🔍 Préparation de l'analyse...")
        self.progress_handler.update_progress(10)

    async def _analyze_script(self, code: str, filename: str, results: AnalysisResults) -> bool:
        """Analyse un fichier script de manière asynchrone."""
        script_analyzer = self._get_analyzer('script')
        script_results = await self._run_in_executor(script_analyzer.analyze, code, filename)
        
        if script_results['is_script']:
            results.security_issues = script_results['issues']
            results.code_quality.script_type = script_results['script_type']
            self.progress_handler.update_progress(100)
            return True
        return False

    async def _analyze_python(self, code: str, filename: str, results: AnalysisResults) -> None:
        """Analyse un fichier Python de manière asynchrone."""
        try:
            # Analyse avec bandit
            bandit_analyzer = self._get_analyzer('bandit')
            bandit_results = await self._run_in_executor(bandit_analyzer.analyze, code, filename)
            
            # Ajouter les problèmes de sécurité
            for issue in bandit_results:
                results.add_security_issue(SecurityIssue(
                    type=issue['test_id'],
                    severity=issue['issue_severity'],
                    message=issue['issue_text'],
                    line=issue.get('line_number', 0),
                    file=filename,
                    code=issue.get('code', '')
                ))
                
            self.progress_handler.update_progress(50)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse Python : {str(e)}")

    async def _analyze_security(self, code: str, filename: str) -> Dict[str, Any]:
        """Analyse les vulnérabilités de sécurité."""
        self.progress_handler.update_status("🔍 Analyse des vulnérabilités avec Bandit...")
        bandit_analyzer = self._get_analyzer('bandit')
        results = await self._run_in_executor(bandit_analyzer.analyze, code, filename)
        self.progress_handler.update_progress(25)
        return results

    async def _analyze_complexity(self, code: str) -> Dict[str, Any]:
        """Analyse la complexité du code."""
        self.progress_handler.update_status("📊 Analyse de la complexité avec Radon...")
        radon_analyzer = self._get_analyzer('radon')
        results = await self._run_in_executor(radon_analyzer.analyze, code)
        self.progress_handler.update_progress(50)
        return results

    async def _analyze_dead_code(self, code: str) -> Dict[str, Any]:
        """Détecte le code mort."""
        self.progress_handler.update_status("🧹 Détection du code mort avec Vulture...")
        vulture_analyzer = self._get_analyzer('vulture')
        results = await self._run_in_executor(vulture_analyzer.analyze, code)
        self.progress_handler.update_progress(75)
        return results

    async def _analyze_quality(self, code: str) -> Dict[str, Any]:
        """Analyse la qualité du code."""
        self.progress_handler.update_status("✨ Analyse de la qualité avec Prospector...")
        prospector_analyzer = self._get_analyzer('prospector')
        results = await self._run_in_executor(prospector_analyzer.analyze, code)
        self.progress_handler.update_progress(100)
        return results

    def _calculate_score(self, results: AnalysisResults):
        """Calcule le score final."""
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for issue in results.security_issues:
            severity = issue.get('severity', '').lower()
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        score_results = self.scorer.calculate_score(
            severity_counts,
            results.code_quality.complexity,
            self.config.max_complexity
        )
        
        # Mettre à jour le résumé avec le score et le total des problèmes
        results.summary.update(score_results)
        results.summary['total_issues'] = sum(severity_counts.values())

    async def _analyze_typescript(self, code: str, filename: str, results: AnalysisResults):
        """Analyse un fichier TypeScript de manière asynchrone."""
        self.progress_handler.update_status("🔍 Analyse du fichier TypeScript...")
        typescript_analyzer = self._get_analyzer('typescript')
        typescript_results = await self._run_in_executor(typescript_analyzer.analyze, code, filename)
        
        if not typescript_results.get('error'):
            results.security_issues = typescript_results.get('security_issues', [])
            code_quality = typescript_results.get('code_quality', {})
            results.code_quality.complexity = code_quality.get('complexity', 0)
            results.code_quality.functions = code_quality.get('functions', [])
            results.code_quality.unused_code = code_quality.get('unused_code', {})
        
        self.progress_handler.update_progress(100)

    async def _run_in_executor(self, func, *args):
        """Exécute une fonction bloquante dans un thread pool."""
        return await asyncio.get_event_loop().run_in_executor(self.executor, func, *args)

    async def _cleanup(self):
        """Nettoie les ressources de manière asynchrone."""
        self.progress_handler.cleanup()
        cleanup_tasks = [
            self._run_in_executor(analyzer.cleanup)
            for analyzer in self._analyzers.values()
        ]
        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks)
        self.executor.shutdown(wait=False)

    def analyze_file(self, file_path: str) -> AnalysisResults:
        """
        Analyse un fichier.
        
        Args:
            file_path: Chemin du fichier à analyser
            
        Returns:
            Résultats de l'analyse
        """
        try:
            # Lire le contenu du fichier
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
                
            # Créer les résultats
            results = AnalysisResults(file_path)
            results.set_code(code)
            
            # Analyser avec bandit
            bandit_results = self._run_bandit(file_path)
            if bandit_results:
                for issue in bandit_results:
                    results.add_security_issue(SecurityIssue(
                        type=issue['test_id'],
                        severity=issue['issue_severity'],
                        message=issue['issue_text'],
                        line=issue.get('line_number', 0),
                        file=file_path,
                        code=issue.get('code', '')
                    ))
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse : {str(e)}")
            return AnalysisResults.create_default()

    def _run_bandit(self, file_path: str) -> List[Dict[str, Any]]:
        """Exécute l'analyseur Bandit sur un fichier."""
        bandit_analyzer = self._get_analyzer('bandit')
        return bandit_analyzer.analyze(file_path)
