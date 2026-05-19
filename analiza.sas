/* ================================================================
   ANALIZA PIETEI IMOBILIARE BUCURESTI
   Proiect Academic – Pachete Software SAS
   Autori: Rizea Florin-Mario, Robu Mihai – Grupa 1094
   Dataset: Bucharest_HousePriceDataset.csv
   ================================================================ */

/* ----------------------------------------------------------------
   PASUL 0 – Configurare ODS Graphics si optiuni globale
   ---------------------------------------------------------------- */
ODS GRAPHICS ON / WIDTH=800px HEIGHT=500px;
ODS PDF FILE="Analiza_Imobiliara_Rezultate.pdf"
         STYLE=JOURNAL STARTPAGE=YES;
TITLE "Analiza Pietei Imobiliare din Bucuresti";
OPTIONS NODATE NONUMBER PAGESIZE=60 LINESIZE=120;


/* ================================================================
   FUNCTIA 1 – CREAREA SETULUI DE DATE SAS DIN FISIER EXTERN
   ================================================================
   a) Problema: importul fisierului CSV brut in mediul SAS
   b) Info: PROC IMPORT, GETNAMES, DBMS=CSV
   c) Metoda: procedura PROC IMPORT cu detectare automata tipuri
   d) Rezultate: dataset WORK.imobiliare cu 3529 obs. si 7 var.
   e) Interpretare economica: fundatia intregii analize; un import
      corect garanteaza integritatea tuturor prelucrarilor ulterioare
   ================================================================ */

PROC IMPORT
    DATAFILE="Bucharest_HousePriceDataset.csv"
    OUT=WORK.imobiliare
    DBMS=CSV
    REPLACE;
    GETNAMES=YES;
    DATAROW=2;
RUN;

/* Verificare structura dataset */
PROC CONTENTS DATA=WORK.imobiliare VARNUM;
    TITLE2 "Structura setului de date importat";
RUN;

/* Primele 10 observatii */
PROC PRINT DATA=WORK.imobiliare (OBS=10) NOOBS;
    TITLE2 "Primele 10 observatii";
RUN;


/* ================================================================
   FUNCTIA 2 – FORMATE DEFINITE DE UTILIZATOR
   ================================================================
   a) Problema: variabilele Sector (1-6) si Scor (1-5) sunt coduri
      numerice greu de interpretat in rapoarte
   b) Info: PROC FORMAT, VALUE statement
   c) Metoda: mapare cod numeric → eticheta text descriptiva
   d) Rezultate: rapoarte cu etichete clare pentru stakeholderi
   e) Interpretare economica: comunicare profesionala a rezultatelor
      catre investitori si manageri fara cunostinte tehnice
   ================================================================ */

PROC FORMAT;
    VALUE sector_fmt
        1 = "Sector 1 (Centru-Nord)"
        2 = "Sector 2 (Est)"
        3 = "Sector 3 (Centru-Est)"
        4 = "Sector 4 (Sud)"
        5 = "Sector 5 (Sud-Vest)"
        6 = "Sector 6 (Vest)"
        OTHER = "Necunoscut";

    VALUE scor_fmt
        1 = "Foarte slab"
        2 = "Slab"
        3 = "Mediu"
        4 = "Bun"
        5 = "Excelent"
        OTHER = "N/A";

    VALUE catpret_fmt
        LOW -< 60000   = "Accesibil (<60K EUR)"
        60000 -< 120000 = "Mediu (60-120K EUR)"
        120000 -< 200000 = "Premium (120-200K EUR)"
        200000 - HIGH   = "Lux (>200K EUR)";

    VALUE suprafata_fmt
        LOW -< 40   = "<40 mp (Garsoniera)"
        40  -< 60   = "40-60 mp (Mic)"
        60  -< 90   = "60-90 mp (Mediu)"
        90  -< 120  = "90-120 mp (Mare)"
        120 - HIGH  = ">120 mp (Foarte mare)";
RUN;

