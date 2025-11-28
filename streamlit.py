# APPLICATION STREAMLIT - ANALYSE DOMICILIATION DES AGENTS DE PARIS

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

# Configuration de la page
st.set_page_config(
    page_title="Analyse Agents Ville de Paris",
    page_icon="🏛️",
    layout="wide"
)

# Titre principal
st.title("🏛️ Analyse de la Domiciliation des Agents de la Ville de Paris")
st.markdown("---")

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data
def charger_donnees():
    """Charge le fichier CSV nettoyé"""
    df = pd.read_csv('domiciliation_agents_nettoyee_et_enrichie.csv', sep=';', encoding='utf-8')
    return df

# Charger les données
try:
    df = charger_donnees()
    st.success(f"✓ Données chargées : {len(df):,} lignes, {len(df.columns)} colonnes")
except Exception as e:
    st.error(f"Erreur de chargement : {e}")
    st.stop()

# --- SIDEBAR - PRÉSENTATION ---
st.sidebar.header("📊 Navigation")
page = st.sidebar.radio(
    "Choisir une section :",
    [
        "📋 Présentation des données",
        "🗺️ Carte géographique",
        "🎨 Treemap - Directions thématiques",
        "📊 Analyse par catégorie",
        "📈 Évolution temporelle",
        "🦠 Analyse post-COVID",
        "☁️ WordCloud - Text Mining"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info(
    """
    **Source :** Open Data Paris  
    **Période :** 2014-2022  
    **Agents :** ~237,000 observations
    """
)

# =============================================================================
# PAGE 1 : PRÉSENTATION DES DONNÉES
# =============================================================================
if page == "📋 Présentation des données":
    st.header("Présentation du jeu de données")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Nombre d'agents", f"{df['AGENT'].sum():,.0f}")
    with col2:
        st.metric("Villes différentes", f"{df['VILLE'].nunique():,}")
    with col3:
        st.metric("Années analysées", f"{df['DATE'].min()} - {df['DATE'].max()}")
    
    st.subheader("Aperçu des données")
    st.dataframe(df.head(20), use_container_width=True)
    
    st.subheader("Statistiques descriptives")
    st.dataframe(df.describe(), use_container_width=True)
    
    # Distribution des catégories
    st.subheader("Distribution des catégories professionnelles")
    cat_counts = df[df['CATEGORIE'].isin(['A', 'B', 'C'])].groupby('CATEGORIE')['AGENT'].sum()
    
    fig = px.pie(
        values=cat_counts.values,
        names=cat_counts.index,
        title="Répartition A / B / C",
        color=cat_counts.index,
        color_discrete_map={'A': '#d62728', 'B': '#ff7f0e', 'C': '#1f77b4'}
    )
    st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# PAGE 2 : CARTE GÉOGRAPHIQUE
# =============================================================================
elif page == "🗺️ Carte géographique":
    st.header("Concentration géographique des agents")
    
    # Agrégation par ville
    donnees_villes = df.groupby(['VILLE', 'LATITUDE', 'LONGITUDE']).agg({
        'AGENT': 'sum'
    }).reset_index().dropna(subset=['LATITUDE', 'LONGITUDE'])
    
    st.info(f"Carte interactive montrant {len(donnees_villes)} villes")
    
    # Carte Plotly (interactif natif dans Streamlit)
    fig = px.scatter_mapbox(
        donnees_villes,
        lat='LATITUDE',
        lon='LONGITUDE',
        size='AGENT',
        color='AGENT',
        hover_name='VILLE',
        hover_data={'AGENT': ':,', 'LATITUDE': False, 'LONGITUDE': False},
        color_continuous_scale='Bluered',
        size_max=30,
        zoom=8,
        mapbox_style='open-street-map',
        title='Concentration des agents par ville'
    )
    
    fig.update_layout(height=700)
    st.plotly_chart(fig, use_container_width=True)
    
    # Top 10 villes
    st.subheader("Top 10 des villes")
    top_villes = donnees_villes.nlargest(10, 'AGENT')[['VILLE', 'AGENT']]
    st.dataframe(top_villes, use_container_width=True)

# =============================================================================
# PAGE 3 : TREEMAP - DIRECTIONS THÉMATIQUES
# =============================================================================
elif page == "🎨 Treemap - Directions thématiques":
    st.header("Distribution des agents par direction thématique")
    st.markdown("*Couleur = Proportion de femmes (Bleu = Hommes | Rouge = Femmes)*")
    
    # Préparer données
    data_treemap = df.dropna(subset=['DIRECTION_THEMATIQUE', 'SEXE'])
    
    direction_totals = []
    for direction in sorted(data_treemap['DIRECTION_THEMATIQUE'].unique()):
        dir_data = data_treemap[data_treemap['DIRECTION_THEMATIQUE'] == direction]
        total_agents = dir_data['AGENT'].sum()
        women_agents = dir_data[dir_data['SEXE'] == 'FEMININ']['AGENT'].sum()
        pct_women = (women_agents / total_agents * 100) if total_agents > 0 else 0
        
        direction_totals.append({
            'DIRECTION_THEMATIQUE': direction,
            'TOTAL_AGENTS': total_agents,
            'PCT_WOMEN': pct_women
        })
    
    direction_totals_df = pd.DataFrame(direction_totals).sort_values('TOTAL_AGENTS', ascending=False)
    
    # Créer treemap avec Plotly
    fig = go.Figure(go.Treemap(
        labels=direction_totals_df['DIRECTION_THEMATIQUE'].tolist(),
        parents=[''] * len(direction_totals_df),
        values=direction_totals_df['TOTAL_AGENTS'].tolist(),
        marker=dict(
            colorscale='RdBu_r',
            cmid=50,
            colorbar=dict(title="% Femmes"),
            line=dict(width=2, color='white')
        ),
        marker_colorscale='RdBu_r',
        hovertemplate='<b>%{label}</b><br>Agents: %{value:,}<extra></extra>',
        textposition='middle center'
    ))
    
    # Ajouter couleur basada en % femmes
    colors = direction_totals_df['PCT_WOMEN'].tolist()
    fig.data[0].marker.colors = colors
    
    fig.update_layout(
        title='Distribution des Agents par Direction Thématique',
        height=700
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tableau de données
    st.subheader("Données détaillées")
    st.dataframe(
        direction_totals_df.style.format({'TOTAL_AGENTS': '{:,.0f}', 'PCT_WOMEN': '{:.1f}%'}),
        use_container_width=True
    )

# =============================================================================
# PAGE 4 : ANALYSE PAR CATÉGORIE
# =============================================================================
elif page == "📊 Analyse par catégorie":
    st.header("Distribution des catégories par direction thématique")
    
    # Filtrer catégories A, B, C
    data_analyse = df[df['CATEGORIE'].isin(['A', 'B', 'C'])].copy()
    
    # Tableau croisé
    tableau_croise = pd.crosstab(
        data_analyse['DIRECTION_THEMATIQUE'],
        data_analyse['CATEGORIE'],
        values=data_analyse['AGENT'],
        aggfunc='sum'
    )
    
    # Pourcentages
    tableau_pct = tableau_croise.div(tableau_croise.sum(axis=1), axis=0) * 100
    tableau_pct = tableau_pct.sort_values('A', ascending=False)
    
    # Graphique stacked bar (Plotly)
    fig = go.Figure()
    
    couleurs = {'C': '#1f77b4', 'B': '#ff7f0e', 'A': '#d62728'}
    
    for categorie in ['C', 'B', 'A']:
        fig.add_trace(go.Bar(
            name=f'Catégorie {categorie}',
            y=tableau_pct.index,
            x=tableau_pct[categorie],
            orientation='h',
            marker_color=couleurs[categorie],
            text=tableau_pct[categorie].round(0).astype(int).astype(str) + '%',
            textposition='inside'
        ))
    
    fig.update_layout(
        barmode='stack',
        title='Distribution des Catégories par Direction Thématique',
        xaxis_title='Pourcentage (%)',
        yaxis_title='',
        height=600,
        showlegend=True,
        legend=dict(orientation='h', y=1.1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Top directions élitistes
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔴 Plus de Catégorie A")
        top_a = tableau_pct['A'].nlargest(5)
        for direction, pct in top_a.items():
            st.write(f"**{direction}** : {pct:.1f}%")
    
    with col2:
        st.subheader("🔵 Plus de Catégorie C")
        top_c = tableau_pct['C'].nlargest(5)
        for direction, pct in top_c.items():
            st.write(f"**{direction}** : {pct:.1f}%")

# =============================================================================
# PAGE 5 : ÉVOLUTION TEMPORELLE
# =============================================================================
elif page == "📈 Évolution temporelle":
    st.header("Évolution des effectifs dans le temps (2014-2022)")
    
    tab1, tab2 = st.tabs(["Par Direction Thématique", "Par Catégorie"])
    
    with tab1:
        st.subheader("Évolution par direction thématique")
        
        # Agrégation
        evolution_direction = df.groupby(['DATE', 'DIRECTION_THEMATIQUE'])['AGENT'].sum().reset_index()
        
        # Graphique Plotly
        fig = px.line(
            evolution_direction,
            x='DATE',
            y='AGENT',
            color='DIRECTION_THEMATIQUE',
            title='Évolution des Effectifs par Direction Thématique',
            markers=True
        )
        
        fig.update_layout(height=600, xaxis_title='Année', yaxis_title='Nombre d\'agents')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Évolution par catégorie professionnelle")
        
        # Filtrer A, B, C
        data_cat = df[df['CATEGORIE'].isin(['A', 'B', 'C'])].copy()
        evolution_cat = data_cat.groupby(['DATE', 'CATEGORIE'])['AGENT'].sum().reset_index()
        
        # Graphique
        fig = px.line(
            evolution_cat,
            x='DATE',
            y='AGENT',
            color='CATEGORIE',
            title='Évolution des Effectifs par Catégorie',
            markers=True,
            color_discrete_map={'A': '#d62728', 'B': '#ff7f0e', 'C': '#1f77b4'}
        )
        
        fig.update_layout(height=600, xaxis_title='Année', yaxis_title='Nombre d\'agents')
        st.plotly_chart(fig, use_container_width=True)
        
        # Pourcentages
        st.subheader("Composition en pourcentage")
        
        pivot_cat = evolution_cat.pivot(index='DATE', columns='CATEGORIE', values='AGENT')
        pivot_cat_pct = pivot_cat.div(pivot_cat.sum(axis=1), axis=0) * 100
        
        fig = px.area(
            pivot_cat_pct.reset_index(),
            x='DATE',
            y=['C', 'B', 'A'],
            title='Composition par Catégorie (%)',
            color_discrete_map={'A': '#d62728', 'B': '#ff7f0e', 'C': '#1f77b4'}
        )
        
        fig.update_layout(height=500, yaxis_title='Pourcentage (%)')
        st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# PAGE 6 : ANALYSE POST-COVID
# =============================================================================
elif page == "🦠 Analyse post-COVID":
    st.header("Impact du COVID-19 sur la Dispersion Géographique")
    st.markdown("*Analyse de la distance moyenne de Paris avant/après 2020*")
    
    # Distance moyenne par année
    distance_annuelle = df.groupby('DATE')['DISTANCE_PARIS_KM'].mean()
    
    # Graphique
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=distance_annuelle.index,
        y=distance_annuelle.values,
        mode='lines+markers',
        name='Distance moyenne',
        line=dict(color='#2E86AB', width=3),
        marker=dict(size=10)
    ))
    
    # Ligne COVID
    fig.add_vline(x=2019.5, line_dash="dash", line_color="red", 
                  annotation_text="Début COVID-19", annotation_position="top")
    
    fig.update_layout(
        title='Distance Moyenne de Paris par Année',
        xaxis_title='Année',
        yaxis_title='Distance moyenne (km)',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistiques
    col1, col2, col3 = st.columns(3)
    
    pre_covid = df[df['DATE'] <= 2019]['DISTANCE_PARIS_KM'].mean()
    post_covid = df[df['DATE'] >= 2020]['DISTANCE_PARIS_KM'].mean()
    variation = ((post_covid - pre_covid) / pre_covid) * 100
    
    with col1:
        st.metric("Distance pré-COVID (≤2019)", f"{pre_covid:.2f} km")
    with col2:
        st.metric("Distance post-COVID (≥2020)", f"{post_covid:.2f} km")
    with col3:
        st.metric("Variation", f"{variation:+.2f}%", delta_color="normal")
    
    # Boxplot comparatif
    st.subheader("Distribution des distances : Pré vs Post COVID")
    
    df_covid = df.copy()
    df_covid['Période'] = df_covid['DATE'].apply(lambda x: 'Pré-COVID (≤2019)' if x <= 2019 else 'Post-COVID (≥2020)')
    
    fig = px.box(
        df_covid,
        x='Période',
        y='DISTANCE_PARIS_KM',
        color='Période',
        color_discrete_map={
            'Pré-COVID (≤2019)': '#2E86AB',
            'Post-COVID (≥2020)': '#A23B72'
        }
    )
    
    fig.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Interprétation
    if abs(variation) > 2:
        st.success("→ Dispersion géographique détectable (>2%)")
    else:
        st.info("→ Pas de dispersion significative (rigidité du statut fonctionnaire?)")

# =============================================================================
# PAGE 7 : WORDCLOUD
# =============================================================================
elif page == "☁️ WordCloud - Text Mining":
    st.header("Analyse d'un Article de Presse - Text Mining")
    st.markdown("**Source :** Le Figaro - Article sur les effectifs de la Ville de Paris")
    
    st.info("Analyse textuelle d'un article portant sur les effectifs de la mairie de Paris")
    
    # Charger l'image du wordcloud
    try:
        img = Image.open('wordcloud_article_lefigaro.png')
        st.image(img, caption='Nuage de Mots - Article Le Figaro', use_container_width=True)
        
        st.markdown("""
        ### Interprétation
        
        Le nuage de mots met en évidence les termes les plus fréquents dans l'article analysé.
        Les mots en gros caractères sont les plus mentionnés, reflétant les thèmes centraux
        du discours médiatique sur la fonction publique territoriale parisienne.
        
        **Méthodologie :**
        1. Extraction du texte de l'article
        2. Nettoyage (suppression ponctuation, URLs, etc.)
        3. Tokenisation (découpage en mots)
        4. Suppression des stopwords (mots vides)
        5. Génération du WordCloud basé sur les fréquences
        """)
        
    except FileNotFoundError:
        st.error("❌ Fichier wordcloud_article_lefigaro.png non trouvé dans le dossier")
        st.info("Assurez-vous que le fichier est dans le même répertoire que streamlit.py")

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <p>📊 Projet Data Management 2024-2025 | Données : Open Data Paris | Outil : Streamlit + Python</p>
    </div>
    """,
    unsafe_allow_html=True
)