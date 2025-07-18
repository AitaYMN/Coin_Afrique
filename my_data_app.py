import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

st.set_page_config(page_title="Coinafrique Data Collection", layout="wide")

# Titre de l'application
st.title("🛒 Coinafrique Data Collection App")

# Menu de navigation
menu = st.sidebar.selectbox("Menu", ["Accueil", "Scraper des données", "Télécharger données", "Dashboard", "Évaluation"])

# Configuration des catégories
CATEGORIES = {
    "Les Moutons": {
        "url": "https://sn.coinafrique.com/categorie/moutons",
        "type": "mouton"
    },
    "Les Chiens": {
        "url": "https://sn.coinafrique.com/categorie/chiens",
        "type": "chien"
    },
    "Les Poules, Lapins et Pigeons": {
        "url": "https://sn.coinafrique.com/categorie/poules-lapins-et-pigeons",
        "type": "volaille"
    },
    "Autres Animaux": {
        "url": "https://sn.coinafrique.com/categorie/autres-animaux",
        "type": "autre"
    }
}

if menu == "Accueil":
    st.markdown("""
    ## 🏠 Bienvenue dans l'application de collecte de données Coinafrique
    
    Cette application vous permet de:
    - ⚡ Scraper des données depuis Coinafrique
    - 📥 Télécharger des données déjà scrapées
    - 📊 Visualiser les données dans un dashboard
    - ⭐ Évaluer l'application
    
    ### 🗂️ Catégories disponibles
    """)
    
    for cat, infos in CATEGORIES.items():
        st.markdown(f"- **{cat}** (`{infos['type']}`)")

elif menu == "Scraper des données":
    st.header("🔎 Scraper des données depuis Coinafrique")
    
    col1, col2 = st.columns(2)
    
    with col1:
        categorie = st.selectbox("Choisissez une catégorie", list(CATEGORIES.keys()))
        pages = st.slider("Nombre de pages à scraper", 1, 10, 1)
    
    with col2:
        st.markdown("**Informations à collecter :**")
        st.markdown("- 🏷️ Nom/Type")
        st.markdown("- 💰 Prix")
        st.markdown("- 📍 Adresse")
        st.markdown("- 🖼️ Lien de l'image")
    
    if st.button("🚀 Lancer le scraping", key="scrape_btn"):
        st.info(f"Scraping en cours pour {categorie} ({pages} pages)...")
        
        data = []
        base_url = CATEGORIES[categorie]["url"]
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for page in range(1, pages + 1):
            url = f"{base_url}?page={page}"
            try:
                status_text.text(f"Traitement de la page {page}/{pages}...")
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Nouveaux sélecteurs testés
                articles = soup.find_all('div', class_='col s6 m4 l3')
                
                if not articles:
                    st.warning(f"Aucun article trouvé sur la page {page}")
                    continue
                
                for article in articles:
                    try:
                        # Nom
                        nom = article.find('p', class_='ad__card-description').text.strip() if article.find('p', class_='ad__card-description') else "Non spécifié"
                        
                        # Prix
                        prix_elem = article.find('p', class_='ad__card-price')
                        prix = prix_elem.text.strip() if prix_elem else "0 FCFA"
                        
                        # Adresse
                        adresse_elem = article.find('p', class_='ad__card-location')
                        adresse = adresse_elem.text.strip() if adresse_elem else "Non spécifiée"
                        
                        # Image
                        img_elem = article.find('img', class_='ad__card-img')
                        image = img_elem['src'] if img_elem else ""
                        
                        data.append({
                            'Catégorie': categorie,
                            'Nom': nom,
                            'Prix': prix,
                            'Adresse': adresse,
                            'Image': image,
                            'Page': page
                        })
                    except Exception as e:
                        st.warning(f"Erreur sur un article: {str(e)}")
                        continue
                
                time.sleep(1)  # Respect du serveur
                progress_bar.progress(page/pages)
                
            except Exception as e:
                st.error(f"Erreur sur la page {page}: {str(e)}")
                continue
        
        if data:
            df = pd.DataFrame(data)
            st.success(f"✅ {len(df)} éléments scrapés avec succès!")
            
            # Affichage avec ag-grid pour une meilleure visualisation
            st.dataframe(df)
            
            # Téléchargement
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="💾 Télécharger les données",
                data=csv,
                file_name=f"coinafrique_{categorie.lower().replace(' ', '_')}.csv",
                mime='text/csv'
            )
        else:
            st.error("Aucune donnée n'a pu être récupérée. Vérifiez les sélecteurs CSS.")

elif menu == "Télécharger données":
    st.header("📥 Télécharger des données brutes")
    st.info("Données collectées via Web Scraper (non nettoyées)")
    
    FICHIERS_BRUTS = {
        "Les Moutons": "data/Mouton.csv",
        "Les Chiens": "data/Chien.csv",
        "Les Poules, Lapins et Pigeons": "data/Poules.csv",
        "Autres Animaux": "data/Autres.csv"
    }
    
    fichier = st.selectbox("Choisissez un jeu de données", list(FICHIERS_BRUTS.keys()))
    
    try:
        df = pd.read_csv(FICHIERS_BRUTS[fichier])
        st.dataframe(df.head())
        
        st.download_button(
            label="⬇️ Télécharger ce fichier",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name=f"{fichier.replace(' ', '_')}_raw.csv",
            mime='text/csv'
        )
    except Exception as e:
        st.error(f"Erreur: {str(e)}. Vérifiez que le fichier existe bien.")

elif menu == "Dashboard":
    st.header("📊 Dashboard des données nettoyées")
    
    try:
        df = pd.read_csv("data/animaux_clean.csv")
        
        st.subheader("Statistiques principales")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Nombre total d'articles", len(df))
        
        with col2:
            st.metric("Nombre de catégories", df['Catégorie'].nunique())
        
        with col3:
            df['Prix'] = df['Prix'].astype(str)
            avg_price = df['Prix'].str.extract(r'(\d+)')[0].astype(float).mean()
            st.metric("Prix moyen", f"{avg_price:,.0f} FCFA")
        
        st.subheader("Répartition par catégorie")
        st.bar_chart(df['Catégorie'].value_counts())
        
        st.subheader("Top 10 des annonces les plus chères")
        top_chers = df.copy()
        top_chers['Prix_num'] = top_chers['Prix'].str.extract(r'(\d+)')[0].astype(float)
        st.table(top_chers.nlargest(10, 'Prix_num')[['Nom', 'Prix', 'Catégorie']])
        
    except Exception as e:
        st.error(f"Erreur: {str(e)}. Aucune donnée nettoyée disponible.")

elif menu == "Évaluation":
    st.header("⭐ Évaluez notre application")
    
    # Intégration KoboToolbox
    st.markdown("""
    <div style="border: 2px solid #f0f0f0; border-radius: 5px; padding: 20px; text-align: center;">
        <h3>Formulaire d'évaluation</h3>
        <iframe src="https://ee.kobotoolbox.org/x/Tksl9FlE" 
                width="100%" 
                height="800" 
                frameborder="0" 
                style="border: none; margin-top: 20px;">
        </iframe>
    </div>
    """, unsafe_allow_html=True)