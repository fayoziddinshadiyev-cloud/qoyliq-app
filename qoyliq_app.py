import streamlit as st
import pandas as pd

# ==========================================
# ПС «ҚЎЙЛИҚ» — Муҳандислик Бошқарув ва Синов Маркази
# ==========================================

st.set_page_config(
    page_title="ПС Қўйлиқ - 162 та ускуна базаси",
    page_icon="⚡",
    layout="wide"
)

# --- 30 ТА ХОДИМ УЧУН ЛОГИН-ПАРОЛЬ ТИЗИМИ ---
def check_password():
    def password_entered():
        if st.session_state["password"] == "qoyliq2026":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.subheader("🔒 ПС «Қўйлиқ» — Тизимга кириш")
        st.text_input("Паролни киритинг:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.subheader("🔒 ПС «Қўйлиқ» — Тизимга кириш")
        st.text_input("Паролни киритинг:", type="password", on_change=password_entered, key="password")
        st.error("❌ Парол нотўғри! Қайта уриниб кўринг.")
        return False
    else:
        return True

if check_password():

    st.title("⚡ ПС «ҚЎЙЛИҚ» ПОДСТАНЦИЯСИ")
    st.markdown("**elektroekspert** — 162 та асосий юқори кучланишли ускуналарнинг маълумотлар базаси.")
    st.markdown("---")

    # --- 162 ТА УСКУНАНИНГ ТЎЛИҚ БАЗАСИНИ ГЕНЕРАЦИЯ ҚИЛИШ ---
    @st.cache_data
    def load_full_equipment():
        items = []
        
        # 220 kV ускуналар (масалан, 20 та)
        for i in range(1, 21):
            items.append({
                "uskuna_nomi": f"220kV Тармоқ қурилмаси №{i}",
                "kuvvati": "40000 kVA" if i <= 4 else "Ҳолати соз",
                "kuchlanish": "220 kV",
                "holati": "Ремонтда" if i == 7 else "Ишда",
                "sana": "2026-08-04"
            })
            
        # 110 kV ускуналар (масалан, 82 та)
        for i in range(1, 83):
            items.append({
                "uskuna_nomi": f"110kV Учиргич ва Ҳимоя №{i}",
                "kuvvati": "25000 kVA" if i <= 10 else "Ҳолати соз",
                "kuchlanish": "110 kV",
                "holati": "Резервда" if i == 15 else "Ишда",
                "sana": "2026-08-04"
            })
            
        # 35 kV ускуналар (масалан, 60 та)
        for i in range(1, 61):
            items.append({
                "uskuna_nomi": f"35kV Қўрилма ва Танф. №{i}",
                "kuvvati": "10000 kVA" if i <= 12 else "Ҳолати соз",
                "kuchlanish": "35 kV",
                "holati": "Ишда",
                "sana": "2026-08-04"
            })
            
        return pd.DataFrame(items)

    df = load_full_equipment()

    # --- ФИЛЬТР ВА САРАЛАШ ҚИСМИ ---
    st.sidebar.header("🔍 Саралаш ва Қидирув")
    selected_class = st.sidebar.selectbox(
        "Кучланиш синфини танланг:",
        ["Барчаси", "220 kV", "110 kV", "35 kV"]
    )

    if selected_class != "Барчаси":
        filtered_df = df[df["kuchlanish"] == selected_class]
    else:
        filtered_df = df

    # --- АСОСИЙ ЭКРАНГА ЧИҚАРИШ ---
    st.subheader(f"📊 Ускуналар рўйхати ({selected_class})")
    st.dataframe(filtered_df, use_container_width=True)

    # Статистика ва маълумот
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Жами ускуналар сони", len(df))
    with col2:
        st.metric("Танланган синфдагилар", len(filtered_df))
    with col3:
        st.metric("Тизим ҳолати", "Барқарор 🟢")
