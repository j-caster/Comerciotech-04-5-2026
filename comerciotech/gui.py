"""
Sistema de Gestión ComercioTech - Interfaz Gráfica
Autores: Francisco Caster - Marcelo Monsalves
Asignatura: Base de Datos No Estructuradas
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
from dotenv import load_dotenv
from config import MongoDBConnection
from servicios import ClienteService, ProductoService, PedidoService
from models import ClienteDTO, ProductoDTO
from utils import Validator

# Cargar variables del archivo .env
load_dotenv()

# Variables globales
usuario_actual = None
rol_actual = None
cliente_service = None
producto_service = None
pedido_service = None
db_connection = None
ventana_principal = None  # Guardar referencia a la ventana principal


def centrar_ventana(ventana, ancho=800, alto=600):
    """Centra una ventana en la pantalla"""
    ventana.update_idletasks()
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()
    x = (pantalla_ancho - ancho) // 2
    y = (pantalla_alto - alto) // 2
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")


def mantener_principal_detras():
    """Mantiene la ventana principal detrás de las ventanas hijas"""
    global ventana_principal
    if ventana_principal:
        ventana_principal.lower()


# ==================== SISTEMA DE LOGIN ====================
def verificar_login(usuario: str, password: str) -> tuple:
    if usuario == os.getenv("ADMIN_USER") and password == os.getenv("ADMIN_PASSWORD"):
        return (True, "admin")
    if usuario == os.getenv("VENTAS_USER") and password == os.getenv("VENTAS_PASSWORD"):
        return (True, "ventas")
    return (False, None)


def iniciar_sesion():
    global usuario_actual, rol_actual, cliente_service, producto_service, pedido_service, db_connection, ventana_principal
    
    def do_login():
        global usuario_actual, rol_actual
        usuario = entry_usuario.get().strip()
        password = entry_password.get()
        
        exito, rol = verificar_login(usuario, password)
        
        if exito:
            usuario_actual = usuario
            rol_actual = rol
            
            global db_connection, cliente_service, producto_service, pedido_service
            db_connection = MongoDBConnection()
            db = db_connection.connect()
            
            if db is None:
                messagebox.showerror("Error", "No se pudo conectar a MongoDB")
                return
            
            cliente_service = ClienteService(db)
            producto_service = ProductoService(db)
            pedido_service = PedidoService(db)
            
            login_window.destroy()
            mostrar_menu_principal()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
            entry_password.delete(0, tk.END)
    
    login_window = tk.Tk()
    login_window.title("ComercioTech - Inicio de Sesión")
    login_window.geometry("400x350")
    login_window.resizable(False, False)
    
    centrar_ventana(login_window, 400, 350)
    
    main_frame = ttk.Frame(login_window, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(main_frame, text="🔐 COMERCIOTECH", font=("Arial", 18, "bold")).pack(pady=20)
    ttk.Label(main_frame, text="Sistema de Gestión", font=("Arial", 10)).pack(pady=(0, 30))
    
    ttk.Label(main_frame, text="Usuario:", font=("Arial", 10)).pack(anchor=tk.W)
    entry_usuario = ttk.Entry(main_frame, font=("Arial", 11), width=30)
    entry_usuario.pack(pady=(5, 15), fill=tk.X)
    entry_usuario.focus()
    
    ttk.Label(main_frame, text="Contraseña:", font=("Arial", 10)).pack(anchor=tk.W)
    entry_password = ttk.Entry(main_frame, show="*", font=("Arial", 11), width=30)
    entry_password.pack(pady=(5, 25), fill=tk.X)
    
    btn_login = ttk.Button(main_frame, text="Iniciar Sesión", command=do_login, width=25)
    btn_login.pack(pady=10)
    
    entry_password.bind("<Return>", lambda e: do_login())
    
    login_window.mainloop()


# ==================== MENÚ PRINCIPAL ====================
def mostrar_menu_principal():
    global rol_actual, ventana_principal
    
    ventana_principal = tk.Tk()
    ventana_principal.title("ComercioTech - Sistema de Gestión")
    ventana_principal.geometry("500x500")
    ventana_principal.resizable(False, False)
    
    centrar_ventana(ventana_principal, 500, 500)
    
    main_frame = ttk.Frame(ventana_principal, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(main_frame, text="🏪 COMERCIOTECH", font=("Arial", 16, "bold")).pack(pady=10)
    ttk.Label(main_frame, text="Sistema de Gestión Integrado", font=("Arial", 10)).pack()
    
    info_frame = ttk.Frame(main_frame, relief=tk.GROOVE, padding="10")
    info_frame.pack(fill=tk.X, pady=20)
    ttk.Label(info_frame, text=f"👤 Usuario: {usuario_actual}").pack(anchor=tk.W)
    ttk.Label(info_frame, text=f"🔑 Rol: {rol_actual.upper()}").pack(anchor=tk.W)
    
    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(pady=20)
    
    ttk.Button(btn_frame, text="👥 Gestionar Clientes", 
               command=lambda: abrir_gestion_clientes(), width=30).pack(pady=5)
    ttk.Button(btn_frame, text="🛒 Gestionar Productos",
               command=lambda: abrir_gestion_productos(), width=30).pack(pady=5)
    ttk.Button(btn_frame, text="📦 Gestionar Pedidos",
               command=lambda: abrir_gestion_pedidos(), width=30).pack(pady=5)
    
    ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=20)
    
    ttk.Button(main_frame, text="🚪 Cerrar Sesión",
           command=lambda: cerrar_sesion(ventana_principal), width=30).pack(pady=10)
    
    ventana_principal.mainloop()


def salir_sistema(window):
    if messagebox.askyesno("Salir", "¿Está seguro que desea salir del sistema?"):
        if db_connection:
            db_connection.disconnect()
        window.destroy()

def cerrar_sesion(ventana_actual):
    """Cierra la sesión actual y vuelve a la pantalla de login"""
    if messagebox.askyesno("Cerrar Sesión", "¿Está seguro que desea cerrar sesión?"):
        if db_connection:
            db_connection.disconnect()
        ventana_actual.destroy()
        # Volver a mostrar pantalla de login
        iniciar_sesion()
# ==================== GESTIÓN DE CLIENTES ====================
def abrir_gestion_clientes():
    global rol_actual
    
    ventana = tk.Toplevel()
    ventana.title("ComercioTech - Gestión de Clientes")
    ventana.geometry("1100x650")
    ventana.minsize(800, 550)
    ventana.transient(ventana_principal)
    ventana.grab_set()
    
    centrar_ventana(ventana, 1100, 650)
    
    # Frame principal con grid
    main_frame = ttk.Frame(ventana, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    main_frame.grid_columnconfigure(0, weight=3)
    main_frame.grid_columnconfigure(1, weight=1)
    main_frame.grid_rowconfigure(1, weight=1)
    
    ttk.Label(main_frame, text="👥 GESTIÓN DE CLIENTES", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
    
    # Tabla
    left_frame = ttk.Frame(main_frame)
    left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
    left_frame.grid_rowconfigure(0, weight=1)
    left_frame.grid_columnconfigure(0, weight=1)
    
    columns = ("ID", "Nombre", "Email", "Teléfono", "Dirección")
    tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=20)
    
    col_widths = [50, 220, 220, 140, 250]
    for i, col in enumerate(columns):
        tree.heading(col, text=col)
        tree.column(col, width=col_widths[i], minwidth=60)
    
    scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    tree.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")
    
    # Botones
    right_frame = ttk.Frame(main_frame)
    right_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
    
    ttk.Label(right_frame, text="⚡ ACCIONES", font=("Arial", 12, "bold")).pack(pady=(0, 10))
    ttk.Separator(right_frame, orient='horizontal').pack(fill=tk.X, pady=5)
    
    btn_container = ttk.Frame(right_frame)
    btn_container.pack(fill=tk.BOTH, expand=True, pady=10)
    
    def cargar_clientes():
        for item in tree.get_children():
            tree.delete(item)
        clientes = cliente_service.listar_todos()
        for i, c in enumerate(clientes, 1):
            tree.insert("", tk.END, values=(i, c.nombre, c.email, c.telefono, c.direccion))
    
    def registrar_cliente():
        dialog = tk.Toplevel(ventana)
        dialog.title("Registrar Cliente")
        dialog.geometry("420x500")
        dialog.transient(ventana)
        dialog.grab_set()
        centrar_ventana(dialog, 420, 500)
        
        ttk.Label(dialog, text="Registrar Nuevo Cliente", font=("Arial", 12, "bold")).pack(pady=15)
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Nombre completo:").pack(anchor=tk.W)
        entry_nombre = ttk.Entry(frame, width=40)
        entry_nombre.pack(pady=(0, 10), fill=tk.X)
        
        ttk.Label(frame, text="Email:").pack(anchor=tk.W)
        entry_email = ttk.Entry(frame, width=40)
        entry_email.pack(pady=(0, 10), fill=tk.X)
        
        ttk.Label(frame, text="Teléfono (+569XXXXXXXX):").pack(anchor=tk.W)
        entry_telefono = ttk.Entry(frame, width=40)
        entry_telefono.pack(pady=(0, 10), fill=tk.X)
        
        ttk.Label(frame, text="Dirección:").pack(anchor=tk.W)
        entry_direccion = ttk.Entry(frame, width=40)
        entry_direccion.pack(pady=(0, 20), fill=tk.X)
        
        def guardar():
            nombre = entry_nombre.get().strip()
            email = entry_email.get().strip()
            telefono = entry_telefono.get().strip()
            direccion = entry_direccion.get().strip()
            
            if not all([nombre, email, telefono, direccion]):
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return
            if not Validator.solo_texto(nombre):
                messagebox.showerror("Error", "Nombre inválido (solo letras)")
                return
            if not Validator.email(email):
                messagebox.showerror("Error", "Email inválido")
                return
            if not Validator.telefono(telefono):
                messagebox.showerror("Error", "Teléfono inválido (formato: +569XXXXXXXX)")
                return
            
            telefono = Validator.normalizar_telefono(telefono)
            cliente = ClienteDTO(nombre=nombre, email=email, telefono=telefono, direccion=direccion)
            resultado = cliente_service.crear(cliente)
            if resultado:
                messagebox.showinfo("Éxito", f"Cliente registrado con ID: {resultado}")
                cargar_clientes()
                dialog.destroy()
            else:
                messagebox.showerror("Error", "No se pudo registrar el cliente")
        
        ttk.Button(frame, text="Guardar", command=guardar).pack(pady=10)
        ttk.Button(frame, text="Cancelar", command=dialog.destroy).pack()
    
    def buscar_cliente():
        email = simpledialog.askstring("Buscar Cliente", "Ingrese el email del cliente:")
        if email:
            cliente = cliente_service.buscar_por_email(email)
            if cliente:
                messagebox.showinfo("Cliente Encontrado", 
                                   f"Nombre: {cliente.nombre}\n"
                                   f"Email: {cliente.email}\n"
                                   f"Teléfono: {cliente.telefono}\n"
                                   f"Dirección: {cliente.direccion}")
            else:
                messagebox.showerror("Error", "Cliente no encontrado")
    
    def actualizar_cliente():
        """Actualizar datos de un cliente existente"""
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showerror("Error", "Seleccione un cliente de la lista")
            return
        
        values = tree.item(seleccion[0])['values']
        email_actual = values[2]
        nombre_actual = values[1]
        telefono_actual = values[3]
        direccion_actual = values[4]
        
        # Ventana de actualización
        dialog = tk.Toplevel(ventana)
        dialog.title("Actualizar Cliente")
        dialog.geometry("420x500")
        dialog.transient(ventana)
        dialog.grab_set()
        centrar_ventana(dialog, 420, 500)
        
        ttk.Label(dialog, text=f"Actualizar Cliente: {nombre_actual}", font=("Arial", 12, "bold")).pack(pady=15)
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Nombre completo:").pack(anchor=tk.W)
        entry_nombre = ttk.Entry(frame, width=40)
        entry_nombre.insert(0, nombre_actual)
        entry_nombre.pack(pady=(0, 10), fill=tk.X)
        
        ttk.Label(frame, text="Email (no se puede modificar):").pack(anchor=tk.W)
        entry_email = ttk.Entry(frame, width=40)
        entry_email.insert(0, email_actual)
        entry_email.config(state="disabled")  # Email no se puede modificar
        entry_email.pack(pady=(0, 10), fill=tk.X)
        
        ttk.Label(frame, text="Teléfono (+569XXXXXXXX):").pack(anchor=tk.W)
        entry_telefono = ttk.Entry(frame, width=40)
        entry_telefono.insert(0, telefono_actual)
        entry_telefono.pack(pady=(0, 10), fill=tk.X)
        
        ttk.Label(frame, text="Dirección:").pack(anchor=tk.W)
        entry_direccion = ttk.Entry(frame, width=40)
        entry_direccion.insert(0, direccion_actual)
        entry_direccion.pack(pady=(0, 20), fill=tk.X)
        
        def guardar_cambios():
            nombre = entry_nombre.get().strip()
            telefono = entry_telefono.get().strip()
            direccion = entry_direccion.get().strip()
            
            if not all([nombre, telefono, direccion]):
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return
            if not Validator.solo_texto(nombre):
                messagebox.showerror("Error", "Nombre inválido (solo letras)")
                return
            if not Validator.telefono(telefono):
                messagebox.showerror("Error", "Teléfono inválido (formato: +569XXXXXXXX)")
                return
            
            telefono = Validator.normalizar_telefono(telefono)
            
            # Buscar el documento del cliente
            doc = cliente_service.collection.find_one({"email": email_actual})
            if doc:
                # Actualizar campos
                resultado = cliente_service.collection.update_one(
                    {"_id": doc['_id']},
                    {"$set": {
                        "nombre": nombre,
                        "telefono": telefono,
                        "direccion": direccion
                    }}
                )
                if resultado.modified_count > 0:
                    messagebox.showinfo("Éxito", "Cliente actualizado correctamente")
                    cargar_clientes()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo actualizar el cliente")
            else:
                messagebox.showerror("Error", "Cliente no encontrado")
        
        ttk.Button(frame, text="Guardar Cambios", command=guardar_cambios).pack(pady=10)
        ttk.Button(frame, text="Cancelar", command=dialog.destroy).pack()
    
    def eliminar_cliente():
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showerror("Error", "Seleccione un cliente de la lista")
            return
        values = tree.item(seleccion[0])['values']
        email = values[2]
        if messagebox.askyesno("Confirmar", f"¿Eliminar cliente '{values[1]}'?"):
            doc = cliente_service.collection.find_one({"email": email})
            if doc and cliente_service.eliminar(str(doc['_id'])):
                messagebox.showinfo("Éxito", "Cliente eliminado")
                cargar_clientes()
            else:
                messagebox.showerror("Error", "No se pudo eliminar")
    
    # Botones comunes
    ttk.Button(btn_container, text="📝 Registrar Cliente", command=registrar_cliente, width=25).pack(pady=5)
    ttk.Button(btn_container, text="🔍 Buscar Cliente", command=buscar_cliente, width=25).pack(pady=5)
    ttk.Button(btn_container, text="🔄 Actualizar Lista", command=cargar_clientes, width=25).pack(pady=5)
    
    # Botones solo para admin
    if rol_actual == "admin":
        ttk.Button(btn_container, text="✏️ Actualizar Cliente", command=actualizar_cliente, width=25).pack(pady=5)
        ttk.Button(btn_container, text="❌ Eliminar Cliente", command=eliminar_cliente, width=25).pack(pady=5)
    
    ttk.Separator(btn_container, orient='horizontal').pack(fill=tk.X, pady=10)
    ttk.Button(btn_container, text="✖ Cerrar", command=ventana.destroy, width=25).pack(pady=5)
    
    cargar_clientes()

# ==================== GESTIÓN DE PRODUCTOS ====================
def abrir_gestion_productos():
    global rol_actual
    
    ventana = tk.Toplevel()
    ventana.title("ComercioTech - Gestión de Productos")
    ventana.geometry("1100x600")
    ventana.minsize(800, 500)
    ventana.transient(ventana_principal)
    ventana.grab_set()
    
    centrar_ventana(ventana, 1100, 600)
    
    main_frame = ttk.Frame(ventana, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    main_frame.grid_columnconfigure(0, weight=3)
    main_frame.grid_columnconfigure(1, weight=1)
    main_frame.grid_rowconfigure(1, weight=1)
    
    ttk.Label(main_frame, text="🛒 GESTIÓN DE PRODUCTOS", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
    
    left_frame = ttk.Frame(main_frame)
    left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
    left_frame.grid_rowconfigure(0, weight=1)
    left_frame.grid_columnconfigure(0, weight=1)
    
    columns = ("ID", "Nombre", "SKU", "Precio", "Stock", "Categoría")
    tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=20)
    
    col_widths = [50, 200, 100, 120, 80, 150]
    for i, col in enumerate(columns):
        tree.heading(col, text=col)
        tree.column(col, width=col_widths[i], minwidth=60)
    
    scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    tree.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")
    
    right_frame = ttk.Frame(main_frame)
    right_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
    
    ttk.Label(right_frame, text="⚡ ACCIONES", font=("Arial", 12, "bold")).pack(pady=(0, 10))
    ttk.Separator(right_frame, orient='horizontal').pack(fill=tk.X, pady=5)
    
    btn_container = ttk.Frame(right_frame)
    btn_container.pack(fill=tk.BOTH, expand=True, pady=10)
    
    def cargar_productos():
        for item in tree.get_children():
            tree.delete(item)
        productos = producto_service.listar_todos()
        for i, p in enumerate(productos, 1):
            tree.insert("", tk.END, values=(i, p.nombre, p.sku, f"${p.precio:,}", p.stock, p.categoria))
    
    def registrar_producto():
        if rol_actual != "admin":
            messagebox.showerror("Error", "No tiene permisos para registrar productos")
            return
        
        dialog = tk.Toplevel(ventana)
        dialog.title("Registrar Producto")
        dialog.geometry("420x500")
        dialog.transient(ventana)
        dialog.grab_set()
        centrar_ventana(dialog, 420, 500)
        
        ttk.Label(dialog, text="Registrar Nuevo Producto", font=("Arial", 12, "bold")).pack(pady=15)
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Nombre:").pack(anchor=tk.W)
        entry_nombre = ttk.Entry(frame, width=40)
        entry_nombre.pack(pady=(0, 10), fill=tk.X)
        
        ttk.Label(frame, text="SKU (XXX-000):").pack(anchor=tk.W)
        entry_sku = ttk.Entry(frame, width=40)
        entry_sku.pack(pady=(0, 10), fill=tk.X)
        
        ttk.Label(frame, text="Precio:").pack(anchor=tk.W)
        entry_precio = ttk.Entry(frame, width=40)
        entry_precio.pack(pady=(0, 10), fill=tk.X)
        
        ttk.Label(frame, text="Stock:").pack(anchor=tk.W)
        entry_stock = ttk.Entry(frame, width=40)
        entry_stock.pack(pady=(0, 10), fill=tk.X)
        
        ttk.Label(frame, text="Categoría:").pack(anchor=tk.W)
        entry_categoria = ttk.Entry(frame, width=40)
        entry_categoria.pack(pady=(0, 20), fill=tk.X)
        
        def guardar():
            nombre = entry_nombre.get().strip()
            sku = entry_sku.get().strip().upper()
            try:
                precio = int(entry_precio.get().strip())
                stock = int(entry_stock.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Precio y stock deben ser números")
                return
            categoria = entry_categoria.get().strip()
            
            if not all([nombre, sku, categoria]):
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return
            if not Validator.sku(sku):
                messagebox.showerror("Error", "SKU inválido (formato: XXX-000)")
                return
            
            producto = ProductoDTO(nombre=nombre, sku=sku, precio=precio, stock=stock, categoria=categoria)
            resultado = producto_service.crear(producto)
            if resultado:
                messagebox.showinfo("Éxito", "Producto registrado")
                cargar_productos()
                dialog.destroy()
            else:
                messagebox.showerror("Error", "No se pudo registrar (SKU duplicado?)")
        
        ttk.Button(frame, text="Guardar", command=guardar).pack(pady=10)
        ttk.Button(frame, text="Cancelar", command=dialog.destroy).pack()
    
    def buscar_producto():
        sku = simpledialog.askstring("Buscar Producto", "Ingrese el SKU del producto:")
        if sku:
            producto = producto_service.buscar_por_sku(sku.upper())
            if producto:
                messagebox.showinfo("Producto Encontrado",
                                   f"Nombre: {producto.nombre}\n"
                                   f"SKU: {producto.sku}\n"
                                   f"Precio: ${producto.precio:,}\n"
                                   f"Stock: {producto.stock}\n"
                                   f"Categoría: {producto.categoria}")
            else:
                messagebox.showerror("Error", "Producto no encontrado")
    
    def actualizar_stock():
        if rol_actual != "admin":
            messagebox.showerror("Error", "No tiene permisos para actualizar stock")
            return
        
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showerror("Error", "Seleccione un producto de la lista")
            return
        values = tree.item(seleccion[0])['values']
        sku = values[2]
        producto = producto_service.buscar_por_sku(sku)
        if producto:
            nuevo_stock = simpledialog.askinteger("Stock", f"Stock actual: {producto.stock}\nNuevo stock:")
            if nuevo_stock is not None:
                if producto_service.actualizar_stock(sku, nuevo_stock):
                    messagebox.showinfo("Éxito", "Stock actualizado")
                    cargar_productos()
                else:
                    messagebox.showerror("Error", "No se pudo actualizar")
    
    def eliminar_producto():
        if rol_actual != "admin":
            messagebox.showerror("Error", "No tiene permisos para eliminar productos")
            return
        
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showerror("Error", "Seleccione un producto de la lista")
            return
        values = tree.item(seleccion[0])['values']
        sku = values[2]
        if messagebox.askyesno("Confirmar", f"¿Eliminar producto '{values[1]}'?"):
            doc = producto_service.collection.find_one({"sku": sku})
            if doc and producto_service.collection.delete_one({"_id": doc['_id']}).deleted_count > 0:
                messagebox.showinfo("Éxito", "Producto eliminado")
                cargar_productos()
            else:
                messagebox.showerror("Error", "No se pudo eliminar")
    
    if rol_actual == "admin":
        ttk.Button(btn_container, text="📝 Registrar Producto", command=registrar_producto, width=25).pack(pady=5)
    
    ttk.Button(btn_container, text="🔍 Buscar Producto", command=buscar_producto, width=25).pack(pady=5)
    
    if rol_actual == "admin":
        ttk.Button(btn_container, text="📦 Actualizar Stock", command=actualizar_stock, width=25).pack(pady=5)
        ttk.Button(btn_container, text="❌ Eliminar Producto", command=eliminar_producto, width=25).pack(pady=5)
    
    ttk.Separator(btn_container, orient='horizontal').pack(fill=tk.X, pady=10)
    ttk.Button(btn_container, text="🔄 Actualizar Lista", command=cargar_productos, width=25).pack(pady=5)
    ttk.Button(btn_container, text="✖ Cerrar", command=ventana.destroy, width=25).pack(pady=5)
    
    cargar_productos()


# ==================== GESTIÓN DE PEDIDOS ====================
def abrir_gestion_pedidos():
    ventana = tk.Toplevel()
    ventana.title("ComercioTech - Gestión de Pedidos")
    ventana.geometry("1100x650")
    ventana.minsize(900, 550)
    ventana.transient(ventana_principal)
    ventana.grab_set()
    
    centrar_ventana(ventana, 1100, 650)
    
    main_frame = ttk.Frame(ventana, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    main_frame.grid_columnconfigure(0, weight=3)
    main_frame.grid_columnconfigure(1, weight=1)
    main_frame.grid_rowconfigure(1, weight=3)
    main_frame.grid_rowconfigure(2, weight=1)
    
    ttk.Label(main_frame, text="📦 GESTIÓN DE PEDIDOS", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
    
    # Tabla de pedidos
    left_frame = ttk.Frame(main_frame)
    left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
    left_frame.grid_rowconfigure(0, weight=3)
    left_frame.grid_rowconfigure(1, weight=1)
    left_frame.grid_columnconfigure(0, weight=1)
    
    columns = ("ID", "Cliente", "Email", "Total", "Estado")
    tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=12)
    
    col_widths = [200, 200, 220, 120, 100]
    for i, col in enumerate(columns):
        tree.heading(col, text=col)
        tree.column(col, width=col_widths[i], minwidth=80)
    
    scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    tree.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")
    
    # Detalle del pedido
    detalle_frame = ttk.LabelFrame(left_frame, text="📄 Detalle del Pedido Seleccionado", padding="10")
    detalle_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
    detalle_frame.grid_rowconfigure(0, weight=1)
    detalle_frame.grid_columnconfigure(0, weight=1)
    
    text_detalle = tk.Text(detalle_frame, height=6, wrap=tk.WORD)
    text_detalle.grid(row=0, column=0, sticky="nsew")
    
    # Botones
    right_frame = ttk.Frame(main_frame)
    right_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
    right_frame.grid_rowconfigure(2, weight=1)
    
    ttk.Label(right_frame, text="⚡ ACCIONES", font=("Arial", 12, "bold")).grid(row=0, column=0, pady=(0, 10))
    ttk.Separator(right_frame, orient='horizontal').grid(row=1, column=0, sticky="ew", pady=5)
    
    btn_container = ttk.Frame(right_frame)
    btn_container.grid(row=2, column=0, sticky="n", pady=10)
    
    def cargar_pedidos():
        for item in tree.get_children():
            tree.delete(item)
        pedidos = pedido_service.listar_todos()
        for p in pedidos:
            tree.insert("", tk.END, values=(
                str(p['_id'])[-12:],
                p.get('cliente_nombre', 'N/A'),
                p.get('cliente_email', 'N/A'),
                f"${p.get('total', 0):,}",
                p.get('estado', 'N/A').capitalize()
            ))
    
    def mostrar_detalle(event):
        seleccion = tree.selection()
        if not seleccion:
            return
        values = tree.item(seleccion[0])['values']
        pedido_id_abreviado = values[0]
        
        pedidos = pedido_service.listar_todos()
        pedido = None
        for p in pedidos:
            if str(p['_id'])[-12:] == pedido_id_abreviado:
                pedido = p
                break
        
        if pedido:
            text_detalle.delete(1.0, tk.END)
            text_detalle.insert(tk.END, "🛒 PRODUCTOS:\n")
            text_detalle.insert(tk.END, "═" * 50 + "\n")
            for item in pedido.get('items', []):
                subtotal = item['cantidad'] * item['precio']
                text_detalle.insert(tk.END, f"  • {item['nombre']}\n")
                text_detalle.insert(tk.END, f"    Cantidad: {item['cantidad']} x ${item['precio']:,} = ${subtotal:,}\n\n")
            text_detalle.insert(tk.END, "═" * 50 + "\n")
            text_detalle.insert(tk.END, f"💰 TOTAL DEL PEDIDO: ${pedido.get('total', 0):,}\n")
    
    def crear_pedido():
        # Pedir email del cliente
        email = simpledialog.askstring("Crear Pedido", "Ingrese el email del cliente:")
        if not email:
            return
        
        cliente = cliente_service.buscar_por_email(email)
        if not cliente:
            messagebox.showerror("Error", "Cliente no encontrado")
            return
        
        # Variable para almacenar items (usando nonlocal para modificarla dentro de funciones anidadas)
        items = []
        
        # Ventana principal del pedido
        pedido_window = tk.Toplevel(ventana)
        pedido_window.title("Crear Pedido - Cliente: " + cliente.nombre)
        pedido_window.geometry("650x550")
        pedido_window.transient(ventana)
        pedido_window.grab_set()
        centrar_ventana(pedido_window, 650, 550)
        
        # Frame principal
        main_frame2 = ttk.Frame(pedido_window, padding="10")
        main_frame2.pack(fill=tk.BOTH, expand=True)
        
        # Información del cliente
        info_frame = ttk.LabelFrame(main_frame2, text="Información del Cliente", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(info_frame, text=f"Nombre: {cliente.nombre}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Email: {cliente.email}").pack(anchor=tk.W)
        
        # Lista de productos agregados
        list_frame = ttk.LabelFrame(main_frame2, text="Productos Agregados", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        columns_items = ("Producto", "Cantidad", "Precio Unitario", "Subtotal")
        tree_items = ttk.Treeview(list_frame, columns=columns_items, show="headings", height=8)
        
        tree_items.heading("Producto", text="Producto")
        tree_items.heading("Cantidad", text="Cantidad")
        tree_items.heading("Precio Unitario", text="Precio Unitario")
        tree_items.heading("Subtotal", text="Subtotal")
        
        tree_items.column("Producto", width=200)
        tree_items.column("Cantidad", width=80)
        tree_items.column("Precio Unitario", width=120)
        tree_items.column("Subtotal", width=120)
        
        scroll_items = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree_items.yview)
        tree_items.configure(yscrollcommand=scroll_items.set)
        
        tree_items.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_items.pack(side=tk.RIGHT, fill=tk.Y)
        
        def actualizar_lista():
            for item in tree_items.get_children():
                tree_items.delete(item)
            total = 0
            for item in items:
                subtotal = item['cantidad'] * item['precio']
                total += subtotal
                tree_items.insert("", tk.END, values=(
                    item['nombre'],
                    item['cantidad'],
                    f"${item['precio']:,}",
                    f"${subtotal:,}"
                ))
            lbl_total.config(text=f"💰 TOTAL: ${total:,}")
        
        def eliminar_producto_seleccionado():
            seleccion = tree_items.selection()
            if seleccion:
                idx = tree_items.index(seleccion[0])
                producto_eliminado = items.pop(idx)
                producto = producto_service.buscar_por_sku(producto_eliminado.get('sku', ''))
                if producto:
                    producto_service.actualizar_stock(producto.sku, producto.stock + producto_eliminado['cantidad'])
                actualizar_lista()
                messagebox.showinfo("Eliminado", f"Producto '{producto_eliminado['nombre']}' eliminado del pedido")
        
        def agregar_producto():
            producto_window = tk.Toplevel(pedido_window)
            producto_window.title("Agregar Producto")
            producto_window.geometry("400x300")
            producto_window.transient(pedido_window)
            producto_window.grab_set()
            centrar_ventana(producto_window, 400, 300)
            
            ttk.Label(producto_window, text="Agregar Producto al Pedido", font=("Arial", 12, "bold")).pack(pady=15)
            
            frame = ttk.Frame(producto_window, padding="20")
            frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(frame, text="SKU del Producto:").pack(anchor=tk.W)
            entry_sku = ttk.Entry(frame, width=30)
            entry_sku.pack(pady=(5, 15), fill=tk.X)
            entry_sku.focus()
            
            ttk.Label(frame, text="Cantidad:").pack(anchor=tk.W)
            entry_cantidad = ttk.Entry(frame, width=30)
            entry_cantidad.pack(pady=(5, 20), fill=tk.X)
            
            def buscar_y_agregar():
                sku = entry_sku.get().strip().upper()
                if not sku:
                    messagebox.showerror("Error", "Ingrese un SKU")
                    return
                
                producto = producto_service.buscar_por_sku(sku)
                if not producto:
                    messagebox.showerror("Error", f"Producto con SKU '{sku}' no encontrado")
                    return
                
                try:
                    cantidad = int(entry_cantidad.get().strip())
                    if cantidad <= 0:
                        messagebox.showerror("Error", "La cantidad debe ser mayor a 0")
                        return
                    if cantidad > producto.stock:
                        messagebox.showerror("Error", f"Stock insuficiente. Stock disponible: {producto.stock}")
                        return
                except ValueError:
                    messagebox.showerror("Error", "Cantidad inválida")
                    return
                
                items.append({
                    'nombre': producto.nombre,
                    'cantidad': cantidad,
                    'precio': producto.precio
                })
                producto_service.actualizar_stock(producto.sku, producto.stock - cantidad)
                actualizar_lista()
                producto_window.destroy()
                messagebox.showinfo("Agregado", f"✅ {producto.nombre} x{cantidad} agregado")
            
            ttk.Button(frame, text="Agregar", command=buscar_y_agregar).pack(pady=10)
            ttk.Button(frame, text="Cancelar", command=producto_window.destroy).pack()
            entry_sku.bind("<Return>", lambda e: buscar_y_agregar())
        
        # Frame para el total y botones
        bottom_frame = ttk.Frame(main_frame2)
        bottom_frame.pack(fill=tk.X)
        
        lbl_total = ttk.Label(bottom_frame, text="💰 TOTAL: $0", font=("Arial", 12, "bold"))
        lbl_total.pack(side=tk.LEFT, pady=10)
        
        btn_frame_inner = ttk.Frame(main_frame2)
        btn_frame_inner.pack(fill=tk.X)
        
        ttk.Button(btn_frame_inner, text="➕ Agregar Producto", command=agregar_producto, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame_inner, text="❌ Eliminar Producto", command=eliminar_producto_seleccionado, width=20).pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(main_frame2, orient='horizontal').pack(fill=tk.X, pady=10)
        
        action_frame = ttk.Frame(main_frame2)
        action_frame.pack(fill=tk.X)
        
        def finalizar_pedido():
            if not items:
                messagebox.showerror("Error", "Debe agregar al menos un producto")
                return
            
            resultado = pedido_service.crear(email, items)
            if resultado:
                messagebox.showinfo("Éxito", f"Pedido creado con ID: {resultado}")
                cargar_pedidos()
                pedido_window.destroy()
            else:
                messagebox.showerror("Error", "No se pudo crear el pedido")
        
        ttk.Button(action_frame, text="✅ Finalizar Pedido", command=finalizar_pedido, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="✖ Cancelar Pedido", command=pedido_window.destroy, width=20).pack(side=tk.LEFT, padx=5)
    
    def cambiar_estado():
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showerror("Error", "Seleccione un pedido de la lista")
            return
        
        values = tree.item(seleccion[0])['values']
        pedido_id_abreviado = values[0]
        estado_actual = values[4].lower()
        
        pedidos = pedido_service.listar_todos()
        pedido_id = None
        for p in pedidos:
            if str(p['_id'])[-12:] == pedido_id_abreviado:
                pedido_id = str(p['_id'])
                break
        
        if not pedido_id:
            messagebox.showerror("Error", "No se encontró el pedido")
            return
        
        estados = ["pendiente", "enviado", "entregado", "cancelado"]
        nuevo_estado = simpledialog.askstring("Cambiar Estado", 
                                               f"Estado actual: {estado_actual}\n"
                                               f"Opciones: {', '.join(estados)}\n\n"
                                               "Nuevo estado:")
        
        if nuevo_estado and nuevo_estado.lower() in estados:
            if pedido_service.actualizar_estado(pedido_id, nuevo_estado.lower()):
                messagebox.showinfo("Éxito", "Estado actualizado")
                cargar_pedidos()
            else:
                messagebox.showerror("Error", "No se pudo actualizar")
        elif nuevo_estado:
            messagebox.showerror("Error", f"Estado inválido. Opciones: {', '.join(estados)}")
    
    # Botones
    ttk.Button(btn_container, text="🛒 Crear Pedido", command=crear_pedido, width=25).pack(pady=5)
    ttk.Button(btn_container, text="📋 Listar Pedidos", command=cargar_pedidos, width=25).pack(pady=5)
    ttk.Button(btn_container, text="🔄 Cambiar Estado", command=cambiar_estado, width=25).pack(pady=5)
    ttk.Button(btn_container, text="🔄 Actualizar Lista", command=cargar_pedidos, width=25).pack(pady=5)
    
    ttk.Separator(btn_container, orient='horizontal').pack(fill=tk.X, pady=10)
    ttk.Button(btn_container, text="✖ Cerrar", command=ventana.destroy, width=25).pack(pady=5)
    
    tree.bind("<<TreeviewSelect>>", mostrar_detalle)
    cargar_pedidos()


# ==================== PUNTO DE ENTRADA ====================
if __name__ == "__main__":
    iniciar_sesion()