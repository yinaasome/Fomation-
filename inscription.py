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
from PIL import Image

# Configuration de la page
st.set_page_config(
    page_title="Plateforme d'inscription - Python Géologie & Mines",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration Admin
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "python2025"
modules_dir = "modules_formation"
config_file = "site_config.json"
ADMIN_ONLY_PAGES = ["admin", "statistiques"]

# Initialiser les variables de session
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False
if 'inscriptions_df' not in st.session_state:
    st.session_state.inscriptions_df = pd.DataFrame()
if 'selected_module' not in st.session_state:
    st.session_state.selected_module = "Module 1"
if 'show_editor' not in st.session_state:
    st.session_state.show_editor = False
if 'menu_page' not in st.session_state:
    st.session_state.menu_page = "accueil"
if 'show_description_editor' not in st.session_state:
    st.session_state.show_description_editor = False
if 'sidebar_collapsed' not in st.session_state:
    st.session_state.sidebar_collapsed = False

# Liste des modules
MODULES = [
    "Module 1 - Introduction à Python",
    "Module 3 - Bases de la programmation",
    "Module 2 - Structures de données",
    "Module 5 - Fonctions et modules",
    "Module 4 - Manipulation de fichiers",
    "Module 7 - Bibliothèques géologiques",
    "Module 6 - Visualisation de données",
    "Module 8 - Projet final"
]

# Configuration par défaut du site
DEFAULT_CONFIG = {
    "site_title": "Formation Python pour Géologie & Mines",
    "site_description": """

# 🐍 **Bienvenue à la Formation Python pour les Sciences Géologiques & Minières**

## 💡 Pourquoi apprendre Python dans le domaine de la géologie et des mines ?

Python est aujourd'hui **le langage incontournable** pour l'analyse et la visualisation de données scientifiques. Dans les domaines de la géologie et des mines, il permet de :

🔹 Automatiser le traitement de données géophysiques et géochimiques
🔹 Cartographier et modéliser des structures géologiques
🔹 Simuler des processus miniers et environnementaux
🔹 Gérer et analyser des données volumineuses avec précision
🔹 Améliorer la prise de décision grâce à des visualisations interactives

**Bref, Python devient un véritable outil d'aide à la décision dans le secteur géo-minier.**



## 🎯 **Objectifs de la formation**

À la fin de cette formation, vous serez capable de :

✅ **Maîtriser les bases de Python**

* Syntaxe simple et intuitive
* Structures de données : listes, dictionnaires, tableaux
* Fonctions, boucles, conditions
* Programmation orientée objet

✅ **Appliquer Python aux problématiques géo-minières**

* Traitement et nettoyage de données issues du terrain
* Analyse statistique de données géologiques
* Visualisation de forages, profils géophysiques, cartes, etc.
* Création de modèles géologiques simplifiés

✅ **Utiliser les bibliothèques incontournables**

* **NumPy** & **Pandas** : Manipulation et analyse de données
* **Matplotlib** & **Plotly** : Graphiques et cartes interactives
* **Geopandas**, **PyGSLIB**, **lasio**, etc. : Pour les applications spécifiques en géosciences



## 👤 **À qui s'adresse cette formation ?**

Cette formation est conçue pour toute personne souhaitant intégrer le numérique et la programmation dans les métiers de la géologie et des mines :

👨‍🎓 **Étudiants** en géologie, génie minier, ou environnement
👷‍♂️ **Professionnels** du secteur minier, pétrolier ou géotechnique
🔬 **Chercheurs** en sciences de la Terre
🛠 **Ingénieurs** en exploration, production ou aménagement

*Aucun niveau avancé en programmation n'est requis. Vous apprendrez de zéro !*


## 📚 **Organisation de la formation**

📅 **Durée** : 8 modules répartis sur 4 semaines
🏫 **Format** : Présentiel ou 100% en ligne
🖥 **Prérequis** : Aisance avec l'ordinateur (Windows/Linux)
🎓 **Attestation** : Certificat délivré à la fin de la formation



## 💥 **Les plus de notre formation**

🔥 **Formation 100% adaptée au terrain géo-minier**
🔥 **Encadrement par des experts en géologie et data science**
🔥 **Exercices pratiques avec des jeux de données réels**
🔥 **Support pédagogique clair, structuré et accessible à vie**
🔥 **Accès à une communauté d'apprentissage et de collaboration**



## 📞 **Contactez-nous dès maintenant !**

📧 **Email** : [formation@gmail.com](mailto:formation@gmail.com)
📱 **Téléphone** : +226 77 77 77 77 / 88 88 88 88
🌐 **Site web** : *En construction — restez connecté !*


### 🧭 Rejoignez-nous et entrez dans le monde de la **géologie numérique avec Python**.

**➡️ Une compétence d'avenir — Une opportunité unique — Un tremplin pour votre carrière !**
Alors
*Rejoignez-nous pour une expérience d'apprentissage unique et enrichissante !*
    """,
    "site_image": None
}

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

def initialiser_config():
    """Crée le fichier de configuration si inexistant"""
    if not os.path.exists(config_file):
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)

