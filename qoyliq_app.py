import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Қўйлиқ подстанцияси - Маълумотлар базаси",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Қўйлиқ подстанцияси юқори кучланишли жиҳозлари")
st.markdown("Ушбу веб-илова юқори кучланишли қурилмаларнинг параметрлари ва маълумотларини кузатиб бориш учун мўлжалланган.")

st.sidebar.header("Бошқарув панели")
menu = st.sidebar.selectbox(
    "Бўлимни танланг:",
    ["Асосий кўриниш", "Жиҳозлар рўйхати", "Маълумот қўшиш"]
)

if menu == "Асосий кўриниш":
    st.subheader("Хуш келибсиз!")
    st.write("Бу ерда подстанция бўйича умумий ҳисоботлар ва кўрсаткичлар жойлашади.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Асосий қурилмалар", value="130+", delta="Назоратда")
    with col2:
        st.metric(label="Трансформаторлар", value="16,000 kVA", delta="Барқарор")
    with col3:
        st.metric(label="Тизим ҳолати", value="Нормал", delta="100%")

elif menu == "Жиҳозлар рўйхати":
    st.subheader("Юқори кучланишли қурилмалар рўйхати")
    st.info("Бу ерда 35-220 кВ ли қурилмаларнинг параметрлари келтирилади.")
    
    data = {
        "Қурилма номи": ["Трансформатор Т-1", "Трансформатор Т-2", "Ўчиргич В-220", "Ажраткич РЛНД"],
        "Кучланиши (кВ)": [220, 110, 220, 35],
        "Ҳолати": ["Ишда", "Ишда", "Резерв", "Ишда"]
    }
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

else:
    st.subheader("Янги маълумот қўшиш")
    with st.form("add_form"):
        device_name = st.text_input("Қурилма номи")
        voltage = st.selectbox("Кучланиши (кВ)", [35, 110, 220, 500])
        status = st.selectbox("Ҳолати", ["Ишда", "Резерв", "Таъмирда"])
        submit = st.form_submit_button("Сақлаш")
        
        if submit:
            st.success(f"'{device_name}' муваффақиятли қўшилди!")
