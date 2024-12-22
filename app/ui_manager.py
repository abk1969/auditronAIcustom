"""Module de gestion de l'interface utilisateur."""
import streamlit as st
import threading
import time
import random
from typing import Callable, List

class UIManager:
    """Gère l'interface utilisateur de l'analyse."""
    
    def __init__(self):
        """Initialise le gestionnaire d'UI."""
        self.progress_bar = None
        self.percentage_text = None
        self.status_text = None
        self.tips_container = None
        self.stop_thread = False
        self.tips_thread = None
        
        # Liste complète des conseils de sécurité
        self.security_tips = [
            "🔒 **Validation des entrées** : Toujours valider et assainir les entrées utilisateur",
            "🔑 **Gestion des secrets** : Ne jamais stocker de secrets en dur dans le code",
            "🛡️ **Code Review** : Faire des revues de code régulières",
            "📚 **Documentation** : Documenter les choix de sécurité et les procédures",
            "🔍 **Tests** : Implémenter des tests de sécurité automatisés",
            "🚫 **Principe du moindre privilège** : Limiter les accès au minimum nécessaire",
            "🔐 **Authentification** : Utiliser des méthodes d'authentification sécurisées",
            "🔄 **Mises à jour** : Maintenir les dépendances à jour",
            "📝 **Logging** : Mettre en place un système de logging sécurisé",
            "🛡️ **OWASP** : Suivre les bonnes pratiques OWASP",
            "🔍 **Audit** : Effectuer des audits de sécurité réguliers",
            "🔒 **HTTPS** : Toujours utiliser HTTPS en production",
            "⚡ **Rate Limiting** : Implémenter des limites de taux pour les API",
            "🔐 **Hachage** : Utiliser des algorithmes modernes pour les mots de passe",
            "🗄️ **Base de données** : Utiliser des requêtes paramétrées"
        ]
    
    def setup_ui(self):
        """Configure l'interface utilisateur."""
        col1, col2 = st.columns([10, 1])
        with col1:
            self.progress_bar = st.progress(0)
        with col2:
            self.percentage_text = st.empty()
        
        self.status_text = st.empty()
        self.tips_container = st.empty()
    
    def update_progress(self, value: int):
        """Met à jour la barre de progression."""
        if self.progress_bar and self.percentage_text:
            self.progress_bar.progress(value)
            self.percentage_text.markdown(f"**{value}%**")
    
    def update_status(self, text: str):
        """Met à jour le texte de statut."""
        if self.status_text:
            self.status_text.text(text)
    
    def start_tips(self):
        """Démarre l'affichage des conseils."""
        self.stop_thread = False
        self.tips_thread = threading.Thread(target=self._tips_cycler, daemon=True)
        self.tips_thread.start()
    
    def stop_tips(self):
        """Arrête l'affichage des conseils."""
        self.stop_thread = True
        if self.tips_thread:
            self.tips_thread.join(timeout=1)
        self.cleanup()
    
    def cleanup(self):
        """Nettoie l'interface."""
        for element in [self.progress_bar, self.percentage_text, 
                       self.status_text, self.tips_container]:
            if element:
                element.empty()
    
    def _tips_cycler(self):
        """Affiche les conseils en rotation."""
        tips_shown = set()  # Pour éviter de répéter les mêmes conseils
        
        while not self.stop_thread:
            try:
                # Réinitialiser si tous les conseils ont été montrés
                if len(tips_shown) == len(self.security_tips):
                    tips_shown.clear()
                
                # Sélectionner un conseil non montré
                available_tips = [tip for tip in self.security_tips if tip not in tips_shown]
                tip = random.choice(available_tips)
                tips_shown.add(tip)
                
                if self.tips_container and st.runtime.exists():
                    self.tips_container.info(f"{tip}")
                
                # Pause avec vérification périodique
                for _ in range(50):  # 50 * 0.1s = 5s
                    if self.stop_thread:
                        break
                    time.sleep(0.1)
                    
            except Exception as e:
                time.sleep(1) 