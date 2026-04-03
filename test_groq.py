import streamlit as st
from groq import Groq
from sqlalchemy import create_engine, text
import sqlite3
import pandas as pd
from datetime import datetime
import re
import excel_engine  # Το βοηθητικό αρχείο για Excel

# -------- CONFIG & API KEY SETTINGS --------
st.set_page_config(page_title="AI Data Assistant", layout="wide")

# Προεπιλεγμένο κλειδί (το δικό σου)
DEFAULT_GROQ_KEY = ""

st.sidebar.title("🔑 API Settings")
user_api_key = st.sidebar.text_input(
    "Enter Groq API Key", 
    value=DEFAULT_GROQ_KEY, 
    type="password",
    help="Αν έχετε δικό σας κλειδί Groq, εισάγετε το εδώ. Αλλιώς χρησιμοποιείται το προεπιλεγμένο."
)

# Αρχικοποίηση του Client με το κλειδί από το UI
if user_api_key:
    client = Groq(api_key=user_api_key)
else:
    st.error("⚠️ Παρακαλώ εισάγετε ένα API Key για να συνεχίσετε.")
    st.stop()

# -------- SECURITY CHECK --------
def is_safe_query(sql):
    sql_upper = sql.upper().strip()
    
    # Πρέπει να ξεκινάει υποχρεωτικά με SELECT
    if not sql_upper.startswith("SELECT"):
        return False
        
    # Απαγορευμένες λέξεις που τροποποιούν δεδομένα
    forbidden = ["DELETE", "UPDATE", "INSERT", "DROP", "ALTER", "CREATE", "TRUNCATE", "REPLACE"]
    for word in forbidden:
        # Έλεγχος αν η λέξη υπάρχει ως αυτόνομη (όχι μέσα σε άλλη λέξη)
        if re.search(r'\b' + word + r'\b', sql_upper):
            return False
    return True

# -------- DATABASE FUNCTIONS --------
@st.cache_data
def get_db_schema(_engine, _db_mode, _db_path):
    if _engine is None: return ""
    schema = ""
    try:
        if _db_mode == "SQLite":
            conn = sqlite3.connect(_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name})")
                col_names = [col[1] for col in cursor.fetchall()]
                schema += f"\n{table_name}({', '.join(col_names)})"
            conn.close()
        else: # MySQL
            with _engine.connect() as conn:
                query = text("SELECT table_name, column_name FROM information_schema.columns WHERE table_schema = DATABASE()")
                rows = conn.execute(query).fetchall()
                tables_dict = {}
                for t, c in rows:
                    if t not in tables_dict: tables_dict[t] = []
                    tables_dict[t].append(c)
                for t, cols in tables_dict.items():
                    schema += f"\n{t}({', '.join(cols)})"
    except Exception as e: 
        schema = f"Error loading schema: {e}"
    return schema

# -------- SIDEBAR: DATA SOURCE --------
st.sidebar.divider()
st.sidebar.title("⚙️ Data Configuration")
db_mode = st.sidebar.radio("Select Source Type:", ["SQLite", "MySQL", "Excel"])

engine = None
DB_PATH = None
excel_file = None
db_schema = ""

if db_mode == "SQLite":
    uploaded_db = st.sidebar.file_uploader("Upload SQLite (.db)", type=["db", "sqlite"])
    if uploaded_db:
        with open("temp_db.db", "wb") as f: 
            f.write(uploaded_db.getbuffer())
        DB_PATH = "temp_db.db"
        engine = create_engine(f"sqlite:///{DB_PATH}")
        db_schema = get_db_schema(engine, "SQLite", DB_PATH)

elif db_mode == "Excel":
    excel_file = st.sidebar.file_uploader("Upload Excel (.xlsx, .xls)", type=["xlsx", "xls"])
    if excel_file:
        db_schema = excel_engine.get_excel_schema(excel_file)
        st.sidebar.success("✅ Excel Loaded Successfully!")

else: # MySQL
    h = st.sidebar.text_input("Host")
    u = st.sidebar.text_input("User")
    p = st.sidebar.text_input("Password", type="password")
    n = st.sidebar.text_input("Database Name")
    if h and u and n:
        try:
            engine = create_engine(f"mysql+mysqlconnector://{u}:{p}@{h}/{n}")
            db_schema = get_db_schema(engine, "MySQL", None)
        except Exception as e:
            st.sidebar.error(f"Connection Error: {e}")

# -------- MAIN UI --------
st.title("🤖 AI Data Assistant")
st.info("Ρωτήστε την AI για τα δεδομένα σας (SQLite, MySQL ή Excel)")

if db_schema:
    with st.expander("📊 Προβολή Δομής Δεδομένων (Schema)"):
        st.code(db_schema)
else:
    st.warning("Παρακαλώ συνδέστε μια πηγή δεδομένων από το sidebar για να ξεκινήσετε.")

# Είσοδος χρήστη
question = st.chat_input("π.χ. Ποιες ήταν οι συνολικές πωλήσεις τον προηγούμενο μήνα;")

if question and db_schema:
    st.chat_message("user").write(question)
    
    # Προετοιμασία Prompt για την AI
    today = datetime.now().strftime('%Y-%m-%d')
    prompt = f"""
    You are a professional SQL expert.
    Current date: {today}.
    
    Database Schema:
    {db_schema}
    
    Instructions:
    1. If the source is Excel, the table name is always 'data'.
    2. Use standard SQL syntax. 
    3. For relative dates (yesterday, last month), use appropriate SQL functions.
    4. Return ONLY the raw SQL SELECT query. Do not include markdown code blocks or explanations.
    
    Question: {question}
    """

    try:
        # 1. Κλήση στην Groq
        with st.spinner("Η AI επεξεργάζεται την ερώτηση..."):
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
        
        # Καθαρισμός του query από τυχόν περιττά σύμβολα
        sql = res.choices[0].message.content.replace("```sql", "").replace("```", "").strip()
        
        st.chat_message("assistant").write("χμμμμ νομίζω το βρήκα:")
        st.code(sql, language="sql")

        # 2. Έλεγχος Ασφαλείας και Εκτέλεση
        if is_safe_query(sql):
            if db_mode == "Excel":
                # Εκτέλεση μέσω του excel_engine
                result_df = excel_engine.query_excel(excel_file, sql)
                if isinstance(result_df, str): 
                    st.error(result_df)
                else: 
                    st.write("📈 Αποτελέσματα:")
                    st.dataframe(result_df, use_container_width=True)
            else:
                # Εκτέλεση σε SQLite ή MySQL
                with engine.connect() as conn:
                    df = pd.read_sql(text(sql), conn)
                    st.write("📈 Αποτελέσματα:")
                    st.dataframe(df, use_container_width=True)
        else:
            st.error("❌ Η εντολή ακυρώθηκε για λόγους ασφαλείας. Επιτρέπονται μόνο εντολές SELECT.")
            
    except Exception as e:
        st.error(f"Παρουσιάστηκε σφάλμα: {e}")