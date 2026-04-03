import pandas as pd
from sqlalchemy import create_engine

def load_data(file):
    """Βοηθητική συνάρτηση για να διαβάζει είτε Excel είτε CSV"""
    file_details = file.name.lower()
    if file_details.endswith('.csv'):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

def query_excel(file, query):
    try:
        # Χρησιμοποιούμε τη νέα συνάρτηση load_data
        df = load_data(file)
        
        # Καθαρισμός στηλών (για να μην χτυπάει η SQL)
        df.columns = [c.replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_') for c in df.columns]
        
        engine = create_engine('sqlite:///', echo=False)
        df.to_sql('data', engine, index=False)
        
        with engine.connect() as conn:
            return pd.read_sql(query, conn)
    except Exception as e:
        return f"Σφάλμα ανάγνωσης: {str(e)}"

def get_excel_schema(file):
    try:
        # Χρησιμοποιούμε τη νέα συνάρτηση load_data
        df = load_data(file)
        cols = [c.replace(' ', '_').replace('-', '_') for c in df.columns]
        return "data(" + ", ".join(cols) + ")"
    except Exception as e:
        return f"Error reading schema: {str(e)}"