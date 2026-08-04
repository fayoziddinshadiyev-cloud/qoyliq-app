import streamlit as st
import pandas as pd
import datetime

# Ортиқча панелларни яшириш
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="ПС Қўйлиқ - Оператор", layout="wide")

st.title("⚡ ПС 220/110/6 кВ «Қўйлиқ» - Оператор Панели")

# Паролни экраннинг ўзида сўраймиз (бошқарув панелисиз)
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("### 🔐 Тизимга кириш учун паролни киритинг:")
    password_input = st.text_input("Пароль:", type="password")
    
    if st.button("🔓 Кириш"):
        if password_input == "8080" or password_input == "operator2026":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Пароль нотўғри! Қайтадан уриниб кўринг (Пароль: 8080)")
    st.stop()

st.success("✅ Тизимга муваффақиятли кирдингиз!")

# Намунавий маълумотлар базаси
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

# Маълумот киритиш қисми
st.markdown("---")
st.subheader("✍️ Оператив маълумот қўшиш ва янгилаш")

with st.form("operator_form"):
    selected_device = st.selectbox("Ускунани танланг:", df["Ускуна номи"].tolist() if not df.empty else ["Маълумот йўқ"])
    new_status = st.selectbox("Ускуна ҳолати:", ["Ишда", "Резервда", "Таъмирда", "Авария ҳолатида"])
    operator_comment = st.text_area("Оператор изоҳи / Кўрсаткичлар:")
    
    submit_btn = st.form_submit_button("💾 Маълумотни сақлаш")
    
    if submit_btn:
        st.session_state.data.loc[st.session_state.data["Ускуна номи"] == selected_device, "Жорий ҳолати"] = new_status
        st.session_state.data.loc[st.session_state.data["Ускуна номи"] == selected_device, "Охирги текширув"] = str(datetime.date.today())
        st.session_state.data.loc[st.session_state.data["Ускуна номи"] == selected_device, "Оператор изоҳи"] = operator_comment
        
        st.success(f"✅ «{selected_device}» бўйича маълумот муваффақиятли сақланди!")
        st.rerun()
