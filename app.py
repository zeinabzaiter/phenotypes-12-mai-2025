# Générer une application Streamlit complète et autonome lisant directement depuis le fichier Excel brut

final_dashboard_code = """
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go

# --- Chargement des données Excel brutes ---
df = pd.read_excel("staph_aureus_pheno_final.xlsx")
df["week"] = pd.to_datetime(df["week"], errors="coerce")
df = df.dropna(subset=["week"])
df["Week"] = df["week"].dt.date

# --- Liste des phénotypes ---
phenotypes = ["MRSA", "Other", "VRSA", "Wild"]
df["Total"] = df[phenotypes].sum(axis=1)

# --- Calcul des pourcentages et des alertes ---
for pheno in phenotypes:
    df[f"% {pheno}"] = (df[pheno] / df["Total"]) * 100

st.title("📊 Dashboard - Phénotypes Staphylococcus aureus (depuis Excel)")

# Sélecteur de phénotype
selected_pheno = st.selectbox("🔬 Choisir un phénotype", phenotypes)

# Slider plage de semaines
min_date = df["Week"].min()
max_date = df["Week"].max()
week_range = st.slider("📅 Plage de semaines", min_value=min_date, max_value=max_date,
                       value=(min_date, max_date))

# Filtrer la plage sélectionnée
filtered_df = df[(df["Week"] >= week_range[0]) & (df["Week"] <= week_range[1])]

# Colonnes utiles
pct_col = f"% {selected_pheno}"
nb_col = selected_pheno

# Calcul des seuils Tukey pour cette période
values = filtered_df[pct_col].dropna()
q1 = np.percentile(values, 25)
q3 = np.percentile(values, 75)
iqr = q3 - q1
lower = max(q1 - 1.5 * iqr, 0)
upper = q3 + 1.5 * iqr

# Graphique des pourcentages
fig = go.Figure()
fig.add_trace(go.Scatter(x=filtered_df["Week"], y=filtered_df[pct_col],
                         mode='lines+markers', name=f"% {selected_pheno}"))

fig.add_trace(go.Scatter(x=filtered_df["Week"], y=[upper]*len(filtered_df),
                         mode='lines', name="Seuil haut Tukey",
                         line=dict(dash='dash', color='red')))
fig.add_trace(go.Scatter(x=filtered_df["Week"], y=[lower]*len(filtered_df),
                         mode='lines', name="Seuil bas Tukey",
                         line=dict(dash='dot', color='red')))

fig.update_layout(
    title=f"Évolution du % de {selected_pheno} avec seuils Tukey",
    xaxis_title="Semaine",
    yaxis_title="% de cas",
    yaxis=dict(range=[0, 100]),
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

# Graphique du nombre de cas
st.subheader(f"📈 Nombre hebdomadaire de cas : {selected_pheno}")
st.line_chart(filtered_df.set_index("Week")[nb_col])
"""

# Sauvegarder le code dans un fichier Python
final_dashboard_path = "/mnt/data/app_phenotypes_final.py"
with open(final_dashboard_path, "w") as f:
    f.write(final_dashboard_code)

final_dashboard_path