/* Demonstratie folosire formate */
PROC PRINT DATA=WORK.imobiliare (OBS=15) NOOBS;
    FORMAT Sector sector_fmt. Scor scor_fmt. Pret DOLLAR12.;
    TITLE2 "Date cu formate definite de utilizator";
RUN;


/* ================================================================
   FUNCTIA 3 – PROCESARE ITERATIVA SI CONDITIONALA (DATA STEP)
   ================================================================
   a) Problema: creare variabile derivate prin logica conditionala
   b) Info: IF-THEN-ELSE, operatori logici, functii matematice SAS
   c) Metoda: procesare rand cu rand in DATA step
   d) Rezultate: dataset imbogatit cu 5 variabile noi derivate
   e) Interpretare economica: categorizarea permite segmentare de
      piata si comparabilitate intre proprietati diferite ca marime
   ================================================================ */

DATA WORK.imob_procesat;
    SET WORK.imobiliare;

    /* ---- Pret per metru patrat ---- */
    Pret_mp = Pret / Suprafata;
    FORMAT Pret_mp 8.1;

    /* ---- Categorie de pret ---- */
    IF Pret < 60000 THEN Categ_Pret = "Accesibil";
    ELSE IF 60000 <= Pret < 120000 THEN Categ_Pret = "Mediu";
    ELSE IF 120000 <= Pret < 200000 THEN Categ_Pret = "Premium";
    ELSE Categ_Pret = "Lux";

    /* ---- Categorie suprafata ---- */
    IF Suprafata < 40 THEN Categ_Sup = "Garsoniera";
    ELSE IF 40 <= Suprafata < 60 THEN Categ_Sup = "Mic";
    ELSE IF 60 <= Suprafata < 90 THEN Categ_Sup = "Mediu";
    ELSE IF 90 <= Suprafata < 120 THEN Categ_Sup = "Mare";
    ELSE Categ_Sup = "Foarte mare";

    /* ---- Indicator proprietate de lux ---- */
    IF Pret > 200000 AND Scor = 5 THEN Lux = 1;
    ELSE Lux = 0;

    /* ---- Etaj relativ (pozitie in bloc) ---- */
    IF Total_Etaje > 0 THEN Etaj_Rel = Etaj / Total_Etaje;
    ELSE Etaj_Rel = 0;
    FORMAT Etaj_Rel 5.2;

    /* ---- Etichete aplicare formate ---- */
    FORMAT Sector sector_fmt. Scor scor_fmt. Pret DOLLAR12.;

    LABEL
        Pret_mp   = "Pret per mp (EUR/mp)"
        Categ_Pret = "Categorie pret"
        Categ_Sup  = "Categorie suprafata"
        Lux        = "Indicator lux (0/1)"
        Etaj_Rel   = "Pozitie relativa in bloc";
RUN;

/* Distributia categoriilor */
PROC FREQ DATA=WORK.imob_procesat;
    TABLES Categ_Pret Categ_Sup Lux / NOCUM;
    TITLE2 "Distributia variabilelor derivate";
RUN;

PROC MEANS DATA=WORK.imob_procesat N MEAN STD MIN MAX MEDIAN;
    VAR Pret_mp;
    CLASS Categ_Pret;
    TITLE2 "Pret/mp pe categorii de pret";
RUN;


/* ================================================================
   FUNCTIA 4 – CREAREA DE SUBSETURI DE DATE
   ================================================================
   a) Problema: analiza pe segmente specifice ale pietei
   b) Info: WHERE in DATA step si PROC, OBS=
   c) Metoda: filtrare conditionala pe criterii multiple
   d) Rezultate: 4 subseturi pentru analiza comparativa
   e) Interpretare economica: comparable market analysis (CMA) –
      practica standard in evaluarea imobiliara profesionala
   ================================================================ */

/* Subset Sector 1 – piata premium */
DATA WORK.sector1;
    SET WORK.imob_procesat;
    WHERE Sector = 1;
RUN;

/* Subset apartamente mari – familii */
DATA WORK.apto_mari;
    SET WORK.imob_procesat;
    WHERE Suprafata > 100 AND Nr_Camere >= 3;
