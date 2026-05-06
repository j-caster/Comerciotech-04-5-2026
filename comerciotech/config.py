"""
Configuración y conexión a MongoDB
Responsable: Establecer y gestionar la conexión con la base de datos
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv
import os  # ✅ Importante: necesario para os.getenv()

# Cargar variables del archivo .env
load_dotenv()


class MongoDBConnection:
    """Gestor de conexión a MongoDB"""
    
    def __init__(self, host=None, port=None, database=None):
        # Usar variables de entorno o valores por defecto
        self.host = host or os.getenv('MONGO_HOST', 'localhost')
        self.port = port or int(os.getenv('MONGO_PORT', 27017))
        self.database_name = database or os.getenv('MONGO_DATABASE', 'comerciotech')
        
        # Leer credenciales desde variables de entorno
        self.user = os.getenv('MONGO_USER')
        self.password = os.getenv('MONGO_PASSWORD')
        
        self.client = None
        self.db = None
    
    def connect(self):
        """Establece la conexión con MongoDB"""
        try:
            # Verificar que existan las credenciales
            if not self.user or not self.password:
                print("⚠️ ADVERTENCIA: Credenciales no configuradas en .env")
                print("   Usando conexión sin autenticación")
                uri = f"mongodb://{self.host}:{self.port}/"
            else:
                # ✅ URI con autenticación usando variables de entorno
                uri = f"mongodb://{self.user}:{self.password}@{self.host}:{self.port}/{self.database_name}?authSource=admin"
            
            self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            print(f"✅ Conectado a MongoDB en {self.host}:{self.port}")
            print(f"📁 Base de datos: {self.database_name}")
            print(f"👤 Usuario: {self.user or 'sin autenticación'}")
            return self.db
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"❌ Error de conexión: {e}")
            return None
    
    def disconnect(self):
        """Cierra la conexión"""
        if self.client:
            self.client.close()
            print("🔌 Conexión cerrada")


def get_collection(db, collection_name):
    """Obtiene una colección, creándola si no existe"""
    return db[collection_name]


def conectar_mongodb_simple():
    """Conexión simple para scripts rápidos"""
    try:
        host = os.getenv('MONGO_HOST', 'localhost')
        port = int(os.getenv('MONGO_PORT', 27017))
        
        cliente = MongoClient(f'mongodb://{host}:{port}/')
        cliente.admin.command('ping')
        db = cliente[os.getenv('MONGO_DATABASE', 'comerciotech')]
        print("✅ Conexión exitosa a MongoDB")
        return db
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None