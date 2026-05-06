"""
Sistema de Gestión ComercioTech
Punto de entrada principal de la aplicación
Autores: Francisco Caster - Marcelo Monsalves
Asignatura: Base de Datos No Estructuradas
"""

from config import MongoDBConnection
from servicios import ClienteService, ProductoService, PedidoService
from models import ClienteDTO, ProductoDTO
from utils import Validator
import os
import getpass
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

# ===== SISTEMA DE LOGIN CON ROLES =====
def obtener_rol(usuario: str) -> str:
    """Retorna el rol del usuario según las variables de entorno"""
    if usuario == os.getenv("ADMIN_USER"):
        return "admin"
    elif usuario == os.getenv("VENTAS_USER"):
        return "ventas"
    else:
        return "desconocido"


def verificar_login(usuario: str, password: str) -> tuple:
    """Verifica credenciales y retorna (exito, rol)"""
    
    # Verificar admin
    if usuario == os.getenv("ADMIN_USER") and password == os.getenv("ADMIN_PASSWORD"):
        return (True, "admin")
    
    # Verificar ventas
    if usuario == os.getenv("VENTAS_USER") and password == os.getenv("VENTAS_PASSWORD"):
        return (True, "ventas")
    
    return (False, None)


def pantalla_login() -> tuple:
    """Muestra pantalla de login y retorna (exito, rol)"""
    intentos = 0
    max_intentos = 3
    
    while intentos < max_intentos:
        print("\n" + "="*50)
        print("🔐 COMERCIOTECH - SISTEMA DE GESTIÓN")
        print("="*50)
        print(f"Intentos restantes: {max_intentos - intentos}")
        print("-"*30)
        
        usuario = input("👤 Usuario: ").strip()
        password = getpass.getpass("🔒 Contraseña: ")
        
        exito, rol = verificar_login(usuario, password)
        
        if exito:
            print(f"\n✅ Bienvenido {usuario} ({rol})")
            return (True, rol, usuario)
        else:
            intentos += 1
            print("\n❌ Usuario o contraseña incorrectos")
    
    print("\n🔒 Demasiados intentos fallidos. Acceso denegado.")
    return (False, None, None)
# ===== FIN SISTEMA DE LOGIN =====


def mostrar_menu(rol: str):
    """Muestra el menú principal según el rol del usuario"""
    print("\n" + "="*50)
    print("🏪 COMERCIOTECH - SISTEMA DE GESTIÓN")
    print("="*50)
    print(f"👤 Rol: {rol.upper()}")
    print("-"*30)
    print("1. Gestionar Clientes")
    print("2. Gestionar Productos")
    print("3. Gestionar Pedidos")
    
    # Opciones según rol
    if rol == "admin":
        print("4. Salir")
    elif rol == "ventas":
        print("4. Salir")
    
    print("="*50)
    return input("Seleccione una opción: ")