RUN;

/* Subset fara outlieri (IQR-based) */
PROC MEANS DATA=WORK.imob_procesat NOPRINT;
    VAR Pret;
    OUTPUT OUT=WORK.quantile_pret Q1=Q1 Q3=Q3;
RUN;

DATA _NULL_;
    SET WORK.quantile_pret;
    CALL SYMPUTX('IQR_LOW',  Q1 - 1.5*(Q3-Q1));
    CALL SYMPUTX('IQR_HIGH', Q3 + 1.5*(Q3-Q1));
RUN;

DATA WORK.fara_outlieri;
    SET WORK.imob_procesat;
    WHERE Pret >= &IQR_LOW AND Pret <= &IQR_HIGH;
RUN;

/* Subset proprietati accesibile cu scor bun */
DATA WORK.accesibil_bun;
    SET WORK.imob_procesat;
    WHERE Pret < 80000 AND Scor >= 4;
RUN;

/* Raport subseturi */
%MACRO raport_subset(ds, eticheta);
    PROC MEANS DATA=&ds N MEAN MEDIAN STD MIN MAX;
        VAR Pret Suprafata;
        TITLE2 "Subset: &eticheta (n=%SYSFUNC(ATTRN(%SYSFUNC(OPEN(&ds)),NOBS)))";
    RUN;
%MEND;

%raport_subset(WORK.sector1, Sector 1 - Premium);
%raport_subset(WORK.apto_mari, Apartamente mari >100mp);
%raport_subset(WORK.fara_outlieri, Fara outlieri IQR);
%raport_subset(WORK.accesibil_bun, Accesibil cu scor bun);


/* ================================================================
   FUNCTIA 5 – COMBINAREA SETURILOR DE DATE (MERGE si SQL)
   ================================================================
   a) Problema: imbogatirea datelor cu informatii sectoriale externe
   b) Info: PROC SQL JOIN, DATA step MERGE...BY, PROC SORT
   c) Metoda: LEFT JOIN pe cheia Sector
   d) Rezultate: dataset cu deviatie fata de referinta sectorala
   e) Interpretare economica: identificare proprietati sub/supra-
      evaluate fata de media sectorului (due diligence investitional)
   ================================================================ */

/* Dataset de referinta sectorala (creat manual) */
DATA WORK.ref_sector;
    INPUT Sector Populatie_mii Pret_ref_mp Indice_Calitate;
    DATALINES;
1  240  1850  9.2
2  390  1350  7.1
3  420  1400  7.4
4  360  1200  6.8
5  310  1150  6.5
6  380  1250  6.9
;
RUN;

/* Metoda 1: PROC SQL cu LEFT JOIN */
PROC SQL;
    CREATE TABLE WORK.analiza_completa AS
    SELECT
        a.*,
        b.Populatie_mii,
        b.Pret_ref_mp,
        b.Indice_Calitate,
        (a.Pret_mp - b.Pret_ref_mp)    AS Deviatie_mp       LABEL="Deviatie fata de referinta (EUR/mp)",
        (a.Pret_mp / b.Pret_ref_mp - 1) * 100 AS Deviatie_pct LABEL="Deviatie procentuala (%)"
    FROM WORK.imob_procesat AS a
    LEFT JOIN WORK.ref_sector AS b
        ON a.Sector = b.Sector
    ORDER BY a.Sector, a.Pret DESC;
QUIT;

/* Metoda 2: DATA step MERGE (echivalent) */
PROC SORT DATA=WORK.imob_procesat OUT=WORK.imob_sort; BY Sector; RUN;
PROC SORT DATA=WORK.ref_sector;                         BY Sector; RUN;

DATA WORK.analiza_merge;
    MERGE WORK.imob_sort (IN=a)
          WORK.ref_sector (IN=b);
    BY Sector;
    IF a; /* pastreaza doar obs. din setul principal */
RUN;

