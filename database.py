import os
import sys

import mysql.connector

#Agregar carpeta
dll_path = os.path.abspath(os.path.dirname(sys.executable))
os.environ['PATH'] = dll_path + os.pathsep + os.environ['PATH']

def conectar_bd():
    config = {
        'host':"alejandroapps.duckdns.org",
        'port':3306,
        'user':"administrador",
        'password':"ATM_4dm1n_25?",
        'database':"sistemasolicitudes",
        'raise_on_warnings': True,
        'auth_plugin': 'mysql_native_password'
    }

    try:
        conexion = mysql.connector.connect(**config)
        return conexion
    except mysql.connector.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None