def menu_clientes(cliente_service, rol: str):
    """Submenú para gestión de clientes con permisos según rol"""
    from models import ClienteDTO
    
    while True:
        print("\n" + "="*40)
        print("👥 GESTIÓN DE CLIENTES")
        print("="*40)
        print("1. Registrar nuevo cliente")
        print("2. Listar todos los clientes")
        print("3. Buscar cliente por email")
        
        # Opciones según rol
        if rol == "admin":
            print("4. Actualizar cliente")
            print("5. Eliminar cliente")
        
        print("6. Volver al menú principal")
        print("="*40)
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            print("\n📝 REGISTRO DE NUEVO CLIENTE")
            print("⚠️  Todos los campos son obligatorios\n")
            
            while True:
                nombre = input("Nombre completo: ").strip()
                if not nombre:
                    print("❌ El nombre es obligatorio. Intente nuevamente.")
                    continue
                if not Validator.solo_texto(nombre):
                    print("❌ El nombre solo debe contener letras, espacios y acentos. No se permiten números.")
                    continue
                break
            
            while True:
                email = input("Email: ").strip()
                if not email:
                    print("❌ El email es obligatorio. Intente nuevamente.")
                    continue
                if not Validator.email(email):
                    print("❌ Email inválido. Debe tener un formato válido (ej: usuario@dominio.cl) y no puede ser solo números.")
                    continue
                existente = cliente_service.collection.find_one({"email": email})
                if existente:
                    print(f"❌ Ya existe un cliente con el email '{email}'")
                    continue
                break
            
            while True:
                telefono = input("Teléfono (formato: +569XXXXXXXX): ").strip()
                if not telefono:
                    print("❌ El teléfono es obligatorio. Intente nuevamente.")
                    continue
                if not Validator.telefono(telefono):
                    print("❌ Formato de teléfono inválido.")
                    print("   Debe ser: +56912345678 (con +56, luego 9, luego 8 dígitos)")
                    continue
                telefono = Validator.normalizar_telefono(telefono)
                break
            
            while True:
                direccion = input("Dirección: ").strip()
                if direccion:
                    break
                print("❌ La dirección es obligatoria. Intente nuevamente.")
            
            cliente = ClienteDTO(
                nombre=nombre,
                email=email,
                telefono=telefono,
                direccion=direccion
            )
            
            resultado = cliente_service.crear(cliente)
            if resultado:
                print(f"\n✅ Cliente registrado con ID: {resultado}")
            else:
                print("\n❌ Error al registrar cliente. Verifique los datos ingresados.")
            
            input("\n🔹 Presione Enter para continuar...")

        elif opcion == "2":
            print("\n📋 LISTADO DE CLIENTES")
            clientes = cliente_service.listar_todos()
            if clientes:
                for i, c in enumerate(clientes, 1):
                    print(f"\n{i}. {c.nombre}")
                    print(f"   📧 Email: {c.email}")
                    print(f"   📞 Teléfono: {c.telefono}")
                    print(f"   📍 Dirección: {c.direccion}")
            else:
                print("   No hay clientes registrados")
            input("\n🔹 Presione Enter para continuar...")
        
        elif opcion == "3":
            email = input("\nIngrese el email del cliente: ").strip()
            cliente = cliente_service.buscar_por_email(email)
            if cliente:
                print(f"\n✅ Cliente encontrado:")
                print(f"   Nombre: {cliente.nombre}")
                print(f"   Email: {cliente.email}")
                print(f"   Teléfono: {cliente.telefono}")
                print(f"   Dirección: {cliente.direccion}")
            else:
                print("\n❌ Cliente no encontrado")
            input("\n🔹 Presione Enter para continuar...")
        
        elif opcion == "4" and rol == "admin":
            email = input("\nIngrese el email del cliente a actualizar: ").strip()
            cliente = cliente_service.buscar_por_email(email)
            if cliente:
                print(f"\nCliente encontrado: {cliente.nombre}")
                print("\nDeje en blanco los campos que no desea modificar:")
                
                nuevo_nombre = input(f"Nuevo nombre ({cliente.nombre}): ").strip()
                nuevo_telefono = input(f"Nuevo teléfono ({cliente.telefono}): ").strip()
                nueva_direccion = input(f"Nueva dirección ({cliente.direccion}): ").strip()
                
                datos_actualizar = {}
                if nuevo_nombre:
                    if Validator.solo_texto(nuevo_nombre):
                        datos_actualizar['nombre'] = nuevo_nombre
                    else:
                        print("❌ El nombre solo debe contener letras. No se actualizará.")
                if nuevo_telefono:
                    if Validator.telefono(nuevo_telefono):
                        datos_actualizar['telefono'] = Validator.normalizar_telefono(nuevo_telefono)
                    else:
                        print("❌ Formato de teléfono inválido, no se actualizará.")
                if nueva_direccion:
                    datos_actualizar['direccion'] = nueva_direccion
                
                if datos_actualizar:
                    from bson import ObjectId
                    doc = cliente_service.collection.find_one({"email": email})
                    if doc:
                        resultado = cliente_service.collection.update_one(
                            {"_id": doc['_id']},
                            {"$set": datos_actualizar}
                        )
                        if resultado.modified_count > 0:
                            print("\n✅ Cliente actualizado correctamente")
                        else:
                            print("\n⚠️ No se realizaron cambios")
                else:
                    print("\n⚠️ No se ingresaron datos válidos para actualizar")
            else:
                print("\n❌ Cliente no encontrado")
            input("\n🔹 Presione Enter para continuar...")
        
        elif opcion == "5" and rol == "admin":
            email = input("\nIngrese el email del cliente a eliminar: ").strip()
            cliente = cliente_service.buscar_por_email(email)
            if cliente:
                confirmar = input(f"¿Está seguro de eliminar a '{cliente.nombre}'? (s/n): ").lower()
                if confirmar == 's':
                    doc = cliente_service.collection.find_one({"email": email})
                    if doc:
                        from bson import ObjectId
                        resultado = cliente_service.collection.delete_one({"_id": doc['_id']})
                        if resultado.deleted_count > 0:
                            print("\n✅ Cliente eliminado correctamente")
                        else:
                            print("\n❌ Error al eliminar cliente")
            else:
                print("\n❌ Cliente no encontrado")
            input("\n🔹 Presione Enter para continuar...")
        
        elif opcion == "6":
            break
        
        else:
            print("\n❌ Opción no válida")
            input("\n🔹 Presione Enter para continuar...")


