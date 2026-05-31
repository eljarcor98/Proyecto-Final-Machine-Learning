# %% [markdown]
# # Análisis Exploratorio (EDA) - Inteligencia Multifuente
# Este notebook conecta a PostgreSQL, carga los resultados de NLP y visualiza tendencias en el tiempo, tópicos y lugares.

# %%
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.db import engine

# %% [markdown]
# ## 1. Cargar Datos desde PostgreSQL

# %%
query = """
SELECT a.id, a.source, a.title, a.published_at, 
       n.locations, n.organizations, n.topic
FROM news_articles a
JOIN news_analysis n ON a.id = n.article_id
"""
df = pd.read_sql(query, engine)
df['published_at'] = pd.to_datetime(df['published_at'])
print(f"Total de noticias procesadas: {len(df)}")
df.head()

# %% [markdown]
# ## 2. Análisis Temporal (Trazabilidad)

# %%
# Agrupar por fecha (día)
df['date'] = df['published_at'].dt.date
daily_counts = df.groupby('date').size().reset_index(name='count')

plt.figure(figsize=(12, 6))
sns.lineplot(data=daily_counts, x='date', y='count', marker='o')
plt.title("Volumen de Noticias por Día")
plt.xlabel("Fecha")
plt.ylabel("Cantidad de Artículos")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('timeline.png')
plt.show()

# %% [markdown]
# ## 3. Distribución de Tópicos

# %%
plt.figure(figsize=(10, 6))
sns.countplot(data=df, y='topic', order=df['topic'].value_counts().index, palette='viridis')
plt.title("Distribución de Tópicos en las Noticias")
plt.xlabel("Cantidad")
plt.ylabel("Tópico")
plt.tight_layout()
plt.savefig('topics.png')
plt.show()

# %% [markdown]
# ## 4. Lugares Más Mencionados

# %%
# Parsear el JSON de locations
all_locations = []
for loc_str in df['locations'].dropna():
    locs = json.loads(loc_str)
    all_locations.extend(locs)

loc_counts = Counter(all_locations).most_common(20)
loc_df = pd.DataFrame(loc_counts, columns=['Location', 'Count'])

plt.figure(figsize=(12, 8))
sns.barplot(data=loc_df, x='Count', y='Location', palette='magma')
plt.title("Top 20 Lugares (GPE) Más Mencionados")
plt.xlabel("Menciones")
plt.ylabel("Lugar")
plt.tight_layout()
plt.savefig('locations.png')
plt.show()

# %% [markdown]
# ## 5. Trazabilidad: Tópicos en el Tiempo

# %%
topic_time = df.groupby(['date', 'topic']).size().reset_index(name='count')

plt.figure(figsize=(14, 7))
sns.lineplot(data=topic_time, x='date', y='count', hue='topic', marker='o')
plt.title("Tópicos a lo Largo del Tiempo")
plt.xlabel("Fecha")
plt.ylabel("Cantidad")
plt.xticks(rotation=45)
plt.legend(title='Tópico')
plt.tight_layout()
plt.savefig('topics_timeline.png')
plt.show()

print("¡Análisis completado! Gráficos generados.")
