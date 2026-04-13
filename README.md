# Analiza Pieței Imobiliare - Proiect Academic Python & SAS

Acest proiect reprezintă o analiză a pieței imobiliare, realizată ca cerință academică pentru evaluarea cunoștințelor de analiză a datelor și programare statistică. Proiectul este împărțit în două componente majore: o aplicație web interactivă dezvoltată în Python (Streamlit) și un script de prelucrare statistică în SAS.

## 📁 Structura Proiectului

- `app.py` - Codul sursă pentru aplicația web Streamlit (Python).
- `analiza.sas` - Scriptul pentru curățarea, formatarea și analiza datelor în SAS.
- `imobiliare.csv` - Setul de date brut conținând informații despre proprietăți (preț, suprafață, nr. camere, locație etc.).
- `Documentatie_Proiect.pdf` - Documentația oficială a proiectului, incluzând definirea problemelor, metodele de calcul și interpretarea economică a rezultatelor.

## 🐍 Componenta Python (Aplicația Streamlit)

Aplicația vizualizează și modelează prețurile imobiliare, integrând următoarele facilități:
1. Afișare interactivă folosind `streamlit`.
2. Reprezentări cartografice de bază (`geopandas` / `st.map`).
3. Curățarea datelor (tratarea valorilor lipsă și a extremelor).
4. Codificarea variabilelor categorice (One-Hot Encoding).
5. Scalarea datelor numerice (`StandardScaler`).
6. Agregarea datelor pe cartiere folosind `pandas`.
7. Segmentarea proprietăților folosind clusterizare K-Means (`scikit-learn`).
8. Predicția prețurilor printr-un model de Regresie Multiplă (`statsmodels`).