def charger_config():
    """Charge la configuration du site"""
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return DEFAULT_CONFIG

def sauvegarder_config(config):
    """Sauvegarde la configuration du site"""
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

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
    return f"Veuillez cliquer sur le  {module_name} pour voir le Contenu."

def sauvegarder_contenu_module(module_name, content):
    """Sauvegarde le contenu d'un module spécifique"""
    module_file = os.path.join(modules_dir, f"{module_name}.txt")
    with open(module_file, "w", encoding="utf-8") as f:
        f.write(content)

def generer_fichier_excel_download():
    """Génère un fichier Excel téléchargeable avec toutes les inscriptions"""
    try:
        df = charger_inscriptions()
        if df.empty:
            return None
        
        # Créer un buffer en mémoire
        buffer = io.BytesIO()
        
        # Créer le fichier Excel avec pandas
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Inscriptions', index=False)
            
            # Ajouter une feuille de statistiques
            if not df.empty:
                # Statistiques générales
                stats_data = {
                    'Statistique': [
                        'Total inscriptions',
                        'Hommes',
                        'Femmes',
                        'Âge moyen',
                        'Niveau débutant',
                        'Niveau intermédiaire',
                        'Niveau avancé',
                        'Présentiel',
                        'En ligne',
                        'Hybride'
                    ],
                    'Valeur': [
                        len(df),
                        len(df[df['Sexe'] == 'Homme']),
                        len(df[df['Sexe'] == 'Femme']),
                        round(df['Âge'].mean(), 1),
                        len(df[df['Niveau'] == 'Débutant']),
                        len(df[df['Niveau'] == 'Intermédiaire']),
                        len(df[df['Niveau'] == 'Avancé']),
                        len(df[df['Option de suivi'] == 'Présentiel']),
                        len(df[df['Option de suivi'] == 'En ligne']),
                        len(df[df['Option de suivi'] == 'Hybride'])
                    ]
                }
                
                stats_df = pd.DataFrame(stats_data)
                stats_df.to_excel(writer, sheet_name='Statistiques', index=False)
        
        buffer.seek(0)
        return buffer.getvalue()
    
    except Exception as e:
        st.error(f"Erreur lors de la génération du fichier : {str(e)}")
        return None

def generer_rapport_csv():
    """Génère un rapport CSV téléchargeable"""
    try:
        df = charger_inscriptions()
        if df.empty:
            return None
        
        # Convertir en CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8')
        csv_buffer.seek(0)
        return csv_buffer.getvalue()
    
    except Exception as e:
        st.error(f"Erreur lors de la génération du CSV : {str(e)}")
        return None

# Initialiser les dossiers et fichiers
initialiser_dossier_modules()
initialiser_excel()
initialiser_config()

