"""
Modelos de datos (DTOs) para la aplicación
Define la estructura de los documentos en MongoDB
"""

from datetime import datetime
from typing import List, Dict
from dataclasses import dataclass, field


@dataclass
class ClienteDTO:
    """DTO para la entidad Cliente"""
    nombre: str
    email: str
    telefono: str
    direccion: str
    activo: bool = True
    fecha_registro: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convierte el DTO a diccionario para MongoDB"""
        return {
            "nombre": self.nombre,
            "email": self.email,
            "telefono": self.telefono,
            "direccion": self.direccion,
            "fecha_registro": self.fecha_registro,
            "activo": self.activo
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'ClienteDTO':
        """Crea un DTO desde un diccionario de MongoDB"""
        return ClienteDTO(
            nombre=data.get('nombre'),
            email=data.get('email'),
            telefono=data.get('telefono'),
            direccion=data.get('direccion'),
            activo=data.get('activo', True),
            fecha_registro=data.get('fecha_registro', datetime.now())
        )


@dataclass
class ProductoDTO:
    """DTO para la entidad Producto"""
    nombre: str
    precio: int
    stock: int
    categoria: str
    sku: str
    fecha_creacion: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convierte el DTO a diccionario para MongoDB"""
        return {
            "nombre": self.nombre,
            "precio": self.precio,
            "sku": self.sku,
            "stock": self.stock,
            "categoria": self.categoria,
            "fecha_creacion": self.fecha_creacion
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'ProductoDTO':
        """Crea un DTO desde un diccionario de MongoDB"""
        return ProductoDTO(
            nombre=data.get('nombre'),
            precio=data.get('precio'),
            stock=data.get('stock'),
            categoria=data.get('categoria'),
            sku=data.get('sku'),
            fecha_creacion=data.get('fecha_creacion', datetime.now())
        )


@dataclass
class ItemPedidoDTO:
    """DTO para un item dentro de un pedido"""
    nombre: str
    cantidad: int
    precio: int
    
    def subtotal(self) -> int:
        return self.cantidad * self.precio
    
    def to_dict(self) -> Dict:
        return {
            "nombre": self.nombre,
            "cantidad": self.cantidad,
            "precio": self.precio
        }


@dataclass
class PedidoDTO:
    """DTO para la entidad Pedido"""
    id_cliente: str
    cliente_nombre: str
    cliente_email: str
    items: List[ItemPedidoDTO]
    estado: str = "pendiente"
    fecha_pedido: datetime = field(default_factory=datetime.now)
    
    def total(self) -> int:
        """Calcula el total del pedido"""
        return sum(item.subtotal() for item in self.items)
    
    def to_dict(self) -> Dict:
        return {
            "id_cliente": self.id_cliente,
            "cliente_nombre": self.cliente_nombre,
            "cliente_email": self.cliente_email,
            "fecha_pedido": self.fecha_pedido,
            "estado": self.estado,
            "items": [item.to_dict() for item in self.items],
            "total": self.total()
        }