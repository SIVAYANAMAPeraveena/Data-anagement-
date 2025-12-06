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
    page_icon="📊",
    layout="wide"
)

# Titre principal
st.title("Analyse de la Domiciliation des Agents de la Ville de Paris")
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
    st.success(f"Données chargées : {len(df):,} lignes, {len(df.columns)} colonnes")
except Exception as e:
    st.error(f"Erreur de chargement : {e}")
    st.stop()

# Mapping des directions vers leurs catégories thématiques avec noms complets
DIRECTION_MAPPING = {
    'Education & Jeunesse': {
        'DAE': 'Direction des Affaires Scolaires',
        'DASCO': 'Direction des Affaires Scolaires',
        'DJS': 'Direction de la Jeunesse et des Sports',
        'DPJEV': 'Direction des Politiques Jeunesse, Éducation et Vie associative',
        'AUT.ADM.PARIS.EPPM': 'Établissements Publics Parisiens'
    },
    'Urbanisme & Environnement': {
        'DVD': 'Direction de la Voirie et des Déplacements',
        'DEVE': 'Direction des Espaces Verts et de l\'Environnement',
        'DU': 'Direction de l\'Urbanisme',
        'DILT': 'Direction de l\'Immobilier, de la Logistique et des Transports',
        'DLH': 'Direction du Logement et de l\'Habitat',
        'DPE': 'Direction de la Propreté et de l\'Eau',
        'DPA': 'Direction de la Propreté et des Achats',
        'DPP': 'Direction du Patrimoine et de l\'Architecture',
        'DTEC': 'Direction Technique'
    },
    'Social & Santé': {
        'DASES': 'Direction de l\'Action Sociale, de l\'Enfance et de la Santé',
        'DAS': 'Direction de l\'Action Sociale',
        'DSOL': 'Direction de la Solidarité',
        'AUT.ADM.PARIS.CASVP': 'Centre d\'Action Sociale de la Ville de Paris',
        'CASVP': 'Centre d\'Action Sociale de la Ville de Paris'
    },
    'Culture & Citoyenneté': {
        'DAC': 'Direction des Affaires Culturelles',
        'DCPA': 'Direction de la Citoyenneté, de la Participation et de l\'Action citoyenne',
        'DDCT': 'Direction de la Démocratie, des Citoyen·ne·s et des Territoires',
        'DDEEES': 'Direction du Développement Économique, de l\'Emploi et de l\'Enseignement Supérieur'
    },
    'Administration & RH': {
        'DRH': 'Direction des Ressources Humaines',
        'GESTION RH': 'Gestion des Ressources Humaines',
        'SG': 'Secrétariat Général',
        'DSTI': 'Direction des Systèmes et Technologies de l\'Information',
        'DSIN': 'Direction des Systèmes d\'Information et du Numérique',
        'DSP': 'Direction de la Sécurité de Proximité',
        'DPSP': 'Direction de la Prévention, de la Sécurité et de la Protection',
        'DPMP': 'Direction de la Prévention, de la Mission de Préfiguration'
    },
    'Finances & Juridique': {
        'DFA': 'Direction des Finances et des Achats',
        'DFPE': 'Direction des Finances, des Achats et de l\'Immobilier',
        'DAJ': 'Direction des Affaires Juridiques',
        'DICOM': 'Direction de l\'Information et de la Communication'
    },
    'Cabinet & Gouvernance': {
        'CABINET DE LA MAIRIE': 'Cabinet de la Mairie',
        'CABINET DU MAIRE': 'Cabinet du Maire'
    },
    'Administration Départementale': {
        'ADMINISTRATION DEPARTEMENTALE': 'Administration Départementale',
        'AUTRES ADMIN. PARIS.': 'Autres administrations parisiennes'
    }
}

