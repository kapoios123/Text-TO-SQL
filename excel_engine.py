import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import create_engine, MetaData, Table
import re

def clean_table_name(filename):
    """Μετατρέπει το όνομα του αρχείου σε έγκυρο όνομα πίνακα SQL"""
    # Παίρνουμε μόνο το όνομα χωρίς την κατάληξη
    name = filename.split('.')[0].lower()
    return re.sub(r'[^a-z0-9_]', '_', name)
    # Κρατάμε μόνο γράμματα, αριθμούς και underscores
    clean_name = re.sub(r'[^a-z0-9_]', '_', name)
    # Αποφεύγουμε πολλαπλά underscores
    clean_name = re.sub(r'_+', '_', clean_name).strip('_')
    return clean_name if clean_name else "table_data"

def load_multiple_files(files, engine):
    """Φορτώνει πολλά αρχεία στην ίδια βάση δεδομένων με προστασία διπλότυπων στηλών"""
    """Φορτώνει πολλά αρχεία καθαρίζοντας την προηγούμενη μνήμη της SQLAlchemy"""
    schema_info = []
    
    # ΚΑΘΑΡΙΣΜΟΣ: Διαγράφουμε τα πάντα από την προηγούμενη συνεδρία 
    # για να μην πετάει ArgumentError η SQLAlchemy
    metadata = MetaData()
    metadata.reflect(bind=engine)
    metadata.drop_all(bind=engine)
    
    for file in files:
        table_name = clean_table_name(file.name)
        
        # Αναγνώριση τύπου αρχείου
        if file.name.lower().endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        # Νέα λογική καθαρισμού με προστασία διπλοτύπων
        # Καθαρισμός στηλών με προστασία διπλοτύπων
        new_cols = []
        seen_cols = {}

        for col in df.columns:
            # Βασικός καθαρισμός: κενά σε κάτω παύλες και αφαίρεση ειδικών χαρακτήρων
            # Βασικός καθαρισμός ονόματος στήλης
            clean_col = str(col).strip().replace(' ', '_')
            clean_col = re.sub(r'[^a-zA-Z0-9_]', '', clean_col)

            # Αν το όνομα υπάρχει ήδη, πρόσθεσε αριθμό (π.χ. Price_1, Price_2)
            if not clean_col: clean_col = "column"
            
            # Αν το όνομα υπάρχει ήδη, πρόσθεσε αριθμό
            if clean_col in seen_cols:
                seen_cols[clean_col] += 1
                clean_col = f"{clean_col}_{seen_cols[clean_col]}"
            else:
                seen_cols[clean_col] = 0

            new_cols.append(clean_col)

        df.columns = new_cols

        # Ανέβασμα στη βάση
        # Ανέβασμα στη βάση - if_exists='replace'
        df.to_sql(table_name, engine, index=False, if_exists='replace')

        # Προσθήκη στο schema string
        schema_info.append(f"{table_name}({', '.join(df.columns)})")

    return " | ".join(schema_info)

def query_db(engine, query):
    """Εκτελεί το query στη μνήμη"""
    try:
        with engine.connect() as conn:
            return pd.read_sql(query, conn)
    except Exception as e:
        return f"SQL Error: {str(e)}"
