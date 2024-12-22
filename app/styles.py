def load_security_report_styles():
    """Charge les styles CSS pour le rapport de sécurité."""
    return """
        <style>
        .security-box {
            background: #2E2E2E;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .security-box h3 {
            color: white;
            margin-top: 0;
        }
        .security-box ul {
            list-style-type: none;
            padding-left: 0;
            margin: 0;
        }
        .security-box li {
            padding: 8px 12px;
            margin: 5px 0;
            background: #1a1a1a;
            border-radius: 5px;
            color: #DDD;
            transition: all 0.2s ease;
        }
        .issue-box {
            background: #1a1a1a;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            border-left: 4px solid var(--severity-color);
        }
        .metric-box {
            text-align: center;
            padding: 10px;
            border-radius: 8px;
            background: #1a1a1a;
        }
        .explanation-box {
            background: #2E2E2E;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
            border-left: 4px solid #00C851;
        }
        .explanation-box h3 {
            color: white;
            margin-top: 0;
        }
        .explanation-box code {
            background: #1a1a1a;
            padding: 5px;
            border-radius: 4px;
        }
        .security-box li:hover {
            transform: translateX(5px);
            background: #252525;
        }
        
        .issue-box:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            transition: all 0.2s ease;
        }
        
        .metric-box h2 {
            font-size: 2.5em;
            margin: 10px 0;
        }
        
        code {
            font-family: 'Consolas', 'Monaco', monospace;
        }
        
        /* Styles pour les expanders */
        .streamlit-expanderHeader {
            background: #2E2E2E !important;
            border-radius: 8px !important;
            color: white !important;
        }
        
        .streamlit-expanderContent {
            background: #1a1a1a !important;
            border: none !important;
            border-radius: 0 0 8px 8px !important;
            padding: 15px !important;
        }
        
        /* Styles pour les métriques */
        .metric-container {
            background: #2E2E2E;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            transition: all 0.2s ease;
            cursor: help;
        }
        
        .metric-container:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }
        
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #00C851;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .metric-label {
            color: #DDD;
            margin-top: 5px;
            font-weight: 500;
        }
        
        /* Styles pour les graphiques */
        .plot-container {
            background: #2E2E2E;
            padding: 20px;
            border-radius: 10px;
            margin: 15px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        /* Amélioration des tooltips */
        .tooltip {
            background: white !important;
            color: black !important;
            padding: 8px 12px !important;
            border-radius: 6px !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
        }
        
        .metric-help {
            font-size: 0.8em;
            color: #666;
            margin-top: 5px;
            opacity: 0;
            transition: opacity 0.2s ease;
        }
        
        .metric-container:hover .metric-help {
            opacity: 1;
        }
        
        /* Amélioration des expanders */
        .streamlit-expanderHeader:hover {
            background: #3E3E3E !important;
            transform: translateX(5px);
            transition: all 0.2s ease;
        }
        
        .streamlit-expanderContent {
            background: #1a1a1a !important;
            border: none !important;
            border-radius: 0 0 8px 8px !important;
            padding: 20px !important;
            margin-top: 5px !important;
        }
        
        /* Styles pour les résultats détaillés */
        .detail-section {
            background: #2E2E2E;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
        
        .detail-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 1px solid #3E3E3E;
        }
        
        .detail-title {
            color: white;
            font-size: 1.1em;
            font-weight: 500;
        }
        
        .detail-content {
            color: #DDD;
            font-size: 0.9em;
            line-height: 1.5;
        }
        
        /* Animations */
        @keyframes slideIn {
            from {
                transform: translateX(-10px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        /* Appliquer les animations */
        .detail-section {
            animation: slideIn 0.3s ease-out;
        }
        
        .metric-container {
            animation: fadeIn 0.5s ease-out;
        }
        
        /* Améliorer les transitions */
        .detail-section:hover {
            transform: translateX(5px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            transition: all 0.2s ease;
        }
        
        .metric-container:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        
        /* Messages de statut */
        .success-message {
            background: #00C851;
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            animation: fadeIn 0.5s ease-out;
            box-shadow: 0 2px 4px rgba(0,200,81,0.2);
        }
        
        .error-message {
            background: #ff4444;
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            animation: fadeIn 0.5s ease-out;
            box-shadow: 0 2px 4px rgba(255,68,68,0.2);
        }
        
        .info-message {
            background: #33b5e5;
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            animation: fadeIn 0.5s ease-out;
            box-shadow: 0 2px 4px rgba(51,181,229,0.2);
        }
        
        /* Améliorer les messages */
        .success-message, .error-message, .info-message {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .message-icon {
            font-size: 1.5em;
        }
        </style>
    """ 