from flask import Flask, request, jsonify
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import os
import re
from datetime import datetime

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

def verificar_token(token_recibido):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        # Buscar el token recibido en la base de datos
        cursor.execute("SELECT tokens FROM tokens WHERE tokens = %s", (token_recibido,))
        result = cursor.fetchone()
        print(f"Token recibido: {token_recibido}")  # Print del token recibido

        
        return result is not None
    except Error as e:
        print(f"Error al verificar el token: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/')
def home():
    return '<h1>Bienvenido a la API</h1>'

@app.route('/MBconsulta', methods=['POST'])
def consulta_clientes():
    try:
        headers = request.headers
        
        print(f"Headers recibidos: {headers}")  # Print de los headers
        
        token_recibido = headers.get('Authorization')
        print(f"Token recibido en MBconsulta: {token_recibido}")  # Print del token recibido

        if not token_recibido:
            return jsonify({"status": False, "error": "Falta el token de autorización."}), 401

        if not verificar_token(token_recibido):
            return jsonify({"status": False, "error": "Token no válido."}), 403

        data = request.json
        id_cliente = data.get("IdCliente")
        monto = data.get("Monto")
        telefono_comercio = data.get("TelefonoComercio")

        if (id_cliente and isinstance(id_cliente, str) and id_cliente.strip() and
                monto and isinstance(monto, str) and monto.strip() and
                telefono_comercio and isinstance(telefono_comercio, str) and telefono_comercio.strip()):
            return jsonify({"status": True})
        else:
            return jsonify({"status": False, "error": "Faltan datos obligatorios en el JSON."})

    except Exception as ex:
        return jsonify({"status": False, "error": str(ex)})

@app.route('/MBnotifica', methods=['POST'])
def MBnotifica():
    connection = None  
    try:
       
        headers = request.headers
        print(f"Headers recibidos: {headers}")  # Print de los headers
        
        token_recibido = headers.get('Authorization')
        print(f"Token recibido en MBnotifica: {token_recibido}")  # Print del token recibido

        if not token_recibido:
            return jsonify({"abono": False, "error": "Falta el token de autorización."}), 401

        if not verificar_token(token_recibido):
            return jsonify({"abono": False, "error": "Token no válido."}), 403

        data = request.json
        required_fields = ["IdComercio", "TelefonoComercio", "TelefonoEmisor", "Concepto", 
                           "BancoEmisor", "Monto", "FechaHora", "Referencia", "CodigoRed"]
        
        for field in required_fields:
            if field not in data:
                return jsonify({"abono": False, "error": f"El campo '{field}' es obligatorio."}), 400

        id_comercio = data.get("IdComercio")
        if not isinstance(id_comercio, str) or not id_comercio.isalnum() or len(id_comercio) > 20:
            return jsonify({"abono": False, "error": "El 'IdComercio' debe ser alfanumérico y de hasta 20 caracteres."}), 400

        telefono_comercio = data.get("TelefonoComercio")
        if not isinstance(telefono_comercio, str) or not re.match(r"^\d{10,15}$", telefono_comercio):
            return jsonify({"abono": False, "error": "El 'TelefonoComercio' debe ser un número de 10 a 15 dígitos."}), 400

        telefono_emisor = data.get("TelefonoEmisor")
        if not isinstance(telefono_emisor, str) or not re.match(r"^\d{10,15}$", telefono_emisor):
            return jsonify({"abono": False, "error": "El 'TelefonoEmisor' debe ser un número de 10 a 15 dígitos."}), 400

        concepto = data.get("Concepto")
        if not isinstance(concepto, str) or len(concepto) > 50:
            return jsonify({"abono": False, "error": "El 'Concepto' debe ser una cadena de hasta 50 caracteres."}), 400

        banco_emisor = data.get("BancoEmisor")
        if not isinstance(banco_emisor, str) or not re.match(r"^\d{3}$", banco_emisor):
            return jsonify({"abono": False, "error": "El 'BancoEmisor' debe ser un código de 3 dígitos."}), 400

        monto = data.get("Monto")
        if not isinstance(monto, str) or not re.match(r"^\d+(\.\d{1,2})?$", monto) or float(monto) <= 0:
            return jsonify({"abono": False, "error": "El 'Monto' debe ser un número válido mayor que cero, con hasta dos decimales."}), 400

        fecha_hora = data.get("FechaHora")
        if not isinstance(fecha_hora, str) or not re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$", fecha_hora):
            return jsonify({"abono": False, "error": "El 'FechaHora' debe estar en el formato 'YYYY-MM-DDTHH:MM:SS.sssZ'."}), 400
        
        try:
            fecha_hora_dt = datetime.strptime(fecha_hora, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            return jsonify({"abono": False, "error": "El 'FechaHora' no es una fecha válida."}), 400

        referencia = data.get("Referencia")
        if not isinstance(referencia, str) or not referencia.isalnum() or len(referencia) > 50:
            return jsonify({"abono": False, "error": "La 'Referencia' debe ser alfanumérica y de hasta 50 caracteres."}), 400

        codigo_red = data.get("CodigoRed")
        if not isinstance(codigo_red, str) or not (2 <= len(codigo_red) <= 5) or not codigo_red.isalnum():
            return jsonify({"abono": False, "error": "El 'CodigoRed' debe ser alfanumérico y tener entre 3 y 5 caracteres."}), 400

        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        sql_insert_query = """INSERT INTO registros_mibanco 
                              (IdComercio, TelefonoComercio, TelefonoEmisor, Concepto, BancoEmisor, 
                              Monto, FechaHora, Fecha, Hora, Referencia, CodigoRed)
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql_insert_query, (
            id_comercio,
            telefono_comercio,
            telefono_emisor,
            concepto,
            banco_emisor,
            monto,
            fecha_hora,
            fecha_hora_dt.strftime("%Y-%m-%d"),
            fecha_hora_dt.strftime("%H:%M:%S"),
            referencia,
            codigo_red
        ))

        connection.commit()
        return jsonify({"abono": True}), 200

    except Error as e:
        return jsonify({"abono": False, "error": str(e)}), 500

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
   app.run(host="0.0.0.0", debug=True)
