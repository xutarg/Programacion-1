#NOTA: 06_barrido.py



import importlib
import os
import sys

# Asegura que Python encuentre los demas archivos del TFI en esta misma carpeta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

mod_mag = importlib.import_module("02_magnitudes")
a_numero = mod_mag.a_numero


MAGNITUDES_BARRIDO = [
    ("FREQ", "FREQuency", "Hz"),
    ("PKPK", "PKPK", "V"),
    ("CYCRMS", "CYCRms", "V"),
]


def barrer(instrumento, canales):
    """
    Le pide al instrumento las tres magnitudes (FREQuency, PKPK y CYCRms)
    de cada canal indicado y devuelve una lista de diccionarios con:
    canal, magnitud, unidad, crudo y valor.
    """
    resultados = []

    for canal in canales:
        for mag_corta, cmd_scpi, unidad in MAGNITUDES_BARRIDO:
            comando = f":MEASUrement:{canal}:{cmd_scpi}?"
            crudo = instrumento.preguntar(comando)
            valor = a_numero(crudo)

            resultados.append({
                "canal": canal,
                "magnitud": mag_corta,
                "unidad": unidad,
                "crudo": crudo,
                "valor": valor,
            })

    return resultados


# ---- pruebas ----
class InstrumentoMentira:
    """
    Instrumento simulado para probar barrer() sin red, sin esperas
    y con resultados fijos que no tiemblan.
    """

    def __init__(self, respuestas):
        self.respuestas = respuestas

    def preguntar(self, comando):
        return self.respuestas.get(comando, "ERROR: comando desconocido")


if __name__ == "__main__":
    # 1. Prueba normal de barrido en dos canales (6 mediciones) con clase simulada
    respuestas_fijas = {
        ":MEASUrement:CH1:FREQuency?": "1.000000E+03",
        ":MEASUrement:CH1:PKPK?": "2.000000E+00",
        ":MEASUrement:CH1:CYCRms?": "7.071068E-01",
        ":MEASUrement:CH2:FREQuency?": "2.500000E+03",
        ":MEASUrement:CH2:PKPK?": "8.000000E-01",
        ":MEASUrement:CH2:CYCRms?": "2.828427E-01",
    }
    inst_falso = InstrumentoMentira(respuestas_fijas)
    mediciones = barrer(inst_falso, ["CH1", "CH2"])

    assert len(mediciones) == 6
    assert mediciones[0] == {
        "canal": "CH1",
        "magnitud": "FREQ",
        "unidad": "Hz",
        "crudo": "1.000000E+03",
        "valor": 1000.0,
    }
    assert mediciones[4]["canal"] == "CH2"
    assert mediciones[4]["magnitud"] == "PKPK"
    assert mediciones[4]["valor"] == 0.8

    # 2. Caso raro obligatorio: el equipo contesta error -> valor en None, crudo se guarda igual
    inst_con_falla = InstrumentoMentira({
        ":MEASUrement:CH1:FREQuency?": "1.000000E+03",
        ":MEASUrement:CH1:PKPK?": "ERROR: comando desconocido",
        ":MEASUrement:CH1:CYCRms?": "ERROR: sin senal",
    })
    med_falla = barrer(inst_con_falla, ["CH1"])
    assert len(med_falla) == 3
    assert med_falla[1]["valor"] is None
    assert med_falla[1]["crudo"] == "ERROR: comando desconocido"
    assert med_falla[2]["valor"] is None
    assert med_falla[2]["crudo"] == "ERROR: sin senal"

    # 3. Caso raro: lista de canales vacia devuelve lista vacia
    assert barrer(inst_falso, []) == []

    # 4. Prueba contra instrumento_virtual.py si esta corriendo en otra terminal
    mod_cliente = importlib.import_module("05_cliente")
    try:
        inst_real = mod_cliente.Instrumento()
    except OSError:
        inst_real = None

    if inst_real is not None:
        try:
            med_reales = barrer(inst_real, ["CH1", "CH2"])
            assert len(med_reales) == 6
            assert all(m["valor"] is not None for m in med_reales)
            assert abs(med_reales[0]["valor"] - 1000.0) / 1000.0 < 0.01
        finally:
            inst_real.cerrar()

    print("pruebas OK")