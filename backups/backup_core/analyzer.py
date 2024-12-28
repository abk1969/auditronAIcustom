"""Module d'analyse de code."""
from app.core.logger import logger
from app.core.security.security_analyzer import SecurityAnalyzer
from app.core.quality.code_analyzer import CodeQualityAnalyzer

def analyze_code(code: str, filename: str = "code.py") -> dict:
    """Analyse un code Python donné.
    
    Args:
        code: Code à analyser
        filename: Nom du fichier
        
    Returns:
        Résultats de l'analyse incluant:
        - Statistiques de base
        - Analyse de sécurité
        - Analyse de qualité du code
    """
    try:
        # Analyse de sécurité
        security_analyzer = SecurityAnalyzer()
        security_results = security_analyzer.analyze(code, filename)
        
        # Analyse de qualité
        quality_analyzer = CodeQualityAnalyzer()
        quality_results = quality_analyzer.analyze(code, filename)
        
        # Statistiques de base
        lines = code.split('\n')
        stats = {
            'Lignes de code': len(lines),
            'Caractères': len(code),
            'Fonctions': len([l for l in lines if l.strip().startswith('def ')]),
            'Classes': len([l for l in lines if l.strip().startswith('class ')])
        }
        
        # Score global combinant sécurité et qualité
        global_score = (security_results['score'] + quality_results['quality_score']) / 2
        
        # Résultat complet
        result = {
            "file": filename,
            "code": code,
            "stats": stats,
            "security": security_results,
            "quality": quality_results,
            "global_score": round(global_score, 2)
        }
        
        logger.info(f"Analyse réussie pour {filename}")
        return result
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse: {str(e)}")
        raise
