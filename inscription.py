import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from openpyxl import load_workbook, Workbook
import io
import json

# Configuration de la page
st.set_page_config(
    page_title="Plateforme d'inscription - Python Géologie & Mines",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Configuration Admin
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "python2025"
modules_dir = "modules_formation"

# Initialiser les variables de session
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False
if 'inscriptions_df' not in st.session_state:
    st.session_state.inscriptions_df = pd.DataFrame()
if 'selected_module' not in st.session_state:
    st.session_state.selected_module = "Module 1"
if 'show_editor' not in st.session_state:
    st.session_state.show_editor = False

# Liste des modules
MODULES = [
    "Module 1 - Introduction à Python",
    "Module 2 - Bases de la programmation",
    "Module 3 - Structures de données",
    "Module 4 - Fonctions et modules",
    "Module 5 - Manipulation de fichiers",
    "Module 6 - Bibliothèques géologiques",
    "Module 7 - Visualisation de données",
    "Module 8 - Projet final"
]

# Fonctions utilitaires
def initialiser_dossier_modules():
    """Crée le dossier modules si inexistant"""
    if not os.path.exists(modules_dir):
        os.makedirs(modules_dir)
    
    # Créer les fichiers modules s'ils n'existent pas
    for module in MODULES:
        module_file = os.path.join(modules_dir, f"{module}.txt")
        if not os.path.exists(module_file):
            with open(module_file, "w", encoding="utf-8") as f:
                f.write(f"# {module}\n\nContenu du {module.lower()} à définir...")

def initialiser_excel():
    """Crée le fichier Excel si inexistant"""
    if not os.path.exists("inscriptions.xlsx"):
        wb = Workbook()
        ws = wb.active
        ws.title = "Inscriptions"
        ws.append(["Nom", "Prénom", "Numéro CNIB", "Téléphone", "Structure", 
                   "Période souhaitée", "Sexe", "Âge", "Niveau", "Option de suivi", "Date d'inscription"])
        wb.save("inscriptions.xlsx")

def valider_telephone(tel):
    """Valide le format du numéro de téléphone"""
    pattern = r'^(\+226|00226)?\s?[0-9]{8}$'
    return re.match(pattern, tel.replace(' ', '')) is not None

def valider_cnib(cnib):
    """Valide le format du numéro CNIB"""
    pattern = r'^[A-Z]{1,2}[0-9]{6,8}$'
    return re.match(pattern, cnib.upper()) is not None

def valider_age(age):
    """Valide l'âge (doit être entre 16 et 80 ans)"""
    try:
        age_int = int(age)
        return 16 <= age_int <= 80
    except ValueError:
        return False

def valider_nom(nom):
    """Valide le nom (pas de chiffres, minimum 2 caractères)"""
    return len(nom) >= 2 and nom.replace(' ', '').replace('-', '').isalpha()

def charger_inscriptions():
    """Charge les inscriptions depuis le fichier Excel"""
    try:
        if os.path.exists("inscriptions.xlsx"):
            df = pd.read_excel("inscriptions.xlsx")
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur lors du chargement des inscriptions : {str(e)}")
        return pd.DataFrame()

def sauvegarder_inscription(data):
    """Sauvegarde une nouvelle inscription"""
    try:
        wb = load_workbook("inscriptions.xlsx")
        ws = wb["Inscriptions"]
        
        # Vérifier les doublons CNIB
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row and row[2] == data["Numéro CNIB"]:
                return False, "Ce numéro CNIB est déjà enregistré."
        
        # Ajouter la nouvelle inscription
        data_row = [
            data["Nom"], data["Prénom"], data["Numéro CNIB"], data["Téléphone"],
            data["Structure"], data["Période souhaitée"], data["Sexe"], data["Âge"],
            data["Niveau"], data["Option de suivi"], datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
        ws.append(data_row)
        wb.save("inscriptions.xlsx")
        return True, "Inscription enregistrée avec succès!"
    except Exception as e:
        return False, f"Erreur lors de l'enregistrement : {str(e)}"

def charger_contenu_module(module_name):
    """Charge le contenu d'un module spécifique"""
    module_file = os.path.join(modules_dir, f"{module_name}.txt")
    if os.path.exists(module_file):
        with open(module_file, "r", encoding="utf-8") as f:
            return f.read()
    return f"Contenu du {module_name} non trouvé."

def sauvegarder_contenu_module(module_name, content):
    """Sauvegarde le contenu d'un module spécifique"""
    module_file = os.path.join(modules_dir, f"{module_name}.txt")
    with open(module_file, "w", encoding="utf-8") as f:
        f.write(content)

# Initialiser les dossiers et fichiers
initialiser_dossier_modules()
initialiser_excel()

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 2.5rem;
        margin-bottom: 2rem;
    }
    .section-header {
        color: #A23B72;
        font-size: 1.5rem;
        margin: 1rem 0;
    }
    .nav-tabs {
        display: flex;
        justify-content: center;
        margin-bottom: 2rem;
        border-bottom: 2px solid #e0e0e0;
    }
    .nav-tab {
        padding: 15px 30px;
        margin: 0 5px;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-bottom: none;
        cursor: pointer;
        font-weight: 500;
        border-radius: 10px 10px 0 0;
        transition: all 0.3s ease;
    }
    .nav-tab:hover {
        background-color: #e9ecef;
        transform: translateY(-2px);
    }
    .nav-tab.active {
        background-color: #007bff;
        color: white;
        border-color: #007bff;
    }
    .module-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-bottom: 20px;
        justify-content: center;
    }
    .module-btn {
        padding: 10px 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        cursor: pointer;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .module-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    .module-btn.active {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        transform: translateY(-1px);
    }
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 10px 0;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
    }
    .module-content {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #007bff;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown('<h1 class="main-header">🐍 Plateforme d\'inscription - Python Géologie & Mines</h1>', unsafe_allow_html=True)

# Navigation horizontale
st.markdown("""
<div class="nav-tabs">
    <div class="nav-tab">📘 Contenu Formation</div>
    <div class="nav-tab">📝 Inscription</div>
    <div class="nav-tab">📊 Statistiques</div>
    <div class="nav-tab">👤 Admin</div>
</div>
""", unsafe_allow_html=True)

# Sélection de page avec boutons
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📘 Contenu Formation", use_container_width=True):
        st.session_state.page = "contenu"

with col2:
    if st.button("📝 Inscription", use_container_width=True):
        st.session_state.page = "inscription"

with col3:
    if st.button("📊 Statistiques", use_container_width=True):
        st.session_state.page = "statistiques"

with col4:
    if st.button("👤 Admin", use_container_width=True):
        st.session_state.page = "admin"

# Initialiser la page par défaut
if 'page' not in st.session_state:
    st.session_state.page = "contenu"

# ==================== SECTION ADMIN ====================
if st.session_state.page == "admin":
    st.markdown('<h2 class="section-header">👤 Connexion Admin</h2>', unsafe_allow_html=True)
    
    if not st.session_state.admin_logged_in:
        with st.form("login_form"):
            st.write("Connectez-vous pour accéder aux fonctions administrateur")
            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password")
            submit_login = st.form_submit_button("Se connecter")
            
            if submit_login:
                if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                    st.session_state.admin_logged_in = True
                    st.success("Connexion réussie ! Vous êtes maintenant connecté en tant qu'admin.")
                    st.rerun()
                else:
                    st.error("Nom d'utilisateur ou mot de passe incorrect.")
    else:
        st.success("Vous êtes connecté en tant qu'admin.")
        if st.button("Se déconnecter"):
            st.session_state.admin_logged_in = False
            st.rerun()

# ==================== SECTION CONTENU FORMATION ====================
elif st.session_state.page == "contenu":
    st.markdown('<h2 class="section-header">📘 Contenu de la Formation</h2>', unsafe_allow_html=True)
    
    # Boutons de sélection des modules
    st.markdown("### Sélectionnez un module :")
    
    # Créer les boutons de modules en grille
    cols = st.columns(4)
    for i, module in enumerate(MODULES):
        with cols[i % 4]:
            if st.button(f"📖 {module.split(' - ')[0]}", 
                        key=f"module_{i}",
                        use_container_width=True):
                st.session_state.selected_module = module
                st.session_state.show_editor = False
    
    # Afficher le contenu du module sélectionné
    st.markdown(f"### 📚 {st.session_state.selected_module}")
    
    contenu = charger_contenu_module(st.session_state.selected_module)
    
    st.markdown(f"""
    <div class="module-content">
        <h4>📄 Contenu du {st.session_state.selected_module}</h4>
        <pre style="white-space: pre-wrap; font-family: inherit;">{contenu}</pre>
    </div>
    """, unsafe_allow_html=True)
    
    # Fonctions admin pour modifier le contenu
    if st.session_state.admin_logged_in:
        st.markdown("---")
        st.markdown("### 🔧 Fonctions Admin")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📁 Téléverser un fichier")
            uploaded_file = st.file_uploader("Choisir un fichier texte", type=['txt'])
            if uploaded_file is not None:
                content = uploaded_file.read().decode('utf-8')
                if st.button("Téléverser pour ce module"):
                    sauvegarder_contenu_module(st.session_state.selected_module, content)
                    st.success(f"Contenu du {st.session_state.selected_module} mis à jour avec succès!")
                    st.rerun()
        
        with col2:
            st.subheader("✏️ Modifier le contenu")
            if st.button("Ouvrir l'éditeur"):
                st.session_state.show_editor = True
        
        # Éditeur de contenu
        if st.session_state.show_editor:
            st.markdown("---")
            st.subheader(f"✏️ Éditeur - {st.session_state.selected_module}")
            nouveau_contenu = st.text_area("Modifier le contenu", value=contenu, height=400)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Sauvegarder"):
                    sauvegarder_contenu_module(st.session_state.selected_module, nouveau_contenu)
                    st.success(f"Contenu du {st.session_state.selected_module} sauvegardé avec succès!")
                    st.session_state.show_editor = False
                    st.rerun()
            
            with col2:
                if st.button("❌ Annuler"):
                    st.session_state.show_editor = False
                    st.rerun()
    
    else:
        st.info("💡 Connectez-vous en tant qu'admin pour modifier le contenu des modules.")

# ==================== SECTION INSCRIPTION ====================
elif st.session_state.page == "inscription":
    st.markdown('<h2 class="section-header">📝 Formulaire d\'inscription</h2>', unsafe_allow_html=True)
    
    with st.form("inscription_form"):
        st.write("Veuillez remplir tous les champs ci-dessous :")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nom = st.text_input("Nom *", help="Saisir en lettres uniquement")
            prenom = st.text_input("Prénom *", help="Saisir en lettres uniquement")
            cnib = st.text_input("Numéro CNIB *", help="Format attendu (ex: B1234567)")
            telephone = st.text_input("Téléphone *", help="Format international (+226) ou national")
            structure = st.text_input("Structure *")
            periode = st.text_input("Période souhaitée *")
        
        with col2:
            sexe = st.selectbox("Sexe *", ["", "Homme", "Femme"])
            age = st.number_input("Âge *", min_value=16, max_value=80, value=20)
            niveau = st.selectbox("Niveau *", ["", "Débutant", "Intermédiaire", "Avancé"])
            option_suivi = st.selectbox("Option de suivi *", ["", "Présentiel", "En ligne", "Hybride"])
        
        st.markdown("**Instructions :**")
        st.markdown("""
        - Nom et Prénom : Saisir en lettres uniquement
        - Numéro CNIB : Format attendu (ex: B1234567)
        - Téléphone : Format international (+226) ou national
        - Âge : Entre 16 et 80 ans
        - Tous les champs sont obligatoires
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("✅ S'inscrire", type="primary")
        with col2:
            reset = st.form_submit_button("🔄 Réinitialiser")
        
        if submit:
            # Validation
            erreurs = []
            
            if not nom or not prenom or not cnib or not telephone or not structure or not periode:
                erreurs.append("Tous les champs sont obligatoires.")
            
            if not sexe or not niveau or not option_suivi:
                erreurs.append("Veuillez sélectionner toutes les options.")
            
            if nom and not valider_nom(nom):
                erreurs.append("Le nom doit contenir uniquement des lettres (minimum 2 caractères).")
            
            if prenom and not valider_nom(prenom):
                erreurs.append("Le prénom doit contenir uniquement des lettres (minimum 2 caractères).")
            
            if cnib and not valider_cnib(cnib):
                erreurs.append("Format CNIB invalide (ex: B1234567).")
            
            if telephone and not valider_telephone(telephone):
                erreurs.append("Format téléphone invalide (ex: +226 70123456 ou 70123456).")
            
            if not valider_age(age):
                erreurs.append("L'âge doit être entre 16 et 80 ans.")
            
            if erreurs:
                for erreur in erreurs:
                    st.error(erreur)
            else:
                # Sauvegarder l'inscription
                data = {
                    "Nom": nom,
                    "Prénom": prenom,
                    "Numéro CNIB": cnib,
                    "Téléphone": telephone,
                    "Structure": structure,
                    "Période souhaitée": periode,
                    "Sexe": sexe,
                    "Âge": age,
                    "Niveau": niveau,
                    "Option de suivi": option_suivi
                }
                
                success, message = sauvegarder_inscription(data)
                if success:
                    st.success(message)
                    st.balloons()
                else:
                    st.error(message)

# ==================== SECTION STATISTIQUES ====================
elif st.session_state.page == "statistiques":
    st.markdown('<h2 class="section-header">📊 Statistiques d\'inscription</h2>', unsafe_allow_html=True)
    
    if not st.session_state.admin_logged_in:
        st.warning("Vous devez être connecté en tant qu'admin pour voir les statistiques.")
        st.info("Rendez-vous dans la section Admin pour vous connecter.")
    else:
        # Charger les données
        df = charger_inscriptions()
        
        if df.empty:
            st.info("Aucune inscription trouvée.")
        else:
            # Métriques principales
            st.subheader("📈 Métriques principales")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total inscrits", len(df))
            
            with col2:
                age_moyen = df['Âge'].mean() if 'Âge' in df.columns else 0
                st.metric("Âge moyen", f"{age_moyen:.1f} ans")
            
            with col3:
                hommes = len(df[df['Sexe'] == 'Homme']) if 'Sexe' in df.columns else 0
                st.metric("Hommes", hommes)
            
            with col4:
                femmes = len(df[df['Sexe'] == 'Femme']) if 'Sexe' in df.columns else 0
                st.metric("Femmes", femmes)
            
            # Graphiques
            st.subheader("📊 Visualisations")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if 'Sexe' in df.columns:
                    fig_sexe = px.pie(df, names='Sexe', title='Répartition par sexe')
                    st.plotly_chart(fig_sexe, use_container_width=True)
            
            with col2:
                if 'Niveau' in df.columns:
                    fig_niveau = px.pie(df, names='Niveau', title='Répartition par niveau')
                    st.plotly_chart(fig_niveau, use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if 'Option de suivi' in df.columns:
                    fig_option = px.bar(df['Option de suivi'].value_counts().reset_index(), 
                                       x='index', y='Option de suivi',
                                       title='Répartition par option de suivi')
                    st.plotly_chart(fig_option, use_container_width=True)
            
            with col2:
                if 'Âge' in df.columns:
                    fig_age = px.histogram(df, x='Âge', title='Distribution des âges')
                    st.plotly_chart(fig_age, use_container_width=True)
            
            # Top structures
            if 'Structure' in df.columns:
                st.subheader("🏢 Top 10 des structures")
                top_structures = df['Structure'].value_counts().head(10)
                fig_structures = px.bar(x=top_structures.values, y=top_structures.index,
                                       orientation='h', title='Top 10 des structures')
                st.plotly_chart(fig_structures, use_container_width=True)
            
            # Tableau des inscriptions
            st.subheader("📋 Liste des inscriptions")
            st.dataframe(df, use_container_width=True)
            
            # Export des données
            st.subheader("📤 Export des données")
            col1, col2 = st.columns(2)
            
            with col1:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Télécharger CSV",
                    data=csv,
                    file_name=f"inscriptions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Export Excel
                buffer = io.BytesIO()
                df.to_excel(buffer, index=False)
                buffer.seek(0)
                
                st.download_button(
                    label="Télécharger Excel",
                    data=buffer,
                    file_name=f"inscriptions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; margin-top: 2rem;'>
    <p>© 2025 Plateforme d'inscription - Python Géologie & Mines</p>
    <p>Développé avec ❤️ et Streamlit</p>
    <p>Tel :+266 77 77 77 77/88 88 88 88</p>
    <p>Email: formation@gmail.com/p>
</div>
""", unsafe_allow_html=True)
