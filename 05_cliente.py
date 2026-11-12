#NOTA: 05_cliente.py



import importlib
import os
import socket
import sys

# Asegura que Python encuentre 01_identificacion.py en esta misma carpeta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class Instrumento:
    """
    Cliente TCP para comunicarse con un instrumento SCPI por red.
    """

    def __init__(self, direccion="127.0.0.1", puerto=5555):
        self.direccion = direccion
        self.puerto = puerto
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((direccion, puerto))
        self.lector = self.sock.makefile("r", encoding="utf-8")

    def enviar(self, comando):
        """
        Manda una orden SCPI terminada en salto de linea y no espera respuesta.
        """
        mensaje = comando.strip() + "\n"
        self.sock.sendall(mensaje.encode("utf-8"))

    def preguntar(self, comando):
        """
        Manda una consulta SCPI terminada en salto de linea y devuelve la respuesta.
        """
        self.enviar(comando)
        respuesta = self.lector.readline()
        return respuesta.strip()

    def cerrar(self):
        """
        Cierra la conexion con el instrumento.
        """
        try:
            self.lector.close()
        finally:
            self.sock.close()


# ---- pruebas ----
if __name__ == "__main__":
    mod_idn = importlib.import_module("01_identificacion")
    parsear_idn = mod_idn.parsear_idn

    inst = Instrumento()
    try:
        # 1. Prueba minima obligatoria: *IDN? y verificacion con parsear_idn
        respuesta_idn = inst.preguntar("*IDN?")
        assert respuesta_idn == "OWON,ADS3202,25470803,V1.2.0"

        datos_idn = parsear_idn(respuesta_idn)
        assert datos_idn is not None
        assert datos_idn["modelo"] == "ADS3202"

        # 2. Prueba de enviar una orden y consultar que surtio efecto
        inst.enviar(":CH2:DISPlay ON")
        assert inst.preguntar(":CH2:DISPlay?") == "ON"
        inst.enviar(":CH2:DISPlay OFF")
        assert inst.preguntar(":CH2:DISPlay?") == "OFF"

        # 3. Caso raro: comando desconocido devuelve mensaje de error
        respuesta_error = inst.preguntar(":COMANDO:INEXISTENTE?")
        assert respuesta_error == "ERROR: comando desconocido"
        assert parsear_idn(respuesta_error) is None
    finally:
        inst.cerrar()

    print("pruebas OK")