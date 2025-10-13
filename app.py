import streamlit as st
import pandas as pd
import numpy as np
from urllib.parse import urlparse
import re
from io import BytesIO
from PIL import Image

# Charger et redimensionner le logo
logo = Image.open("360_capital_vc_logo.jpeg")
logo = logo.resize((64, 64))


# Configuration de la page
st.set_page_config(
    page_title="Nettoyage Données Crunchbase",
    page_icon=logo,
    layout="wide"
)

def get_domain(url):
    """Extrait le domaine d'une URL et le formate"""
    if pd.isna(url):
        return None
    try:
        domain = urlparse(url).netloc
        domain = re.sub(r'^www\d*\.', '', domain).split(':')[0]
        return domain.lower()
    except:
        return None

def clean_crunchbase_data(df):
    """
    Nettoie les données de levées de fonds Crunchbase
    
    Args:
        df: DataFrame avec les colonnes Crunchbase
        
    Returns:
        DataFrame nettoyé avec les colonnes formatées
    """
    # Créer une copie pour ne pas modifier l'original
    df_clean = df.copy()
    
    # 1. Filtrer les types de financement non désirés
    funding_types_to_remove = [
        'Corporate Round',
        'Grant',
        'Post-IPO Debt',
        'Equity Crowdfunding',
        'Debt Financing',
        'Convertible Note',
        'Series C'
    ]
    
    initial_count = len(df_clean)
    df_clean = df_clean[~df_clean['Funding Type'].isin(funding_types_to_remove)]
    filtered_count = initial_count - len(df_clean)
    
    # 2. Convertir les montants USD en devise originale
    mask_usd = df_clean['Money Raised Currency'] == 'USD'
    mask_has_both = pd.notna(df_clean['Money Raised']) & pd.notna(df_clean['Money Raised (in USD)'])
    
    # Calculer le taux de change moyen pour les lignes non-USD
    rates = df_clean[~mask_usd & mask_has_both].apply(
        lambda row: row['Money Raised (in USD)'] / row['Money Raised'] 
        if row['Money Raised'] != 0 else np.nan,
        axis=1
    )
    avg_rate = rates.median() if len(rates) > 0 else 1.0
    
    # Appliquer la conversion inverse pour les montants USD
    df_clean.loc[mask_usd & pd.isna(df_clean['Money Raised']) & pd.notna(df_clean['Money Raised (in USD)']), 'Money Raised'] = \
        df_clean.loc[mask_usd & pd.isna(df_clean['Money Raised']) & pd.notna(df_clean['Money Raised (in USD)']), 'Money Raised (in USD)'] / avg_rate
    
    # 3. Appliquer le formatage des URLs avec get_domain
    df_clean['Website_formatted'] = df_clean['Organization Website'].apply(get_domain)
    
    # 3bis Changer le format des montants 

    df_clean['Money Raised'] = df_clean['Money Raised'].apply(lambda x: f"€M {x:,.0f}" if pd.notna(x) else x)  

    # 4. Créer le nouveau DataFrame avec les colonnes demandées
    df_final = pd.DataFrame({
        'Company Name': df_clean['Organization Name'],
        'Website 2': '',
        'Website': df_clean['Website_formatted'],
        'Description': df_clean['Organization Description'],
        'Secteur': df_clean['Organization Industries'],
        'Date annonce levée': '',
        'Montant': df_clean['Money Raised'],
        'Investisseurs': df_clean['Investor Names']
    })
    
    # Réinitialiser l'index
    df_final = df_final.reset_index(drop=True)
    
    return df_final, filtered_count


# Interface principale
st.title("Nettoyage de Données Crunchbase")
st.markdown("---")

st.markdown("""
### Instructions
        1. Téléchargez votre fichier CSV exporté depuis Crunchbase.
        2. Cliquez sur "Nettoyer les données" pour lancer le processus de nettoyage.
        3. Téléchargez les données nettoyées au format CSV ou Excel.
""")

st.markdown("---")

# Upload du fichier
uploaded_file = st.file_uploader(
    "Chargez votre fichier CSV Crunchbase",
    type=['csv'],
    help="Le fichier doit contenir les colonnes standard de Crunchbase"
)

if uploaded_file is not None:
    try:
        # Lecture du fichier
        df = pd.read_csv(uploaded_file)
        
        st.success(f"✅ Fichier chargé : {len(df)} lignes détectées")
        
        # Afficher un aperçu des données originales
        with st.expander("Aperçu des données originales"):
            st.dataframe(df.head(10), use_container_width=True)
        
        # Bouton de nettoyage
        if st.button("Nettoyer les données", type="primary", use_container_width=True):
            with st.spinner("Nettoyage en cours..."):
                # Nettoyage
                df_clean, filtered_count = clean_crunchbase_data(df)
                
                # Stocker dans session state
                st.session_state['df_clean'] = df_clean
                st.session_state['filtered_count'] = filtered_count
        
        # Afficher les résultats si disponibles
        if 'df_clean' in st.session_state:
            df_clean = st.session_state['df_clean']
            filtered_count = st.session_state['filtered_count']
            
            st.markdown("---")
            st.success("Nettoyage terminé !")
            
            # Statistiques
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Lignes initiales", len(df))
            with col2:
                st.metric("Lignes filtrées", filtered_count)
            with col3:
                st.metric("Lignes finales", len(df_clean))
            
            # Aperçu des données nettoyées
            st.subheader("Données nettoyées")
            st.dataframe(df_clean, use_container_width=True)
            
            # Boutons de téléchargement
            st.markdown("---")
            st.subheader("Télécharger les résultats")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # CSV
                csv = df_clean.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Télécharger en CSV",
                    data=csv,
                    file_name="crunchbase_cleaned.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
    
    except Exception as e:
        st.error(f"❌ Erreur lors du traitement du fichier : {str(e)}")
        st.info("Vérifiez que votre fichier contient bien toutes les colonnes requises.")

else:
    st.info("Charger un fichier CSV")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    Outil de nettoyage de données Crunchbase 360 Capital 
    </div>
    """,
    unsafe_allow_html=True
)