def menu_productos(producto_service, rol: str):
    """Submenú para gestión de productos con permisos según rol"""
    from models import ProductoDTO
    
    while True:
        print("\n" + "="*40)
        print("🛒 GESTIÓN DE PRODUCTOS")
        print("="*40)
        
        # Opciones según rol
        if rol == "admin":
            print("1. Registrar producto")
            print("2. Listar productos")
            print("3. Buscar por SKU")
            print("4. Actualizar stock")
            print("5. Eliminar producto")
        elif rol == "ventas":
            print("1. Listar productos")
            print("2. Buscar por SKU")
        
        print("6. Volver")
        print("="*40)
        
        opcion = input("Seleccione: ")
        
        if opcion == "1" and rol == "admin":
            print("\n📝 REGISTRO DE NUEVO PRODUCTO")
            nombre = input("Nombre: ").strip()
            sku = input("SKU (XXX-000): ").strip().upper()
            try:
                precio = int(input("Precio: "))
                stock = int(input("Stock: "))
            except ValueError:
                print("❌ Precio y stock deben ser números")
                input("Enter...")
                continue
            categoria = input("Categoría: ").strip()
            
            if not all([nombre, sku, categoria]):
                print("❌ Todos los campos son obligatorios")
                input("Enter...")
                continue
            
            producto = ProductoDTO(nombre=nombre, sku=sku, precio=precio, stock=stock, categoria=categoria)
            if producto_service.crear(producto):
                print("✅ Producto registrado")
            else:
                print("❌ Error al registrar producto")
        
        elif (opcion == "1" and rol == "ventas") or (opcion == "2" and rol == "admin"):
            print("\n📋 LISTADO DE PRODUCTOS")
            productos = producto_service.listar_todos()
            if productos:
                for p in productos:
                    print(f"\n📦 {p.nombre} (SKU: {p.sku})")
                    print(f"   Precio: ${p.precio:,}")
                    print(f"   Stock: {p.stock} unidades")
                    print(f"   Categoría: {p.categoria}")
            else:
                print("   No hay productos registrados")
        
        elif (opcion == "2" and rol == "ventas") or (opcion == "3" and rol == "admin"):
            sku = input("SKU: ").strip().upper()
            p = producto_service.buscar_por_sku(sku)
            if p:
                print(f"\n✅ Producto encontrado:")
                print(f"   Nombre: {p.nombre}")
                print(f"   Precio: ${p.precio:,}")
                print(f"   Stock: {p.stock}")
                print(f"   Categoría: {p.categoria}")
            else:
                print("❌ Producto no encontrado")
        
        elif opcion == "4" and rol == "admin":
            sku = input("SKU: ").strip().upper()
            try:
                nuevo_stock = int(input("Nuevo stock: "))
            except ValueError:
                print("❌ El stock debe ser un número")
                input("Enter...")
                continue
            if producto_service.actualizar_stock(sku, nuevo_stock):
                print("✅ Stock actualizado")
            else:
                print("❌ Error al actualizar stock")
        
        elif opcion == "5" and rol == "admin":
            sku = input("SKU a eliminar: ").strip().upper()
            confirmar = input(f"¿Eliminar producto con SKU '{sku}'? (s/n): ").lower()
            if confirmar == 's':
                from bson import ObjectId
                doc = producto_service.collection.find_one({"sku": sku})
                if doc and producto_service.collection.delete_one({"_id": doc['_id']}).deleted_count > 0:
                    print("✅ Producto eliminado")
                else:
                    print("❌ Error al eliminar")
        
        elif opcion == "6":
            break
        
        else:
            print("❌ Opción no válida")
        
        input("\n🔹 Enter para continuar...")


