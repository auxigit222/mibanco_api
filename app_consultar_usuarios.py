from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Configuración de la base de datos
db_config = {
    'host': 'localhost', 
    'port': '3306', 
    'user': 'root',
    'password': 'T3cn0l0g1a**',  
    'database': 'aplication_web'
}

@app.route('/')
def home():
    return '<h1>Bienvenido a la API</h1>'

# Ruta para la consulta de clientes
@app.route('/MBconsulta', methods=['POST'])
def consulta_clientes():
    try:
        data = request.json
        id_cliente = data.get("IdCliente")  
        monto = data.get("Monto")          
        telefono_comercio = data.get("TelefonoComercio")  

        # Validar que el monto esté presente y no sea vacío
        if monto and isinstance(monto, str) and monto.strip():
            return jsonify({"status": True})
        else:
            return jsonify({"status": False})

    except Exception as ex:
        return jsonify({"status": False, "error": str(ex)})

@app.route('/MBnotifica', methods=['POST'])
def MBnotifica():
    data = request.json

    # Validar campos requeridos
    required_fields = ["IdComercio", "TelefonoComercio", "TelefonoEmisor", "Concepto", "BancoEmisor", "Monto", "Referencia", "CodigoRed"]
    for field in required_fields:
        if field not in data:
            return jsonify({"abono": False}), 400

    connection = None  # Inicializar la variable aquí
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Insertar datos en la tabla
        sql_insert_query = """INSERT INTO usuarios_mibanco (IdComercio, TelefonoComercio, TelefonoEmisor, Concepto, BancoEmisor, Monto, Referencia, CodigoRed)
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql_insert_query, (
            data['IdComercio'],
            data['TelefonoComercio'],
            data.get('TelefonoEmisor'),
            data.get('Concepto'),
            data['BancoEmisor'],
            data['Monto'],
            data['Referencia'],
            data['CodigoRed']
        ))

        connection.commit()  # Confirmar la transacción
        return jsonify({"abono": True}), 200

    except Error as e:
        print(f"Error: {e}")
        return jsonify({"abono": False}), 500

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)

"""
from flask import Flask, jsonify, request

app = Flask(__name__)


# Simulación de usuarios en memoria
usuarios = [
    {"IdCliente": "13536734", "Nombre": "Juan Perez"},
    {"IdCliente": "98765432", "Nombre": "Maria Gomez"},
]

# Lógica de validación
def validar_monto(monto):
    try:
        monto_float = float(monto)
        return monto_float > 0  # Validar que el monto sea positivo
    except ValueError:
        return False  # Si no se puede convertir a float, es inválido

def validar_telefono(telefono):
    return telefono.isdigit() and len(telefono) == 11  # Validar que sea un número de 11 dígitos

@app.route('/')
def home():
    return '<h1>Bienvenido a la API</h1>'

@app.route('/MBconsulta', methods=['POST'])
def consulta_clientes():
    try:
        data = request.json
        id_cliente = data.get("IdCliente")
        monto = data.get("Monto")
        telefono_comercio = data.get("TelefonoComercio")

        # Validar el usuario en la lista
        usuario = next((user for user in usuarios if user["IdCliente"] == id_cliente), None)

        if usuario and validar_monto(monto) and validar_telefono(telefono_comercio):
            return jsonify({"status": True})
        else:
            return jsonify({"status": False})


    except Exception as ex:
        return jsonify({"status": False, "error": str(ex)})

@app.errorhandler(404)
def pagina_no_encontrada(error):
    return '<h1>La página que intenta buscar NO existe</h1>', 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
"""
