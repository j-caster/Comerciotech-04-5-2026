"""
Configuración y conexión a MongoDB
Responsable: Establecer y gestionar la conexión con la base de datos
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError


class MongoDBConnection:
    """Gestor de conexión a MongoDB"""
    
    def __init__(self, host='localhost', port=27017, database='comerciotech'):
        self.host = host
        self.port = port
        self.database_name = database
        self.client = None
        self.db = None
    
    def connect(self):
        """Establece la conexión con MongoDB"""
        try:
            uri = f"mongodb://admin_comerciotech:Admin12345@{self.host}:{self.port}/{self.database_name}?authSource=admin"
            self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            print(f"✅ Conectado a MongoDB en {self.host}:{self.port}")
            print(f"📁 Base de datos: {self.database_name}")
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
        cliente = MongoClient('mongodb://localhost:27017/')
        cliente.admin.command('ping')
        db = cliente['comerciotech']
        print("✅ Conexión exitosa a MongoDB")
        return db
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None