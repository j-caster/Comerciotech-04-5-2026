"""
Utilidades generales para el sistema ComercioTech
Funciones de ayuda para formateo, validación y manejo de datos
"""

from datetime import datetime
from typing import Any
import re


class Formatter:
    """Clase para formateo de datos"""
    
    @staticmethod
    def formato_moneda(valor: int) -> str:
        """Convierte un número a formato de moneda chilena"""
        try:
            return f"${valor:,.0f}".replace(",", ".")
        except (ValueError, TypeError):
            return "$0"
    
    @staticmethod
    def formato_fecha(fecha: datetime, formato: str = "%d-%m-%Y %H:%M") -> str:
        """Formatea una fecha a string legible"""
        if fecha is None:
            return "Fecha no disponible"
        try:
            return fecha.strftime(formato)
        except Exception:
            return str(fecha)
    
    @staticmethod
    def formato_telefono(telefono: str) -> str:
        """Formatea un número de teléfono chileno"""
        if not telefono:
            return "Sin teléfono"
        limpio = re.sub(r'\D', '', telefono)
        if len(limpio) == 11 and limpio.startswith('56'):
            return f"+{limpio[0:2]} {limpio[2:4]} {limpio[4:8]} {limpio[8:12]}"
        elif len(limpio) == 9:
            return f"+56 {limpio[0:1]} {limpio[1:5]} {limpio[5:9]}"
        return telefono
    
    @staticmethod
    def formato_nombre_archivo(base: str) -> str:
        """Limpia un string para usarlo como nombre de archivo"""
        return re.sub(r'[\\/*?:"<>|]', "_", base)


class Validator:
    """Clase para validación de datos"""
    
    @staticmethod
    def solo_texto(valor: str) -> bool:
        """Valida que el campo solo contenga letras, espacios, acentos y ñ"""
        if not valor:
            return False
        # Permite letras (mayúsculas/minúsculas), espacios, acentos, ñ, y apóstrofes
        patron = r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s\']+$'
        return bool(re.match(patron, valor.strip()))
    
    @staticmethod
    def email(email: str) -> bool:
        """Valida formato de email - debe tener texto antes del @ y dominio válido"""
        if not email:
            return False
        # El email debe tener al menos un caracter antes del @ (no solo números)
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(patron, email):
            return False
        # Obtener la parte local (antes del @)
        parte_local = email.split('@')[0]
        # La parte local debe tener al menos una letra (no puede ser solo números)
        if not re.search(r'[a-zA-Z]', parte_local):
            return False
        return True
    
    @staticmethod
    def telefono(telefono: str) -> bool:
        """Valida formato de teléfono chileno: +569XXXXXXXX (11 dígitos, solo números después del +56)"""
        if not telefono:
            return False
        
        # Eliminar espacios
        telefono_limpio = telefono.replace(" ", "")
        
        # Verificar formato +569XXXXXXXX
        patron = r'^\+569\d{8}$'
        if re.match(patron, telefono_limpio):
            return True
        
        # También aceptar 9XXXXXXXX (sin +56)
        if re.match(r'^9\d{8}$', telefono_limpio):
            return True
        
        return False
    
    @staticmethod
    def normalizar_telefono(telefono: str) -> str:
        """Normaliza el teléfono al formato +569XXXXXXXX"""
        if not telefono:
            return ""
        
        # Eliminar espacios
        telefono_limpio = telefono.replace(" ", "")
        
        # Si es 9XXXXXXXX, agregar +56
        if re.match(r'^9\d{8}$', telefono_limpio):
            return f"+56{telefono_limpio}"
        
        # Si ya es +569XXXXXXXX, devolver igual
        if re.match(r'^\+569\d{8}$', telefono_limpio):
            return telefono_limpio
        
        return telefono
    
    @staticmethod
    def campo_no_vacio(valor: str) -> bool:
        """Valida que un campo no esté vacío o solo con espacios"""
        return bool(valor and valor.strip())
    
    @staticmethod
    def sku(sku: str) -> bool:
        """Valida formato de SKU (letras mayúsculas, números y guiones)"""
        patron = r'^[A-Z0-9]{3}-[0-9]{3}$'
        return bool(re.match(patron, sku))
    
    @staticmethod
    def precio(precio: Any) -> bool:
        """Valida que el precio sea un número positivo"""
        try:
            return float(precio) > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def stock(stock: Any) -> bool:
        """Valida que el stock sea un entero no negativo"""
        try:
            return int(stock) >= 0
        except (ValueError, TypeError):
            return False


class Logger:
    """Clase simple para logging de operaciones"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
    
    def info(self, mensaje: str):
        if self.verbose:
            print(f"ℹ️ {mensaje}")
    
    def success(self, mensaje: str):
        if self.verbose:
            print(f"✅ {mensaje}")
    
    def error(self, mensaje: str):
        if self.verbose:
            print(f"❌ {mensaje}")
    
    def warning(self, mensaje: str):
        if self.verbose:
            print(f"⚠️ {mensaje}")
    
    def separador(self, titulo: str = "", caracter: str = "=", longitud: int = 50):
        if self.verbose:
            if titulo:
                print(f"\n{caracter * 5} {titulo} {caracter * 5}")
            else:
                print(caracter * longitud)


def limpiar_console():
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def esperar_enter(mensaje: str = "Presione Enter para continuar..."):
    input(mensaje)


def ahora() -> datetime:
    return datetime.now()