# CSS personnalisé avec sidebar moderne et bouton de réduction
st.markdown("""
<style>
    /* Toggle button for sidebar collapse */
    .sidebar-toggle {
        position: fixed;
        top: 1rem;
        left: 1rem;
        z-index: 9999;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 15px;
        font-size: 1.2rem;
        font-weight: bold;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    
    .sidebar-toggle:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    /* Sidebar styling */
    .stSidebar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        transition: all 0.3s ease;
    }
    
    .stSidebar.collapsed {
        width: 0 !important;
        min-width: 0 !important;
    }
    
    .stSidebar > div {
        padding-top: 3rem;
    }
    
    .sidebar-title {
        color: white;
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: rgba(255,255,255,0.1);
        padding: 15px;
        border-radius: 10px;
    }
    
    .sidebar-button {
        width: 100%;
        padding: 15px;
        margin: 8px 0;
        border: none;
        border-radius: 10px;
        font-size: 1.1rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: flex-start;
    }
    
    .sidebar-button:hover {
        transform: translateX(5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .sidebar-button.active {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    
    .sidebar-button:not(.active) {
        background: rgba(255,255,255,0.1);
        color: white;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .sidebar-admin-status {
        background: rgba(255,255,255,0.1);
        color: white;
        padding: 10px;
        border-radius: 8px;
        margin: 1rem 0;
        text-align: center;
    }
    
    .sidebar-contact {
        background: rgba(255,255,255,0.05);
        color: white;
        padding: 15px;
        border-radius: 8px;
        margin-top: 2rem;
        font-size: 0.9rem;
    }
    
    /* Main content styling with margin adjustment for collapsed sidebar */
    .main-content {
        transition: all 0.3s ease;
        margin-left: 0;
    }
    
    .main-content.expanded {
        margin-left: 0;
    }
    
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 2.5rem;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .section-header {
        color: #A23B72;
        font-size: 1.8rem;
        margin: 1rem 0;
        border-bottom: 3px solid #A23B72;
        padding-bottom: 10px;
    }
    
    .page-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    .description-content {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 30px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .admin-section {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
        border-left: 5px solid #ff6b6b;
    }
    
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 10px 0;
    }
    
    .module-content {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #007bff;
        margin: 20px 0;
    }
    
    .module-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 15px;
        margin: 20px 0;
    }
    
    .module-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        border: none;
        font-size: 1rem;
    }
    
    .module-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
    
    .module-card.active {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    }
    
    .site-image {
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        margin: 20px 0;
    }
    
    .cta-section {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px;
        border-radius: 15px;
        color: white;
        margin: 30px 0;
    }
    
    .footer {
        text-align: center;
        color: #666;
        margin-top: 3rem;
        padding: 2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
    }
    
    .download-section {
        background: linear-gradient(135deg, #e8f5e8 0%, #b8e6b8 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
        border-left: 5px solid #28a745;
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Bouton de réduction/expansion de la sidebar
col_toggle, col_spacer = st.columns([1, 9])
with col_toggle:
    if st.button("≡", key="sidebar_toggle", help="Réduire/Développer le menu"):
        st.session_state.sidebar_collapsed = not st.session_state.sidebar_collapsed
        st.rerun()

# SIDEBAR MENU (Conditionnel selon l'état de réduction)
config = charger_config()

# Modifier la partie sidebar pour cacher "Statistiques" si pas admin
if not st.session_state.sidebar_collapsed:
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-title">
            🐍 Menu Principal
        </div>
        """, unsafe_allow_html=True)
        
        # Boutons de navigation
        if st.button("🏠 Accueil", key="nav_accueil", use_container_width=True):
            st.session_state.menu_page = "accueil"
            st.rerun()
        
        if st.button("📘 Contenu Formation", key="nav_contenu", use_container_width=True):
            st.session_state.menu_page = "contenu"
            st.rerun()
        
        if st.button("📝 Inscription", key="nav_inscription", use_container_width=True):
            st.session_state.menu_page = "inscription"
            st.rerun()
        
        # Afficher le bouton Statistiques seulement pour les admins
        if st.session_state.admin_logged_in:
            if st.button("📊 Statistiques", key="nav_stats", use_container_width=True):
                st.session_state.menu_page = "statistiques"
                st.rerun()
        
        if st.button("👤 Administration", key="nav_admin", use_container_width=True):
            st.session_state.menu_page = "admin"
            st.rerun()