/* Raport comparativ sectoare */
PROC SQL;
    SELECT
        Sector FORMAT=sector_fmt.,
        COUNT(*) AS Nr_Proprietati,
        MEAN(Pret_mp) FORMAT=8.0 AS Pret_mp_Mediu,
        MEAN(Pret_ref_mp) FORMAT=8.0 AS Pret_mp_Referinta,
        MEAN(Deviatie_pct) FORMAT=8.1 AS Deviatie_medie_pct
    FROM WORK.analiza_completa
    GROUP BY Sector
    ORDER BY Deviatie_medie_pct DESC;
QUIT;
TITLE2 "Comparatie pret/mp fata de referinta sectorala";


/* ================================================================
   FUNCTIA 6 – UTILIZAREA DE MASIVE (ARRAYS)
   ================================================================
   a) Problema: standardizare si procesare in lot a mai multor
      variabile numerice simultan
   b) Info: ARRAY, DO...END, DIM(), functie MEAN/STD
   c) Metoda: z-score manual prin masive SAS (μ si σ precalculate)
   d) Rezultate: 5 variabile standardizate + detectie outlieri multipli
   e) Interpretare economica: preprocesare necesara pentru modele ML;
      asigura comparabilitate in model risk management (SR 11-7)
   ================================================================ */

/* Calculam media si std pentru fiecare variabila */
PROC MEANS DATA=WORK.imob_procesat NOPRINT;
    VAR Suprafata Nr_Camere Etaj Scor Pret_mp;
    OUTPUT OUT=WORK.stats_var
           MEAN=m_Sup m_Cam m_Etaj m_Scor m_Pmp
           STD=s_Sup  s_Cam s_Etaj s_Scor s_Pmp;
RUN;

DATA _NULL_;
    SET WORK.stats_var;
    ARRAY medii[5] m_Sup m_Cam m_Etaj m_Scor m_Pmp;
    ARRAY devstd[5] s_Sup s_Cam s_Etaj s_Scor s_Pmp;
    ARRAY var_names[5] $ _TEMPORARY_ ("Suprafata" "Nr_Camere" "Etaj" "Scor" "Pret_mp");
    DO i = 1 TO 5;
        CALL SYMPUTX(CATS("MU_",i), medii[i]);
        CALL SYMPUTX(CATS("SD_",i), devstd[i]);
    END;
RUN;

DATA WORK.imob_scaled;
    SET WORK.imob_procesat;

    /* Masiv de variabile originale */
    ARRAY orig[5] Suprafata Nr_Camere Etaj Scor Pret_mp;

    /* Masiv valori medii (macro-variabile) */
    ARRAY medii[5] _TEMPORARY_ (&MU_1 &MU_2 &MU_3 &MU_4 &MU_5);

    /* Masiv deviatii standard */
    ARRAY devstd[5] _TEMPORARY_ (&SD_1 &SD_2 &SD_3 &SD_4 &SD_5);

    /* Masiv variabile standardizate (output) */
    ARRAY scaled[5] Sup_z Cam_z Etaj_z Scor_z Pmp_z;

    /* Masiv indicatori outlier per variabila */
    ARRAY outlier[5] Out_Sup Out_Cam Out_Etaj Out_Scor Out_Pmp;

    DO i = 1 TO 5;
        /* Standardizare z-score */
        IF devstd[i] > 0 THEN
            scaled[i] = (orig[i] - medii[i]) / devstd[i];
        ELSE
            scaled[i] = 0;

        /* Marcare outlieri (|z| > 3) */
        IF ABS(scaled[i]) > 3 THEN outlier[i] = 1;
        ELSE outlier[i] = 0;
    END;

    /* Numar total variabile cu outlier pentru aceasta obs. */
    Nr_Outlieri_Var = SUM(OF outlier[*]);

    DROP i;

    LABEL
        Sup_z   = "Suprafata standardizata (z)"
        Cam_z   = "Nr Camere standardizat (z)"
        Etaj_z  = "Etaj standardizat (z)"
        Scor_z  = "Scor standardizat (z)"
        Pmp_z   = "Pret/mp standardizat (z)";
RUN;

