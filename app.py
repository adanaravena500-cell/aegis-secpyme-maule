from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import jwt
import datetime

app = Flask(__name__)
CORS(app)  # Indicador 7: CORS habilitado

# Clave secreta para JWT (Indicador 4)
SECRET_KEY = "aegis_secret_key_maule_2026"

# Base de datos simulada en memoria (recurso principal: Inventario de Productos)
inventario_db = [
    {"id": 1, "nombre": "Pan Amasado Artesanal (Kg)", "precio": 2500, "stock": 50},
    {"id": 2, "nombre": "Queso de Campo Maucho (Kg)", "precio": 8900, "stock": 20},
    {"id": 3, "nombre": "Vino Pajarete Curicano (750ml)", "precio": 6500, "stock": 15}
]

# --- RUTA PRINCIPAL: Interfaz Web con HTML/JS y fetch() (Indicadores 5 y 6) ---
FRONTEND_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Sistema de Inventario para Comercio Regional — Aegis SecPyME Maule (API y Panel Web)</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f4f8; color: #333; margin: 0; padding: 30px; }
        .container { max-width: 900px; margin: auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        h1 { color: #0284c7; border-bottom: 2px solid #0284c7; padding-bottom: 10px; font-size: 24px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; border: 1px solid #cbd5e1; text-align: left; }
        th { background: #0284c7; color: white; }
        form { background: #f8fafc; padding: 20px; border-radius: 8px; margin-top: 20px; border: 1px solid #e2e8f0; }
        input, button { padding: 10px; margin: 5px 0; width: 100%; box-sizing: border-box; border: 1px solid #cbd5e1; border-radius: 5px; }
        button { background: #0284c7; color: white; font-weight: bold; cursor: pointer; }
        button:hover { background: #0369a1; }
        .token-box { background: #ecfdf5; border: 1px solid #10b981; padding: 10px; margin-bottom: 15px; border-radius: 5px; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📦 Sistema de Inventario para Comercio Regional — Aegis SecPyME Maule</h1>
        <p>Panel web interactivo (API REST + Interfaz HTML con fetch() y JWT).</p>

        <div class="token-box">
            <b>Estado del Token JWT:</b> <span id="tokenStatus">Obteniendo token de autenticación...</span>
        </div>

        <h2>Listado de Productos en Tiempo Real</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Nombre del Producto</th>
                    <th>Precio ($ CLP)</th>
                    <th>Stock Actual</th>
                </tr>
            </thead>
            <tbody id="tablaProductos">
                <!-- Datos cargados dinámicamente con fetch() -->
            </tbody>
        </table>

        <h2>Registrar Nuevo Producto (Protegido por JWT)</h2>
        <form id="productForm">
            <input type="text" id="nombre" placeholder="Nombre del producto" required>
            <input type="number" id="precio" placeholder="Precio ($ CLP)" required>
            <input type="number" id="stock" placeholder="Stock inicial" required>
            <button type="submit">Agregar al Inventario</button>
        </form>
    </div>

    <script>
        let jwtToken = "";

        // 1. Obtener Token JWT automáticamente al cargar la página
        async function obtenerToken() {
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({usuario: "admin_aegis", password: "123"})
                });
                const data = await response.json();
                jwtToken = data.token;
                document.getElementById("tokenStatus").innerText = "Token JWT activo y verificado ✅";
            } catch (error) {
                document.getElementById("tokenStatus").innerText = "Error al obtener token ❌";
            }
        }

        // 2. Cargar productos usando fetch() (Indicador 5)
        async function cargarInventario() {
            try {
                const response = await fetch('/api/productos');
                const productos = await response.json();
                const tbody = document.getElementById("tablaProductos");
                tbody.innerHTML = "";
                productos.forEach(p => {
                    tbody.innerHTML += `<tr>
                        <td>${p.id}</td>
                        <td>${p.nombre}</td>
                        <td>$${p.precio.toLocaleString()}</td>
                        <td>${p.stock} un.</td>
                    </tr>`;
                });
            } catch (error) {
                console.error("Error al cargar inventario:", error);
            }
        }

        // 3. Enviar nuevo producto con formulario (Indicador 6)
        document.getElementById("productForm").addEventListener("submit", async (e) => {
            e.preventDefault();
            const nuevoProducto = {
                nombre: document.getElementById("nombre").value,
                precio: Number(document.getElementById("precio").value),
                stock: Number(document.getElementById("stock").value)
            };

            const response = await fetch('/api/productos', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + jwtToken // Indicador 4: Envío de JWT
                },
                body: JSON.stringify(nuevoProducto)
            });

            if (response.ok) {
                document.getElementById("productForm").reset();
                cargarInventario(); // Actualiza la lista sin recargar la página
            } else {
                alert("Error al registrar producto (Verifique datos / Validación 400).");
            }
        });

        // Inicializar al cargar
        window.onload = async () => {
            await obtenerToken();
            cargarInventario();
        };
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(FRONTEND_HTML)

# --- RUTA DE AUTENTICACIÓN (Generación de Token JWT) ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if data and data.get("usuario") == "admin_aegis" and data.get("password") == "123":
        token = jwt.encode({
            'user': data["usuario"],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, SECRET_KEY, algorithm="HS256")
        return jsonify({"token": token})
    return jsonify({"error": "Credenciales inválidas"}), 401

# --- API REST: ENDPOINTS CRUD (Indicador 1 y 2) ---

# 1. Listar todos los productos (GET)
@app.route('/api/productos', methods=['GET'])
def listar_productos():
    return jsonify(inventario_db), 200

# 2. Listar un producto por ID (GET)
@app.route('/api/productos/<int:id>', methods=['GET'])
def obtener_producto(id):
    producto = next((p for p in inventario_db if p["id"] == id), None)
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404
    return jsonify(producto), 200

# 3. Crear producto con validación estricta y protección JWT (Indicadores 3 y 4)
@app.route('/api/productos', methods=['POST'])
def crear_producto():
    # Validación de Autenticación JWT
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Token JWT ausente o inválido"}), 401
    
    token = auth_header.split(" ")[1]
    try:
        jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401

    # Recepción y Validación de Datos (Indicador 3: Status 400 ante datos inválidos)
    data = request.get_json()
    if not data or not data.get("nombre") or data.get("precio", 0) <= 0 or data.get("stock", -1) < 0:
        return jsonify({"error": "Datos inválidos: nombre requerido, precio > 0 y stock >= 0"}), 400

    nuevo_id = max([p["id"] for p in inventario_db], default=0) + 1
    nuevo_producto = {
        "id": nuevo_id,
        "nombre": data["nombre"],
        "precio": data["precio"],
        "stock": data["stock"]
    }
    inventario_db.append(nuevo_producto)
    return jsonify(nuevo_producto), 201

# 4. Actualizar producto (PUT)
@app.route('/api/productos/<int:id>', methods=['PUT'])
def actualizar_producto(id):
    producto = next((p for p in inventario_db if p["id"] == id), None)
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404

    data = request.get_json()
    if not data or data.get("precio", 0) <= 0 or data.get("stock", -1) < 0:
        return jsonify({"error": "Datos de actualización inválidos"}), 400

    producto["nombre"] = data.get("nombre", producto["nombre"])
    producto["precio"] = data.get("precio", producto["precio"])
    producto["stock"] = data.get("stock", producto["stock"])
    return jsonify(producto), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)