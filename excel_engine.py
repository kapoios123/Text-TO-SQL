import pandas as pd
from sqlalchemy import create_engine, MetaData
import re

def clean_name(text):
    """Γενικός καθαρισμός για ονόματα πινάκων και στηλών"""
    clean = str(text).strip().replace(' ', '_')
    clean = re.sub(r'[^a-zA-Z0-9_]', '', clean)
    return clean if clean else "item"

def load_multiple_files(files, engine):
    """Φορτώνει όλα τα αρχεία ΚΑΙ όλα τα φύλλα τους στη βάση"""
    schema_info = []
    
    # Καθαρισμός προηγούμενης μνήμης
    metadata = MetaData()
    metadata.reflect(bind=engine)
    metadata.drop_all(bind=engine)
    
    for file in files:
        file_name_clean = clean_name(file.name.split('.')[0].lower())
        
        if file.name.lower().endswith('.csv'):
            # Τα CSV έχουν μόνο ένα "φύλλο"
            datasets = {file_name_clean: pd.read_csv(file)}
        else:
            # Διάβασμα όλων των φύλλων του Excel (sheet_name=None)
            all_sheets = pd.read_excel(file, sheet_name=None)
            datasets = {}
            for sheet_name, df in all_sheets.items():
                # Συνδυάζουμε όνομα αρχείου και όνομα φύλλου για το όνομα του πίνακα
                full_table_name = f"{file_name_clean}_{clean_name(sheet_name).lower()}"
                datasets[full_table_name] = df

        for table_name, df in datasets.items():
            # Καθαρισμός στηλών με προστασία διπλοτύπων
            new_cols = []
            seen_cols = {}
            for col in df.columns:
                c = clean_name(col)
                if c in seen_cols:
                    seen_cols[c] += 1
                    c = f"{c}_{seen_cols[c]}"
                else:
                    seen_cols[c] = 0
                new_cols.append(c)
            
            df.columns = new_cols
            
            # Ανέβασμα στη βάση
            df.to_sql(table_name, engine, index=False, if_exists='replace')
            
            # Προσθήκη στο schema
            schema_info.append(f"{table_name}({', '.join(df.columns)})")
    
    return " | ".join(schema_info)

def query_db(engine, query):
    try:
        with engine.connect() as conn:
            return pd.read_sql(pd.io.sql.text(query), conn)
    except Exception as e:
        return f"SQL Error: {str(e)}"
