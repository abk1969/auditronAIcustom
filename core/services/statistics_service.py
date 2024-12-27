"""
Service for managing analysis history and usage statistics
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from AuditronAI.core.logger import setup_logging
from AuditronAI.core.history import AnalysisHistory
from AuditronAI.core.usage_stats import UsageStats

logger = setup_logging()

class StatisticsService:
    """Service responsible for managing analysis history and usage statistics."""
    
    def __init__(self):
        """Initialize the statistics service with history and usage stats."""
        self.history = AnalysisHistory()
        self.usage_stats = UsageStats()
    
    def record_analysis(self, result: Dict[str, Any], service: str = 'openai') -> None:
        """
        Record an analysis result in history and update usage stats.
        
        Args:
            result (Dict[str, Any]): Analysis result to record
            service (str): AI service used for analysis
        """
        try:
            # Extract values safely with defaults
            filename = result.get('file', 'unknown')
            security_data = result.get('security', {})
            if isinstance(security_data, dict):
                summary = security_data.get('summary', {})
                score = summary.get('score', 0.0) if isinstance(summary, dict) else 0.0
                issues = security_data.get('security_issues', [])
                issues_count = len(issues) if isinstance(issues, list) else 0
                code_quality = security_data.get('code_quality', {})
                complexity = code_quality.get('complexity', 0.0) if isinstance(code_quality, dict) else 0.0
            else:
                score = 0.0
                issues_count = 0
                complexity = 0.0
            
            # Record in history
            self.history.add_record(
                filename=filename,
                score=score,
                issues_count=issues_count,
                complexity=complexity,
                details=result
            )
            
            # Update usage stats
            self.usage_stats.record_analysis(service)
            
            logger.info(f"Analysis recorded for {filename}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement des statistiques: {str(e)}")
            raise
    
    def get_analysis_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get recent analysis history.
        
        Args:
            limit (Optional[int]): Maximum number of entries to return
            
        Returns:
            List[Dict[str, Any]]: List of analysis history entries
        """
        try:
            return self.history.get_records(limit)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'historique: {str(e)}")
            return []
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics.
        
        Returns:
            Dict[str, Any]: Dictionary containing usage statistics
        """
        try:
            return {
                'total_analyses': self.usage_stats.get_total_analyses(),
                'analyses_by_service': self.usage_stats.get_analyses_by_service(),
                'analyses_by_date': self.usage_stats.get_analyses_by_date(),
                'error_rate': self.usage_stats.get_error_rate(),
                'last_analysis': self.usage_stats.get_last_analysis_time()
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques: {str(e)}")
            return {}
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """
        Get summary statistics for dashboard display.
        
        Returns:
            Dict[str, Any]: Dictionary containing summary statistics
        """
        try:
            history_entries = self.get_analysis_history()
            usage_stats = self.get_usage_stats()
            
            return {
                'total_files_analyzed': usage_stats['total_analyses'],
                'average_score': sum(entry['score'] for entry in history_entries) / len(history_entries) if history_entries else 0,
                'total_issues_found': sum(entry['issues_count'] for entry in history_entries),
                'average_complexity': sum(entry['complexity'] for entry in history_entries) / len(history_entries) if history_entries else 0,
                'error_rate': usage_stats['error_rate'],
                'last_analysis': usage_stats['last_analysis']
            }
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques résumées: {str(e)}")
            return {}
    
    def clear_history(self) -> bool:
        """
        Clear analysis history.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.history.clear()
            logger.info("Historique effacé")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'effacement de l'historique: {str(e)}")
            return False
    
    def export_statistics(self) -> Dict[str, Any]:
        """
        Export all statistics data.
        
        Returns:
            Dict[str, Any]: Dictionary containing all statistics data
        """
        try:
            return {
                'history': self.get_analysis_history(),
                'usage_stats': self.get_usage_stats(),
                'summary': self.get_summary_stats(),
                'export_time': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'export des statistiques: {str(e)}")
            return {}
