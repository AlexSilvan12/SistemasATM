from database import conectar_bd
import mysql.connector

class CargaSolicitud():

    @classmethod
    def cargar_autorizaciones(cls):
            
        conexion = None
        cursor = None

        try:
            #Conectar a la base de datos
            conexion = conectar_bd()
            if conexion is None:
                print ("❌No se pudo establecer la conexion")
                return
            auto = []
            cursor = conexion.cursor()

            #Consulta de datos de la solicitud de pago
            query = "SELECT id_autorizacion, fecha_solicitud, monto, instruccion, fecha_requerida FROM autorizacionescompra"
            cursor.execute(query)
            autorizaciones = cursor.fetchall()
            for row in autorizaciones:
                auto.append(row)    

            return autorizaciones   
        


        except mysql.connector.Error as e:
            print(f"❌Error al cargar autorizaciones: {e}")

        finally:
            #Cierra el cursor y la conexion si fueron creados correctamente
            if cursor is not None:
                cursor.close()
            if conexion is not None:
                conexion.close()

    @classmethod
    def cargar_proveedores(cls):
            
        conexion = None
        cursor = None

        try:
            #Conectar a la base de datos
            conexion = conectar_bd()
            if conexion is None:
                print ("❌No se pudo establecer la conexion")
                return
            prov = []
            cursor = conexion.cursor()

            #Consulta de datos de los proveedores
            query1 = "SELECT nombre, rfc, email, clave_bancaria, cuenta_bancaria, banco FROM proveedores"
            cursor.execute(query1)
            proveedores = cursor.fetchall()
            for row in proveedores:
                prov.append(row)

            return proveedores
   
        


        except mysql.connector.Error as e:
            print(f"❌Error al cargar autorizaciones: {e}")

        finally:
            #Cierra el cursor y la conexion si fueron creados correctamente
            if cursor is not None:
                cursor.close()
            if conexion is not None:
                conexion.close()

    @classmethod
    def cargar_articulos(cls):
            
        conexion = None
        cursor = None

        try:
            #Conectar a la base de datos
            conexion = conectar_bd()
            if conexion is None:
                print ("❌No se pudo establecer la conexion")
                return
            art = []
            cursor = conexion.cursor()

            #Consulta de datos de los articulos
            query2 = "SELECT cantidad, unidad, articulo, observaciones FROM articulosautorizacion"
            cursor.execute(query2)
            articulo = cursor.fetchall()
            for row in articulo:
                art.append(row)
            
            return articulo
        


        except mysql.connector.Error as e:
            print(f"❌Error al cargar autorizaciones: {e}")

        finally:
            #Cierra el cursor y la conexion si fueron creados correctamente
            if cursor is not None:
                cursor.close()
            if conexion is not None:
                conexion.close()