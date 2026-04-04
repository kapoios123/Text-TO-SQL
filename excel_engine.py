import pandas as pd
from sqlalchemy import create_engine
import re

def clean_table_name(filename):
    """Μετατρέπει το όνομα του αρχείου σε έγκυρο όνομα πίνακα SQL"""
    name = filename.split('.')[0].lower()
    return re.sub(r'[^a-z0-9_]', '_', name)

def load_multiple_files(files, engine):
    """Φορτώνει πολλά αρχεία στην ίδια βάση δεδομένων"""
    schema_info = []
    for file in files:
        table_name = clean_table_name(file.name)
        if file.name.lower().endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
            
        # Καθαρισμός στηλών
        df.columns = [re.sub(r'[^a-zA-Z0-9_]', '_', c.strip()) for c in df.columns]
        
        # Ανέβασμα στη βάση
        df.to_sql(table_name, engine, index=False, if_exists='replace')
        
        # Προσθήκη στο schema string για την AI
        schema_info.append(f"{table_name}({', '.join(df.columns)})")
    
    return " | ".join(schema_info)

def query_db(engine, query):
    """Εκτελεί το query στη μνήμη"""
    try:
        with engine.connect() as conn:
            return pd.read_sql(query, conn)
    except Exception as e:
        return f"SQL Error: {str(e)}"
