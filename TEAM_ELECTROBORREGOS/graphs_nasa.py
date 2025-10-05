import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from collections import Counter
import re
import os
import sys

# --- CONFIGURACIÓN GENERAL Y DE ESTILO ---
# El directorio de salida es AHORA SIMPLEMENTE "graficos" (local)
OUTPUT_DIR_NAME = "graficos"
PALETTE = "viridis" 

BEAUTIFUL_NAMES = {
    'plant_biology': 'Biología Vegetal', 'radiation_biology': 'Biología de la Radiación',
    'cell_and_developmental_biology': 'Biología Celular y del Desarrollo', 'cardiovascular_system': 'Sistema Cardiovascular',
    'comparative_biology_and_model_organisms': 'Biología Comparativa y Organismos Modelo', 'genomics_and_multi_omics': 'Genómica y Multi-ómica',
    'immunology': 'Inmunología', 'microbiology_and_microbiome': 'Microbiología y Microbioma',
    'microgravity_and_environment': 'Microgravedad y Ambiente', 'musculoskeletal_system': 'Sistema Musculoesquelético',
    'other': 'Otra', 'unknown': 'Desconocida', 'bone_health': 'Salud Ósea', 'muscle_health': 'Salud Muscular',
    'neuroscience': 'Neurociencia', 'immune_system': 'Sistema Inmune', 'microgravity_effects': 'Efectos de la Microgravedad',
    'genomics_proteomics': 'Genómica y Proteómica', 'microbiome': 'Microbioma', 'cell_biology': 'Biología Celular',
    'human_factors': 'Factores Humanos', 'method_development': 'Desarrollo de Métodos'
}


# --- FUNCIÓN PRINCIPAL DE CARGA Y LIMPIEZA DE DATOS ---
def load_and_clean_data(filename="nasa_articles.csv"):
    """Carga el CSV asumiendo que está en el mismo directorio que el script."""
    
    # 1. Determina la ruta del directorio del script actual (necesario para el CSV)
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    filepath = os.path.join(script_dir, filename)

    try:
        df = pd.read_csv(filepath)
        print("✅ Archivo CSV cargado exitosamente desde:", filepath)
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo '{filename}' en la ruta: {filepath}")
        return None
        
    # 2. Limpieza de datos (tu código original)
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df.dropna(subset=['year'], inplace=True)
    df['year'] = df['year'].astype(int)
    df = df[df['research_area'].notna() & ~df['research_area'].isin(['Error', 'unclassified'])].copy()
    df['research_area'] = df['research_area'].map(BEAUTIFUL_NAMES).fillna(df['research_area'])
    
    return df

# --- FUNCIONES PARA GENERAR CADA GRÁFICO (Se mantuvieron sin cambios mayores) ---

def plot_research_area_distribution(df, output_dir):
    print("📊 Generando Gráfico 1: Distribución de Áreas...")
    plt.figure(figsize=(12, 8))
    area_counts = df['research_area'].value_counts()
    sns.barplot(x=area_counts.index, y=area_counts.values, palette=PALETTE)
    plt.title('Distribución de Artículos por Área de Investigación', fontsize=16, weight='bold')
    plt.xlabel('Área de Investigación', fontsize=12); plt.ylabel('Número de Artículos', fontsize=12)
    plt.xticks(rotation=45, ha='right'); plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "1_distribucion_areas.png"), dpi=300); plt.close()

def plot_publications_over_time(df, output_dir):
    print("📈 Generando Gráfico 2: Publicaciones en el Tiempo...")
    plt.figure(figsize=(12, 6))
    year_counts = df['year'].value_counts().sort_index()
    year_counts = year_counts[year_counts.index > 1990]
    sns.lineplot(x=year_counts.index, y=year_counts.values, marker='o', color=sns.color_palette(PALETTE, 1)[0])
    plt.title('Volumen de Publicaciones por Año', fontsize=16, weight='bold')
    plt.xlabel('Año de Publicación', fontsize=12); plt.ylabel('Número de Artículos', fontsize=12)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5); plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "2_publicaciones_por_año.png"), dpi=300); plt.close()

def plot_top_keywords(df, output_dir, top_n=25):
    print("☁️ Generando Gráfico 3: Palabras Clave Frecuentes...")
    keywords = df['keywords'].dropna().str.lower()
    stop_words = ['keywords', 'key words', 'no encontradas', 'introduction', 'results', 'conclusions', 'methods']
    all_words = [word.strip() for text in keywords for word in re.split(r'[;,]', text) if word.strip() and word.strip() not in stop_words and len(word.strip()) > 2]
    word_counts = Counter(all_words)
    if not word_counts: return

    wc = WordCloud(width=1200, height=600, background_color='white', colormap=PALETTE).generate_from_frequencies(word_counts)
    plt.figure(figsize=(15, 7)); plt.imshow(wc, interpolation='bilinear'); plt.axis('off'); plt.title('Nube de Palabras Clave', fontsize=16, weight='bold'); plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "3a_nube_keywords.png"), dpi=300); plt.close()

    df_keywords = pd.DataFrame(word_counts.most_common(top_n), columns=['Keyword', 'Frecuencia'])
    plt.figure(figsize=(12, 10)); sns.barplot(x='Frecuencia', y='Keyword', data=df_keywords, palette=PALETTE + "_r")
    plt.title(f'Top {top_n} Palabras Clave', fontsize=16, weight='bold'); plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "3b_barras_keywords.png"), dpi=300); plt.close()