# Modifier la partie navigation horizontale (quand sidebar réduite) de la même façon
if st.session_state.sidebar_collapsed:
    st.markdown("### 🧭 Navigation")
    col_count = 4 if not st.session_state.admin_logged_in else 5
    cols = st.columns(col_count)
    
    with cols[0]:
        if st.button("🏠 Accueil", key="nav_accueil_h", use_container_width=True):
            st.session_state.menu_page = "accueil"
            st.rerun()
    
    with cols[1]:
        if st.button("📘 Formation", key="nav_contenu_h", use_container_width=True):
            st.session_state.menu_page = "contenu"
            st.rerun()
    
    with cols[2]:
        if st.button("📝 Inscription", key="nav_inscription_h", use_container_width=True):
            st.session_state.menu_page = "inscription"
            st.rerun()
    
    # Afficher le bouton Stats seulement pour les admins
    if st.session_state.admin_logged_in:
        with cols[3]:
            if st.button("📊 Stats", key="nav_stats_h", use_container_width=True):
                st.session_state.menu_page = "statistiques"
                st.rerun()
        
        with cols[4]:
            if st.button("👤 Admin", key="nav_admin_h", use_container_width=True):
                st.session_state.menu_page = "admin"
                st.rerun()
    else:
        with cols[3]:
            if st.button("👤 Admin", key="nav_admin_h", use_container_width=True):
                st.session_state.menu_page = "admin"
                st.rerun()

# Modifier la page Statistiques pour vérifier les droits d'accès
elif st.session_state.menu_page == "statistiques":
    if not st.session_state.admin_logged_in:
        st.warning("🔒 Accès réservé aux administrateurs")
        st.session_state.menu_page = "accueil"
        st.rerun()
    else:
        st.markdown('<div class="page-container">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">📊 Statistiques des Inscriptions</h2>', unsafe_allow_html=True)

# CONTENU PRINCIPAL
st.markdown(f'<h1 class="main-header">{config["site_title"]}</h1>', unsafe_allow_html=True)

