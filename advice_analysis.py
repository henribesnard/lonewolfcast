import sqlite3
import csv
from pathlib import Path
from datetime import datetime

def analyze_prediction_advice_categories():
    """
    Extrait les différentes catégories de conseils (partie avant les ':') 
    depuis la table Prediction et les sauvegarde dans un CSV
    """
    try:
        # Connexion à la base de données
        conn = sqlite3.connect('data/football.db')
        cursor = conn.cursor()
        
        # Requête pour obtenir les catégories d'advice avec leur fréquence
        query = """
        SELECT 
            TRIM(substr(advice, 1, instr(advice, ':') - 1)) as category,
            COUNT(*) as count
        FROM predictions 
        WHERE advice IS NOT NULL 
            AND advice LIKE '%:%'
        GROUP BY TRIM(substr(advice, 1, instr(advice, ':') - 1))
        ORDER BY count DESC;
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Créer le fichier CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = Path('dataset') / f"advice_categories_{timestamp}.csv"
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['category', 'count'])  # Headers
            writer.writerows(results)
        
        print(f"\nAnalyse terminée!")
        print(f"Nombre total de catégories uniques: {len(results)}")
        print(f"Fichier CSV créé: {csv_path}")
        
        # Afficher un aperçu
        print("\nAperçu des catégories de conseils les plus fréquentes:")
        for category, count in results[:5]:
            print(f"- {category}: {count}")
            
    except Exception as e:
        print(f"Erreur lors de l'analyse: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    analyze_prediction_advice_categories()