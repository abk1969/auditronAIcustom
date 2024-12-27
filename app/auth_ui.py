"""Interface d'authentification pour Streamlit."""
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database.models import Base, User
from core.auth.auth import AuthManager

def init_db():
    """Initialise la connexion à la base de données."""
    try:
        database_url = st.secrets.get("DATABASE_URL") or st.session_state.get("DATABASE_URL")
        if not database_url:
            database_url = "postgresql://postgres:postgres@localhost:5432/auth_db"
        
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        
        # Create test user if it doesn't exist
        auth_manager = AuthManager(db)
        test_user = db.query(User).filter_by(email='test@example.com').first()
        if not test_user:
            try:
                auth_manager.register_user(
                    email='test@example.com',
                    password='password123',
                    first_name='Test',
                    last_name='User'
                )
            except ValueError:
                # L'utilisateur existe déjà, ce n'est pas une erreur
                pass
        
        return db
    except Exception as e:
        st.error(f"Erreur de connexion à la base de données : {str(e)}")
        raise

def show_login_page():
    """Affiche la page de connexion."""
    st.title(" Connexion")
    
    # Formulaire de connexion
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        submit = st.form_submit_button("Se connecter")
        
        if submit:
            if email and password:
                db = init_db()
                auth_manager = AuthManager(db)
                success, message, user = auth_manager.authenticate_user(email, password)
                
                if success:
                    # Stocker uniquement les informations nécessaires dans la session
                    st.session_state["user"] = {
                        "id": str(user.id),  # Convertir UUID en string
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name
                    }
                    st.success("Connexion réussie!")
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Veuillez remplir tous les champs")

def show_register_page():
    """Affiche la page d'inscription."""
    st.title(" Inscription")
    
    # Formulaire d'inscription
    with st.form("register_form"):
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        confirm_password = st.text_input("Confirmer le mot de passe", type="password")
        first_name = st.text_input("Prénom")
        last_name = st.text_input("Nom")
        submit = st.form_submit_button("S'inscrire")
        
        if submit:
            if email and password and confirm_password:
                if password != confirm_password:
                    st.error("Les mots de passe ne correspondent pas")
                    return
                    
                db = init_db()
                auth_manager = AuthManager(db)
                success, message, user = auth_manager.register_user(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                
                if success:
                    st.success(message)
                    st.info("Vous pouvez maintenant vous connecter")
                else:
                    st.error(message)
            else:
                st.error("Veuillez remplir tous les champs obligatoires")

def show_auth_page():
    """Affiche la page d'authentification."""
    if "auth_page" not in st.session_state:
        st.session_state["auth_page"] = "login"
        
    # Boutons de navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Connexion", use_container_width=True):
            st.session_state["auth_page"] = "login"
    with col2:
        if st.button("Inscription", use_container_width=True):
            st.session_state["auth_page"] = "register"
            
    # Affichage de la page appropriée
    if st.session_state["auth_page"] == "login":
        show_login_page()
    else:
        show_register_page()

def is_authenticated():
    """Vérifie si l'utilisateur est authentifié."""
    return "user" in st.session_state

def get_current_user():
    """
    Retourne l'utilisateur actuellement connecté.
    
    Returns:
        dict: Les informations de l'utilisateur ou None si non connecté
    """
    user = st.session_state.get("user")
    if isinstance(user, dict):
        return user
    return None

def logout():
    """Déconnecte l'utilisateur."""
    if "user" in st.session_state:
        del st.session_state["user"]
    st.rerun()
