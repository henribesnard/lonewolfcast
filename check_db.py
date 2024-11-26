from sqlalchemy import create_engine, inspect
import sqlite3

def check_sqlite_db():
    # Vérifier le fichier SQLite
    try:
        conn = sqlite3.connect('data/football.db')
        cursor = conn.cursor()
        
        # Lister toutes les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("Tables trouvées dans la base SQLite:")
        for table in tables:
            print(f"- {table[0]}")
            
            # Compter les enregistrements
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  Nombre d'enregistrements: {count}")
            
            # Lister les colonnes
            cursor.execute(f"PRAGMA table_info({table[0]})")
            columns = cursor.fetchall()
            print("  Colonnes:")
            for col in columns:
                print(f"    - {col[1]} ({col[2]})")
                
        conn.close()
        print("\nVérification terminée avec succès!")
        
    except Exception as e:
        print(f"Erreur lors de la vérification: {str(e)}")

if __name__ == "__main__":
    check_sqlite_db()