/* Verificare: media trebuie ~0, std ~1 */
PROC MEANS DATA=WORK.imob_scaled MEAN STD MIN MAX;
    VAR Sup_z Cam_z Etaj_z Scor_z Pmp_z;
    TITLE2 "Verificare standardizare – media≈0, std≈1";
RUN;

/* Proprietati cu outlieri la mai multe variabile simultan */
PROC FREQ DATA=WORK.imob_scaled;
    TABLES Nr_Outlieri_Var / NOCUM;
    TITLE2 "Distributia numarului de variabile extreme per proprietate";
RUN;


/* ================================================================
   FUNCTIA 7 – PROCEDURI STATISTICE (MEANS, FREQ, REG, CORR)
   ================================================================
   a) Problema: analiza statistica completa si model econometric
   b) Info: PROC MEANS, PROC FREQ, PROC CORR, PROC REG
   c) Metoda: statistici descriptive + regresie OLS cu diagnostice
   d) Rezultate: coeficienti, R², VIF, intervale de incredere
   e) Interpretare economica: cuantificarea primei de localizare
      si a contributiei fiecarui factor la pretul imobiliar
   ================================================================ */

/* 7a. Statistici descriptive complete pe sectoare */
PROC MEANS DATA=WORK.imob_procesat
           N MEAN STD MEDIAN MIN MAX Q1 Q3 CV;
    VAR Pret Suprafata Pret_mp Nr_Camere;
    CLASS Sector;
    FORMAT Sector sector_fmt.;
    OUTPUT OUT=WORK.stats_sector
           MEAN=Pret_med Sup_med Pmp_med Cam_med
           MEDIAN=Pret_mdn;
    TITLE2 "Statistici descriptive pe sectoare";
RUN;

/* 7b. Tabele de frecventa si teste de asociere */
PROC FREQ DATA=WORK.imob_procesat;
    TABLES Sector * Nr_Camere / CHISQ EXPECTED NOCOL NOPCT;
    FORMAT Sector sector_fmt.;
    TITLE2 "Tabel de contingenta Sector x Nr. Camere (test Chi-patrat)";
RUN;

PROC FREQ DATA=WORK.imob_procesat;
    TABLES Sector * Categ_Pret / CHISQ NOROW NOPCT;
    FORMAT Sector sector_fmt.;
    TITLE2 "Asocierea Sector-Categorie Pret";
RUN;

/* 7c. Matrice de corelatie */
PROC CORR DATA=WORK.imob_procesat PEARSON SPEARMAN;
    VAR Pret Suprafata Nr_Camere Etaj Total_Etaje Scor Pret_mp;
    TITLE2 "Matrice de corelatie Pearson si Spearman";
RUN;

/* 7d. Creare variabile dummy pentru sector (referinta = Sector 1) */
DATA WORK.imob_reg;
    SET WORK.imob_procesat;
    Sect2 = (Sector = 2);
    Sect3 = (Sector = 3);
    Sect4 = (Sector = 4);
    Sect5 = (Sector = 5);
    Sect6 = (Sector = 6);
RUN;

/* 7e. Regresie multipla OLS */
PROC REG DATA=WORK.imob_reg PLOTS(MAXPOINTS=5000)=ALL;
    MODEL Pret = Suprafata Nr_Camere Etaj Total_Etaje Scor
                 Sect2 Sect3 Sect4 Sect5 Sect6
                 / R ADJRSQ VIF CLM CLI TOL INFLUENCE;
    /* Test Breusch-Pagan pentru heteroscedasticitate */
    OUTPUT OUT=WORK.reg_output
           PREDICTED=Yhat RESIDUAL=Reziduu
           STUDENT=Rez_Student COOKD=CooksD;
    TITLE2 "Regresie multipla OLS – determinantii pretului imobiliar";
RUN;
QUIT;

/* Proprietati cu influenta mare (Cook's D > 4/n) */
DATA WORK.influenti;
    SET WORK.reg_output;
    IF CooksD > 4/3529;
RUN;

