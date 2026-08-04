import streamlit as st
import pandas as pd

# ==========================================
# ПС «ҚЎЙЛИҚ» — Муҳандислик Бошқарув ва Синов Маркази
# ==========================================

st.set_page_config(
    page_title="ПС Қўйлиқ - Жонли База",
    page_icon="⚡",
    layout="wide"
)

# --- 30 ТА ХОДИМ УЧУН ЛОГИН-ПАРОЛЬ ТИЗИМИ ---
def check_password():
    """Қулф тизими: Фақат рухсат этилган ходимлар киради"""
    def password_entered():
        if st.session_state["password"] == "qoyliq2026":  # Пароль
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

# Агар парол тўғри киритилсагина илова очилади
if check_password():

    st.title("⚡ ПС «ҚЎЙЛИҚ» ПОДСТАНЦИЯСИ")
    st.markdown("**elektroekspert** — Маълумотлар базаси ва ускуналар параметрларини кучланиш синфлари бўйича саралаш.")
    st.markdown("---")

    # Маълумотларни тўғридан-тўғри коднинг ўзидан оламиз (файлга ҳожат йўқ!)
    data = {
        "uskuna_nomi": [
            "Трансформатор Т-1", 
            "Трансформатор Т-2", 
            "Выключатель В-110", 
            "Қурилма 35кВ",
            "Автотрансформатор АТ-1",
            "Трансформатор Т-3"
        ],
        "kuvvati": [
            "40000 kVA", 
            "25000 kVA", 
            "Ҳолати соз", 
            "10000 kVA", 
            "125000 kVA", 
            "6300 kVA"
        ],
        "kuchlanish": [
            "220 kV", 
            "110 kV", 
            "110 kV", 
            "35 kV", 
            "220 kV", 
            "35 kV"
        ],
        "holati": [
            "Ишда", 
            "Ремонтда", 
            "Ишда", 
            "Ишда", 
            "Ишда", 
            "Резервда"
        ],
        "sana": [
            "2026-08-04", 
            "2026-08-04", 
            "2026-08-04", 
            "2026-08-04", 
            "2026-08-04", 
            "2026-08-04"
        ]
    }
    
    df = pd.DataFrame(data)

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
