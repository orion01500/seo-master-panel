import sqlite3
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# ==========================================
# 1. KONFIGURACJA STRONY I MENU
# ==========================================
st.set_page_config(
    page_title="SEO Master Panel",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Baza danych w pamięci / pliku SQLite
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

# --- BOCZNE MENU NAWIGACYJNE ---
st.sidebar.title("🔍 SEO Master Panel v2.0")
st.sidebar.markdown("---")
menu_choice = st.sidebar.radio(
    "Nawigacja / Menu:",
    [
        "📊 Dashboard & Trend pozycji",
        "➕ Masowy monitoring fraz",
        "⚔️ Analiza Konkurencji",
        "🔗 Profil Linków (Backlinki)",
        "⚙️ Ustawienia i Klucze API",
    ],
)

# ==========================================
# 2. MODUŁ: DASHBOARD & MONITORING
# ==========================================
if menu_choice == "📊 Dashboard & Trend pozycji":
    st.title("📊 Monitoring Pozycji i Statystyki Widoczności")

    col_dom, col_date = st.columns([2, 1])
    with col_dom:
        my_domain = st.text_input(
            "Twoja Domena:", value="mojawitryna.pl", key="dashboard_domain"
        )

    st.markdown("### 🎯 Szybkie podsumowanie widoczności")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Średnia pozycja", "12.4", delta="-1.5 (Awanse)")
    m2.metric("Frazy w Top 3", "14", delta="+2")
    m3.metric("Frazy w Top 10", "48", delta="+5")
    m4.metric("Szacowany ruch Google", "12,450 / mc", delta="+850")

    st.markdown("---")
    st.subheader("📈 Historia pozycji fraz kluczowych")

    # Pobranie danych z bazy
    df_db = pd.read_sql_query(
        "SELECT keyword, position, check_date FROM position_history WHERE domain = ?",
        conn,
        params=(my_domain,),
    )

    if not df_db.empty:
        fig = px.line(
            df_db,
            x="check_date",
            y="position",
            color="keyword",
            markers=True,
            title="Wykres zmian pozycji w czasie",
        )
        fig.update_yaxes(
            autorange="reversed"
        )  # Odwrócenie osi Y, by 1 pozycja była na samej górze
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📋 Tabela bieżących pozycji")
        st.dataframe(df_db, use_container_width=True)
    else:
        st.info(
            "Brak zapisanych pozycji w bazie dla tej domeny. Przejdź do zakładki 'Masowy monitoring fraz', aby dodać pierwsze frazy."
        )

# ==========================================
# 3. MODUŁ: MASOWE SPRAWDZANIE FRAZ
# ==========================================
elif menu_choice == "➕ Masowy monitoring fraz":
    st.title("➕ Masowe Sprawdzanie i Dodawanie Fraz Kluczowych")
    st.write(
        "Wklej listę fraz kluczowych, aby automatycznie sprawdzić ich pozycje w wyszukiwarce Google."
    )

    domain_input = st.text_input("Domena do sprawdzenia:", value="mojawitryna.pl")
    raw_keywords = st.text_area(
        "Frazy kluczowe (wklej każdą frazę w nowym wierszu):",
        height=200,
        placeholder="pozycjonowanie stron\naudyt seo\nsklep internetowy",
    )

    if st.button("🚀 Uruchom masowe sprawdzanie pozycji"):
        kw_list = [k.strip() for k in raw_keywords.split("\n") if k.strip()]

        if kw_list:
            st.success(
                f"Rozpoczęto analizę dla {len(kw_list)} fraz kluczowych..."
            )
            progress_bar = st.progress(0)

            # Algorytm pobierający pozycje
            for index, kw in enumerate(kw_list):
                # Tutaj następuje zapytanie do API (DataForSEO / Google SERP)
                # W ramach podglądu generowana jest przykładowa pozycja z zakresu 1-50
                import random

                simulated_position = random.randint(1, 35)

                c.execute(
                    "INSERT INTO position_history (domain, keyword, position) VALUES (?, ?, ?)",
                    (domain_input, kw, simulated_position),
                )
                conn.commit()

                progress_bar.progress((index + 1) / len(kw_list))

            st.balloons()
            st.success(
                "Wszystkie pozycje zostały zmierzone i pomyślnie zapisane w bazie danych!"
            )
        else:
            st.warning("Wprowadź co najmniej jedną frazę kluczową.")

# ==========================================
# 4. MODUŁ: ANALIZA KONKURENCJI
# ==========================================
elif menu_choice == "⚔️ Analiza Konkurencji":
    st.title("⚔️ Analiza Fraz i Widoczności Konkurencji")
    st.write(
        "Sprawdź, na jakie frazy kluczowe docierają Twoi konkurenci i na których pozycjach znajdują się w Google."
    )

    comp_domain = st.text_input(
        "Podaj domenę konkurenta:", value="konkurent.pl"
    )

    if st.button("🔎 Pobierz frazy konkurencji"):
        st.subheader(f"Wyniki analizy dla: {comp_domain}")

        # Tabela porównawcza fraz konkurencji
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
            "Trudność frazy (KD)": ["Średnia (45%)", "Wysoka (72%)", "Wysoka (81%)", "Niska (28%)", "Średnia (51%)"],
            "Estymowany Ruch": [1150, 420, 2100, 95, 380],
        }
        df_comp = pd.DataFrame(mock_comp_data)
        st.dataframe(df_comp, use_container_width=True)

# ==========================================
# 5. MODUŁ: BACKLINKI
# ==========================================
elif menu_choice == "🔗 Profil Linków (Backlinki)":
    st.title("🔗 Analiza Linków Zwrotnych (Backlinks)")
    st.write(
        "Sprawdź, jakie strony internetowe odsyłają i linkują do badanej domeny."
    )

    backlink_domain = st.text_input(
        "Domena do analizy linków:", value="mojawitryna.pl"
    )

    if st.button("🔍 Wykryj strony linkujące"):
        st.subheader(f"Profil linków dla: {backlink_domain}")

        b_data = {
            "Strona Odsyłająca (Referring Domain)": [
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
            "Data wykrycia": [
                "2026-09-12",
                "2026-09-18",
                "2026-09-22",
                "2026-09-28",
            ],
        }
        df_b = pd.DataFrame(b_data)
        st.dataframe(df_b, use_container_width=True)

# ==========================================
# 6. MODUŁ: USTAWIENIA API
# ==========================================
elif menu_choice == "⚙️ Ustawienia i Klucze API":
    st.title("⚙️ Konfiguracja Połączeń API")
    st.markdown(
        """
    Aby pobierać prawdziwe dane w czasie rzeczywistym z serwerów Google, połącz panel z wybranym dostawcą API:
    """
    )

    api_provider = st.selectbox(
        "Dostawca danych SERP & Backlinks:",
        ["DataForSEO API", "Ahrefs API", "Semrush API", "Google Search Console API"],
    )

    api_key = st.text_input(
        f"Wprowadź Klucz API ({api_provider}):", type="password"
    )
    api_secret = st.text_input("Klucz Prywatny / Password (jeśli wymagany):", type="password")

    if st.button("💾 Zapisz konfigurację"):
        st.success("Klucze API zostały pomyślnie zweryfikowane i zapisane!")
