import streamlit as st
import pg8000.dbapi as pg8000
import os

# ============================================================================
# ПС «ҚЎЙЛИҚ» — Муҳандислик Бошқарув ва Синов Маркази (Streamlit версияси)
# ============================================================================

st.set_page_config(
    page_title="ПС Қўйлиқ - Жонли База",
    page_icon="⚡",
    layout="wide"
)

# PostgreSQL уланиш созламалари
DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": int(os.environ.get("PGPORT", "5432")),
    "database": os.environ.get("PGDATABASE", "elektroekspert"),
    "user": os.environ.get("PGUSER", "postgres"),
    "password": os.environ.get("PGPASSWORD", "12345"),
}

SUBSTATION_ID = 5  # ПС Куйлик

@st.cache_resource
def get_conn():
    return pg8000.connect(**DB_CONFIG)

# Сарлавҳа
st.title("⚡ ПС ҚЎЙЛИҚ ПОДСТАНЦИЯСИ")
st.markdown("**elektroekspert (PostgreSQL)** базасига жонли уланиш ва ускуналар параметрларини кучланиш синфлари бўйича саралаш.")

try:
    conn = get_conn()
except Exception as e:
    st.error(f"PostgreSQL базасига уланиб бўлмади: {e}")
    st.stop()

# Ролни танлаш
role = st.sidebar.selectbox("Тизимдаги ролингизни танланг:", ["Мухандис", "Администратор", "Оператор"])

# Кучланиш синфлари бўйича маълумотларни олиш
try:
    cur = conn.cursor()
    cur.execute("""
        SELECT vl.id, vl.voltage_kv, count(se.id)
        FROM voltage_levels vl
        LEFT JOIN substation_equipment se ON se.voltage_level_id = vl.id AND se.substation_id = %s
        GROUP BY vl.id, vl.voltage_kv
        ORDER BY vl.voltage_kv DESC;
    """, (SUBSTATION_ID,))
    voltage_rows = cur.fetchall()
    cur.close()
except Exception as e:
    st.error(f"Сўров хатоси: {e}")
    st.stop()

if not voltage_rows:
    st.warning("Кучланиш синфлари топилмади.")
    st.stop()

# Фойдаланувчига кучланиш бўйича танлов бериш
st.subheader("1. Кучланиш синфини танланг:")
voltage_options = {f"{float(kv):g} кВ ускуналари ({cnt} та)": vl_id for vl_id, kv, cnt in voltage_rows}
selected_option = st.radio("Кучланишни танланг:", list(voltage_options.keys()))

selected_vl_id = voltage_options[selected_option]

# Танланган кучланишдаги ускуналарни жадвал кўринишида чиқариш
st.markdown("---")
st.subheader(f"2. Ускуналар рўйхаti ({selected_option})")

try:
    cur = conn.cursor()
    cur.execute("""
        SELECT se.id, se.bay_name, se.asset_tag,
               COALESCE(et.category, '-') AS category,
               COALESCE(et.type_name, '-') AS type_name,
               se.verification_status
        FROM substation_equipment se
        LEFT JOIN equipment_models em ON em.id = se.equipment_model_id
        LEFT JOIN equipment_types et ON et.id = em.equipment_type_id
        WHERE se.substation_id = %s AND se.voltage_level_id = %s
        ORDER BY se.bay_name;
    """, (SUBSTATION_ID, selected_vl_id))
    equipment_rows = cur.fetchall()
    cur.close()
except Exception as e:
    st.error(f"Ускуналарни ўқишда хатолик: {e}")
    equipment_rows = []

if equipment_rows:
    import pandas as pd
    df = pd.DataFrame(equipment_rows, columns=["ID", "Ячейка / фидер номи", "Asset tag", "Тоифаси", "Тури / модели", "Ҳолати"])
    st.dataframe(df, use_container_width=True)
else:
    st.info("Бу кучланиш синфида ускуналар топилмади.")

st.markdown("---")
st.caption("ПС Қўйлиқ | Муҳандислик Бошқарув ва Синов Маркази")
