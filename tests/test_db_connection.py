import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import asyncio
from urllib.parse import urlparse
import ssl

# Charger les variables d'environnement
load_dotenv()

# Chemins
ROOT_DIR = Path(__file__).parent.parent
CA_PATH = ROOT_DIR / "ca.pem"

# Récupérer les variables d'environnement
DB_URL = os.getenv("DB_URL")

def get_async_url():
    """Crée une URL propre pour asyncpg"""
    parsed = urlparse(DB_URL)
    return f"postgresql+asyncpg://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port}/{parsed.path.lstrip('/')}"

def create_ssl_context():
    """Crée un contexte SSL avec le certificat CA"""
    ssl_context = ssl.create_default_context(
        purpose=ssl.Purpose.SERVER_AUTH,
        cafile=str(CA_PATH)
    )
    return ssl_context

def test_sync_connection():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute('SELECT version();')
        version = cur.fetchone()[0]
        print("✅ Connexion synchrone réussie!")
        print(f"Version PostgreSQL: {version}")
        cur.close()
        conn.close()
        return True
    except psycopg2.Error as e:
        print("❌ Erreur de connexion synchrone:")
        print(e)
        return False

async def test_async_connection():
    engine = None
    try:
        # Vérifier que le certificat existe
        if not CA_PATH.exists():
            raise FileNotFoundError(f"Certificat CA non trouvé: {CA_PATH}")
            
        # Créer le contexte SSL avec le certificat
        ssl_context = create_ssl_context()
        
        # Créer le moteur asynchrone
        engine = create_async_engine(
            get_async_url(),
            echo=True,
            connect_args={
                "ssl": ssl_context
            }
        )
        
        # Tester la connexion
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version();"))
            version = result.scalar()
            print("✅ Connexion asynchrone réussie!")
            print(f"Version PostgreSQL: {version}")
            
            # Test supplémentaire - liste des tables
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public';
            """))
            tables = result.scalars().all()
            if tables:
                print("\nTables trouvées:")
                for table in tables:
                    print(f"- {table}")
            else:
                print("\nAucune table trouvée dans le schéma public")
            
            return True
            
    except ImportError as e:
        print("❌ Erreur: Module manquant")
        print("Installez asyncpg avec: pip install asyncpg")
        return False
    except FileNotFoundError as e:
        print("❌ Erreur: Certificat CA")
        print(e)
        print("\nAssurez-vous que le fichier ca.pem est présent à la racine du projet")
        return False
    except Exception as e:
        print("❌ Erreur de connexion asynchrone:")
        print(e)
        print("\nDétails:")
        print(f"URL utilisée: {get_async_url()}")
        print(f"Certificat CA: {CA_PATH}")
        return False
    finally:
        if engine:
            await engine.dispose()

if __name__ == "__main__":
    print("\n=== Test de connexion synchrone ===")
    test_sync_connection()
    
    print("\n=== Test de connexion asynchrone ===")
    try:
        asyncio.run(test_async_connection())
    except ImportError:
        print("\n⚠️ Pour utiliser la connexion asynchrone, installez asyncpg:")
        print("pip install asyncpg")