def plot_area_evolution(df, output_dir, top_n=7):
    print("⏳ Generando Gráfico 4: Evolución de Áreas...")
    top_areas = df['research_area'].value_counts().nlargest(top_n).index
    df_filtered = df[df['research_area'].isin(top_areas)]
    evolution_data = df_filtered.groupby(['year', 'research_area']).size().unstack(fill_value=0)
    if evolution_data.empty: return

    evolution_data.plot(kind='area', stacked=True, figsize=(15, 8), colormap=PALETTE)
    plt.title(f'Evolución de las Top {top_n} Áreas de Investigación', fontsize=16, weight='bold')
    plt.xlabel('Año'); plt.ylabel('Número de Artículos')
    plt.legend(title='Área de Investigación', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout(rect=[0, 0, 0.85, 1]); plt.savefig(os.path.join(output_dir, "4_evolucion_areas.png"), dpi=300); plt.close('all')

def plot_top_authors(df, output_dir, top_n=20):
    print("👩‍🔬 Generando Gráfico 5: Autores Más Prolíficos...")
    authors = df['authors'].dropna().str.strip().str.lower(); authors = authors[authors != 'no encontrados']
    all_authors = [name.strip().title() for author_list in authors for name in author_list.split(',')]
    if not all_authors: return

    author_counts = Counter(all_authors)
    df_authors = pd.DataFrame(author_counts.most_common(top_n), columns=['Autor', 'Publicaciones'])
    plt.figure(figsize=(12, 10)); sns.barplot(x='Publicaciones', y='Autor', data=df_authors, palette=PALETTE + "_r")
    plt.title(f'Top {top_n} Autores con Más Publicaciones', fontsize=16, weight='bold'); plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "5_top_autores.png"), dpi=300); plt.close()

def plot_author_specialization_bubble_chart(df, output_dir, top_n_authors=15):
    """Genera un gráfico de burbujas que muestra la especialización por autor y tema."""
    print("🔵 Generando Gráfico 6: Especialización de Autores (Burbujas)...")
    
    author_topic_counts = []
    for _, row in df.iterrows():
        authors = [a.strip().title() for a in str(row['authors']).split(',') if a.strip()]
        for author in authors:
            author_topic_counts.append({'Author': author, 'Topic': row['research_area']})
            
    df_author_topic = pd.DataFrame(author_topic_counts)
    publications_by_author_topic = df_author_topic.groupby(['Author', 'Topic']).size().reset_index(name='Publications')
    
    top_authors = df_author_topic['Author'].value_counts().nlargest(top_n_authors).index
    publications_by_author_topic = publications_by_author_topic[publications_by_author_topic['Author'].isin(top_authors)]

    if publications_by_author_topic.empty:
        print("Advertencia: No hay suficientes datos para el Gráfico de Burbujas.")
        return

    plt.figure(figsize=(16, 10))
    sns.scatterplot(
        data=publications_by_author_topic,
        x='Author', y='Topic', size='Publications', 
        sizes=(100, 2000), 
        hue='Topic', 
        palette=PALETTE, 
        edgecolor='gray',
        alpha=0.8
    )
    plt.title(f'Especialización de los Top {top_n_authors} Autores (Burbujas)', fontsize=18, weight='bold')
    plt.xlabel('Autor', fontsize=12); plt.ylabel('Área de Investigación', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Área de Investigación', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout(rect=[0, 0, 0.85, 1]); plt.savefig(os.path.join(output_dir, "6_especializacion_autores_burbujas.png"), dpi=300); plt.close()


# --- EJECUCIÓN DEL SCRIPT ---
if __name__ == "__main__":
    
    # 1. Define la ruta de salida (simplemente la carpeta local)
    OUTPUT_DIR_PATH = "graficos" 

    if not os.path.exists(OUTPUT_DIR_PATH):
        try:
            os.makedirs(OUTPUT_DIR_PATH)
            print(f"📁 Directorio '{OUTPUT_DIR_PATH}' creado.")
        except Exception as e:
            print(f"❌ ERROR CRÍTICO al crear directorio. Verifique permisos: {e}")
            sys.exit(1)

    # 2. Carga de datos
    main_df = load_and_clean_data()
    
    # 3. Generación de gráficos
    if main_df is not None:
        plot_research_area_distribution(main_df, OUTPUT_DIR_PATH)
        plot_publications_over_time(main_df, OUTPUT_DIR_PATH)
        plot_top_keywords(main_df, OUTPUT_DIR_PATH)
        plot_area_evolution(main_df, OUTPUT_DIR_PATH)
        plot_top_authors(main_df, OUTPUT_DIR_PATH)
        plot_author_specialization_bubble_chart(main_df, OUTPUT_DIR_PATH)

        print("\n🎉 ¡Todos los gráficos han sido generados y guardados correctamente en:", OUTPUT_DIR_PATH, "!")