# --- SIDEBAR - PRÉSENTATION ---
st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Choisir une section :",
    [
        "Présentation des données",
        "Carte géographique",
        "Analyse géographique détaillée",
        "Treemap - Directions thématiques",
        "Analyse par catégorie",
        "Évolution temporelle",
        "Analyse post-COVID",
        "WordCloud - Text Mining"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info(
    """
    **Source :** Open Data Paris  
    **Période :** 2014-2022  
    **Note :** Les données sont agrégées par combinaisons de critères
    """
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔗 Accès aux données")
st.sidebar.markdown(
    """
    [📊 Dataset OpenData Paris](https://opendata.paris.fr/explore/dataset/domiciliation-des-agents-bilan-social/information/)
    """
)

# =============================================================================
# PAGE 1 : PRÉSENTATION DES DONNÉES
# =============================================================================
if page == "Présentation des données":
    st.header("Présentation du jeu de données")
    
    # FILTRO DE AÑO
    st.sidebar.markdown("---")
    st.sidebar.subheader("Filtres")
    annee_selectionnee = st.sidebar.selectbox(
        "Sélectionner une année :",
        options=sorted(df['DATE'].unique(), reverse=True),
        index=0  # Por defecto el más reciente (2022)
    )
    
    # Filtrar datos por año
    df_filtree = df[df['DATE'] == annee_selectionnee].copy()
    
    # Mensaje claro
    st.info(f"Données affichées pour l'année {annee_selectionnee} (pour éviter le double comptage des agents)")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Nombre d'agents", f"{df_filtree['AGENT'].sum():,.0f}")
    with col2:
        st.metric("Villes différentes", f"{df_filtree['VILLE'].nunique():,}")
    with col3:
        st.metric("Directions thématiques", f"{df_filtree['DIRECTION_THEMATIQUE'].nunique()}")
    
    st.subheader(f"Aperçu des données - {annee_selectionnee}")
    st.dataframe(df_filtree.head(20), use_container_width=True)
    
    st.subheader("Statistiques descriptives")
    st.dataframe(df_filtree.describe(), use_container_width=True)
    
    # Distribution des catégories
    st.subheader("Distribution des catégories professionnelles")
    cat_counts = df_filtree[df_filtree['CATEGORIE'].isin(['A', 'B', 'C'])].groupby('CATEGORIE')['AGENT'].sum()
    
    fig = px.pie(
        values=cat_counts.values,
        names=cat_counts.index,
        title=f"Répartition A / B / C en {annee_selectionnee}",
        color=cat_counts.index,
        color_discrete_map={'A': '#d62728', 'B': '#ff7f0e', 'C': '#1f77b4'}
    )
    st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# PAGE 2 : CARTE GÉOGRAPHIQUE
# =============================================================================
elif page == "Carte géographique":
    st.header("Concentration géographique des agents")
    
    # FILTRO DE AÑO
    st.sidebar.markdown("---")
    st.sidebar.subheader("Filtres")
    annee_selectionnee = st.sidebar.selectbox(
        "Sélectionner une année :",
        options=sorted(df['DATE'].unique(), reverse=True),
        index=0  # 2022 por defecto
    )
    
    # Filtrar datos por año
    df_filtree = df[df['DATE'] == annee_selectionnee].copy()
    
    # Mensaje claro
    st.info(f"Carte pour l'année {annee_selectionnee} (évite le double comptage)")
    
    # Agrégation par ville (ya viene con PARIS 1, PARIS 10, etc en la columna VILLE)
    donnees_villes = df_filtree.groupby(['VILLE', 'LATITUDE', 'LONGITUDE']).agg({
        'AGENT': 'sum'
    }).reset_index().dropna(subset=['LATITUDE', 'LONGITUDE'])
    
    st.success(f"Carte interactive montrant {len(donnees_villes)} localisations")
    
    # Carte Plotly
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
        title=f'Concentration des agents par ville - {annee_selectionnee}'
    )
    
    fig.update_layout(
        height=700,
        mapbox=dict(
            center=dict(lat=48.8566, lon=2.3522),
            zoom=8
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Interpretación descriptiva
    st.markdown("""
    La carte montre une forte concentration d'agents dans Paris intra-muros, 
    avec une présence importante dans les communes limitrophes de la petite couronne. 
    La taille et l'intensité des bulles correspondent au nombre d'agents par localisation.
    """)
    
    # Top 20 villes avec totaux et pourcentages
    st.subheader(f"Top 20 des localisations par nombre d'agents - {annee_selectionnee}")
    top_villes = donnees_villes.nlargest(20, 'AGENT')[['VILLE', 'AGENT']].copy()
    
    # Calculer totaux et pourcentages
    total_agents = donnees_villes['AGENT'].sum()
    top_villes['POURCENTAGE'] = (top_villes['AGENT'] / total_agents * 100).round(2)
    top_villes['RANG'] = range(1, len(top_villes) + 1)
    
    # Réorganiser colonnes
    top_villes = top_villes[['RANG', 'VILLE', 'AGENT', 'POURCENTAGE']]
    top_villes.columns = ['RANG', 'LOCALISATION', 'AGENTS', 'POURCENTAGE']
    
    # Ajouter ligne de total
    total_top20 = top_villes['AGENTS'].sum()
    pct_top20 = (total_top20 / total_agents * 100).round(2)
    
    st.dataframe(
        top_villes.style.format({'AGENTS': '{:,.0f}', 'POURCENTAGE': '{:.2f}%'}),
        use_container_width=True
    )
    
    # Métriques de synthèse
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total agents (toutes localisations)", f"{total_agents:,.0f}")
    with col2:
        st.metric("Total Top 20", f"{total_top20:,.0f}")
    with col3:
        st.metric("% du total", f"{pct_top20:.2f}%")
    
    # Interpretación descriptiva
    st.markdown("""
    Le tableau montre que les 20 premières localisations concentrent 
    une part importante des effectifs. Les arrondissements parisiens dominent, 
    suivis par des communes de banlieue proche.
    """)

# =============================================================================
# PAGE 3 : ANALYSE GÉOGRAPHIQUE DÉTAILLÉE
# =============================================================================
elif page == "Analyse géographique détaillée":
    st.header("Analyse de la Distance à Paris : Catégorie et Genre")
    st.markdown("Exploration de la relation entre localisation résidentielle, hiérarchie professionnelle et genre")
    
    # Filtrer données valides et au 95% (éliminer outliers extremos)
    df_geo = df[df['DISTANCE_PARIS_KM'].notna()].copy()
    
    # Calcular percentiles 2.5 y 97.5 para filtrar outliers
    p_low = df_geo['DISTANCE_PARIS_KM'].quantile(0.025)
    p_high = df_geo['DISTANCE_PARIS_KM'].quantile(0.975)
    df_geo = df_geo[(df_geo['DISTANCE_PARIS_KM'] >= p_low) & (df_geo['DISTANCE_PARIS_KM'] <= p_high)]
    
    st.info(f"Analyse basée sur 95% des données (outliers extrêmes exclus) : {len(df_geo):,} observations")
    
    # GRAPHIQUE 1: Boxplot par catégorie
    st.subheader("Distribution des distances à Paris selon la catégorie professionnelle")
    
    data_cat = df_geo[df_geo['CATEGORIE'].isin(['A', 'B', 'C'])].copy()
    
    fig1 = px.box(
        data_cat,
        x='CATEGORIE',
        y='DISTANCE_PARIS_KM',
        color='CATEGORIE',
        color_discrete_map={'A': '#d62728', 'B': '#ff7f0e', 'C': '#1f77b4'},
        labels={'DISTANCE_PARIS_KM': 'Distance à Paris (km)', 'CATEGORIE': 'Catégorie Professionnelle'}
    )
    
    fig1.update_traces(
        quartilemethod="linear",
        hovertemplate='<b>Catégorie %{x}</b><br>' +
                      'Médiane: %{median:.1f} km<br>' +
                      'Q1 (25%%): %{q1:.1f} km<br>' +
                      'Q3 (75%%): %{q3:.1f} km<br>' +
                      'Min: %{lowerfence:.1f} km<br>' +
                      'Max: %{upperfence:.1f} km<br>' +
                      '<extra></extra>'
    )
    
    fig1.update_layout(
        title='Distribution des Distances à Paris par Catégorie Professionnelle',
        height=500,
        showlegend=False
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # Interprétation descriptiva
    st.markdown("""
    Les boxplots montrent les distributions de distances pour chaque catégorie professionnelle. 
    La médiane (ligne centrale) indique la distance typique, tandis que la boîte représente 50% des agents.
    """)
    
    # GRAPHIQUE 2: Boxplot par sexe
    st.subheader("Distribution des distances à Paris selon le genre")
    
    data_sexe = df_geo[df_geo['SEXE'].isin(['FEMININ', 'MASCULIN'])].copy()
    
    fig2 = px.box(
        data_sexe,
        x='SEXE',
        y='DISTANCE_PARIS_KM',
        color='SEXE',
        color_discrete_map={'FEMININ': '#e377c2', 'MASCULIN': '#17becf'},
        labels={'DISTANCE_PARIS_KM': 'Distance à Paris (km)', 'SEXE': 'Genre'}
    )
    
    fig2.update_traces(
        quartilemethod="linear",
        hovertemplate='<b>%{x}</b><br>' +
                      'Médiane: %{median:.1f} km<br>' +
                      'Q1 (25%%): %{q1:.1f} km<br>' +
                      'Q3 (75%%): %{q3:.1f} km<br>' +
                      'Min: %{lowerfence:.1f} km<br>' +
                      'Max: %{upperfence:.1f} km<br>' +
                      '<extra></extra>'
    )
    
    fig2.update_layout(
        title='Distribution des Distances à Paris par Genre',
        height=500,
        showlegend=False
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Interprétation descriptiva
    st.markdown("""
    La comparaison par genre montre les différences de distribution des distances résidentielles. 
    Les médianes et quartiles permettent d'identifier les tendances centrales et la dispersion pour chaque groupe.
    """)
    
    # GRAPHIQUE 3: Boxplot Catégorie × Genre
    st.subheader("Distribution des distances : Analyse croisée Catégorie × Genre")
    
    data_croisee = df_geo[(df_geo['CATEGORIE'].isin(['A', 'B', 'C'])) & 
                          (df_geo['SEXE'].isin(['FEMININ', 'MASCULIN']))].copy()
    
    fig3 = px.box(
        data_croisee,
        x='CATEGORIE',
        y='DISTANCE_PARIS_KM',
        color='SEXE',
        color_discrete_map={'FEMININ': '#e377c2', 'MASCULIN': '#17becf'},
        labels={'DISTANCE_PARIS_KM': 'Distance à Paris (km)', 'CATEGORIE': 'Catégorie Professionnelle'}
    )
    
    fig3.update_traces(
        quartilemethod="linear"
    )
    
    fig3.update_layout(
        title='Distribution des Distances à Paris par Catégorie et Genre',
        height=600
    )
    
    st.plotly_chart(fig3, use_container_width=True)
    
    # Interprétation descriptiva
    st.markdown("""
    L'analyse croisée compare simultanément les effets de la catégorie professionnelle 
    et du genre sur la localisation résidentielle. Pour chaque catégorie (A, B, C), les distributions sont présentées 
    séparément pour les hommes et les femmes.
    """)
    
    # GRAPHIQUE 4: Heatmap - Tableau croisé
    st.subheader("Synthèse : Distance médiane par Catégorie et Genre")
    
    tableau_croise = data_croisee.groupby(['CATEGORIE', 'SEXE'])['DISTANCE_PARIS_KM'].median().reset_index()
    pivot_table = tableau_croise.pivot(index='CATEGORIE', columns='SEXE', values='DISTANCE_PARIS_KM')
    
    fig4 = go.Figure(data=go.Heatmap(
        z=pivot_table.values,
        x=pivot_table.columns,
        y=pivot_table.index,
        colorscale='RdYlBu_r',
        text=pivot_table.values.round(2),
        texttemplate='%{text} km',
        textfont={"size": 14},
        colorbar=dict(title="Distance<br>médiane (km)")
    ))
    
    fig4.update_layout(
        title='Distance Médiane à Paris : Heatmap Catégorie × Genre',
        xaxis_title='Genre',
        yaxis_title='Catégorie Professionnelle',
        height=400
    )
    
    st.plotly_chart(fig4, use_container_width=True)
    
    # Interprétation descriptiva
    st.markdown("""
    La heatmap synthétise les distances médianes pour chaque combinaison de catégorie et genre. 
    Les couleurs facilitent l'identification des groupes résidant plus près ou plus loin de Paris.
    """)

# =============================================================================
# PAGE 4 : TREEMAP - DIRECTIONS THÉMATIQUES (JERÁRQUICO 2 NIVELES)
# =============================================================================
elif page == "Treemap - Directions thématiques":
    st.header("Distribution des agents par direction thématique")
    st.markdown("Treemap hiérarchique : Catégories thématiques > Directions individuelles")
    st.markdown("Couleur = Proportion de femmes (Bleu = Hommes | Rouge = Femmes)")
    
    # Préparer données hiérarchiques
    data_treemap = df.dropna(subset=['DIRECTION_THEMATIQUE', 'DIRECTION', 'SEXE'])
    
    # Crear estructura jerárquica
    labels = []
    parents = []
    values = []
    colors = []
    hover_texts = []
    
    # Primero agregar las categorías temáticas (nivel 1)
    for thematique in sorted(data_treemap['DIRECTION_THEMATIQUE'].unique()):
        them_data = data_treemap[data_treemap['DIRECTION_THEMATIQUE'] == thematique]
        total_agents = them_data['AGENT'].sum()
        women_agents = them_data[them_data['SEXE'] == 'FEMININ']['AGENT'].sum()
        pct_women = (women_agents / total_agents * 100) if total_agents > 0 else 0
        
        labels.append(thematique)
        parents.append('')
        values.append(total_agents)
        colors.append(pct_women)
        hover_texts.append(
            f"<b>{thematique}</b><br>"
            f"Total: {int(total_agents):,} agents<br>"
            f"Femmes: {pct_women:.1f}%"
        )
    
    # Luego agregar las direcciones individuales (nivel 2)
    for thematique in sorted(data_treemap['DIRECTION_THEMATIQUE'].unique()):
        them_data = data_treemap[data_treemap['DIRECTION_THEMATIQUE'] == thematique]
        
        # Por cada dirección en esta temática
        for direction in them_data['DIRECTION'].unique():
            dir_data = them_data[them_data['DIRECTION'] == direction]
            total_agents = dir_data['AGENT'].sum()
            women_agents = dir_data[dir_data['SEXE'] == 'FEMININ']['AGENT'].sum()
            pct_women = (women_agents / total_agents * 100) if total_agents > 0 else 0
            
            # Buscar nombre completo
            nom_complet = direction
            for them_key, directions_dict in DIRECTION_MAPPING.items():
                if direction in directions_dict:
                    nom_complet = f"{direction} - {directions_dict[direction]}"
                    break
            
            labels.append(direction)
            parents.append(thematique)
            values.append(total_agents)
            colors.append(pct_women)
            hover_texts.append(
                f"<b>{nom_complet}</b><br>"
                f"Catégorie: {thematique}<br>"
                f"Total: {int(total_agents):,} agents<br>"
                f"Femmes: {pct_women:.1f}%"
            )
    
    # Créer treemap hiérarchique
    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        marker=dict(
            colorscale='RdBu_r',
            cmid=50,
            colorbar=dict(title="% Femmes"),
            line=dict(width=2, color='white'),
            colors=colors
        ),
        hovertemplate='%{customdata}<extra></extra>',
        customdata=hover_texts,
        textposition='middle center',
        textfont=dict(size=10, color='white', family='Arial')
    ))
    
    fig.update_layout(
        title='Distribution Hiérarchique : Catégories Thématiques > Directions',
        height=800
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Interpretación descriptiva
    st.markdown("""
    Le treemap présente une visualisation hiérarchique à deux niveaux. 
    La taille de chaque rectangle est proportionnelle au nombre d'agents. Le premier niveau montre 
    les catégories thématiques principales, et en cliquant dessus, on peut explorer les directions 
    individuelles qui les composent. La couleur indique la proportion de femmes, du bleu (majorité masculine) 
    au rouge (majorité féminine).
    """)
    
    # Tableau de composition des catégories thématiques (CON % FEMMES)
    st.subheader("Composition détaillée par catégorie thématique")
    
    for thematique in sorted(DIRECTION_MAPPING.keys()):
        with st.expander(f"**{thematique}**"):
            directions = DIRECTION_MAPPING[thematique]
            
            # Table des directions avec % femmes
            data_table = []
            for sigla, nom_complet in directions.items():
                # Compter agents pour cette direction
                dir_data = df[df['DIRECTION'] == sigla]
                nb_agents = dir_data['AGENT'].sum()
                
                if nb_agents > 0:
                    women_agents = dir_data[dir_data['SEXE'] == 'FEMININ']['AGENT'].sum()
                    pct_women = (women_agents / nb_agents * 100)
                    
                    data_table.append({
                        'Sigle': sigla,
                        'Nom complet': nom_complet,
                        'Agents': nb_agents,
                        '% Femmes': pct_women
                    })
            
            table_df = pd.DataFrame(data_table)
            if not table_df.empty:
                total = table_df['Agents'].sum()
                table_df['% Total'] = (table_df['Agents'] / total * 100).round(2)
                table_df = table_df.sort_values('Agents', ascending=False)
                
                st.dataframe(
                    table_df.style.format({
                        'Agents': '{:,.0f}', 
                        '% Total': '{:.2f}%',
                        '% Femmes': '{:.1f}%'
                    }),
                    use_container_width=True
                )
                st.metric(f"Total {thematique}", f"{total:,.0f} agents")
            else:
                st.info("Aucune donnée disponible pour cette catégorie")
    
    # Tableau récapitulatif global
    st.subheader("Tableau récapitulatif par catégorie thématique")
    
    summary_data = []
    for thematique in sorted(data_treemap['DIRECTION_THEMATIQUE'].unique()):
        them_data = data_treemap[data_treemap['DIRECTION_THEMATIQUE'] == thematique]
        total_agents = them_data['AGENT'].sum()
        women_agents = them_data[them_data['SEXE'] == 'FEMININ']['AGENT'].sum()
        pct_women = (women_agents / total_agents * 100) if total_agents > 0 else 0
        
        summary_data.append({
            'Catégorie Thématique': thematique,
            'Total Agents': total_agents,
            '% Femmes': pct_women
        })
    
    summary_df = pd.DataFrame(summary_data).sort_values('Total Agents', ascending=False)
    total_general = summary_df['Total Agents'].sum()
    summary_df['% du Total'] = (summary_df['Total Agents'] / total_general * 100).round(2)
    
    st.dataframe(
        summary_df.style.format({
            'Total Agents': '{:,.0f}',
            '% du Total': '{:.2f}%',
            '% Femmes': '{:.1f}%'
        }),
        use_container_width=True
    )
    
    # Interpretación descriptiva
    st.markdown("""
    Les tableaux détaillés montrent la composition exacte de chaque catégorie thématique, 
    avec les effectifs par direction, leur poids relatif, et la proportion de femmes.
    """)

# =============================================================================
# PAGE 5 : ANALYSE PAR CATÉGORIE
# =============================================================================
elif page == "Analyse par catégorie":
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
    
    # Interpretación descriptiva
    st.markdown("""
    Le graphique en barres empilées montre la composition de chaque direction thématique 
    selon les trois catégories professionnelles (A, B, C). Les directions sont classées par ordre décroissant 
    de proportion de catégorie A.
    """)
    
    # Top directions élitistes
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Plus de Catégorie A")
        top_a = tableau_pct['A'].nlargest(5)
        for direction, pct in top_a.items():
            st.write(f"**{direction}** : {pct:.1f}%")
    
    with col2:
        st.subheader("Plus de Catégorie C")
        top_c = tableau_pct['C'].nlargest(5)
        for direction, pct in top_c.items():
            st.write(f"**{direction}** : {pct:.1f}%")
    
    # Interpretación descriptiva
    st.markdown("""
    Les classements montrent les cinq directions avec les plus fortes concentrations 
    de catégorie A (cadres) et de catégorie C (agents d'exécution). Ces différences reflètent les missions 
    et besoins spécifiques de chaque service.
    """)

# =============================================================================
# PAGE 6 : ÉVOLUTION TEMPORELLE
# =============================================================================
elif page == "Évolution temporelle":
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
        
        # Interpretación descriptiva
        st.markdown("""
        L'évolution temporelle montre les tendances d'effectifs pour chaque direction thématique 
        entre 2014 et 2022. Certaines directions présentent une croissance continue, d'autres une stabilité, 
        et quelques-unes un déclin.
        """)
    
    with tab2:
        st.subheader("Évolution par catégorie professionnelle")
        
        # Filtrer A, B, C
        data_cat = df[df['CATEGORIE'].isin(['A', 'B', 'C'])].copy()
        evolution_cat = data_cat.groupby(['DATE', 'CATEGORIE'])['AGENT'].sum().reset_index()
        
        # Graphique 1: Valeurs absolues
        fig1 = px.line(
            evolution_cat,
            x='DATE',
            y='AGENT',
            color='CATEGORIE',
            title='Évolution des Effectifs par Catégorie (valeurs absolues)',
            markers=True,
            color_discrete_map={'A': '#d62728', 'B': '#ff7f0e', 'C': '#1f77b4'}
        )
        
        fig1.update_layout(height=500, xaxis_title='Année', yaxis_title='Nombre d\'agents')
        st.plotly_chart(fig1, use_container_width=True)
        
        # Graphique 2: Pourcentages (stacked area)
        st.subheader("Composition en pourcentage")
        
        pivot_cat = evolution_cat.pivot(index='DATE', columns='CATEGORIE', values='AGENT')
        pivot_cat_pct = pivot_cat.div(pivot_cat.sum(axis=1), axis=0) * 100
        
        fig2 = go.Figure()
        
        for categorie in ['C', 'B', 'A']:
            couleurs_cat = {'A': '#d62728', 'B': '#ff7f0e', 'C': '#1f77b4'}
            fig2.add_trace(go.Scatter(
                x=pivot_cat_pct.index,
                y=pivot_cat_pct[categorie],
                name=f'Catégorie {categorie}',
                mode='lines',
                stackgroup='one',
                fillcolor=couleurs_cat[categorie]
            ))
        
        fig2.update_layout(
            title='Composition par Catégorie (%) - Aire empilée',
            xaxis_title='Année',
            yaxis_title='Pourcentage (%)',
            height=500,
            yaxis=dict(range=[0, 100])
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
        # Interpretación descriptiva
        st.markdown("""
        Les deux graphiques présentent l'évolution des catégories professionnelles. 
        Le premier montre les effectifs absolus, le second révèle les changements de composition 
        en pourcentages.
        """)
        
        # Analyse des tendances
        st.subheader("Analyse des tendances")
        col1, col2, col3 = st.columns(3)
        
        for i, cat in enumerate(['A', 'B', 'C']):
            val_debut = pivot_cat[cat].iloc[0]
            val_fin = pivot_cat[cat].iloc[-1]
            variation = ((val_fin - val_debut) / val_debut * 100)
            
            with [col1, col2, col3][i]:
                st.metric(
                    f"Catégorie {cat}",
                    f"{val_fin:,.0f}",
                    f"{variation:+.1f}%",
                    delta_color="normal"
                )

# =============================================================================
# PAGE 7 : ANALYSE POST-COVID
# =============================================================================
elif page == "Analyse post-COVID":
    st.header("Impact du COVID-19 sur la Dispersion Géographique")
    st.markdown("Analyse de la distance moyenne de Paris avant/après 2020")
    
    # Distance moyenne par année
    distance_annuelle = df.groupby('DATE')['DISTANCE_PARIS_KM'].mean()
    
    # GRAPHIQUE 1: Distance moyenne par année
    st.subheader("Distance moyenne de Paris par année")
    
    fig1 = go.Figure()
    
    fig1.add_trace(go.Scatter(
        x=distance_annuelle.index,
        y=distance_annuelle.values,
        mode='lines+markers',
        name='Distance moyenne',
        line=dict(color='#2E86AB', width=3),
        marker=dict(size=10)
    ))
    
    # Ligne COVID
    fig1.add_vline(x=2019.5, line_dash="dash", line_color="red", 
                  annotation_text="Début COVID-19", annotation_position="top")
    
    fig1.update_layout(
        title='Distance Moyenne de Paris par Année',
        xaxis_title='Année',
        yaxis_title='Distance moyenne (km)',
        height=500
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
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
    
    # Interpretación descriptiva
    st.markdown("""
    L'évolution de la distance moyenne montre la tendance de localisation résidentielle 
    avant et après le début de la pandémie COVID-19 (marquée par la ligne verticale rouge). 
    Les métriques comparent les périodes pré-COVID (2014-2019) et post-COVID (2020-2022).
    """)
    
    # GRAPHIQUE 2: Boxplot comparatif
    st.subheader("Distribution des distances : Pré vs Post COVID")
    
    df_covid = df.copy()
    df_covid['Période'] = df_covid['DATE'].apply(lambda x: 'Pré-COVID (≤2019)' if x <= 2019 else 'Post-COVID (≥2020)')
    
    fig2 = px.box(
        df_covid,
        x='Période',
        y='DISTANCE_PARIS_KM',
        color='Période',
        color_discrete_map={
            'Pré-COVID (≤2019)': '#2E86AB',
            'Post-COVID (≥2020)': '#A23B72'
        }
    )
    
    fig2.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)
    
    # Interpretación descriptiva
    st.markdown("""
    Les boxplots comparent les distributions complètes des distances pour les deux périodes. 
    Cette visualisation révèle les changements dans la médiane, les quartiles et la dispersion globale.
    """)
    
    # GRAPHIQUE 3: Évolution Paris vs Hors Paris
    st.subheader("Répartition Paris vs Hors Paris dans le temps")
    
    zone_evolution = df.groupby(['DATE', 'ZONE_SIMPLIFIEE'])['AGENT'].sum().reset_index()
    zone_pivot = zone_evolution.pivot(index='DATE', columns='ZONE_SIMPLIFIEE', values='AGENT')
    zone_pct = zone_pivot.div(zone_pivot.sum(axis=1), axis=0) * 100
    
    fig3 = go.Figure()
    
    if 'HORS PARIS' in zone_pct.columns:
        fig3.add_trace(go.Scatter(
            x=zone_pct.index,
            y=zone_pct['HORS PARIS'],
            name='Hors Paris',
            mode='lines',
            stackgroup='one',
            fillcolor='#A23B72'
        ))
    
    if 'PARIS' in zone_pct.columns:
        fig3.add_trace(go.Scatter(
            x=zone_pct.index,
            y=zone_pct['PARIS'],
            name='Paris',
            mode='lines',
            stackgroup='one',
            fillcolor='#F18F01'
        ))
    
    fig3.add_vline(x=2019.5, line_dash="dash", line_color="red",
                   annotation_text="COVID-19")
    
    fig3.update_layout(
        title='Répartition Paris vs Hors Paris (%)',
        xaxis_title='Année',
        yaxis_title='Pourcentage (%)',
        height=500,
        yaxis=dict(range=[0, 100])
    )
    
    st.plotly_chart(fig3, use_container_width=True)
    
    # Interpretación descriptiva
    st.markdown("""
    Le graphique en aires empilées montre l'évolution de la proportion d'agents 
    résidant à Paris intra-muros versus hors Paris.
    """)
    
    # GRAPHIQUE 4: Agents à >50km
    st.subheader("Agents vivant à plus de 50km de Paris")
    
    agents_loin = df[df['DISTANCE_PARIS_KM'] > 50].groupby('DATE')['AGENT'].sum()
    
    fig4 = go.Figure()
    
    fig4.add_trace(go.Bar(
        x=agents_loin.index,
        y=agents_loin.values,
        marker_color=['#2E86AB' if x < 2020 else '#A23B72' for x in agents_loin.index],
        showlegend=False
    ))
    
    fig4.add_vline(x=2019.5, line_dash="dash", line_color="red")
    
    fig4.update_layout(
        title='Nombre d\'agents vivant à >50km de Paris',
        xaxis_title='Année',
        yaxis_title='Nombre d\'agents',
        height=500
    )
    
    st.plotly_chart(fig4, use_container_width=True)
    
    # Interpretación descriptiva
    st.markdown("""
    Ce graphique se concentre sur les agents résidant à plus de 50 km de Paris, 
    une distance significative impliquant généralement des trajets quotidiens conséquents ou du télétravail régulier.
    """)
    
    # Interprétation finale
    st.subheader("Synthèse")
    if abs(variation) > 2:
        st.success(f"Variation détectable de {variation:+.2f}% entre les périodes pré et post-COVID")
    else:
        st.info(f"Variation limitée ({variation:+.2f}%) : stabilité relative des patterns résidentiels")

# =============================================================================
# PAGE 8 : WORDCLOUD
# =============================================================================
elif page == "WordCloud - Text Mining":
    st.header("Analyse d'un Article de Presse - Text Mining")
    st.markdown("**Source :** [Le Figaro - Article sur les effectifs de la Ville de Paris](https://www.lefigaro.fr/actualite-france/une-armee-de-55-000-personnes-la-mairie-de-paris-emploie-t-elle-plus-d-agents-que-toutes-les-prefectures-de-france-reunies-20241029)")
    
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
        
        # Interpretación descriptiva
        st.markdown("""
        Le nuage de mots révèle les termes dominants du discours médiatique : 
        les mots de plus grande taille apparaissent plus fréquemment dans le texte. Cette visualisation 
        permet d'identifier rapidement les thèmes principaux abordés dans l'article (effectifs, services, 
        administration, budget, etc.).
        """)
        
    except FileNotFoundError:
        st.error("Fichier wordcloud_article_lefigaro.png non trouvé dans le dossier")
        st.info("Assurez-vous que le fichier est dans le même répertoire que streamlit.py")

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <p>Projet Data Management 2025 | Données : Open Data Paris | Outil : Streamlit + Python</p>
    </div>
    """,
    unsafe_allow_html=True
)