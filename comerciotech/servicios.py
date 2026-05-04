"""
Servicios de negocio - Operaciones CRUD
Capa intermedia entre los controladores y la base de datos
"""

from typing import List, Optional
from bson import ObjectId
from datetime import datetime

from models import ClienteDTO, ProductoDTO, PedidoDTO, ItemPedidoDTO
from utils import Formatter, Validator, Logger

# Logger global
logger = Logger()


class ClienteService:
    """Servicio para operaciones CRUD de Clientes"""
    
    COLLECTION = 'clientes'
    
    def __init__(self, db):
        self.collection = db[self.COLLECTION]

    def listar_todos(self) -> List[ClienteDTO]:
        """Read - Obtener todos los clientes"""
        try:
            clientes = []
            for doc in self.collection.find():
                clientes.append(ClienteDTO.from_dict(doc))
            return clientes
        except Exception as e:
            logger.error(f"Error al listar clientes: {e}")
            return []

    def crear(self, cliente_dto: ClienteDTO) -> Optional[str]:
        """Create - Insertar un nuevo cliente con validación de todos los campos"""
        
        # ✅ VALIDACIÓN DE CAMPOS VACÍOS
        if not Validator.campo_no_vacio(cliente_dto.nombre):
            logger.error("❌ El nombre es obligatorio")
            return None
        
        if not Validator.campo_no_vacio(cliente_dto.email):
            logger.error("❌ El email es obligatorio")
            return None
        
        if not Validator.campo_no_vacio(cliente_dto.telefono):
            logger.error("❌ El teléfono es obligatorio")
            return None
        
        if not Validator.campo_no_vacio(cliente_dto.direccion):
            logger.error("❌ La dirección es obligatoria")
            return None
        
        # ✅ VALIDACIÓN DE FORMATOS
        if not Validator.email(cliente_dto.email):
            logger.error(f"❌ Email inválido: {cliente_dto.email}")
            return None
        
        if not Validator.telefono(cliente_dto.telefono):
            logger.error(f"❌ Teléfono inválido: {cliente_dto.telefono}. Formato requerido: +56 9 XXXX XXXX o +569XXXXXXXX")
            return None
        
        # ✅ VALIDACIÓN DE EMAIL DUPLICADO
        existente = self.collection.find_one({"email": cliente_dto.email})
        if existente:
            logger.error(f"❌ Ya existe un cliente con el email: {cliente_dto.email}")
            return None
        
        try:
            result = self.collection.insert_one(cliente_dto.to_dict())
            logger.success(f"✅ Cliente creado: {cliente_dto.nombre}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"❌ Error al crear cliente: {e}")
            return None
    
    def buscar_por_email(self, email: str) -> Optional[ClienteDTO]:
        """Read - Buscar cliente por email"""
        if not Validator.email(email):
            logger.error(f"Email inválido para búsqueda: {email}")
            return None
        
        try:
            doc = self.collection.find_one({"email": email})
            if doc:
                return ClienteDTO.from_dict(doc)
            return None
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
            return None
    
    def buscar_por_id(self, cliente_id: str) -> Optional[ClienteDTO]:
        """Read - Buscar cliente por ID"""
        try:
            doc = self.collection.find_one({"_id": ObjectId(cliente_id)})
            if doc:
                return ClienteDTO.from_dict(doc)
            return None
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
            return None

    def buscar_por_email_con_id(self, email: str) -> Optional[tuple]:
        """Busca cliente y retorna (id, ClienteDTO)"""
        if not Validator.email(email):
            return None
        try:
            doc = self.collection.find_one({"email": email})
            if doc:
                return (str(doc['_id']), ClienteDTO.from_dict(doc))
            return None
        except Exception as e:
            logger.error(f"Error: {e}")
            return None
    
    def actualizar(self, cliente_id: str, datos: dict) -> bool:
        """Update - Actualizar un cliente"""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(cliente_id)},
                {"$set": datos}
            )
            if result.modified_count > 0:
                logger.success("Cliente actualizado correctamente")
            else:
                logger.warning("No se realizaron cambios")
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error al actualizar: {e}")
            return False
    
    def eliminar(self, cliente_id: str) -> bool:
        """Delete - Eliminar un cliente"""
        try:
            result = self.collection.delete_one({"_id": ObjectId(cliente_id)})
            if result.deleted_count > 0:
                logger.success("Cliente eliminado correctamente")
            else:
                logger.warning("No se encontró el cliente")
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error al eliminar: {e}")
            return False


