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

# Configuration par défaut du site
DEFAULT_CONFIG = {
    "site_title": "Formation Python pour Géologie & Mines",
    "site_description": """

# 🐍 **Bienvenue à la Formation Python pour les Sciences Géologiques & Minières**

## 💡 Pourquoi apprendre Python dans le domaine de la géologie et des mines ?

Python est aujourd’hui **le langage incontournable** pour l’analyse et la visualisation de données scientifiques. Dans les domaines de la géologie et des mines, il permet de :

🔹 Automatiser le traitement de données géophysiques et géochimiques
🔹 Cartographier et modéliser des structures géologiques
🔹 Simuler des processus miniers et environnementaux
🔹 Gérer et analyser des données volumineuses avec précision
🔹 Améliorer la prise de décision grâce à des visualisations interactives

**Bref, Python devient un véritable outil d’aide à la décision dans le secteur géo-minier.**



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



## 👤 **À qui s’adresse cette formation ?**

Cette formation est conçue pour toute personne souhaitant intégrer le numérique et la programmation dans les métiers de la géologie et des mines :

👨‍🎓 **Étudiants** en géologie, génie minier, ou environnement
👷‍♂️ **Professionnels** du secteur minier, pétrolier ou géotechnique
🔬 **Chercheurs** en sciences de la Terre
🛠 **Ingénieurs** en exploration, production ou aménagement

*Aucun niveau avancé en programmation n’est requis. Vous apprendrez de zéro !*


## 📚 **Organisation de la formation**

📅 **Durée** : 8 modules répartis sur 4 semaines
🏫 **Format** : Présentiel ou 100% en ligne
🖥 **Prérequis** : Aisance avec l’ordinateur (Windows/Linux)
🎓 **Attestation** : Certificat délivré à la fin de la formation



## 💥 **Les plus de notre formation**

🔥 **Formation 100% adaptée au terrain géo-minier**
🔥 **Encadrement par des experts en géologie et data science**
🔥 **Exercices pratiques avec des jeux de données réels**
🔥 **Support pédagogique clair, structuré et accessible à vie**
🔥 **Accès à une communauté d’apprentissage et de collaboration**



## 📞 **Contactez-nous dès maintenant !**

📧 **Email** : [formation@tcg-expertise.com](mailto:formation@tcg-expertise.com)
📱 **Téléphone** : 25 45 67 67 / ‪+33779185080
🌐 **Site web** : *En construction — restez connecté !*


### 🧭 Rejoignez-nous et entrez dans le monde de la **géologie numérique avec Python**.

**➡️ Une compétence d’avenir — Une opportunité unique — Un tremplin pour votre carrière !**
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

# CSS personnalisé avec sidebar moderne
st.markdown("""
<style>
    /* Sidebar styling */
    .stSidebar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .stSidebar > div {
        padding-top: 2rem;
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
    
    /* Main content styling */
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

# SIDEBAR MENU
config = charger_config()

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
    
    if st.button("📊 Statistiques", key="nav_stats", use_container_width=True):
        st.session_state.menu_page = "statistiques"
        st.rerun()
    
    if st.button("👤 Administration", key="nav_admin", use_container_width=True):
        st.session_state.menu_page = "admin"
        st.rerun()
    
    # Statut admin
    if st.session_state.admin_logged_in:
        st.markdown("""
        <div class="sidebar-admin-status">
            ✅ Connecté en tant qu'Admin
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="sidebar-admin-status">
            👤 Visiteur
        </div>
        """, unsafe_allow_html=True)
    
    # Informations de contact
    st.markdown("""
    <div class="sidebar-contact">
        <h4>📞 Contact</h4>
        <p>📧 formation@tcg-expertise.com</p>
        <p>📱 +226 25 45 67 67</p>
        <p>📱 ‪+33779185080</p>
    </div>
    """, unsafe_allow_html=True)

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
            st.info("Utilisez le menu latéral pour accéder aux autres sections.")
        
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
                        label="📄 Télécharger CSV",
                        data=csv_data,
                        file_name=f"inscriptions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        type="secondary",
                        use_container_width=True
                    )
            
            with col3:
                # Bouton d'actualisation
                if st.button("🔄 Actualiser", type="secondary", use_container_width=True):
                    st.rerun()
            
            # Aperçu des données
            st.markdown("### 👀 Aperçu des dernières inscriptions")
            if len(df) > 0:
                # Afficher les 5 dernières inscriptions
                latest_df = df.tail(5)
                st.dataframe(
                    latest_df,
                    use_container_width=True,
                    height=200
                )
            
            # Statistiques rapides
            st.markdown("### 📈 Statistiques rapides")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("👥 Total", len(df))
            
            with col2:
                hommes = len(df[df['Sexe'] == 'Homme'])
                st.metric("👨 Hommes", hommes)
            
            with col3:
                femmes = len(df[df['Sexe'] == 'Femme'])
                st.metric("👩 Femmes", femmes)
            
            with col4:
                age_moyen = round(df['Âge'].mean(), 1)
                st.metric("🎂 Âge moyen", f"{age_moyen} ans")
        
        else:
            st.markdown("""
            <div class="download-section">
                <h4>📭 Aucune donnée disponible</h4>
                <p>Aucune inscription n'a été enregistrée pour le moment.</p>
                <p>Les téléchargements seront disponibles dès qu'il y aura des inscriptions.</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Page Contenu Formation
elif st.session_state.menu_page == "contenu":
    st.markdown('<div class="page-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-header">📘 Contenu de la Formation</h2>', unsafe_allow_html=True)
    
    # Sélection des modules en grille
    st.markdown("### 🎯 Sélectionnez un module")
    
    # Créer une grille de modules
    cols = st.columns(4)
    for i, module in enumerate(MODULES):
        with cols[i % 4]:
            if st.button(
                f"📖 {module.split(' - ')[0]}",
                key=f"module_{i}",
                use_container_width=True,
                type="primary" if st.session_state.selected_module == module else "secondary"
            ):
                st.session_state.selected_module = module
                st.session_state.show_editor = False
                st.rerun()
    
    # Affichage du contenu
    st.markdown(f"### 📚 {st.session_state.selected_module}")
    contenu = charger_contenu_module(st.session_state.selected_module)
    
    st.markdown(f"""
    <div class="module-content">
        <h4>📄 Contenu du {st.session_state.selected_module}</h4>
        <pre style="white-space: pre-wrap; font-family: inherit; font-size: 14px;">{contenu}</pre>
    </div>
    """, unsafe_allow_html=True)
    
    # Fonctions admin
    if st.session_state.admin_logged_in:
        st.markdown("---")
        st.markdown("### 🔧 Fonctions Administrateur")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📁 Téléverser un fichier")
            uploaded_file = st.file_uploader("Choisir un fichier texte", type=['txt'])
            if uploaded_file is not None:
                content = uploaded_file.read().decode('utf-8')
                if st.button("📤 Téléverser pour ce module", type="primary"):
                    sauvegarder_contenu_module(st.session_state.selected_module, content)
                    st.success(f"✅ Contenu du {st.session_state.selected_module} mis à jour!")
                    st.rerun()
        
        with col2:
            st.markdown("#### ✏️ Éditer le contenu")
            if st.button("✏️ Éditer le contenu", type="secondary"):
               st.session_state.show_editor = not st.session_state.show_editor
               st.rerun()
            if st.session_state.show_editor:
                st.markdown("#### 📝 Éditeur de contenu")
                nouveau_contenu = st.text_area(
               "Contenu du module",
               value=contenu,
               height=300,
               key="editor_content"
           )
                col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Sauvegarder", type="primary"):
                   sauvegarder_contenu_module(st.session_state.selected_module, nouveau_contenu)
                   st.success(f"✅ Contenu du {st.session_state.selected_module} sauvegardé!")
                   st.session_state.show_editor = False
                   st.rerun()
           
        with col2:
            if st.button("❌ Annuler", type="secondary"):
                   st.session_state.show_editor = False
                   st.rerun()
                   st.markdown('</div>', unsafe_allow_html=True)

# Page Accueil
elif st.session_state.menu_page == "accueil":
   st.markdown('<div class="page-container">', unsafe_allow_html=True)
   
   # Affichage de l'image si disponible
   if config.get("site_image"):
       try:
           image = Image.open(config["site_image"])
           st.image(image, use_column_width=True, caption="Formation Python pour Géologie & Mines")
       except:
           pass
   
   # Contenu principal
   st.markdown(f"""
   <div class="description-content">
       {config["site_description"]}
   </div>
   """, unsafe_allow_html=True)
   
   # CTA Section
   st.markdown("""
   <div class="cta-section">
       <h3>🚀 Prêt à commencer votre apprentissage ?</h3>
       <p>Rejoignez notre formation et développez vos compétences Python dans le domaine géologique !</p>
   </div>
   """, unsafe_allow_html=True)
   
   # Bouton d'inscription
   col1, col2, col3 = st.columns([1, 2, 1])
   with col2:
       if st.button("📝 S'inscrire maintenant", type="primary", use_container_width=True):
           st.session_state.menu_page = "inscription"
           st.rerun()
   
   # Fonctions admin pour la page d'accueil
   if st.session_state.admin_logged_in:
       st.markdown("---")
       st.markdown('<div class="admin-section">', unsafe_allow_html=True)
       st.markdown("### 🔧 Gestion de la page d'accueil")
       
       col1, col2 = st.columns(2)
       
       with col1:
           nouveau_titre = st.text_input("Titre du site", value=config["site_title"])
           
           # Upload d'image
           uploaded_image = st.file_uploader(
               "Image de la formation",
               type=['png', 'jpg', 'jpeg'],
               help="Téléversez une image pour la page d'accueil"
           )
           
           if uploaded_image is not None:
               # Sauvegarder l'image
               image_path = f"site_image.{uploaded_image.name.split('.')[-1]}"
               with open(image_path, "wb") as f:
                   f.write(uploaded_image.getbuffer())
               config["site_image"] = image_path
               st.success("✅ Image téléversée avec succès!")
       
       with col2:
           if st.button("✏️ Éditer la description", type="secondary"):
               st.session_state.show_description_editor = not st.session_state.show_description_editor
               st.rerun()
       
       if st.session_state.show_description_editor:
           nouvelle_description = st.text_area(
               "Description du site",
               value=config["site_description"],
               height=400,
               key="description_editor"
           )
           
           col1, col2 = st.columns(2)
           with col1:
               if st.button("💾 Sauvegarder description", type="primary"):
                   config["site_description"] = nouvelle_description
                   config["site_title"] = nouveau_titre
                   sauvegarder_config(config)
                   st.success("✅ Configuration sauvegardée!")
                   st.session_state.show_description_editor = False
                   st.rerun()
           
           with col2:
               if st.button("❌ Annuler édition", type="secondary"):
                   st.session_state.show_description_editor = False
                   st.rerun()
       
       st.markdown('</div>', unsafe_allow_html=True)
   
   st.markdown('</div>', unsafe_allow_html=True)

# Page Inscription
elif st.session_state.menu_page == "inscription":
   st.markdown('<div class="page-container">', unsafe_allow_html=True)
   st.markdown('<h2 class="section-header">📝 Formulaire d\'inscription</h2>', unsafe_allow_html=True)
   
   st.markdown("### 📋 Remplissez ce formulaire pour vous inscrire à la formation")
   
   with st.form("inscription_form", clear_on_submit=True):
       # Informations personnelles
       st.markdown("#### 👤 Informations personnelles")
       col1, col2 = st.columns(2)
       
       with col1:
           nom = st.text_input("Nom *", placeholder="Votre nom de famille")
           prenom = st.text_input("Prénom *", placeholder="Votre prénom")
           cnib = st.text_input("Numéro CNIB *", placeholder="Ex: A1234567")
           telephone = st.text_input("Téléphone *", placeholder="Ex: 70123456")
       
       with col2:
           structure = st.text_input("Structure/Organisation", placeholder="Université, entreprise, etc.")
           sexe = st.selectbox("Sexe *", ["", "Homme", "Femme"])
           age = st.number_input("Âge *", min_value=16, max_value=80, value=25)
           niveau = st.selectbox("Niveau en programmation *", 
                               ["", "Débutant", "Intermédiaire", "Avancé"])
       
       # Préférences de formation
       st.markdown("#### 🎯 Préférences de formation")
       col1, col2 = st.columns(2)
       
       with col1:
           periode = st.selectbox("Période souhaitée *", 
                                ["", "Matinée (8h-12h)", "Après-midi (14h-18h)", 
                                 "Soirée (18h-22h)", "Week-end"])
       
       with col2:
           option_suivi = st.selectbox("Option de suivi *", 
                                     ["", "Présentiel", "En ligne", "Hybride"])
       
       # Motivation
       st.markdown("#### 💭 Motivation (optionnel)")
       motivation = st.text_area("Pourquoi souhaitez-vous suivre cette formation ?", 
                               placeholder="Décrivez vos objectifs et motivations...")
       
       # Soumission
       st.markdown("---")
       submitted = st.form_submit_button("🚀 Envoyer l'inscription", type="primary", use_container_width=True)
       
       if submitted:
           erreurs = []
           
           # Validation des champs obligatoires
           if not nom or not valider_nom(nom):
               erreurs.append("❌ Le nom est requis et ne doit contenir que des lettres")
           
           if not prenom or not valider_nom(prenom):
               erreurs.append("❌ Le prénom est requis et ne doit contenir que des lettres")
           
           if not cnib or not valider_cnib(cnib):
               erreurs.append("❌ Le numéro CNIB est requis et doit être au format valide (ex: A1234567)")
           
           if not telephone or not valider_telephone(telephone):
               erreurs.append("❌ Le numéro de téléphone est requis et doit être au format valide")
           
           if not sexe:
               erreurs.append("❌ Le sexe est requis")
           
           if not age or not valider_age(age):
               erreurs.append("❌ L'âge doit être entre 16 et 80 ans")
           
           if not niveau:
               erreurs.append("❌ Le niveau en programmation est requis")
           
           if not periode:
               erreurs.append("❌ La période souhaitée est requise")
           
           if not option_suivi:
               erreurs.append("❌ L'option de suivi est requise")
           
           if erreurs:
               for erreur in erreurs:
                   st.error(erreur)
           else:
               # Préparer les données
               data = {
                   "Nom": nom.strip().title(),
                   "Prénom": prenom.strip().title(),
                   "Numéro CNIB": cnib.strip().upper(),
                   "Téléphone": telephone.strip(),
                   "Structure": structure.strip() if structure else "Non renseigné",
                   "Période souhaitée": periode,
                   "Sexe": sexe,
                   "Âge": age,
                   "Niveau": niveau,
                   "Option de suivi": option_suivi
               }
               
               # Sauvegarder l'inscription
               success, message = sauvegarder_inscription(data)
               
               if success:
                   st.success(f"✅ {message}")
                   st.balloons()
                   
                   # Afficher un récapitulatif
                   st.markdown("### 📄 Récapitulatif de votre inscription")
                   st.markdown(f"""
                   **Nom complet :** {data['Prénom']} {data['Nom']}  
                   **CNIB :** {data['Numéro CNIB']}  
                   **Téléphone :** {data['Téléphone']}  
                   **Structure :** {data['Structure']}  
                   **Période :** {data['Période souhaitée']}  
                   **Option :** {data['Option de suivi']}  
                   **Niveau :** {data['Niveau']}
                   """)
                   
                   st.info("📧 Vous recevrez bientôt un email de confirmation avec tous les détails de la formation.")
               else:
                   st.error(f"❌ {message}")
   
   st.markdown('</div>', unsafe_allow_html=True)

# Page Statistiques
elif st.session_state.menu_page == "statistiques":
    st.markdown('<div class="page-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-header">📊 Statistiques des inscriptions</h2>', unsafe_allow_html=True)
    
    # Vérification des droits d'accès administrateur
    if not st.session_state.admin_logged_in:
        st.markdown("""
        <div class="admin-section">
            <h3>🔒 Accès restreint</h3>
            <p>Cette page est réservée aux administrateurs.</p>
            <p>Veuillez vous connecter en tant qu'administrateur pour accéder aux statistiques.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("👤 Aller à la page Administration", type="primary", use_container_width=True):
                st.session_state.menu_page = "admin"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()
    
    df = charger_inscriptions()
    if df.empty:
       st.markdown("""
       <div class="stats-card">
           <h3>📭 Aucune inscription</h3>
           <p>Il n'y a pas encore d'inscriptions enregistrées.</p>
           <p>Les statistiques apparaîtront dès qu'il y aura des données.</p>
       </div>
       """, unsafe_allow_html=True)
    else:
       # Statistiques générales
       st.markdown("### 📈 Vue d'ensemble")
       
       col1, col2, col3, col4 = st.columns(4)
       
       with col1:
           st.markdown(f"""
           <div class="stats-card">
               <h3>👥 Total</h3>
               <h2>{len(df)}</h2>
               <p>Inscriptions</p>
           </div>
           """, unsafe_allow_html=True)
       
       with col2:
           hommes = len(df[df['Sexe'] == 'Homme'])
           pourcentage_hommes = (hommes / len(df)) * 100
           st.markdown(f"""
           <div class="stats-card">
               <h3>👨 Hommes</h3>
               <h2>{hommes}</h2>
               <p>{pourcentage_hommes:.1f}%</p>
           </div>
           """, unsafe_allow_html=True)
       
       with col3:
           femmes = len(df[df['Sexe'] == 'Femme'])
           pourcentage_femmes = (femmes / len(df)) * 100
           st.markdown(f"""
           <div class="stats-card">
               <h3>👩 Femmes</h3>
               <h2>{femmes}</h2>
               <p>{pourcentage_femmes:.1f}%</p>
           </div>
           """, unsafe_allow_html=True)
       
       with col4:
           age_moyen = df['Âge'].mean()
           st.markdown(f"""
           <div class="stats-card">
               <h3>🎂 Âge moyen</h3>
               <h2>{age_moyen:.1f}</h2>
               <p>ans</p>
           </div>
           """, unsafe_allow_html=True)
       
       # Graphiques
       st.markdown("### 📊 Graphiques détaillés")
       
       col1, col2 = st.columns(2)
       
       with col1:
           # Graphique sexe
           sexe_counts = df['Sexe'].value_counts()
           fig_sexe = px.pie(
               values=sexe_counts.values,
               names=sexe_counts.index,
               title="Répartition par sexe",
               color_discrete_sequence=['#667eea', '#764ba2']
           )
           st.plotly_chart(fig_sexe, use_container_width=True)
       
       with col2:
           # Graphique niveau
           niveau_counts = df['Niveau'].value_counts()
           fig_niveau = px.bar(
               x=niveau_counts.index,
               y=niveau_counts.values,
               title="Répartition par niveau",
               color=niveau_counts.values,
               color_continuous_scale='viridis'
           )
           st.plotly_chart(fig_niveau, use_container_width=True)
       
       col1, col2 = st.columns(2)
       
       with col1:
           # Graphique période
           periode_counts = df['Période souhaitée'].value_counts()
           fig_periode = px.bar(
               x=periode_counts.values,
               y=periode_counts.index,
               title="Préférences de période",
               orientation='h',
               color=periode_counts.values,
               color_continuous_scale='plasma'
           )
           st.plotly_chart(fig_periode, use_container_width=True)
       
       with col2:
           # Graphique option de suivi
           option_counts = df['Option de suivi'].value_counts()
           fig_option = px.pie(
               values=option_counts.values,
               names=option_counts.index,
               title="Options de suivi",
               color_discrete_sequence=['#f093fb', '#f5576c', '#4facfe']
           )
           st.plotly_chart(fig_option, use_container_width=True)
       
       # Distribution des âges
       st.markdown("### 📊 Distribution des âges")
       fig_age = px.histogram(
           df,
           x='Âge',
           nbins=20,
           title="Distribution des âges des inscrits",
           color_discrete_sequence=['#667eea']
       )
       st.plotly_chart(fig_age, use_container_width=True)
       
       # Tableau des inscriptions récentes
       #st.markdown("### 📋 Inscriptions récentes")
       #if len(df) > 0:
       #    recent_df = df.tail(10)[['Nom', 'Prénom', 'Sexe', 'Âge', 'Niveau', 'Date d\'inscription']]
       #    st.dataframe(recent_df, use_container_width=True)
       
       # Bouton de rafraîchissement
       col1, col2, col3 = st.columns([1, 1, 1])
       with col2:
           if st.button("🔄 Actualiser les statistiques", type="primary", use_container_width=True):
               st.rerun()
   
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
   <p>© 2025 Formation Python pour Géologie & Mines</p>
   <p>Développé avec ❤️ par l'équipe de formation</p>
   <p>📧 formation@tcg-expertise.com | 📱 25 45 67 67 / ‪+33779185080</p>
</div>
""", unsafe_allow_html=True)
