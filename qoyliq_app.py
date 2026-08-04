import streamlit as st
import pandas as pd
import datetime

# Ортиқча қора панел ва Streamlit элементларини тўлиқ яшириш (блокировка)
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Саҳифа кенглиги
st.set_page_config(page_title="ПС Қўйлиқ - Оператор", layout="wide")

st.title("⚡ ПС 220/110/6 кВ «Қўйлиқ» - Оператор Панели")

# Оператор учун кириш пароли
st.sidebar.header("🔐 Оператор тизими")
operator_pass = st.sidebar.text_input("Оператор паролини киритинг:", type="password", value="")

# Паролни текшириш (Оператор учун пароль: 8080 ёки operator2026)
if operator_pass != "8080" and operator_pass != "operator2026":
    st.warning("⚠️ Илтимос, ишлашни бошлаш учун оператор паролини киритинг! (Пароль: 8080)")
    st.stop()

st.sidebar.success("✅ Оператор ҳуқуқи билан кирдингиз!")

# Намунавий маълумотлар базаси (Ускуналар)
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        "Ускуна номи": [
            "Трансформатор AT-1 (220 кВ)", 
            "Трансформатор T-2 (110 кВ)", 
            "6кВ Секция ва Мос қурилма №11", 
            "6кВ Секция ва Мос қурилма №12"
        ],
        "Кучланиш": ["220 kV", "110 kV", "6 kV", "6 kV"],
        "Жорий ҳолати": ["Ишда", "Ишда", "Резервда", "Ишда"],
        "Охирги текширув": [str(datetime.date.today()), str(datetime.date.today()), str(datetime.date.today()), str(datetime.date.today())],
        "Оператор изоҳи": ["Норма", "Норма", "Текширилди", "Норма"]
    })

# Кучланиш синфини танлаш
voltage_group = st.selectbox("Энг аввал кучланиш синфини танланг:", ["Барчаси", "220 kV", "110 kV", "35 kV", "6 kV"])

# Фильтрлаш
df = st.session_state.data
if voltage_group != "Барчаси":
    df = df[df["Кучланиш"] == voltage_group]

st.subheader(f"📊 Ускуналар рўйхати: {voltage_group}")
st.dataframe(df, use_container_width=True)

# Оператор учун маълумот киритиш ва ўзгартириш бўлими
st.markdown("---")
st.subheader("✍️ Оператив маълумот қўшиш ва янгилаш")

with st.form("operator_form"):
    selected_device = st.selectbox("Ускунани танланг:", df["Ускуна номи"].tolist() if not df.empty else ["Маълумот йўқ"])
    new_status = st.selectbox("Ускуна ҳолати:", ["Ишда", "Резервда", "Таъмирда", "Авария ҳолатида"])
    operator_comment = st.text_area("Оператор изоҳи / Кўрсаткичлар:")
    
    submit_btn = st.form_submit_button("💾 Маълумотни сақлаш")
    
    if submit_btn:
        # Танланган ускуна ҳолатини янгилаш
        st.session_state.data.loc[st.session_state.data["Ускуна номи"] == selected_device, "Жорий ҳолати"] = new_status
        st.session_state.data.loc[st.session_state.data["Ускуна номи"] == selected_device, "Охирги текширув"] = str(datetime.date.today())
        st.session_state.data.loc[st.session_state.data["Ускуна номи"] == selected_device, "Оператор изоҳи"] = operator_comment
        
        st.success(f"✅ «{selected_device}» бўйича маълумот муваффақиятли сақланди!")
        st.rerun()