def menu_pedidos(pedido_service, cliente_service, producto_service, rol: str):
    """Submenú para gestión de pedidos (ambos roles tienen acceso completo)"""
    while True:
        print("\n" + "="*40)
        print("📦 GESTIÓN DE PEDIDOS")
        print("="*40)
        print("1. Crear pedido")
        print("2. Listar pedidos")
        print("3. Buscar por cliente")
        print("4. Cambiar estado")
        print("5. Volver")
        print("="*40)
        
        opcion = input("Seleccione: ")
        
        if opcion == "1":
            email = input("Email del cliente: ").strip()
            cliente = cliente_service.buscar_por_email(email)
            if not cliente:
                print("❌ Cliente no encontrado")
                input("Enter...")
                continue
            
            items = []
            print("\n🛒 AGREGAR PRODUCTOS AL PEDIDO (escriba 'fin' para terminar)")
            while True:
                sku = input("SKU producto: ").strip().upper()
                if sku == 'FIN':
                    break
                producto = producto_service.buscar_por_sku(sku)
                if not producto:
                    print("❌ Producto no existe")
                    continue
                try:
                    cantidad = int(input(f"Cantidad (stock disponible: {producto.stock}): "))
                except ValueError:
                    print("❌ Cantidad inválida")
                    continue
                if cantidad > producto.stock:
                    print("❌ Stock insuficiente")
                    continue
                items.append({"nombre": producto.nombre, "cantidad": cantidad, "precio": producto.precio})
                producto_service.actualizar_stock(sku, producto.stock - cantidad)
                print(f"   ✅ Agregado: {producto.nombre} x{cantidad}")
            
            if items and pedido_service.crear(email, items):
                print("✅ Pedido creado exitosamente")
            else:
                print("❌ Error al crear pedido")
        
        elif opcion == "2":
            pedidos = pedido_service.listar_todos()
            if not pedidos:
                print("📭 No hay pedidos registrados")
            else:
                print("\n" + "="*60)
                print("📦 LISTADO DE PEDIDOS")
                print("="*60)
                for p in pedidos:
                    print(f"\n🆔 ID: {p['_id']}")
                    print(f"👤 Cliente: {p.get('cliente_nombre', 'N/A')}")
                    print(f"📧 Email: {p.get('cliente_email', 'N/A')}")
                    print(f"💰 Total: ${p.get('total', 0):,}")
                    print(f"📌 Estado: {p.get('estado', 'N/A')}")
                    print(f"📅 Fecha: {p.get('fecha_pedido', 'N/A')}")
                    print("🛒 Productos:")
                    for item in p.get('items', []):
                        print(f"   - {item.get('nombre')} x{item.get('cantidad')} = ${item.get('cantidad',0) * item.get('precio',0):,}")
                    print("-"*40)
        
        elif opcion == "3":
            email = input("Email del cliente: ").strip()
            cliente = cliente_service.buscar_por_email(email)
            if not cliente:
                print("❌ Cliente no encontrado")
            else:
                pedidos = pedido_service.buscar_por_cliente(email)
                if not pedidos:
                    print(f"📭 No hay pedidos para {cliente.nombre}")
                else:
                    print(f"\n📦 PEDIDOS DE {cliente.nombre}:")
                    for p in pedidos:
                        print(f"\n   ID: {p['_id']} | Total: ${p.get('total',0):,} | Estado: {p.get('estado')}")
                        for item in p.get('items', []):
                            print(f"     - {item.get('nombre')} x{item.get('cantidad')}")
        
        elif opcion == "4":
            pedido_id = input("ID del pedido: ").strip()
            print("\nEstados disponibles:")
            print("1. pendiente")
            print("2. enviado")
            print("3. entregado")
            print("4. cancelado")
            estados = {"1": "pendiente", "2": "enviado", "3": "entregado", "4": "cancelado"}
            op = input("Seleccione nuevo estado (1-4): ").strip()
            nuevo = estados.get(op)
            if nuevo and pedido_service.actualizar_estado(pedido_id, nuevo):
                print("✅ Estado actualizado")
            else:
                print("❌ Error al actualizar estado")
        
        elif opcion == "5":
            break
        
        else:
            print("❌ Opción no válida")
        
        input("\n🔹 Enter para continuar...")


def main():
    """Función principal"""
    
    # === PANTALLA DE LOGIN ===
    print("\n" + "="*50)
    print("🔐 COMERCIOTECH - CONTROL DE ACCESO")
    print("="*50)
    
    exito, rol, usuario = pantalla_login()
    
    if not exito:
        print("\n❌ Acceso denegado. El sistema se cerrará.")
        return
    # ========================
    
    conn = MongoDBConnection()
    db = conn.connect()
    
    if db is None:
        print("❌ No se pudo establecer conexión con MongoDB")
        return
    
    cliente_service = ClienteService(db)
    producto_service = ProductoService(db)
    pedido_service = PedidoService(db)
    
    while True:
        opcion = mostrar_menu(rol)
        
        if opcion == "1":
            menu_clientes(cliente_service, rol)
        elif opcion == "2":
            menu_productos(producto_service, rol)
        elif opcion == "3":
            menu_pedidos(pedido_service, cliente_service, producto_service, rol)
        elif opcion == "4":
            print("\n👋 Saliendo del sistema...")
            conn.disconnect()
            break
        else:
            print("\n❌ Opción no válida")


if __name__ == "__main__":
    main()