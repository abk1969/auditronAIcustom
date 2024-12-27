"""Gestionnaire principal pour l'analyse de sécurité."""
import asyncio
import tempfile
from typing import Dict, Any, Optional, List
from pathlib import Path

from .analyzers.interfaces import (
    AnalyzerType,
    AnalyzerContext,
    IAnalyzer
)
from .analyzers.factory import AnalyzerRegistry
from .config.analyzer_config import AnalyzerConfig
from .logger import logger
from .analysis_progress import ProgressHandler, DefaultProgressHandler
from .scoring import SecurityScorer
from .analysis_results import AnalysisResults

class SecurityManager:
    """Gestionnaire principal pour l'analyse de sécurité du code."""
    
    def __init__(
        self,
        progress_handler: Optional[ProgressHandler] = None,
        config: Optional[AnalyzerConfig] = None
    ):
        """
        Initialise le gestionnaire de sécurité.
        
        Args:
            progress_handler: Gestionnaire de progression optionnel
            config: Configuration optionnelle
        """
        self.config = config or AnalyzerConfig.from_env()
        self.progress_handler = progress_handler or DefaultProgressHandler()
        self.scorer = SecurityScorer(self.config.thresholds)
        self.factory = AnalyzerRegistry.get_instance()
        
    async def analyze_code(self, code: str, filename: str = "code.py") -> AnalysisResults:
        """
        Analyse complète du code source.
        
        Args:
            code: Code source à analyser
            filename: Nom du fichier (utilisé pour déterminer le type)
            
        Returns:
            Résultats de l'analyse
        """
        try:
            self._setup_analysis()
            results = AnalysisResults(file=filename)
            
            # Créer un répertoire temporaire pour l'analyse
            with tempfile.TemporaryDirectory() as temp_dir:
                context = AnalyzerContext(
                    filename=filename,
                    code=code,
                    config=self.config.to_dict(),
                    temp_dir=temp_dir
                )
                
                if filename.endswith('.ts'):
                    await self._analyze_typescript(context, results)
                else:
                    # Vérifier si c'est un script
                    is_script = await self._analyze_script(context, results)
                    if not is_script:
                        # Analyse Python standard
                        await self._analyze_python(context, results)
                
                # Calculer le score final
                self._calculate_score(results)
                
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse : {str(e)}")
            return AnalysisResults.create_default()
            
        finally:
            self.progress_handler.cleanup()

    def _setup_analysis(self):
        """Configure l'interface pour l'analyse."""
        self.progress_handler.setup_ui()
        self.progress_handler.update_status("🔍 Préparation de l'analyse...")
        self.progress_handler.update_progress(10)

    async def _analyze_script(self, context: AnalyzerContext, results: AnalysisResults) -> bool:
        """
        Analyse un fichier script.
        
        Args:
            context: Contexte d'analyse
            results: Résultats à mettre à jour
            
        Returns:
            True si c'est un script, False sinon
        """
        try:
            analyzer = self.factory.create_analyzer(AnalyzerType.SCRIPT)
            await analyzer.initialize(context)
            script_results = await analyzer.analyze()
            
            if script_results.get('is_script'):
                results.security_issues = script_results.get('issues', [])
                results.code_quality.script_type = script_results.get('script_type')
                self.progress_handler.update_progress(100)
                return True
                
            return False
            
        finally:
            if analyzer:
                await analyzer.cleanup()

    async def _analyze_python(self, context: AnalyzerContext, results: AnalysisResults):
        """
        Analyse Python complète.
        
        Args:
            context: Contexte d'analyse
            results: Résultats à mettre à jour
        """
        analysis_tasks = [
            self._run_analyzer(AnalyzerType.SECURITY, context),
            self._run_analyzer(AnalyzerType.COMPLEXITY, context),
            self._run_analyzer(AnalyzerType.DEAD_CODE, context),
            self._run_analyzer(AnalyzerType.QUALITY, context)
        ]
        
        analysis_results = await asyncio.gather(*analysis_tasks)
        
        # Mise à jour des résultats
        security, complexity, dead_code, quality = analysis_results
        
        if not security.get('error'):
            results.security_issues = security.get('issues', [])
            
        if not complexity.get('error'):
            results.code_quality.complexity = complexity.get('average_complexity', 0)
            results.code_quality.functions = complexity.get('functions', [])
            results.code_quality.complex_functions = complexity.get('complex_functions', [])
            
        if not dead_code.get('error'):
            results.code_quality.unused_code = {
                'variables': dead_code.get('unused_vars', []),
                'functions': dead_code.get('unused_funcs', []),
                'classes': dead_code.get('unused_classes', []),
                'imports': dead_code.get('unused_imports', []),
                'stats': dead_code.get('stats', {})
            }
            
        if not quality.get('error'):
            results.code_quality.style_issues = quality.get('messages', [])
            results.code_quality.quality_summary = quality.get('summary', {})

    async def _analyze_typescript(self, context: AnalyzerContext, results: AnalysisResults):
        """
        Analyse TypeScript.
        
        Args:
            context: Contexte d'analyse
            results: Résultats à mettre à jour
        """
        try:
            analyzer = self.factory.create_analyzer(AnalyzerType.TYPESCRIPT)
            await analyzer.initialize(context)
            typescript_results = await analyzer.analyze()
            
            if not typescript_results.get('error'):
                results.security_issues = typescript_results.get('security_issues', [])
                code_quality = typescript_results.get('code_quality', {})
                results.code_quality.complexity = code_quality.get('complexity', 0)
                results.code_quality.functions = code_quality.get('functions', [])
                results.code_quality.unused_code = code_quality.get('unused_code', {})
            
            self.progress_handler.update_progress(100)
            
        finally:
            if analyzer:
                await analyzer.cleanup()

    async def _run_analyzer(
        self,
        analyzer_type: AnalyzerType,
        context: AnalyzerContext
    ) -> Dict[str, Any]:
        """
        Exécute un analyseur spécifique.
        
        Args:
            analyzer_type: Type d'analyseur à utiliser
            context: Contexte d'analyse
            
        Returns:
            Résultats de l'analyse
        """
        try:
            analyzer = self.factory.create_analyzer(analyzer_type)
            await analyzer.initialize(context)
            return await analyzer.analyze()
            
        except Exception as e:
            logger.error(f"Erreur avec l'analyseur {analyzer_type}: {str(e)}")
            return {"error": True, "message": str(e)}
            
        finally:
            if analyzer:
                await analyzer.cleanup()

    def _calculate_score(self, results: AnalysisResults):
        """
        Calcule le score final.
        
        Args:
            results: Résultats à mettre à jour
        """
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
        
        results.summary.update(score_results)
        results.summary['total_issues'] = sum(severity_counts.values())
