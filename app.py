from flask import Flask, render_template_string, request, redirect, url_for, send_file
import webbrowser
import threading
import os
import datetime
from security import AegisSecurityManager
from monitor import AegisSecurityMonitor

app = Flask(__name__)
app.secret_key = "aegis_secret_key_maule"

security_manager = AegisSecurityManager()
security_monitor = AegisSecurityMonitor(threshold=2)

carrito_actual = []
ultima_boleta_datos = {}

# Interfaz Web Principal (POS + Inventario + Ciberseguridad)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aegis SecPyME Maule - Terminal POS & Seguridad</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 0; padding: 15px; color: #333; }
        .container { max-width: 1100px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h1, h2, h3 { color: #007acc; }
        .header { background: #007acc; color: white; padding: 15px; border-radius: 6px; text-align: center; margin-bottom: 20px; }
        .layout { display: flex; flex-wrap: wrap; gap: 20px; }
        .panel { flex: 1; min-width: 300px; background: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; margin-top: 10px; }
        .card { background: white; border: 2px solid #007acc; border-radius: 6px; padding: 12px; text-align: center; cursor: pointer; transition: 0.2s; }
        .card:hover { background: #eef2f7; transform: translateY(-2px); }
        .btn { background: #28a745; color: white; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%; margin-top: 10px; text-align: center; text-decoration: none; display: inline-block;}
        .btn-danger { background: #d9534f; }
        .btn-primary { background: #007acc; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; background: white; }
        th, td { border: 1px solid #cbd5e1; padding: 8px; text-align: left; font-size: 14px; }
        th { background-color: #007acc; color: white; }
        .total-box { background: #e2e8f0; padding: 12px; border-radius: 6px; margin-top: 15px; font-weight: bold; font-size: 16px; }
        select, input { width: 100%; padding: 8px; margin-top: 5px; margin-bottom: 10px; border: 1px solid #cbd5e1; border-radius: 4px; box-sizing: border-box;}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🛡️ AEGIS SECPYME MAULE — CENTRO DE CONTROL DIGITAL Y POS</h2>
            <p style="margin:0; font-size: 13px;">Solución Integral para Comercios y PyMEs de la Región del Maule</p>
        </div>

        <div class="layout">
            <!-- PANEL IZQUIERDO: TICKET DE VENTA Y PAGOS -->
            <div class="panel">
                <h3>🛒 Ticket de Venta Actual</h3>
                <table>
                    <tr>
                        <th>Producto</th>
                        <th>Cant</th>
                        <th>Subtotal</th>
                    </tr>
                    {% for item in carrito %}
                    <tr>
                        <td>{{ item.name }}</td>
                        <td>{{ item.qty }}</td>
                        <td>${{ item.qty * item.price }}</td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="3" style="text-align: center; color: #777;">El carrito está vacío</td>
                    </tr>
                    {% endfor %}
                </table>

                <div class="total-box">
                    <div>Subtotal: ${{ subtotal }}</div>
                    <div>IVA (19%): ${{ tax }}</div>
                    <div style="color: #28a745; font-size: 18px; margin-top: 5px;">TOTAL: ${{ total }}</div>
                </div>

                {% if carrito %}
                <form action="/procesar_pago" method="POST" style="margin-top: 15px;">
                    <label for="metodo"><b>Seleccione Medio de Pago:</b></label>
                    <select name="metodo" id="metodo">
                        <option value="Efectivo">Efectivo</option>
                        <option value="Tarjeta (Débito/Crédito)">Tarjeta (Débito / Crédito)</option>
                        <option value="Transferencia Bancaria">Transferencia Bancaria</option>
                    </select>
                    <button type="submit" class="btn">💳 Pagar y Mostrar Boleta en Pantalla</button>
                </form>
                <form action="/limpiar_carrito" method="POST">
                    <button type="submit" class="btn btn-danger" style="margin-top: 5px;">Cancelar Venta</button>
                </form>
                {% endif %}
            </div>

            <!-- PANEL DERECHO: CATÁLOGO TÁCTIL POS -->
            <div class="panel">
                <h3>📦 Catálogo Táctil Regional</h3>
                <p style="font-size: 12px; color: #666;">Haga clic en un producto para agregarlo al ticket:</p>
                <div class="grid">
                    {% for prod, info in inventory.items() %}
                    <form action="/agregar" method="POST">
                        <input type="hidden" name="producto" value="{{ prod }}">
                        <button type="submit" class="card" style="width: 100%;">
                            <b>{{ prod }}</b><br>
                            <span style="color: #007acc; font-weight: bold;">${{ info['precio'] }}</span><br>
                            <small>Stock: {{ info['stock'] }}</small>
                        </button>
                    </form>
                    {% endfor %}
                </div>
            </div>
        </div>

        <!-- SECCIÓN INVENTARIO Y REPOSICIÓN -->
        <div class="panel" style="margin-top: 20px;">
            <h3>📦 Gestión y Reposición de Inventario PyME</h3>
            <table>
                <tr>
                    <th>Producto Regional</th>
                    <th>Stock Actual</th>
                    <th>Precio Unitario</th>
                    <th>Acción</th>
                </tr>
                {% for prod, info in inventory.items() %}
                <tr>
                    <td><b>{{ prod }}</b></td>
                    <td>{{ info['stock'] }}</td>
                    <td>${{ info['precio'] }}</td>
                    <td>
                        <form action="/reponer" method="POST" style="display:inline; margin:0;">
                            <input type="hidden" name="producto" value="{{ prod }}">
                            <input type="number" name="cantidad" value="15" min="1" max="500" style="width: 60px; display:inline; padding: 4px;">
                            <button type="submit" class="btn-primary" style="padding: 5px 10px; border:none; border-radius:4px; color:white; cursor:pointer;">Reponer</button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </table>

            <h4 style="margin-top: 20px;">➕ Incorporar Nuevo Producto al Sistema</h4>
            <form action="/nuevo_producto" method="POST" style="display: flex; gap: 10px; flex-wrap: wrap;">
                <input type="text" name="nombre" placeholder="Nombre del producto" required style="flex: 2; margin:0;">
                <input type="number" name="stock" placeholder="Stock inicial" required style="flex: 1; margin:0;">
                <input type="number" name="precio" placeholder="Precio ($)" required style="flex: 1; margin:0;">
                <button type="submit" class="btn" style="flex: 1; margin:0; padding: 8px;">Registrar Producto</button>
            </form>
        </div>

        <!-- SECCIÓN CIBERSEGURIDAD -->
        <div class="panel" style="margin-top: 20px; border-color: #d9534f;">
            <h3 style="color: #d9534f;">🔒 Monitoreo Proactivo y Seguridad (AEGIS Vanguard)</h3>
            <p style="font-size: 13px;">{{ seguridad_msg }}</p>
            <a href="/escanear" class="btn btn-danger" style="display: inline-block; width: auto; margin-right: 10px;">🔍 Ejecutar Escaneo de Anomalías</a>
            <a href="/exportar_reporte" class="btn btn-primary" style="display: inline-block; width: auto;">📄 Descargar Reporte Ejecutivo (.txt)</a>
        </div>
    </div>
</body>
</html>
"""

# Plantilla HTML Boleta Estilo Voucher Detallado en Pantalla con opción de Impresión
BOLETA_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Boleta Electrónica - Aegis SecPyME Maule</title>
    <style>
        body { font-family: 'Courier New', Courier, monospace; background: #e2e8f0; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .voucher { background: white; padding: 30px; width: 340px; border-radius: 6px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
        h2, h3, p { text-align: center; margin: 6px 0; }
        .line { border-bottom: 1px dashed #333; margin: 12px 0; }
        table { width: 100%; font-size: 13px; }
        th, td { padding: 4px; text-align: left; }
        .totals { margin-top: 12px; font-size: 14px; }
        .btn-print { background: #28a745; color: white; border: none; padding: 12px; width: 100%; font-weight: bold; border-radius: 5px; cursor: pointer; margin-top: 15px; font-size: 14px; }
        .btn-print:hover { background: #218838; }
        .btn-back { background: #007acc; color: white; border: none; padding: 10px; width: 100%; font-weight: bold; border-radius: 5px; cursor: pointer; margin-top: 8px; text-decoration: none; display: block; text-align: center; box-sizing: border-box;}
        .btn-back:hover { background: #0056b3; }
        @media print {
            body { background: white; }
            .btn-print, .btn-back { display: none; }
            .voucher { box-shadow: none; width: 100%; padding: 0; }
        }
    </style>
</head>
<body>
    <div class="voucher">
        <h2>🛡️ AEGIS SECPYME MAULE</h2>
        <p><b>Comercio Seguro Regional</b></p>
        <p><small>Fecha: {{ fecha }}</small></p>
        <p><small>Medio de Pago: <b>{{ metodo }}</b></small></p>
        <div class="line"></div>
        <table>
            <tr><th>Cant</th><th>Producto</th><th>Total</th></tr>
            {% for item in carrito %}
            <tr>
                <td>{{ item.qty }}x</td>
                <td>{{ item.name }}</td>
                <td>${{ item.qty * item.price }}</td>
            </tr>
            {% endfor %}
        </table>
        <div class="line"></div>
        <div class="totals">
            <p>Subtotal: ${{ subtotal }}</p>
            <p>IVA (19%): ${{ tax }}</p>
            <p style="font-size: 16px; font-weight: bold;">TOTAL: ${{ total }}</p>
        </div>
        <div class="line"></div>
        <p><small>¡Gracias por su compra local!<br>Transacción blindada por Aegis Vanguard Security</small></p>
        
        <button class="btn-print" onclick="window.print()">🖨️ Imprimir / Guardar Voucher</button>
        <a href="/" class="btn-back">⬅️ Volver al Terminal POS</a>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    subtotal = sum(item['qty'] * item['price'] for item in carrito_actual)
    tax = int(subtotal * 0.19)
    total = subtotal + tax
    _, msg = security_monitor.analizar_alertas_logs()
    
    return render_template_string(
        HTML_TEMPLATE, 
        inventory=security_manager.inventory,
        carrito=carrito_actual,
        subtotal=subtotal,
        tax=tax,
        total=total,
        seguridad_msg=msg
    )

@app.route("/agregar", methods=["POST"])
def agregar():
    producto = request.form.get("producto")
    if producto in security_manager.inventory:
        stock_disponible = security_manager.inventory[producto]["stock"]
        precio = security_manager.inventory[producto]["precio"]
        
        found = False
        for item in carrito_actual:
            if item["name"] == producto:
                if item["qty"] < stock_disponible:
                    item["qty"] += 1
                found = True
                break
        if not found:
            if stock_disponible > 0:
                carrito_actual.append({"name": producto, "qty": 1, "price": precio})
    return redirect(url_for("index"))

@app.route("/limpiar_carrito", methods=["POST"])
def limpiar_carrito():
    carrito_actual.clear()
    return redirect(url_for("index"))

@app.route("/procesar_pago", methods=["POST"])
def procesar_pago():
    global ultima_boleta_datos
    if not carrito_actual:
        return redirect(url_for("index"))
    
    metodo = request.form.get("metodo", "Efectivo")
    subtotal = sum(item['qty'] * item['price'] for item in carrito_actual)
    tax = int(subtotal * 0.19)
    total = subtotal + tax
    
    # Descontar stock real
    for item in carrito_actual:
        if item["name"] in security_manager.inventory:
            security_manager.inventory[item["name"]]["stock"] -= item["qty"]

    # Almacenar en memoria para renderizar en pantalla
    ultima_boleta_datos = {
        "carrito": list(carrito_actual),
        "metodo": metodo,
        "subtotal": subtotal,
        "tax": tax,
        "total": total,
        "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    carrito_actual.clear()
    
    # Redirige explícitamente a la ruta que muestra la boleta en pantalla
    return redirect(url_for("ver_boleta"))

@app.route("/ver_boleta")
def ver_boleta():
    if not ultima_boleta_datos:
        return redirect(url_for("index"))
    return render_template_string(BOLETA_TEMPLATE, **ultima_boleta_datos)

@app.route("/reponer", methods=["POST"])
def reponer():
    producto = request.form.get("producto")
    try:
        cantidad = int(request.form.get("cantidad", 15))
    except ValueError:
        cantidad = 15
    security_manager.gestionar_inventario("Administrador", producto, cantidad)
    return redirect(url_for("index"))

@app.route("/nuevo_producto", methods=["POST"])
def nuevo_producto():
    nombre = request.form.get("nombre")
    try:
        stock = int(request.form.get("stock", 10))
        precio = int(request.form.get("precio", 1000))
    except ValueError:
        stock, precio = 10, 1000
    security_manager.agregar_nuevo_producto("Administrador", nombre, stock, precio)
    return redirect(url_for("index"))

@app.route("/escanear")
def escanear():
    _, msg = security_monitor.analizar_alertas_logs()
    return f"<script>alert('{msg}'); window.location.href='/';</script>"

@app.route("/exportar_reporte")
def exportar_reporte():
    exito, path = security_manager.exportar_reporte_ejecutivo()
    if exito:
        return send_file(path, as_attachment=True)
    return "Error al generar reporte", 500

if __name__ == "__main__":
    # Abre el navegador automáticamente en un hilo separado al iniciar
    def abrir_navegador():
        webbrowser.open("http://127.0.0.1:5000")

    threading.Timer(1.0, abrir_navegador).start()
    
    # Inicia el servidor web local
    app.run(host="127.0.0.1", port=5000, debug=False)
