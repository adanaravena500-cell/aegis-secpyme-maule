import datetime
import logging
import os

LOG_DIR = "logs"
BOLETAS_DIR = "boletas"
for d in [LOG_DIR, BOLETAS_DIR]:
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

# Limpiar handlers previos
for h in logging.root.handlers[:]:
    logging.root.removeHandler(h)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "aegis_maule_audit.log"),
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)

class AegisSecurityManager:
    def __init__(self):
        self.users = {
            "admin_maule": {"pass": "SecurePass2026!", "role": "Administrador"},
            "operador_local": {"pass": "Ventas123*", "role": "Operador"}
        }
        # Catálogo base optimizado para PyMEs del Maule
        self.inventory = {
            "Pan Amasado": {"stock": 50, "precio": 1200},
            "Queso de Fundo": {"stock": 20, "precio": 4500},
            "Vino Artesanal": {"stock": 15, "precio": 6000},
            "Empanada de Pino": {"stock": 30, "precio": 2000},
            "Mote con Huesillo": {"stock": 25, "precio": 1500},
            "Chicha de Curicó": {"stock": 18, "precio": 3500}
        }

    def authenticate(self, username, password):
        if username in self.users and self.users[username]["pass"] == password:
            logging.info(f"Éxito de autenticación [Aegis SecPyME Maule]: '{username}' (Rol: {self.users[username]['role']})")
            return self.users[username]["role"]
        else:
            logging.warning(f"ALERTA DE SEGURIDAD [Aegis SecPyME Maule]: Acceso fallido para '{username}'")
            return None

    def gestionar_inventario(self, role, producto, cantidad):
        if role not in ["Administrador", "Operador"]:
            logging.warning("ALERTA: Intento de modificación sin privilegios válidos.")
            return False, "Permisos insuficientes."

        if producto in self.inventory:
            self.inventory[producto]["stock"] += cantidad
            logging.info(f"Inventario actualizado: '{producto}' modificado en {cantidad}. Rol: {role}")
            return True, self.inventory[producto]["stock"]
        else:
            return False, "El producto no existe."

    def agregar_nuevo_producto(self, role, nombre, stock_inicial, precio):
        if role != "Administrador":
            logging.warning("ALERTA: Intento no autorizado de agregar producto.")
            return False, "Solo el Administrador puede registrar nuevos productos."
        
        nombre = nombre.strip()
        if not nombre:
            return False, "El nombre del producto no puede estar vacío."
        if nombre in self.inventory:
            return False, "El producto ya existe en el inventario."

        try:
            stock_inicial = int(stock_inicial)
            precio = int(precio)
            if stock_inicial < 0 or precio < 0:
                raise ValueError()
        except ValueError:
            return False, "El stock y el precio deben ser valores numéricos válidos."

        self.inventory[nombre] = {"stock": stock_inicial, "precio": precio}
        logging.info(f"Nuevo producto agregado: '{nombre}' (Stock: {stock_inicial}, Precio: ${precio}) por {role}")
        return True, "Producto agregado exitosamente."

    def generar_boleta(self, cart, metodo_pago, subtotal, tax, total):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        boleta_path = os.path.join(BOLETAS_DIR, f"boleta_{timestamp}.txt")
        try:
            with open(boleta_path, "w", encoding="utf-8") as f:
                f.write("====================================================\n")
                f.write("          AEGIS SECPYME MAULE - BOLETA DE VENTA     \n")
                f.write("====================================================\n")
                f.write(f"Fecha de Emisión: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Método de Pago:   {metodo_pago}\n")
                f.write("----------------------------------------------------\n")
                f.write(f"{'PRODUCTO':<20} | {'CANT':<5} | {'SUBTOTAL':<10}\n")
                f.write("-" * 52 + "\n")
                for item in cart:
                    sub = item['qty'] * item['price']
                    f.write(f"{item['name']:<20} | {item['qty']:<5} | ${sub:<9}\n")
                f.write("-" * 52 + "\n")
                f.write(f"Subtotal:        ${subtotal}\n")
                f.write(f"IVA (19%):       ${tax}\n")
                f.write(f"TOTAL GENERAL:   ${total}\n")
                f.write("====================================================\n")
                f.write(" ¡Gracias por preferir el comercio local del Maule!\n")
                f.write(" Transacción segura blindada por Aegis Vanguard Security\n")
            
            logging.info(f"Boleta electrónica generada: {boleta_path} (Pago: {metodo_pago})")
            return True, boleta_path
        except Exception as e:
            return False, str(e)

    def exportar_reporte_ejecutivo(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(LOG_DIR, f"reporte_ejecutivo_{timestamp}.txt")
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write("====================================================\n")
                f.write("       AEGIS SECPYME MAULE - REPORTE EJECUTIVO      \n")
                f.write("====================================================\n")
                f.write(f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("--- 1. INVENTARIO Y PRECIOS ACTUALES ---\n")
                for prod, data in self.inventory.items():
                    f.write(f"• {prod}: {data['stock']} unidades | Precio: ${data['precio']}\n")
                f.write("\n--- 2. LOGS DE AUDITORÍA Y SEGURIDAD ---\n")
                log_file = os.path.join(LOG_DIR, "aegis_maule_audit.log")
                if os.path.exists(log_file):
                    with open(log_file, "r", encoding="utf-8", errors="replace") as log_f:
                        f.write(log_f.read())
                else:
                    f.write("Sin registros previos.\n")
            return True, report_path
        except Exception as e:
            return False, str(e)