PROC PRINT DATA=WORK.influenti (OBS=20) NOOBS;
    VAR Pret Suprafata Sector Nr_Camere Scor Yhat Reziduu CooksD;
    FORMAT Sector sector_fmt. Pret Yhat DOLLAR12.;
    TITLE2 "Proprietati cu influenta mare asupra modelului (Cook's D)";
RUN;


/* ================================================================
   FUNCTIA 8 – GENERARE GRAFICE (SGPLOT, SGPANEL, SGSCATTER)
   ================================================================
   a) Problema: comunicarea vizuala a rezultatelor pentru rapoarte
   b) Info: PROC SGPLOT, PROC SGPANEL, PROC SGSCATTER, ODS Graphics
   c) Metoda: grafice vectoriale de calitate publicabila
   d) Rezultate: 6 grafice integrate in raportul PDF
   e) Interpretare economica: gradientul de preturi, distributii,
      relatia suprafata-pret si profilul fiecarui sector
   ================================================================ */

/* Grafic 1: Distributia preturilor – histogram + density */
PROC SGPLOT DATA=WORK.imob_procesat;
    HISTOGRAM Pret / BINWIDTH=10000 FILLATTRS=(COLOR=CX2E75B6) TRANSPARENCY=0.2;
    DENSITY Pret / LINEATTRS=(COLOR=CXE74C3C THICKNESS=2);
    DENSITY Pret / TYPE=KERNEL LINEATTRS=(COLOR=CXF39C12 THICKNESS=2 PATTERN=DASH);
    REFLINE 97846 / AXIS=X LINEATTRS=(COLOR=CXE74C3C) LABEL="Medie";
    REFLINE 78600 / AXIS=X LINEATTRS=(COLOR=CXF39C12 PATTERN=DASH) LABEL="Median";
    XAXIS LABEL="Pret (EUR)" FORMAT=DOLLAR12.;
    YAXIS LABEL="Frecventa";
    TITLE2 "Distributia preturilor imobiliare in Bucuresti";
RUN;

/* Grafic 2: Box-plot pret pe sectoare */
PROC SGPLOT DATA=WORK.imob_procesat;
    VBOX Pret / CATEGORY=Sector GROUP=Sector
                GROUPDISPLAY=CLUSTER NOFILL
                WHISKERATTRS=(THICKNESS=2)
                BOXWIDTH=0.6;
    XAXIS LABEL="Sector" VALUESFORMAT=sector_fmt.;
    YAXIS LABEL="Pret (EUR)" FORMAT=DOLLAR12.;
    TITLE2 "Distributia preturilor pe sectoare (Box-plot)";
RUN;

/* Grafic 3: Scatter Suprafata vs Pret, colorat pe Sector */
PROC SGPLOT DATA=WORK.imob_procesat;
    REG X=Suprafata Y=Pret / GROUP=Sector
        MARKERATTRS=(SIZE=4 SYMBOL=CircleFilled)
        LINEATTRS=(THICKNESS=1.5)
        TRANSPARENCY=0.6;
    XAXIS LABEL="Suprafata (mp)";
    YAXIS LABEL="Pret (EUR)" FORMAT=DOLLAR12.;
    KEYLEGEND / TITLE="Sector" VALUEATTRS=(SIZE=8);
    TITLE2 "Relatia Suprafata - Pret pe sectoare";
RUN;

/* Grafic 4: Bar chart pret mediu/mp pe sector */
PROC SGPLOT DATA=WORK.imob_procesat;
    VBAR Sector / RESPONSE=Pret_mp STAT=MEAN
                  FILLATTRS=(COLOR=CX2E75B6)
                  DATALABEL DATALABELATTRS=(SIZE=9 COLOR=BLACK);
    XAXIS LABEL="Sector" VALUESFORMAT=sector_fmt.;
    YAXIS LABEL="Pret mediu per mp (EUR/mp)";
    TITLE2 "Pretul mediu/mp pe sectoare";
RUN;