class ProductoService:
    """Servicio para operaciones CRUD de Productos"""
    
    COLLECTION = 'productos'
    
    def __init__(self, db):
        self.collection = db[self.COLLECTION]
    
    def crear(self, producto_dto: ProductoDTO) -> Optional[str]:
    
        # Validaciones
        if not Validator.sku(producto_dto.sku):
            logger.error(f"❌ SKU inválido: {producto_dto.sku} (formato esperado: XXX-000)")
            return None
        
        # ✅ VALIDACIÓN DE SKU DUPLICADO
        existente = self.collection.find_one({"sku": producto_dto.sku})
        if existente:
            logger.error(f"❌ Ya existe un producto con el SKU: {producto_dto.sku}")
            return None
        
        if not Validator.precio(producto_dto.precio):
            logger.error(f"❌ Precio inválido: {producto_dto.precio}")
            return None
        
        if not Validator.stock(producto_dto.stock):
            logger.error(f"❌ Stock inválido: {producto_dto.stock}")
            return None
        
        try:
            result = self.collection.insert_one(producto_dto.to_dict())
            logger.success(f"✅ Producto creado: {producto_dto.nombre}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"❌ Error al crear producto: {e}")
            return None

    def listar_todos(self) -> List[ProductoDTO]:
        """Read - Obtener todos los productos"""
        try:
            productos = []
            for doc in self.collection.find():
                productos.append(ProductoDTO.from_dict(doc))
            return productos
        except Exception as e:
            logger.error(f"Error al listar productos: {e}")
            return []
    
    def buscar_por_sku(self, sku: str) -> Optional[ProductoDTO]:
        """Read - Buscar producto por SKU"""
        try:
            doc = self.collection.find_one({"sku": sku})
            if doc:
                return ProductoDTO.from_dict(doc)
            return None
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
            return None
    
    def actualizar_stock(self, sku: str, nuevo_stock: int) -> bool:
        """Update - Actualizar stock de un producto"""
        if not Validator.stock(nuevo_stock):
            logger.error(f"Stock inválido: {nuevo_stock}")
            return False
        
        try:
            result = self.collection.update_one(
                {"sku": sku},
                {"$set": {"stock": nuevo_stock}}
            )
            if result.modified_count > 0:
                logger.success(f"Stock actualizado para SKU: {sku}")
            else:
                logger.warning(f"No se encontró el producto con SKU: {sku}")
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error al actualizar stock: {e}")
            return False


class PedidoService:
    """Servicio para operaciones CRUD de Pedidos"""
    
    COLLECTION = 'pedidos'
    
    def __init__(self, db):
        self.collection = db[self.COLLECTION]
        self.cliente_service = ClienteService(db)
    
    def crear(self, email_cliente: str, items: List[dict]) -> Optional[str]:
        """Create - Crear un nuevo pedido"""
        # Validar email del cliente
        if not Validator.email(email_cliente):
            logger.error(f"Email inválido: {email_cliente}")
            return None
        
        # Buscar cliente
        cliente = self.cliente_service.buscar_por_email(email_cliente)
        if not cliente:
            logger.error(f"Cliente no encontrado: {email_cliente}")
            return None
        
        # Validar items
        if not items:
            logger.error("El pedido debe contener al menos un item")
            return None
        
        try:
            items_dto = [ItemPedidoDTO(**item) for item in items]
            
            pedido_dto = PedidoDTO(
                id_cliente="",  # Se puede obtener el ID real si se necesita
                cliente_nombre=cliente.nombre,
                cliente_email=email_cliente,
                items=items_dto
            )
            
            result = self.collection.insert_one(pedido_dto.to_dict())
            logger.success(f"Pedido creado con ID: {result.inserted_id}")
            logger.info(f"💰 Total: {Formatter.formato_moneda(pedido_dto.total())}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error al crear pedido: {e}")
            return None
    
    def listar_todos(self) -> List[dict]:
        """Read - Obtener todos los pedidos"""
        try:
            return list(self.collection.find())
        except Exception as e:
            logger.error(f"Error al listar pedidos: {e}")
            return []
    
    def listar_con_formato(self) -> None:
        """Lista los pedidos con formato legible"""
        pedidos = self.listar_todos()
        if not pedidos:
            logger.warning("No hay pedidos registrados")
            return
        
        logger.separador("PEDIDOS REGISTRADOS")
        for pedido in pedidos:
            print(f"📦 ID: {pedido['_id']}")
            print(f"   Cliente: {pedido['cliente_nombre']}")
            print(f"   Fecha: {Formatter.formato_fecha(pedido['fecha_pedido'])}")
            print(f"   Estado: {pedido['estado']}")
            print(f"   Total: {Formatter.formato_moneda(pedido['total'])}")
            print("   Productos:")
            for item in pedido['items']:
                subtotal = item['cantidad'] * item['precio']
                print(f"     - {item['nombre']} x{item['cantidad']} = {Formatter.formato_moneda(subtotal)}")
            print("-" * 30)
    
    def actualizar_estado(self, pedido_id: str, nuevo_estado: str) -> bool:
        """Update - Actualizar estado de un pedido"""
        estados_validos = ["pendiente", "enviado", "entregado", "cancelado"]
        if nuevo_estado not in estados_validos:
            logger.error(f"Estado inválido: {nuevo_estado}. Válidos: {', '.join(estados_validos)}")
            return False
        
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(pedido_id)},
                {"$set": {"estado": nuevo_estado}}
            )
            if result.modified_count > 0:
                logger.success(f"Pedido actualizado a: {nuevo_estado}")
            else:
                logger.warning("No se encontró el pedido")
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error al actualizar pedido: {e}")
            return False
    
    def buscar_por_cliente(self, email_cliente: str) -> List[dict]:
        """Read - Buscar pedidos por email de cliente"""
        if not Validator.email(email_cliente):
            logger.error(f"Email inválido: {email_cliente}")
            return []
        
        cliente = self.cliente_service.buscar_por_email(email_cliente)
        if not cliente:
            logger.error(f"Cliente no encontrado: {email_cliente}")
            return []
        
        try:
            return list(self.collection.find({"cliente_email": email_cliente}))
        except Exception as e:
            logger.error(f"Error al buscar pedidos: {e}")
            return []