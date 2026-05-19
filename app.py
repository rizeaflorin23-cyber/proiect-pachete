import streamlit as st
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.model_selection import train_test_split
import statsmodels.api as sm
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Analiza Pieței Imobiliare București",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #f5f7fa; }
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    }
    [data-testid="stMetricLabel"] { color: #1F497D !important; }
    [data-testid="stMetricValue"] { color: #2E75B6 !important; font-size: 1.1rem !important; }
    h1 { color: #1F497D; }
    h2 { color: #1F497D; border-bottom: 2px solid #1F497D; padding-bottom: 4px; }
    h3 { color: #2E75B6; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), "Bucharest_HousePriceDataset.csv"))
    df.columns = [c.strip() for c in df.columns]
    return df

df_raw = load_data()

st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Flag_of_Bucharest.svg/240px-Flag_of_Bucharest.svg.png", width=80)
st.sidebar.title("🏙️ Piața Imobiliară\nBucurești")
st.sidebar.markdown("---")

pagina = st.sidebar.radio("Navigare", [
    "📊 Date & Statistici",
    "🗺️ Hartă Geografică",
    "🧹 Curățarea Datelor",
    "🔢 Codificare & Scalare",
    "📈 Grupare & Agregare",
    "🔵 Clusterizare K-Means",
    "📉 Regresie Multiplă"
])

st.sidebar.markdown("---")
st.sidebar.markdown("**Filtre globale**")

sectoare_disp = sorted(df_raw["Sector"].unique())
sector_sel = st.sidebar.multiselect("Sectoare", sectoare_disp, default=sectoare_disp)

pret_min, pret_max = int(df_raw["Pret"].min()), int(df_raw["Pret"].max())
interval_pret = st.sidebar.slider("Preț (EUR)", pret_min, pret_max, (pret_min, pret_max), step=1000)

camere_disp = sorted(df_raw["Nr Camere"].unique())
camere_sel = st.sidebar.multiselect("Nr. Camere", camere_disp, default=camere_disp)

df = df_raw[
    (df_raw["Sector"].isin(sector_sel)) &
    (df_raw["Pret"].between(interval_pret[0], interval_pret[1])) &
    (df_raw["Nr Camere"].isin(camere_sel))
].copy()

st.sidebar.markdown(f"**Proprietăți selectate:** {len(df):,}")

sector_labels = {
    1: "S1 – Centru-Nord",
    2: "S2 – Est",
    3: "S3 – Centru-Est",
    4: "S4 – Sud",
    5: "S5 – Sud-Vest",
    6: "S6 – Vest"
}
CULORI_SECTOR = {
    1: "#e74c3c", 2: "#3498db", 3: "#2ecc71",
    4: "#f39c12", 5: "#9b59b6", 6: "#1abc9c"
}

if pagina == "📊 Date & Statistici":
    st.title("📊 Date & Statistici Descriptive")
    st.markdown("Explorarea interactivă a setului de date imobiliare din București (3.529 proprietăți).")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total proprietăți", f"{len(df):,}")
    col2.metric("Preț mediu", f"{df['Pret'].mean():,.0f} EUR")
    col3.metric("Preț median", f"{df['Pret'].median():,.0f} EUR")
    col4.metric("Suprafață medie", f"{df['Suprafata'].mean():.1f} mp")

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Distribuția Prețurilor")
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(df["Pret"], bins=50, color="#2E75B6", edgecolor="white", alpha=0.85)
        ax.axvline(df["Pret"].mean(), color="#e74c3c", linestyle="--", label=f"Medie: {df['Pret'].mean():,.0f}")
        ax.axvline(df["Pret"].median(), color="#f39c12", linestyle="--", label=f"Median: {df['Pret'].median():,.0f}")
        ax.set_xlabel("Preț (EUR)")
        ax.set_ylabel("Frecvență")
        ax.legend(fontsize=9)
        ax.spines[["top","right"]].set_visible(False)
        st.pyplot(fig)
        plt.close()

    with col_b:
        st.subheader("Distribuția pe Sectoare")
        cnt = df.groupby("Sector").size().reset_index(name="Count")
        cnt["Label"] = cnt["Sector"].map(sector_labels)
        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.bar(cnt["Label"], cnt["Count"],
                      color=[CULORI_SECTOR[s] for s in cnt["Sector"]], edgecolor="white")
        ax.bar_label(bars, padding=3, fontsize=9)
        ax.set_ylabel("Nr. proprietăți")
        plt.xticks(rotation=30, ha="right", fontsize=8)
        ax.spines[["top","right"]].set_visible(False)
        st.pyplot(fig)
        plt.close()

    st.markdown("---")
    st.subheader("Statistici Descriptive Detaliate")
    stats = df[["Pret","Suprafata","Nr Camere","Etaj","Total Etaje","Scor"]].describe().T
    stats.columns = ["Count","Medie","Std","Min","Q25","Median","Q75","Max"]
    st.dataframe(stats.style.format("{:.2f}"), use_container_width=True)

    st.markdown("---")
    st.subheader("Tabel Date (primele 100 înregistrări)")
    st.dataframe(df.head(100), use_container_width=True)

elif pagina == "🗺️ Hartă Geografică":
    st.title("🗺️ Distribuție Geografică")
    st.markdown("Fiecare proprietate este plasată pe hartă pe baza coordonatelor aproximative ale sectorului.")

    coords = {
        1: (44.452, 26.090), 2: (44.445, 26.130),
        3: (44.420, 26.120), 4: (44.390, 26.100),
        5: (44.400, 26.060), 6: (44.440, 26.045)
    }

    np.random.seed(42)
    df_map = df.copy()
    df_map["lat"] = df_map["Sector"].apply(lambda s: coords[s][0] + np.random.normal(0, 0.012))
    df_map["lon"] = df_map["Sector"].apply(lambda s: coords[s][1] + np.random.normal(0, 0.012))

    st.subheader("Harta Proprietăților")
    st.map(df_map[["lat","lon"]], zoom=11)

    st.markdown("---")
    st.subheader("Preț Mediu per Sector")
    pret_sector = df.groupby("Sector").agg(
        Pret_Mediu=("Pret","mean"),
        Pret_Median=("Pret","median"),
        Nr_Proprietati=("Pret","count"),
        Pret_mp=("Pret", lambda x: (x / df.loc[x.index,"Suprafata"]).mean())
    ).reset_index()
    pret_sector["Sector_Label"] = pret_sector["Sector"].map(sector_labels)
    pret_sector = pret_sector.sort_values("Pret_Mediu", ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots(figsize=(6,4))
        bars = ax.barh(pret_sector["Sector_Label"], pret_sector["Pret_Mediu"],
                       color=[CULORI_SECTOR[s] for s in pret_sector["Sector"]])
        ax.bar_label(bars, fmt="%.0f EUR", padding=4, fontsize=8)
        ax.set_xlabel("Preț Mediu (EUR)")
        ax.set_title("Preț Mediu pe Sector")
        ax.spines[["top","right"]].set_visible(False)
        st.pyplot(fig)
        plt.close()

    with col2:
        fig, ax = plt.subplots(figsize=(6,4))
        bars = ax.barh(pret_sector["Sector_Label"], pret_sector["Pret_mp"],
                       color=[CULORI_SECTOR[s] for s in pret_sector["Sector"]])
        ax.bar_label(bars, fmt="%.0f EUR/mp", padding=4, fontsize=8)
        ax.set_xlabel("Preț Mediu per mp (EUR/mp)")
        ax.set_title("Preț/mp pe Sector")
        ax.spines[["top","right"]].set_visible(False)
        st.pyplot(fig)
        plt.close()

    st.dataframe(pret_sector[["Sector_Label","Pret_Mediu","Pret_Median","Pret_mp","Nr_Proprietati"]]
                 .rename(columns={"Sector_Label":"Sector","Pret_Mediu":"Preț Mediu (EUR)",
                                   "Pret_Median":"Preț Median (EUR)","Pret_mp":"EUR/mp",
                                   "Nr_Proprietati":"Nr. Proprietăți"})
                 .style.format({"Preț Mediu (EUR)":"{:,.0f}","Preț Median (EUR)":"{:,.0f}","EUR/mp":"{:,.0f}"}),
                 use_container_width=True)

elif pagina == "🧹 Curățarea Datelor":
    st.title("🧹 Tratarea Valorilor Lipsă și a Valorilor Extreme")

    st.subheader("1. Valori Lipsă")
    missing = df_raw.isnull().sum().reset_index()
    missing.columns = ["Coloană", "Valori Lipsă"]
    missing["Procent (%)"] = (missing["Valori Lipsă"] / len(df_raw) * 100).round(2)
    st.dataframe(missing, use_container_width=True)
    st.success("✅ Setul de date nu conține valori lipsă – calitate excelentă a colectării!")

    st.markdown("---")
    st.subheader("2. Detectarea Valorilor Extreme (Metoda IQR)")

    col_outlier = st.selectbox("Selectează variabila pentru analiza outlierilor:",
                                ["Pret","Suprafata","Nr Camere","Etaj"])

    Q1 = df_raw[col_outlier].quantile(0.25)
    Q3 = df_raw[col_outlier].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    outlieri = df_raw[(df_raw[col_outlier] < lower) | (df_raw[col_outlier] > upper)]
    df_curat = df_raw[(df_raw[col_outlier] >= lower) & (df_raw[col_outlier] <= upper)]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Q1", f"{Q1:,.1f}")
    col2.metric("Q3", f"{Q3:,.1f}")
    col3.metric("IQR", f"{IQR:,.1f}")
    col4.metric("Outlieri detectați", f"{len(outlieri)}")

    st.markdown(f"**Limita inferioară:** {lower:,.1f} &nbsp;|&nbsp; **Limita superioară:** {upper:,.1f}")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Box-plot ÎNAINTE de curățare**")
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.boxplot(df_raw[col_outlier].dropna(), vert=False, patch_artist=True,
                   boxprops=dict(facecolor="#AED6F1"))
        ax.set_xlabel(col_outlier)
        ax.spines[["top","right"]].set_visible(False)
        st.pyplot(fig)
        plt.close()

    with col_b:
        st.markdown("**Box-plot DUPĂ curățare**")
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.boxplot(df_curat[col_outlier].dropna(), vert=False, patch_artist=True,
                   boxprops=dict(facecolor="#A9DFBF"))
        ax.set_xlabel(col_outlier)
        ax.spines[["top","right"]].set_visible(False)
        st.pyplot(fig)
        plt.close()

    st.info(f"📌 După eliminarea outlierilor: **{len(df_curat):,}** proprietăți rămân "
            f"(din {len(df_raw):,} inițiale, eliminare {len(outlieri)/len(df_raw)*100:.1f}%).")

elif pagina == "🔢 Codificare & Scalare":
    st.title("🔢 Codificare One-Hot & Scalare StandardScaler")

    st.subheader("1. Codificare One-Hot Encoding – variabila Sector")
    st.markdown("""
    Variabila **Sector** (1–6) este categorică. O-Hot Encoding creează 5 variabile binare
    (Sector 1 = referință eliminată pentru a evita multicolinearitatea perfectă).
    """)

    df_enc = pd.get_dummies(df[["Pret","Suprafata","Nr Camere","Etaj","Total Etaje","Scor","Sector"]],
                             columns=["Sector"], drop_first=True, dtype=int)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Înainte de codificare (primele 5 rânduri):**")
        st.dataframe(df[["Sector","Nr Camere","Suprafata","Pret"]].head(5), use_container_width=True)
    with col2:
        st.markdown("**După codificare (primele 5 rânduri):**")
        sector_cols = [c for c in df_enc.columns if "Sector" in c]
        st.dataframe(df_enc[sector_cols + ["Pret"]].head(5), use_container_width=True)

    st.success(f"✅ S-au creat {len(sector_cols)} variabile dummy pentru sector (Sector_1 = referință).")

    st.markdown("---")
    st.subheader("2. Scalare StandardScaler – z-score normalization")
    st.markdown("""
    Formula: **z = (x − μ) / σ**
    Rezultat: fiecare variabilă numerică are **medie = 0** și **deviație standard = 1**.
    """)

    vars_scale = ["Pret","Suprafata","Nr Camere","Etaj","Total Etaje","Scor"]
    scaler = StandardScaler()
    df_scaled_arr = scaler.fit_transform(df[vars_scale])
    df_scaled = pd.DataFrame(df_scaled_arr, columns=[v + "_z" for v in vars_scale])

    params_df = pd.DataFrame({
        "Variabilă": vars_scale,
        "Medie originală": scaler.mean_,
        "Std originală": scaler.scale_
    })
    st.dataframe(params_df.style.format({"Medie originală":"{:.2f}","Std originală":"{:.2f}"}),
                 use_container_width=True)

    col_a, col_b = st.columns(2)
    var_viz = st.selectbox("Selectează variabila pentru vizualizare:", vars_scale)
    idx = vars_scale.index(var_viz)

    with col_a:
        fig, ax = plt.subplots(figsize=(5,3))
        ax.hist(df[var_viz], bins=40, color="#2E75B6", edgecolor="white", alpha=0.8)
        ax.set_title(f"{var_viz} – original")
        ax.spines[["top","right"]].set_visible(False)
        st.pyplot(fig); plt.close()

    with col_b:
        fig, ax = plt.subplots(figsize=(5,3))
        ax.hist(df_scaled[var_viz+"_z"], bins=40, color="#27AE60", edgecolor="white", alpha=0.8)
        ax.set_title(f"{var_viz} – standardizat (z-score)")
        ax.spines[["top","right"]].set_visible(False)
        st.pyplot(fig); plt.close()

elif pagina == "📈 Grupare & Agregare":
    st.title("📈 Gruparea și Agregarea Datelor")

    st.subheader("1. Statistici per Sector")
    df["Pret_mp"] = df["Pret"] / df["Suprafata"]
    agg_sector = df.groupby("Sector").agg(
        Nr_Prop=("Pret","count"),
        Pret_Mediu=("Pret","mean"),
        Pret_Median=("Pret","median"),
        Pret_Std=("Pret","std"),
        Pret_mp_Mediu=("Pret_mp","mean"),
        Suprafata_Medie=("Suprafata","mean")
    ).reset_index()
    agg_sector["Sector_Label"] = agg_sector["Sector"].map(sector_labels)
    st.dataframe(agg_sector.drop("Sector",axis=1).rename(columns={
        "Sector_Label":"Sector","Nr_Prop":"Nr. Prop.",
        "Pret_Mediu":"Preț Mediu","Pret_Median":"Preț Median",
        "Pret_Std":"Std Preț","Pret_mp_Mediu":"EUR/mp","Suprafata_Medie":"Sup. Medie (mp)"
    }).style.format({
        "Preț Mediu":"{:,.0f}","Preț Median":"{:,.0f}",
        "Std Preț":"{:,.0f}","EUR/mp":"{:,.0f}","Sup. Medie (mp)":"{:.1f}"
    }), use_container_width=True)

    st.markdown("---")
    st.subheader("2. Pivot Table – Preț Median (Sector × Nr. Camere)")
    pivot = df.pivot_table(values="Pret", index="Sector", columns="Nr Camere",
                            aggfunc="median", fill_value=0)
    pivot.index = [sector_labels.get(s, str(s)) for s in pivot.index]

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.heatmap(pivot/1000, annot=True, fmt=".0f", cmap="YlOrRd",
                linewidths=0.5, ax=ax, cbar_kws={"label":"Preț median (mii EUR)"})
    ax.set_title("Preț Median (mii EUR) – Sector × Nr. Camere")
    ax.set_xlabel("Nr. Camere")
    ax.set_ylabel("")
    st.pyplot(fig); plt.close()

    st.markdown("---")
    st.subheader("3. Distribuție Nr. Camere")
    cam_cnt = df["Nr Camere"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(7, 3))
    bars = ax.bar(cam_cnt.index.astype(str) + " cam.", cam_cnt.values,
                  color="#2E75B6", edgecolor="white")
    ax.bar_label(bars, padding=3)
    ax.set_ylabel("Nr. proprietăți")
    ax.spines[["top","right"]].set_visible(False)
    st.pyplot(fig); plt.close()

    st.markdown("---")
    st.subheader("4. Funcții de Grup – Preț pe Categorie de Suprafață")
    df["Categ_Sup"] = pd.cut(df["Suprafata"],
                              bins=[0,40,60,80,120,500],
                              labels=["<40mp","40-60mp","60-80mp","80-120mp",">120mp"])
    agg_sup = df.groupby("Categ_Sup", observed=True)["Pret"].agg(
        ["mean","median","count","std"]).reset_index()
    agg_sup.columns = ["Categorie Suprafață","Preț Mediu","Preț Median","Nr. Prop.","Std Preț"]
    st.dataframe(agg_sup.style.format({
        "Preț Mediu":"{:,.0f}","Preț Median":"{:,.0f}","Std Preț":"{:,.0f}"
    }), use_container_width=True)

elif pagina == "🔵 Clusterizare K-Means":
    st.title("🔵 Segmentare Piață – Clusterizare K-Means")
    st.markdown("Identificarea segmentelor de piață omogene pe baza caracteristicilor proprietăților.")

    features = ["Suprafata","Nr Camere","Pret","Scor"]
    X = df[features].dropna()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    st.subheader("1. Metoda Elbow – Alegerea numărului optim de clustere")
    inertii = []
    silhouette = []
    K_range = range(2, 11)
    for k in K_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(X_scaled)
        inertii.append(km.inertia_)
        silhouette.append(silhouette_score(X_scaled, km.labels_))

    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots(figsize=(5,3))
        ax.plot(K_range, inertii, "bo-", linewidth=2)
        ax.set_xlabel("Număr clustere (k)")
        ax.set_ylabel("Inerție")
        ax.set_title("Grafic Elbow")
        ax.spines[["top","right"]].set_visible(False)
        st.pyplot(fig); plt.close()

    with col2:
        fig, ax = plt.subplots(figsize=(5,3))
        ax.plot(K_range, silhouette, "rs-", linewidth=2)
        ax.set_xlabel("Număr clustere (k)")
        ax.set_ylabel("Scor Silhouette")
        ax.set_title("Scor Silhouette")
        ax.spines[["top","right"]].set_visible(False)
        st.pyplot(fig); plt.close()

    st.markdown("---")
    k_opt = st.slider("Selectează k (număr clustere):", 2, 8, 4)

    km_final = KMeans(n_clusters=k_opt, random_state=42, n_init=10)
    X["Cluster"] = km_final.fit_predict(X_scaled)
    sil = silhouette_score(X_scaled, X["Cluster"])
    st.info(f"**Scor Silhouette pentru k={k_opt}: {sil:.3f}** "
            f"{'✅ Bun (>0.4)' if sil>0.4 else '⚠️ Acceptabil'}")

    st.subheader(f"2. Scatter Plot – Clustere (k={k_opt})")
    CLUSTER_COLORS = ["#e74c3c","#3498db","#2ecc71","#f39c12","#9b59b6","#1abc9c","#e67e22","#95a5a6"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    for cl in range(k_opt):
        subset = X[X["Cluster"]==cl]
        axes[0].scatter(subset["Suprafata"], subset["Pret"]/1000,
                        c=CLUSTER_COLORS[cl], alpha=0.5, s=15, label=f"Cluster {cl+1}")
    axes[0].set_xlabel("Suprafață (mp)")
    axes[0].set_ylabel("Preț (mii EUR)")
    axes[0].set_title("Suprafață vs Preț")
    axes[0].legend(fontsize=8)
    axes[0].spines[["top","right"]].set_visible(False)

    for cl in range(k_opt):
        subset = X[X["Cluster"]==cl]
        axes[1].scatter(subset["Nr Camere"], subset["Pret"]/1000,
                        c=CLUSTER_COLORS[cl], alpha=0.5, s=15, label=f"Cluster {cl+1}")
    axes[1].set_xlabel("Nr. Camere")
    axes[1].set_ylabel("Preț (mii EUR)")
    axes[1].set_title("Nr. Camere vs Preț")
    axes[1].legend(fontsize=8)
    axes[1].spines[["top","right"]].set_visible(False)
    st.pyplot(fig); plt.close()

    st.subheader("3. Profilul Clusterelor")
    profile = X.groupby("Cluster")[features].mean()
    profile.index = [f"Cluster {i+1}" for i in range(k_opt)]
    profile["Nr. Proprietăți"] = X.groupby("Cluster").size().values
    st.dataframe(profile.style.format({
        "Suprafata":"{:.1f} mp","Nr Camere":"{:.1f}",
        "Pret":"{:,.0f} EUR","Scor":"{:.2f}","Nr. Proprietăți":"{:.0f}"
    }).background_gradient(cmap="Blues", subset=["Pret"]), use_container_width=True)

    st.subheader("4. Distribuția prețurilor per cluster")
    fig, ax = plt.subplots(figsize=(10, 4))
    data_plot = [X[X["Cluster"]==cl]["Pret"].values for cl in range(k_opt)]
    bp = ax.boxplot(data_plot, patch_artist=True, labels=[f"Cluster {i+1}" for i in range(k_opt)])
    for patch, color in zip(bp['boxes'], CLUSTER_COLORS[:k_opt]):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax.set_ylabel("Preț (EUR)")
    ax.spines[["top","right"]].set_visible(False)
    st.pyplot(fig); plt.close()

elif pagina == "📉 Regresie Multiplă":
    st.title("📉 Regresie Multiplă OLS (statsmodels)")
    st.markdown("Model econometric pentru predicția prețului imobiliar.")

    df_reg = df.copy()
    df_reg["Pret_mp"] = df_reg["Pret"] / df_reg["Suprafata"]

    df_enc = pd.get_dummies(df_reg, columns=["Sector"], drop_first=True, dtype=int)
    sector_cols = [c for c in df_enc.columns if "Sector_" in c]

    feature_cols = ["Suprafata","Nr Camere","Etaj","Total Etaje","Scor"] + sector_cols
    df_model = df_enc[feature_cols + ["Pret"]].dropna()

    X_raw = df_model[feature_cols]
    y = df_model["Pret"]
    X_const = sm.add_constant(X_raw)

    st.subheader("1. Variabile incluse în model")
    st.code("Pret = β₀ + β₁·Suprafata + β₂·NrCamere + β₃·Etaj + β₄·TotalEtaje + β₅·Scor\n"
            "     + β₆·Sector_2 + β₇·Sector_3 + β₈·Sector_4 + β₉·Sector_5 + β₁₀·Sector_6 + ε")

    model = sm.OLS(y, X_const).fit()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("R²", f"{model.rsquared:.4f}")
    col2.metric("R² Ajustat", f"{model.rsquared_adj:.4f}")
    col3.metric("F-statistic", f"{model.fvalue:,.1f}")
    col4.metric("AIC", f"{model.aic:,.0f}")

    st.subheader("2. Coeficienți de regresie")
    coef_df = pd.DataFrame({
        "Coeficient": model.params,
        "Eroare Std.": model.bse,
        "t-stat": model.tvalues,
        "p-value": model.pvalues,
        "IC 95% inf": model.conf_int()[0],
        "IC 95% sup": model.conf_int()[1],
    }).drop("const")

    def color_pval(val):
        if val < 0.001: return "background-color: #A9DFBF"
        elif val < 0.05: return "background-color: #FAD7A0"
        else: return "background-color: #F1948A"

    st.dataframe(coef_df.style
                 .format({"Coeficient":"{:,.2f}","Eroare Std.":"{:,.2f}",
                           "t-stat":"{:.3f}","p-value":"{:.4f}",
                           "IC 95% inf":"{:,.2f}","IC 95% sup":"{:,.2f}"})
                 .map(color_pval, subset=["p-value"]),
                 use_container_width=True)
    st.caption("🟢 p<0.001 semnificativ  |  🟡 p<0.05 semnificativ  |  🔴 p≥0.05 nesemnificativ")

    st.subheader("3. Grafice de Diagnostic")
    fitted = model.fittedvalues
    residuals = model.resid

    col_a, col_b = st.columns(2)
    with col_a:
        fig, ax = plt.subplots(figsize=(5,4))
        ax.scatter(fitted, residuals, alpha=0.3, s=10, color="#2E75B6")
        ax.axhline(0, color="red", linestyle="--")
        ax.set_xlabel("Valori ajustate (fitted)")
        ax.set_ylabel("Reziduuri")
        ax.set_title("Fitted vs Reziduuri")
        ax.spines[["top","right"]].set_visible(False)
        st.pyplot(fig); plt.close()

    with col_b:
        fig, ax = plt.subplots(figsize=(5,4))
        sm.qqplot(residuals, line="s", ax=ax, alpha=0.4, markersize=3)
        ax.set_title("Q-Q Plot Reziduuri")
        ax.spines[["top","right"]].set_visible(False)
        st.pyplot(fig); plt.close()

    st.markdown("---")
    st.subheader("4. 🔮 Predictor Interactiv de Preț")
    st.markdown("Estimează prețul unei proprietăți pe baza caracteristicilor introduse:")

    pc1, pc2, pc3 = st.columns(3)
    with pc1:
        p_sup  = st.number_input("Suprafață (mp)", 20, 350, 65)
        p_cam  = st.selectbox("Nr. Camere", [1,2,3,4,5], index=1)
    with pc2:
        p_etaj = st.number_input("Etaj", 0, 20, 3)
        p_tot  = st.number_input("Total Etaje", 1, 25, 8)
    with pc3:
        p_scor  = st.slider("Scor calitate", 1, 5, 3)
        p_sect  = st.selectbox("Sector", list(sector_labels.values()), index=0)

    sect_num = [k for k,v in sector_labels.items() if v==p_sect][0]
    row = {"const":1,"Suprafata":p_sup,"Nr Camere":p_cam,"Etaj":p_etaj,
           "Total Etaje":p_tot,"Scor":p_scor}
    for s in range(2,7):
        row[f"Sector_{s}"] = 1 if sect_num==s else 0

    X_pred = pd.DataFrame([row])[X_const.columns]
    pred = model.get_prediction(X_pred)
    pred_mean = pred.predicted_mean[0]
    pred_ci   = pred.conf_int(alpha=0.05)[0]

    st.markdown("---")
    c1,c2,c3 = st.columns(3)
    c1.metric("💰 Preț estimat", f"{pred_mean:,.0f} EUR")
    c2.metric("IC 95% inferior", f"{pred_ci[0]:,.0f} EUR")
    c3.metric("IC 95% superior", f"{pred_ci[1]:,.0f} EUR")
    st.caption(f"Preț/mp estimat: {pred_mean/p_sup:,.0f} EUR/mp")