# Page Administration
if st.session_state.menu_page == "admin":
    st.markdown('<div class="page-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-header">👤 Administration</h2>', unsafe_allow_html=True)
    
    if not st.session_state.admin_logged_in:
        st.markdown("### 🔐 Connexion Administrateur")
        with st.form("login_form"):
            col1, col2 = st.columns(2)
            with col1:
                username = st.text_input("👤 Nom d'utilisateur", placeholder="Entrez votre nom d'utilisateur")
            with col2:
                password = st.text_input("🔒 Mot de passe", type="password", placeholder="Entrez votre mot de passe")
            
            submit_login = st.form_submit_button("🚀 Se connecter", type="primary", use_container_width=True)
            
            if submit_login:
                if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                    st.session_state.admin_logged_in = True
                    st.success("✅ Connexion réussie ! Bienvenue administrateur.")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Nom d'utilisateur ou mot de passe incorrect.")
    else:
        st.success("✅ Vous êtes connecté en tant qu'administrateur.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚪 Se déconnecter", type="secondary"):
                st.session_state.admin_logged_in = False
                st.success("Déconnexion réussie.")
                st.rerun()
        
        with col2:
            st.info("Utilisez le menu pour accéder aux autres sections.")
        
        # Section de téléchargement des données
        st.markdown("---")
        st.markdown("### 📥 Téléchargement des données")
        
        df = charger_inscriptions()
        
        if not df.empty:
            st.markdown(f"""
            <div class="download-section">
                <h4>📊 Base de données disponible</h4>
                <p>📈 <strong>{len(df)}</strong> inscriptions enregistrées</p>
                <p>📅 Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Téléchargement Excel
                excel_data = generer_fichier_excel_download()
                if excel_data:
                    st.download_button(
                    label="📊 Télécharger Excel",
                    data=excel_data,
                    file_name=f"inscriptions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True
             )
            
            with col2:
                # Téléchargement CSV
                csv_data = generer_rapport_csv()
                if csv_data:
                    st.download_button(
                        label="📋 Télécharger CSV",
                        data=csv_data,
                        file_name=f"inscriptions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        type="secondary",
                        use_container_width=True
                    )
            
            with col3:
                # Bouton de rafraîchissement des données
                if st.button("🔄 Actualiser données", use_container_width=True):
                    st.session_state.inscriptions_df = charger_inscriptions()
                    st.success("Données actualisées!")
                    st.rerun()
        else:
            st.warning("📭 Aucune inscription disponible pour le téléchargement.")
        
        # Section de gestion du contenu
        st.markdown("---")
        st.markdown("### ✏️ Gestion du contenu du site")
        
        # Modification de la description du site
        if st.button("📝 Modifier la description du site", use_container_width=True):
            st.session_state.show_description_editor = not st.session_state.show_description_editor
            st.rerun()
        
        if st.session_state.show_description_editor:
            st.markdown("#### 📋 Éditeur de description")
            new_description = st.text_area(
                "Description du site",
                value=config["site_description"],
                height=400,
                help="Utilisez la syntaxe Markdown pour formater le texte"
            )
            
            col_save, col_cancel, col_preview = st.columns(3)
            with col_save:
                if st.button("💾 Sauvegarder", type="primary"):
                    config["site_description"] = new_description
                    sauvegarder_config(config)
                    st.success("✅ Description mise à jour avec succès!")
                    st.session_state.show_description_editor = False
                    st.rerun()
            
            with col_cancel:
                if st.button("❌ Annuler"):
                    st.session_state.show_description_editor = False
                    st.rerun()
            
            with col_preview:
                if st.button("👁️ Aperçu"):
                    st.markdown("#### Aperçu:")
                    st.markdown(new_description)
        
        # Gestion des modules
        st.markdown("---")
        st.markdown("### 📚 Gestion des modules de formation")
        
        if st.button("📖 Modifier les modules", use_container_width=True):
            st.session_state.show_editor = not st.session_state.show_editor
            st.rerun()
        
        if st.session_state.show_editor:
            st.markdown("#### 📝 Éditeur de modules")
            
            # Sélection du module
            selected_module = st.selectbox(
                "Choisir un module à modifier:",
                MODULES,
                index=MODULES.index(st.session_state.selected_module) if st.session_state.selected_module in MODULES else 0
            )
            st.session_state.selected_module = selected_module
            
            # Contenu actuel du module
            current_content = charger_contenu_module(selected_module)
            
            # Éditeur de texte
            new_content = st.text_area(
                f"Contenu du {selected_module}:",
                value=current_content,
                height=400,
                help="Utilisez la syntaxe Markdown pour formater le contenu"
            )
            
            col_save, col_cancel, col_preview = st.columns(3)
            with col_save:
                if st.button("💾 Sauvegarder le module", type="primary"):
                    sauvegarder_contenu_module(selected_module, new_content)
                    st.success(f"✅ {selected_module} mis à jour avec succès!")
                    st.balloons()
            
            with col_cancel:
                if st.button("❌ Annuler les modifications"):
                    st.session_state.show_editor = False
                    st.rerun()
            
            with col_preview:
                if st.button("👁️ Aperçu du module"):
                    st.markdown("#### Aperçu:")
                    st.markdown(new_content)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Modifier la page Accueil pour supprimer les statistiques pour les non-admins
elif st.session_state.menu_page == "accueil":
    st.markdown('<div class="page-container">', unsafe_allow_html=True)
    
    # Affichage de l'image si disponible
    if config.get("site_image"):
        try:
            image = Image.open(config["site_image"])
            st.image(image, use_column_width=True, caption="Formation Python - Géologie & Mines")
        except:
            pass
    
    # Description du site
    st.markdown('<div class="description-content">', unsafe_allow_html=True)
    st.markdown(config["site_description"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Section CTA
    st.markdown("""
    <div class="cta-section">
        <h2>🚀 Prêt(e) à commencer votre aventure Python ?</h2>
        <p style="font-size: 1.2rem; margin: 20px 0;">
            Rejoignez des centaines de professionnels qui ont déjà transformé leur carrière grâce à Python !
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Afficher les statistiques seulement pour les admins
    if st.session_state.admin_logged_in:
        df = charger_inscriptions()
        if not df.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="stats-card">
                    <h3>{len(df)}</h3>
                    <p>Inscriptions</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                hommes = len(df[df['Sexe'] == 'Homme']) if 'Sexe' in df.columns else 0
                st.markdown(f"""
                <div class="stats-card">
                    <h3>{hommes}</h3>
                    <p>Hommes</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                femmes = len(df[df['Sexe'] == 'Femme']) if 'Sexe' in df.columns else 0
                st.markdown(f"""
                <div class="stats-card">
                    <h3>{femmes}</h3>
                    <p>Femmes</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                age_moyen = round(df['Âge'].mean(), 1) if 'Âge' in df.columns and not df.empty else 0
                st.markdown(f"""
                <div class="stats-card">
                    <h3>{age_moyen}</h3>
                    <p>Âge moyen</p>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Page Contenu Formation
elif st.session_state.menu_page == "contenu":
    st.markdown('<div class="page-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-header">📚 Contenu de la Formation</h2>', unsafe_allow_html=True)
    
    # Grille de modules
    st.markdown("### 🎯 Modules de formation")
    st.markdown('<div class="module-grid">', unsafe_allow_html=True)
    
    # Affichage des modules en grille
    cols = st.columns(2)
    for i, module in enumerate(MODULES):
        with cols[i % 2]:
            module_key = f"module_btn_{i}"
            if st.button(
                f"📖 {module}",
                key=module_key,
                use_container_width=True,
                help=f"Cliquer pour voir le contenu du {module}"
            ):
                st.session_state.selected_module = module.split(" - ")[0]  # Stocker juste "Module X"
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Affichage du contenu du module sélectionné
    if hasattr(st.session_state, 'selected_module') and st.session_state.selected_module:
        # Trouver le module complet correspondant
        full_module_name = next((m for m in MODULES if m.startswith(st.session_state.selected_module)), None)
        
        if full_module_name:
            st.markdown("---")
            st.markdown(f"### 📖 {full_module_name}")
            
            content = charger_contenu_module(full_module_name)
            st.markdown('<div class="module-content">', unsafe_allow_html=True)
            st.markdown(content)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Navigation entre modules
            col_prev, col_next = st.columns(2)
            current_index = MODULES.index(full_module_name)
            
            with col_prev:
                if current_index > 0:
                    prev_module = MODULES[current_index - 1]
                    if st.button(f"⬅️ {prev_module}", use_container_width=True):
                        st.session_state.selected_module = prev_module.split(" - ")[0]
                        st.rerun()
            
            with col_next:
                if current_index < len(MODULES) - 1:
                    next_module = MODULES[current_index + 1]
                    if st.button(f"➡️ {next_module}", use_container_width=True):
                        st.session_state.selected_module = next_module.split(" - ")[0]
                        st.rerun()
        else:
            st.warning("Module non trouvé")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Page Inscription
elif st.session_state.menu_page == "inscription":
    st.markdown('<div class="page-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-header">📝 Formulaire d\'Inscription</h2>', unsafe_allow_html=True)
    
    st.markdown("### 👤 Informations personnelles")
    
    with st.form("inscription_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nom = st.text_input("👤 Nom *", placeholder="Votre nom de famille")
            prenom = st.text_input("👤 Prénom *", placeholder="Votre prénom")
            cnib = st.text_input("🆔 Numéro CNIB *", placeholder="Ex: A1234567")
            telephone = st.text_input("📱 Téléphone *", placeholder="Ex: +226 70 00 00 00")
        
        with col2:
            structure = st.text_input("🏢 Structure", placeholder="Entreprise, université, etc.")
            sexe = st.selectbox("⚧ Sexe *", ["", "Homme", "Femme"])
            age = st.number_input("🎂 Âge *", min_value=16, max_value=80, value=25)
            niveau = st.selectbox("📊 Niveau Python *", 
                                 ["", "Débutant", "Intermédiaire", "Avancé"])
        
        st.markdown("### 📅 Préférences de formation")
        
        col3, col4 = st.columns(2)
        with col3:
            periode = st.selectbox("📅 Période souhaitée *", 
                                  ["", "Janvier 2025", "Février 2025", "Mars 2025", 
                                   "Avril 2025", "Mai 2025", "Juin 2025"])
        
        with col4:
            option_suivi = st.selectbox("💻 Mode de suivi *", 
                                       ["", "Présentiel", "En ligne", "Hybride"])
        
        # Bouton de soumission
        st.markdown("---")
        submit_inscription = st.form_submit_button(
            "🚀 S'inscrire maintenant", 
            type="primary", 
            use_container_width=True
        )
        
        # Validation du formulaire
        if submit_inscription:
            errors = []
            
            # Validation des champs obligatoires
            if not nom or not valider_nom(nom):
                errors.append("❌ Nom invalide (minimum 2 caractères, pas de chiffres)")
            
            if not prenom or not valider_nom(prenom):
                errors.append("❌ Prénom invalide (minimum 2 caractères, pas de chiffres)")
            
            if not cnib or not valider_cnib(cnib):
                errors.append("❌ Numéro CNIB invalide (format: A1234567)")
            
            if not telephone or not valider_telephone(telephone):
                errors.append("❌ Numéro de téléphone invalide")
            
            if not sexe:
                errors.append("❌ Veuillez sélectionner votre sexe")
            
            if not valider_age(age):
                errors.append("❌ Âge doit être entre 16 et 80 ans")
            
            if not niveau:
                errors.append("❌ Veuillez sélectionner votre niveau Python")
            
            if not periode:
                errors.append("❌ Veuillez sélectionner une période")
            
            if not option_suivi:
                errors.append("❌ Veuillez sélectionner un mode de suivi")
            
            # Affichage des erreurs
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Enregistrement de l'inscription
                data_inscription = {
                    "Nom": nom.strip().title(),
                    "Prénom": prenom.strip().title(),
                    "Numéro CNIB": cnib.upper().strip(),
                    "Téléphone": telephone.strip(),
                    "Structure": structure.strip() if structure else "Non renseignée",
                    "Période souhaitée": periode,
                    "Sexe": sexe,
                    "Âge": age,
                    "Niveau": niveau,
                    "Option de suivi": option_suivi
                }
                
                success, message = sauvegarder_inscription(data_inscription)
                
                if success:
                    st.success(message)
                    st.balloons()
                    st.info("📧 Un email de confirmation sera envoyé à votre adresse.")
                else:
                    st.error(message)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Page Statistiques
elif st.session_state.menu_page == "statistiques":
    st.markdown('<div class="page-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-header">📊 Statistiques des Inscriptions</h2>', unsafe_allow_html=True)
    
    df = charger_inscriptions()
    
    if df.empty:
        st.warning("📭 Aucune inscription disponible pour afficher les statistiques.")
    else:
        # Statistiques générales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📈 Total inscriptions", len(df))
        
        with col2:
            hommes = len(df[df['Sexe'] == 'Homme']) if 'Sexe' in df.columns else 0
            st.metric("👨 Hommes", hommes)
        
        with col3:
            femmes = len(df[df['Sexe'] == 'Femme']) if 'Sexe' in df.columns else 0
            st.metric("👩 Femmes", femmes)
        
        with col4:
            age_moyen = round(df['Âge'].mean(), 1) if 'Âge' in df.columns and not df.empty else 0
            st.metric("🎂 Âge moyen", f"{age_moyen} ans")
        
        st.markdown("---")
        
        # Graphiques
        col_left, col_right = st.columns(2)
        
        with col_left:
            # Graphique répartition par sexe
            # Graphique répartition par sexe
            if 'Sexe' in df.columns:
                fig_sexe = px.pie(
                    df, 
                    names='Sexe', 
                    title="👥 Répartition par sexe",
                    color_discrete_sequence=['#667eea', '#764ba2']
                    )
                st.plotly_chart(fig_sexe, use_container_width=True)
                # Graphique répartition par niveau
            if 'Niveau' in df.columns:
                niveau_counts = df['Niveau'].value_counts().reset_index()
                niveau_counts.columns = ['Niveau', 'count']  # Renommer les colonnes
                fig_niveau = px.bar(
                     niveau_counts, 
                     x='Niveau', 
                     y='count',
                     title="📊 Répartition par niveau Python",
                     color_discrete_sequence=['#667eea']
                     )
                fig_niveau.update_xaxes(title="Niveau")
                fig_niveau.update_yaxes(title="Nombre d'inscrits")
                st.plotly_chart(fig_niveau, use_container_width=True)
                with col_right:
                    # Graphique répartition par période
                    if 'Période souhaitée' in df.columns:
                        periode_counts = df['Période souhaitée'].value_counts().reset_index()
                        periode_counts.columns = ['Période', 'count']  # Renommer les colonnes
                        fig_periode = px.bar(
                            periode_counts,
                            x='Période',
                            y='count',
                            title="📅 Périodes préférées",
                            color_discrete_sequence=['#764ba2']
                            )
                        fig_periode.update_xaxes(title="Période")
                        fig_periode.update_yaxes(title="Nombre d'inscrits")
                        st.plotly_chart(fig_periode, use_container_width=True)
                        # Graphique répartition par mode de suivi
                        if 'Option de suivi' in df.columns:
                            fig_suivi = px.pie(
                                df, 
                                names='Option de suivi', 
                                title="💻 Modes de suivi préférés",
                                color_discrete_sequence=['#f093fb', '#f5576c', '#4facfe']
                                )
                            st.plotly_chart(fig_suivi, use_container_width=True)

                            # Histogramme des âges
                        if 'Âge' in df.columns:
                             st.markdown("### 📈 Distribution des âges")
                             fig_age = px.histogram(
                                 df, 
                                x='Âge', 
                                nbins=20, 
                                title="Répartition par tranches d'âge",
                                color_discrete_sequence=['#667eea']
                                )
                             fig_age.update_xaxes(title="Âge")
                             fig_age.update_yaxes(title="Nombre d'inscrits")
                        st.plotly_chart(fig_age, use_container_width=True)
        
        # Tableau des inscriptions récentes
        st.markdown("### 📋 Inscriptions récentes")
        if 'Date d\'inscription' in df.columns:
            df_recent = df.nlargest(10, 'Date d\'inscription')
        else:
            df_recent = df.head(10)
        
        st.dataframe(
            df_recent[['Nom', 'Prénom', 'Sexe', 'Âge', 'Niveau', 'Période souhaitée']],
            use_container_width=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <h3>🐍 Formation Python - Géologie & Mines</h3>
    <p>© 2025 - Tous droits réservés</p>
    <p>📧 formation@gmail.com | 📱 +226 77 77 77 77 / 88 88 88 88</p>
    <p>🌍 <em>Formez-vous aux technologies d'avenir avec Python !</em></p>
</div>
""", unsafe_allow_html=True)
