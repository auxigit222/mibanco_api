import uuid
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def generar_token():
    # Generar un token UUID
    token = str(uuid.uuid4())
    return token

def guardar_token_en_mysql(token):
    # Conectar a la base de datos MySQL
    conexion = mysql.connector.connect(
        host=os.getenv('host'),
        port=int(os.getenv('port')),
        user=os.getenv('user'),
        password=os.getenv('password'),
        database=os.getenv('database')
    )

    cursor = conexion.cursor()

    # Insertar el token en la base de datos
    sql = "INSERT INTO tokens (tokens) VALUES (%s)"
    cursor.execute(sql, (token,))
    conexion.commit()

    print(f'Token guardado: {token}')

    # Cerrar la conexión
    cursor.close()
    conexion.close()

if __name__ == "__main__":
    token = generar_token()
    guardar_token_en_mysql(token)