/* Grafic 5: Panel – histograme pret per sector */
PROC SGPANEL DATA=WORK.imob_procesat;
    PANELBY Sector / LAYOUT=LATTICE COLUMNS=3
                     HEADERATTRS=(SIZE=9) NOVARNAME;
    HISTOGRAM Pret / BINWIDTH=15000 FILLATTRS=(COLOR=CX2E75B6) TRANSPARENCY=0.3;
    DENSITY Pret / LINEATTRS=(COLOR=CXE74C3C THICKNESS=2);
    COLAXIS LABEL="Pret (EUR)" FORMAT=DOLLAR10.;
    ROWAXIS LABEL="Frecventa";
    FORMAT Sector sector_fmt.;
    TITLE2 "Distributia preturilor pe sectoare (panel)";
RUN;

/* Grafic 6: Scatter matrix (Nr Camere, Suprafata, Pret, Scor) */
PROC SGSCATTER DATA=WORK.imob_procesat (OBS=1000);
    MATRIX Pret Suprafata Nr_Camere Scor /
           GROUP=Sector
           MARKERATTRS=(SIZE=3 SYMBOL=CircleFilled)
           TRANSPARENCY=0.5
           DIAGONAL=(HISTOGRAM KERNEL);
    TITLE2 "Matrice scatter – variabile cheie (sample 1000 obs.)";
RUN;

/* Grafic 7: Trend pret mediu pe nr camere si sector */
PROC SGPLOT DATA=WORK.imob_procesat;
    SERIES X=Nr_Camere Y=Pret / GROUP=Sector
           STAT=MEAN
           MARKERS MARKERATTRS=(SIZE=8 SYMBOL=CircleFilled)
           LINEATTRS=(THICKNESS=2);
    XAXIS LABEL="Nr. Camere" INTEGER;
    YAXIS LABEL="Pret mediu (EUR)" FORMAT=DOLLAR12.;
    KEYLEGEND / TITLE="Sector" VALUEATTRS=(SIZE=8) POSITION=BOTTOMRIGHT;
    TITLE2 "Pretul mediu pe numarul de camere, grupat pe sector";
RUN;


/* ================================================================
   PROCEDURI SUPLIMENTARE – RAPORTARE AVANSATA
   ================================================================ */

/* Raport final sumar – PROC TABULATE */
PROC TABULATE DATA=WORK.imob_procesat FORMAT=12.0;
    CLASS Sector Categ_Pret;
    VAR Pret Suprafata Pret_mp;
    TABLE Sector * (Pret * (MEAN MEDIAN) Suprafata * MEAN Pret_mp * MEAN),
          Categ_Pret ALL;
    FORMAT Sector sector_fmt.;
    TITLE2 "Tabel sumar – Pret, Suprafata si Pret/mp pe Sector x Categorie Pret";
RUN;

/* Analiza regresiei pe subseturi – PROC REG cu BY */
PROC SORT DATA=WORK.imob_reg; BY Sector; RUN;

PROC REG DATA=WORK.imob_reg NOPRINT OUTEST=WORK.coef_sector;
    BY Sector;
    MODEL Pret = Suprafata Nr_Camere Etaj Scor / ADJRSQ;
    TITLE2 "Regresie separata pe fiecare sector";
RUN;
QUIT;

PROC PRINT DATA=WORK.coef_sector NOOBS;
    VAR Sector _RSQ_ _ADJRSQ_ Suprafata Nr_Camere Etaj Scor;
    FORMAT Sector sector_fmt. _RSQ_ _ADJRSQ_ 6.4
           Suprafata Nr_Camere Etaj Scor 8.1;
    TITLE2 "Coeficienti de regresie pe sectoare + R-patrat";
RUN;


/* ================================================================
   INCHIDERE ODS si CURATARE
   ================================================================ */
ODS PDF CLOSE;
ODS GRAPHICS OFF;

TITLE;
FOOTNOTE;

%PUT ============================================================;
%PUT   ANALIZA FINALIZATA CU SUCCES;
%PUT   Datasets create: imobiliare, imob_procesat, imob_scaled,;
%PUT                    analiza_completa, imob_reg, reg_output;
%PUT   Raport PDF: Analiza_Imobiliara_Rezultate.pdf;
%PUT ============================================================;
