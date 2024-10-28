from flask import Flask, request, jsonify
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)
load_dotenv()

# Configuración de la base de datos
db_config = {
    'host': os.getenv('host'),
    'port': int(os.getenv('port')),
    'user': os.getenv('user'),
    'password': os.getenv('password'),
    'database': os.getenv('database')
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

        if monto and isinstance(monto, str) and monto.strip():
            return jsonify({"status": True})
        else:
            return jsonify({"status": False})

    except Exception as ex:
        return jsonify({"status": False, "error": str(ex)})

@app.route('/MBnotifica', methods=['POST'])
def MBnotifica():
    data = request.json

    required_fields = ["IdComercio", "TelefonoComercio", "TelefonoEmisor", "Concepto", "BancoEmisor", "Monto", "Referencia", "CodigoRed"]
    for field in required_fields:
        if field not in data:
            return jsonify({"abono": False}), 400

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

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

        connection.commit()
        return jsonify({"abono": True}), 200

    except Error as e:
        print(f"Error: {e}")
        return jsonify({"abono": False, "error": str(e)}), 500

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002)
