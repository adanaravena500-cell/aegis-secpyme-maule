import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                             QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, 
                             QMessageBox, QTableWidget, QTableWidgetItem, QTabWidget,
                             QGridLayout, QFrame, QInputDialog)
from PyQt6.QtCore import Qt

from core.security import AegisSecurityManager
from core.monitor import AegisSecurityMonitor

class AegisMainWindow(QMainWindow):
    def __init__(self, role, username):
        super().__init__()
        self.role = role
        self.username = username
        self.security_manager = AegisSecurityManager()
        self.security_monitor = AegisSecurityMonitor(threshold=2)
        self.cart = []
        
        self.setWindowTitle(f"Aegis SecPyME Maule - Sistema POS & Ciberseguridad [{role.upper()}: {username}]")
        self.resize(1024, 700)
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        header_label = QLabel("🛡️ AEGIS SECPYME MAULE — CENTRO DE CONTROL DIGITAL Y SEGURO")
        header_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #007acc; padding: 10px; background-color: #f0f4f8; border-radius: 5px;")
        layout.addWidget(header_label)

        tabs = QTabWidget()
        layout.addWidget(tabs)

        # ==========================================
        # PESTAÑA 1: TERMINAL POS COMERCIAL
        # ==========================================
        pos_tab = QWidget()
        pos_main_layout = QHBoxLayout(pos_tab)

        left_panel = QVBoxLayout()
        ticket_title = QLabel("🛒 VENTA ACTUAL (TICKET)")
        ticket_title.setStyleSheet("font-weight: bold; color: #333; font-size: 13px;")
        left_panel.addWidget(ticket_title)

        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(3)
        self.cart_table.setHorizontalHeaderLabels(["Producto", "Cant.", "Subtotal"])
        left_panel.addWidget(self.cart_table)

        totals_frame = QFrame()
        totals_frame.setStyleSheet("background-color: #eef2f7; border-radius: 6px; padding: 8px;")
        totals_layout = QVBoxLayout(totals_frame)
        
        self.lbl_subtotal = QLabel("Subtotal: $0")
        self.lbl_tax = QLabel("IVA (19%): $0")
        self.lbl_total = QLabel("TOTAL GENERAL: $0")
        self.lbl_total.setStyleSheet("font-size: 16px; font-weight: bold; color: #28a745;")
        
        totals_layout.addWidget(self.lbl_subtotal)
        totals_layout.addWidget(self.lbl_tax)
        totals_layout.addWidget(self.lbl_total)
        left_panel.addWidget(totals_frame)

        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet("background-color: #d9534f; color: white; font-weight: bold; padding: 8px;")
        btn_cancel.clicked.connect(self.clear_cart)
        
        self.btn_pay = QPushButton("💳 Procesar Pago & Boleta")
        self.btn_pay.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 8px; font-size: 13px;")
        self.btn_pay.clicked.connect(self.process_payment)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(self.btn_pay)
        left_panel.addLayout(btn_layout)

        pos_main_layout.addLayout(left_panel, 45)

        right_panel = QVBoxLayout()
        catalog_title = QLabel("📦 CATÁLOGO TÁCTIL DE PRODUCTOS")
        catalog_title.setStyleSheet("font-weight: bold; color: #333; font-size: 13px;")
        right_panel.addWidget(catalog_title)

        self.grid_products = QGridLayout()
        self.refresh_pos_catalog_grid()
        right_panel.addLayout(self.grid_products)
        right_panel.addStretch()

        pos_main_layout.addLayout(right_panel, 55)
        tabs.addTab(pos_tab, "🖥️ Terminal POS Comercial")

        # ==========================================
        # PESTAÑA 2: GESTIÓN DE INVENTARIO Y NUEVOS PRODUCTOS
        # ==========================================
        inv_tab = QWidget()
        inv_layout = QVBoxLayout(inv_tab)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Producto Regional", "Stock Actual", "Precio Unitario"])
        self.load_inventory_data()
        inv_layout.addWidget(self.table)

        inv_buttons_layout = QHBoxLayout()
        
        btn_restock = QPushButton("⚡ Reponer Stock del Producto Seleccionado")
        btn_restock.setStyleSheet("background-color: #007acc; color: white; padding: 10px; font-weight: bold; border-radius: 4px;")
        btn_restock.clicked.connect(self.restock_selected_product)
        
        btn_add_product = QPushButton("➕ Incorporar Nuevo Producto")
        btn_add_product.setStyleSheet("background-color: #28a745; color: white; padding: 10px; font-weight: bold; border-radius: 4px;")
        btn_add_product.clicked.connect(self.add_new_product_dialog)

        inv_buttons_layout.addWidget(btn_restock)
        inv_buttons_layout.addWidget(btn_add_product)
        inv_layout.addLayout(inv_buttons_layout)
        
        tabs.addTab(inv_tab, "📦 Control de Inventario PyME")

        # ==========================================
        # PESTAÑA 3: CIBERSEGURIDAD & LOGS
        # ==========================================
        sec_tab = QWidget()
        sec_layout = QVBoxLayout(sec_tab)
        
        sec_info = QLabel(
            "🔒 ESTADO DE SEGURIDAD Y DEFENSA ACTIVA\n\n"
            "• Arquitectura: Blindaje de datos mediante Control de Acceso Basado en Roles (RBAC).\n"
            "• Trazabilidad: Registro inmutable de eventos críticos en carpeta local /logs.\n"
            "• Monitoreo Proactivo: Detección automatizada de anomalías y alertas de acceso.\n"
            "• Enfoque Regional: Solución optimizada para la resiliencia de PyMEs del Maule.\n\n"
            "Estado del Nodo: Operativo y Protegido por AEGIS Vanguard Security."
        )
        sec_info.setStyleSheet("font-size: 13px; padding: 12px; color: #333; line-height: 1.4;")
        sec_layout.addWidget(sec_info)

        btn_monitor = QPushButton("🔍 Ejecutar Escaneo de Monitoreo Proactivo")
        btn_monitor.setStyleSheet("background-color: #d9534f; color: white; padding: 10px; font-weight: bold; border-radius: 4px;")
        btn_monitor.clicked.connect(self.run_security_scan)
        sec_layout.addWidget(btn_monitor)

        btn_export = QPushButton("📄 Exportar Reporte Ejecutivo de Auditoría (.txt)")
        btn_export.setStyleSheet("background-color: #28a745; color: white; padding: 10px; font-weight: bold; border-radius: 4px;")
        btn_export.clicked.connect(self.export_report_action)
        sec_layout.addWidget(btn_export)
        
        tabs.addTab(sec_tab, "🛡️ Ciberseguridad & Logs")

    # --- FUNCIONES DE POS Y CATÁLOGO ---
    def refresh_pos_catalog_grid(self):
        # Limpiar grid anterior si existe
        for i in reversed(range(self.grid_products.count())): 
            widget = self.grid_products.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        row, col = 0, 0
        for prod, info in self.security_manager.inventory.items():
            btn_prod = QPushButton(f"{prod}\n${info['precio']}\nStock: {info['stock']}")
            btn_prod.setStyleSheet("""
                background-color: #ffffff; 
                border: 2px solid #007acc; 
                border-radius: 8px; 
                font-weight: bold; 
                color: #004080;
                font-size: 12px;
                padding: 12px;
            """)
            btn_prod.clicked.connect(lambda checked, p=prod: self.add_to_cart(p))
            self.grid_products.addWidget(btn_prod, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

    def add_to_cart(self, product_name):
        item_data = self.security_manager.inventory[product_name]
        if item_data["stock"] <= 0:
            QMessageBox.warning(self, "Sin Stock", f"El producto '{product_name}' no cuenta con stock disponible.")
            return

        found = False
        for cart_item in self.cart:
            if cart_item["name"] == product_name:
                if cart_item["qty"] < item_data["stock"]:
                    cart_item["qty"] += 1
                    found = True
                else:
                    QMessageBox.warning(self, "Stock Límite", "No puedes agregar más unidades que el stock actual.")
                    return
                break
        
        if not found:
            self.cart.append({"name": product_name, "qty": 1, "price": item_data["precio"]})

        self.update_cart_display()

    def update_cart_display(self):
        self.cart_table.setRowCount(len(self.cart))
        subtotal_general = 0
        for row, item in enumerate(self.cart):
            subtotal = item["qty"] * item["price"]
            subtotal_general += subtotal
            self.cart_table.setItem(row, 0, QTableWidgetItem(item["name"]))
            self.cart_table.setItem(row, 1, QTableWidgetItem(str(item["qty"])))
            self.cart_table.setItem(row, 2, QTableWidgetItem(f"${subtotal}"))

        tax = int(subtotal_general * 0.19)
        total = subtotal_general + tax

        self.lbl_subtotal.setText(f"Subtotal: ${subtotal_general}")
        self.lbl_tax.setText(f"IVA (19%): ${tax}")
        self.lbl_total.setText(f"TOTAL GENERAL: ${total}")
        self.btn_pay.setText(f"💳 Pagar (${total})")

    def clear_cart(self):
        self.cart = []
        self.update_cart_display()

    def process_payment(self):
        if not self.cart:
            QMessageBox.warning(self, "Carrito Vacío", "Agregue productos al ticket antes de procesar el pago.")
            return

        # Selección de medio de pago
        metodos = ["Efectivo", "Tarjeta (Débito / Crédito)", "Transferencia Bancaria"]
        metodo_pago, ok = QInputDialog.getItem(self, "Medio de Pago", "Seleccione el método de pago:", metodos, 0, False)
        
        if not ok:
            return

        subtotal = sum(item['qty'] * item['price'] for item in self.cart)
        tax = int(subtotal * 0.19)
        total = subtotal + tax

        # Descontar stock real
        for item in self.cart:
            self.security_manager.inventory[item["name"]]["stock"] -= item["qty"]

        # Generar boleta digital
        exito, path = self.security_manager.generar_boleta(self.cart, metodo_pago, subtotal, tax, total)

        if exito:
            QMessageBox.information(
                self, 
                "¡Venta Exitosa!", 
                f"Pago procesado mediante {metodo_pago}.\n\nBoleta electrónica generada y guardada con éxito en:\n{os.path.abspath(path)}"
            )
            self.clear_cart()
            self.load_inventory_data()
            self.refresh_pos_catalog_grid()
        else:
            QMessageBox.critical(self, "Error", f"No se pudo generar la boleta: {path}")

    # --- FUNCIONES DE INVENTARIO Y GESTIÓN ---
    def load_inventory_data(self):
        inventory = self.security_manager.inventory
        self.table.setRowCount(len(inventory))
        for row, (prod, data) in enumerate(inventory.items()):
            self.table.setItem(row, 0, QTableWidgetItem(prod))
            self.table.setItem(row, 1, QTableWidgetItem(str(data["stock"])))
            self.table.setItem(row, 2, QTableWidgetItem(f"${data['precio']}"))

    def restock_selected_product(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Selección Requerida", "Por favor, seleccione un producto de la tabla para reponer su stock.")
            return

        producto_nombre = self.table.item(selected_row, 0).text()
        cantidad, ok = QInputDialog.getInt(self, "Reponer Stock", f"Ingrese cantidad a sumar para '{producto_nombre}':", 10, 1, 1000, 1)
        
        if ok:
            exito, res = self.security_manager.gestionar_inventario(self.role, producto_nombre, cantidad)
            if exito:
                QMessageBox.information(self, "Stock Actualizado", f"Se han añadido {cantidad} unidades a '{producto_nombre}'.\nNuevo stock: {res}")
                self.load_inventory_data()
                self.refresh_pos_catalog_grid()
            else:
                QMessageBox.warning(self, "Acceso Denegado", str(res))

    def add_new_product_dialog(self):
        if self.role != "Administrador":
            QMessageBox.warning(self, "Acceso Denegado", "Solo el perfil Administrador puede incorporar nuevos productos.")
            return

        nombre, ok1 = QInputDialog.getText(self, "Nuevo Producto", "Ingrese el nombre del nuevo producto regional:")
        if not ok1 or not nombre.strip():
            return

        stock, ok2 = QInputDialog.getInt(self, "Stock Inicial", f"Ingrese el stock inicial para '{nombre}':", 20, 0, 10000, 1)
        if not ok2:
            return

        precio, ok3 = QInputDialog.getInt(self, "Precio Unitario ($)", f"Ingrese el precio en pesos para '{nombre}':", 2500, 1, 1000000, 100)
        if not ok3:
            return

        exito, mensaje = self.security_manager.agregar_nuevo_producto(self.role, nombre, stock, precio)
        if exito:
            QMessageBox.information(self, "Éxito", mensaje)
            self.load_inventory_data()
            self.refresh_pos_catalog_grid()
        else:
            QMessageBox.warning(self, "Error", mensaje)

    def run_security_scan(self):
        count, mensaje = self.security_monitor.analizar_alertas_logs()
        if count >= self.security_monitor.threshold:
            QMessageBox.critical(self, "¡Alerta de Seguridad Activa!", mensaje)
        else:
            QMessageBox.information(self, "Resultado del Escaneo", mensaje)

    def export_report_action(self):
        exito, path = self.security_manager.exportar_reporte_ejecutivo()
        if exito:
            QMessageBox.information(self, "Reporte Exportado", f"¡Reporte generado con éxito!\nGuardado en:\n{os.path.abspath(path)}")
        else:
            QMessageBox.critical(self, "Error", f"No se pudo generar el reporte: {path}")

class AegisLoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.security_manager = AegisSecurityManager()
        self.setWindowTitle("Aegis SecPyME Maule - Autenticación")
        self.resize(360, 240)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("🔑 Aegis SecPyME Maule\nPortal de Acceso Seguro")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 15px; color: #222; margin-bottom: 10px;")
        layout.addWidget(title)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Usuario (ej. admin_maule)")
        self.user_input.setStyleSheet("padding: 8px; font-size: 13px;")
        layout.addWidget(self.user_input)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Contraseña")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setStyleSheet("padding: 8px; font-size: 13px;")
        layout.addWidget(self.pass_input)

        login_btn = QPushButton("Iniciar Sesión Segura")
        login_btn.setStyleSheet("background-color: #007acc; color: white; font-weight: bold; padding: 10px; border-radius: 4px;")
        login_btn.clicked.connect(self.handle_login)
        layout.addWidget(login_btn)

    def handle_login(self):
        username = self.user_input.text().strip()
        password = self.pass_input.text().strip()
        role = self.security_manager.authenticate(username, password)
        
        if role:
            self.main_window = AegisMainWindow(role, username)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Alerta de Seguridad", "Credenciales inválidas. Intento registrado en la auditoría.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = AegisLoginWindow()
    login.show()
    sys.exit(app.exec())