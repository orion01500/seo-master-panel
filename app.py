import random
import sqlite3
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# ==========================================
# 1. KONFIGURACJA STRONY I BAZY DANYCH
# ==========================================
st.set_page_config(
    page_title="SEO Master Panel",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inicjalizacja lokalnej bazy danych SQLite
conn = sqlite3.connect("seo_panel.db", check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS position_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain TEXT,
    keyword TEXT,
    position INTEGER,
    check_date DATE DEFAULT CURRENT_DATE
)
""")
conn.commit()

# ==========================================
# 2. PASEK BOCZNY - MENU NAWIGACYJNE
# ==========================================
st.sidebar.title("🔍 SEO Master Panel v2.0")
st.sidebar.markdown("---")
menu_choice = st.sidebar.radio(
    "MENU NAWIGACJI:",
    [
        "📊 Dashboard & Monitoring",
        "➕ Masowy monitoring fraz",
        "⚔️ Analiza Konkurencji",
        "🔗 Profil Linków (Backlinki)",
        "⚙️ Ustawienia i API",
    ],
)

# Globalne pole wyboru domeny w pasku bocznym
selected_domain = st.sidebar.text_input(
    "🌐 Twoja główna domena:", value="mojawitryna.pl"
)

# ==========================================
# 3. MODUŁ 1: DASHBOARD & MONITORING
# ==========================================
if menu_choice == "📊 Dashboard & Monitoring":
    st.title("📊 Monitoring Pozycji i Widoczności")
    st.caption(f"Aktywna domena: **{selected_domain}**")

    # Kafelki ze statystykami
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Średnia pozycja", "11.8", delta="-1.2 (Wzrost)")
    col2.metric("Frazy w Top 3", "16", delta="+3")
    col3.metric("Frazy w Top 10", "52", delta="+7")
    col4.metric("Estymowany ruch", "14,200 / mc", delta="+1,150")

    st.markdown("---")
    st.subheader("📈 Wykres zmian pozycji w czasie")

    # Pobieranie danych z bazy dla wybranej domeny
    df_db = pd.read_sql_query(
        "SELECT keyword AS 'Fraza', position AS 'Pozycja', check_date AS 'Data' FROM position_history WHERE domain = ?",
        conn,
        params=(selected_domain,),
    )

    if not df_db.empty:
        # Interaktywny wykres Plotly
        fig = px.line(
            df_db,
            x="Data",
            y="Pozycja",
            color="Fraza",
            markers=True,
            title="Historia pozycji w wyszukiwarce Google",
        )
        fig.update_yaxes(
            autorange="reversed"
        )  # Odwrócenie osi Y: Pozycja 1 na samej górze
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📋 Aktualna tabela pozycji")
        st.dataframe(df_db, use_container_width=True)
    else:
        st.info(
            "Brak zapisanych pozycji w bazie. Przejdź do zakładki **'Masowy monitoring fraz'**, aby dodać pierwsze słowa kluczowe."
        )

# ==========================================
# 4. MODUŁ 2: MASOWY MONITORING FRAZ
# ==========================================
elif menu_choice == "➕ Masowy monitoring fraz":
    st.title("➕ Masowe Sprawdzanie i Dodawanie Fraz Kluczowych")
    st.write(
        "Wklej dużą listę fraz kluczowych, aby automatycznie zmierzyć ich pozycję w wyszukiwarce."
    )

    domain_input = st.text_input(
        "Domena do sprawdzania:", value=selected_domain
    )
    raw_keywords = st.text_area(
        "Wklej frazy kluczowe (każda w nowej linii):",
        height=200,
        placeholder="pozycjonowanie stron\naudyt seo\nsklep internetowy\nagencja marketingowa",
    )

    if st.button("🚀 Uruchom masowe sprawdzanie pozycji"):
        kw_list = [k.strip() for k in raw_keywords.split("\n") if k.strip()]

        if kw_list:
            st.info(
                f"Rozpoczęto analizę pozycji dla {len(kw_list)} fraz..."
            )
            progress_bar = st.progress(0)

            # Pętla sprawdzająca pozycje
            for index, kw in enumerate(kw_list):
                # Symulacja wyniku SERP (gotowe pod podpięcie zewnętrznego API, np. DataForSEO)
                simulated_pos = random.randint(1, 40)

                c.execute(
                    "INSERT INTO position_history (domain, keyword, position) VALUES (?, ?, ?)",
                    (domain_input, kw, simulated_pos),
                )
                conn.commit()

                progress_bar.progress((index + 1) / len(kw_list))

            st.balloons()
            st.success(
                f"Pomyślnie zmierzono i zapisano pozycje dla {len(kw_list)} fraz!"
            )
        else:
            st.warning("Proszę wprowadzić przynajmniej jedną frazę kluczową.")

# ==========================================
# 5. MODUŁ 3: ANALIZA KONKURENCJI
# ==========================================
elif menu_choice == "⚔️ Analiza Konkurencji":
    st.title("⚔️ Sprawdzanie Fraz Kluczowych Konkurencji")
    st.write(
        "Wpisz domenę konkurenta, aby zobaczyć, na jakie frazy jest widoczny w Google."
    )

    comp_domain = st.text_input(
        "Podaj domenę konkurenta:", value="konkurencja.pl"
    )

    if st.button("🔎 Analizuj frazy konkurencji"):
        st.subheader(f"Wyniki analizy fraz dla domeny: {comp_domain}")

        # Przykładowe zestawienie fraz konkurencji
        mock_comp_data = {
            "Fraza Kluczowa": [
                "kurs pozycjonowania",
                "agencja seo warszawa",
                "optymalizacja sklepów",
                "link building usługa",
                "audyt strony cena",
            ],
            "Pozycja Konkurencji": [2, 4, 1, 7, 3],
            "Wyszukiwania / mc": [2900, 1900, 4400, 880, 1300],
            "Trudność frazy (KD)": [
                "Średnia (45%)",
                "Wysoka (72%)",
                "Wysoka (81%)",
                "Niska (28%)",
                "Średnia (51%)",
            ],
            "Estymowany Ruch": [1150, 420, 2100, 95, 380],
        }
        df_comp = pd.DataFrame(mock_comp_data)
        st.dataframe(df_comp, use_container_width=True)

# ==========================================
# 6. MODUŁ 4: PROFIL LINKÓW (BACKLINKI)
# ==========================================
elif menu_choice == "🔗 Profil Linków (Backlinki)":
    st.title("🔗 Analiza Linków Zwrotnych (Backlinks)")
    st.write(
        "Sprawdź, z jakich stron internetowych i domeny pozyskują odnośniki (linki zwrotne)."
    )

    backlink_domain = st.text_input(
        "Podaj domenę do analizy linków:", value=selected_domain
    )

    if st.button("🔍 Wykryj strony linkujące"):
        st.subheader(f"Profil linków dla: {backlink_domain}")

        b_data = {
            "Strona Odsyłająca (Referring Page)": [
                "https://portaltechnologiczny.pl/artykuly/seo-2026",
                "https://katalog-firm-polska.pl/oferta/10293",
                "https://blog-marketingowy.com/jak-pozycjonowac",
                "https://forum-biznesowe.pl/watek-20491",
            ],
            "Anchor Text (Tekst linku)": [
                "zobacz pełny raport",
                "mojawitryna.pl",
                "skuteczne pozycjonowanie",
                "kliknij tutaj",
            ],
            "Domain Rating (DR)": [68, 34, 52, 29],
            "Atrybut Linku": ["DoFollow", "NoFollow", "DoFollow", "DoFollow"],
            "Data Wykrycia": [
                "2026-09-12",
                "2026-09-18",
                "2026-09-22",
                "2026-09-28",
            ],
        }
        df_b = pd.DataFrame(b_data)
        st.dataframe(df_b, use_container_width=True)

# ==========================================
# 7. MODUŁ 5: USTAWIENIA I KLUCZE API
# ==========================================
elif menu_choice == "⚙️ Ustawienia i API":
    st.title("⚙️ Konfiguracja Kluczy API i Ustawień")
    st.info(
        "Podepnij wybrane dostawce danych SEO, aby pobierać rzeczywiste pozycje i linki w czasie rzeczywistym."
    )

    st.selectbox(
        "Dostawca danych SERP & Backlinks:",
        ["DataForSEO API", "Ahrefs API", "Semrush API", "Google Search Console API"],
    )

    st.text_input("Klucz API / API Key:", type="password")
    st.text_input("Klucz Prywatny / API Secret:", type="password")

    if st.button("💾 Zapisz ustawienia"):
        st.success("Zapisano konfigurację kluczy API!")
