import streamlit as st
import pandas as pd
import datetime

# Ортиқча панелларни яшириш
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.set_page_config(page_title="ПС Қўйлиқ - Оператор", layout="wide")

st.title("⚡ ПС 220/110/6 кВ «Қўйлиқ» - Оператор Панели")

# Паролни тўғридан-тўғри асосий экранга чиқарамиз (сайдбарсиз)
st.markdown("### 🔐 Ишлашни бошлаш учун паролни киритинг:")
operator_pass = st.text_input("Оператор пароли:", type="password", value="")

if operator_pass != "8080" and operator_pass != "operator2026":
    st.warning("⚠️ Илтимос, давом этиш учун оператор паролини киритинг! (Пароль: 8080)")
    st.stop()

st.success("✅ Оператор ҳуқуқи билан кирдингиз!")

# Тўлиқ ускуналар базаси (Қўйлиқ ПС асосий қурилмалари)
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        "Ускуна номи": [
            "Автотрансформатор АТ-1 (220/110/10 кВ)",
            "Автотрансформатор АТ-2 (220/110/10 кВ)",
            "Трансформатор Т-3 (110/6 кВ)",
            "Трансформатор Т-4 (110/6 кВ)",
            "Ҳаво линияси Л-220 кВ «Қўйлиқ-1»",
            "Ҳаво линияси Л-220 кВ «Қўйлиқ-2»",
            "Очиқ тақсимлаш қурилмаси ОРУ-220 кВ ўчиргичи",
            "Ёпиқ тақсимлаш қурилмаси ЗРУ-6 кВ №1 секция",
            "Ёпиқ тақсимлаш қурилмаси ЗРУ-6 кВ №2 секция",
            "6кВ Секция ва Мос қурилма №11",
            "6кВ Секция ва Мос қурилма №12",
            "6кВ Секция ва Мос қурилма №13",
            "6кВ Секция ва Мос қурилма №14",
            "6кВ Секция ва Мос қурилма №15",
            "6кВ Секция ва Мос қурилма №16",
            "6кВ Секция ва Мос қурилма №17"
        ],
        "Кучланиш": [
            "220 kV", "220 kV", "110 kV", "110 kV", 
            "220 kV", "220 kV", "220 kV", "6 kV", 
            "6 kV", "6 kV", "6 kV", "6 kV", 
            "6 kV", "6 kV", "6 kV", "6 kV"
        ],
        "Жорий ҳолати": ["Ишда"] * 16,
        "Параметр / Юклама": ["Норма"] * 16,
        "Охирги текширув": [str(datetime.date.today())] * 16,
        "Оператор изоҳи": ["Барча кўрсаткичлар жойида"] * 16
    })

# Кучланиш синфини танлаш фильтри
voltage_group = st.selectbox("Энг аввал кучланиш синфини танланг:", ["Барчаси", "220 kV", "110 kV", "35 kV", "6 kV"])

df = st.session_state.data
if voltage_group != "Барчаси":
    df = df[df["Кучланиш"] == voltage_group]

st.subheader(f"📊 Ускуналар рўйхати: {voltage_group}")
st.dataframe(df, use_container_width=True)

# Кенгайтирилган маълумот киритиш формати
st.markdown("---")
st.subheader("✍️ Оператив маълумот қўшиш ва параметрларни янгилаш")

with st.form("operator_form"):
    selected_device = st.selectbox("Ускунани танланг:", df["Ускуна номи"].tolist() if not df.empty else ["Маълумот йўқ"])
    
    col1, col2 = st.columns(2)
    with col1:
        new_status = st.selectbox("Ускуна ҳолати:", ["Ишда", "Резервда", "Жорий таъмирда", "Авария ҳолатида"])
    with col2:
        device_param = st.text_input("Параметр / Юклама / Ҳарорат:", value="Норма (оқим барқарор)")
        
    operator_comment = st.text_area("Оператор журналы учун батафсил изоҳ:")
    
    submit_btn = st.form_submit_button("💾 Маълумотни базага сақлаш")
    
    if submit_btn:
        st.session_state.data.loc[st.session_state.data["Ускуна номи"] == selected_device, "Жорий ҳолати"] = new_status
        st.session_state.data.loc[st.session_state.data["Ускуна номи"] == selected_device, "Параметр / Юклама"] = device_param
        st.session_state.data.loc[st.session_state.data["Ускуна номи"] == selected_device, "Охирги текширув"] = str(datetime.date.today())
        st.session_state.data.loc[st.session_state.data["Ускуна номи"] == selected_device, "Оператор изоҳи"] = operator_comment
        
        st.success(f"✅ «{selected_device}» бўйича оператив маълумотлар муваффақиятли янгиланди!")
        st.rerun()
