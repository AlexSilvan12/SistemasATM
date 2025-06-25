import mysql.connector

try: 
    
    conn = mysql.connector.connect(
        host="192.168.1.77",
        user="administrador",
        password="ATM_4dm1n_25?",
        database="sistemasolicitudes"
    )

    print("Conexión Exitosa")

    conn.close()
except mysql.connector.Error as err:
    print(f"Error: {err}")

#192.168.1.77
#administrador
#ATM_4dm1n_25?
#localhost
#root