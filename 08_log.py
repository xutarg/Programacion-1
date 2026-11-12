#NOTA: 08_log.py
import math
import os


def analizar_linea(linea):
    """
    Analiza una linea del archivo log.
    Retorna un par (medicion, motivo) donde uno de los dos es None.
    Si la linea se ignora (blanca o comentario), retorna (None, None).
    """
    if not linea or not isinstance(linea, str):
        return None, None

    linea_limpia = linea.strip()

    # Se ignoran lineas en blanco o comentarios que empiezan con #
    if not linea_limpia or linea_limpia.startswith("#"):
        return None, None

    # split() sin argumentos separa por espacios y tambien por tabulaciones
    partes = linea_limpia.split()

    # Se rechaza si no tiene exactamente seis campos
    if len(partes) != 6:
        return None, "La linea no tiene exactamente 6 campos"

    fecha, hora, equipo, canal, magnitud, valor_str = partes

    # Validar formato de hora (HH:MM:SS) y rangos logicos
    try:
        partes_hora = hora.split(":")
        if len(partes_hora) != 3:
            return None, "Formato de hora invalido"
        h, m, s = map(int, partes_hora)
        if not (0 <= h <= 23 and 0 <= m <= 59 and 0 <= s <= 59):
            return None, "Hora imposible"
    except (ValueError, AttributeError):
        return None, "Formato de hora invalido"

    # Validar canal
    if canal not in ["CH1", "CH2"]:
        return None, "Canal invalido (debe ser CH1 o CH2)"

    # Validar magnitud
    if magnitud not in ["FREQ", "PKPK", "CYCRMS"]:
        return None, "Magnitud invalida"

    # Validar que el valor sea convertible a numero real finito (rechaza NaN e inf)
    try:
        valor = float(valor_str)
        if not math.isfinite(valor):
            return None, "El valor no es un numero valido"
    except (ValueError, TypeError):
        return None, "El valor no es un numero valido"

    medicion = {
        "fecha": fecha,
        "hora": hora,
        "equipo": equipo,
        "canal": canal,
        "magnitud": magnitud,
        "valor": valor,
    }

    return medicion, None


def _buscar_archivo(ruta):
    """
    Busca el archivo log en la ruta dada, en la carpeta del script
    y en nombres alternativos comunes (medicion.log o .txt).
    """
    if os.path.exists(ruta):
        return ruta

    carpeta_script = os.path.dirname(os.path.abspath(__file__))
    candidatos = [
        os.path.join(carpeta_script, ruta),
        os.path.join(carpeta_script, "mediciones.log"),
        os.path.join(carpeta_script, "medicion.log"),
        os.path.join(carpeta_script, "mediciones.log.txt"),
        os.path.join(carpeta_script, "medicion.log.txt"),
        "medicion.log",
    ]
    for candidato in candidatos:
        if os.path.exists(candidato):
            return candidato
    return ruta


def leer_log(ruta):
    """
    Recorre el archivo de log y devuelve:
    - series: diccionario agrupado por (equipo, canal, magnitud) -> lista de floats
    - rechazadas: lista de diccionarios con linea, texto y motivo
    """
    series = {}
    rechazadas = []
    ruta_real = _buscar_archivo(ruta)

    with open(ruta_real, "r", encoding="utf-8") as archivo:
        for numero_linea, linea in enumerate(archivo, start=1):
            medicion, motivo = analizar_linea(linea)
            if motivo is not None:
                rechazadas.append({
                    "linea": numero_linea,
                    "texto": linea.strip(),
                    "motivo": motivo,
                })
            elif medicion is not None:
                clave = (medicion["equipo"], medicion["canal"], medicion["magnitud"])
                if clave not in series:
                    series[clave] = []
                series[clave].append(medicion["valor"])

    return series, rechazadas


# ---- pruebas ----
if __name__ == "__main__":
    import tempfile

    # 1. Linea valida normal
    med, mot = analizar_linea("2026-09-08 09:14:02 ADS3202 CH1 FREQ 1.000431E+03")
    assert mot is None
    assert med["valor"] == 1000.431

    # 2. Linea con tabulaciones (debe aceptarse)
    med_tab, mot_tab = analizar_linea("2026-09-08\t09:17:31\tADS3202\tCH1\tFREQ\t1.001000E+03")
    assert mot_tab is None
    assert med_tab["valor"] == 1001.0

    # 3. Lineas ignoradas (en blanco y comentarios)
    assert analizar_linea("   ") == (None, None)
    assert analizar_linea("# comentario de sesion") == (None, None)

    # 4. Casos raros rechazados (incluyendo la trampa de NaN)
    assert analizar_linea("2026-09-08 09:16:01 ADS3202 CH2 CYCRMS NaN")[0] is None
    assert analizar_linea("2026-09-08 09:16:01 ADS3202 CH2 CYCRMS NaN")[1] is not None
    assert analizar_linea("2026-09-08 25:61:00 ADS3202 CH2 FREQ 2.500000E+03")[1] is not None
    assert analizar_linea("2026-09-08 09:16:31 ADS3202 CH3 FREQ 1.000000E+03")[1] is not None
    assert analizar_linea("2026-09-08 09:17:01 ADS3202 CH1 TEMP 3.150000E+02")[1] is not None
    assert analizar_linea("2026-09-08 09:15:01 ADS3202 CH2 PKPK")[1] is not None

    # 5. Prueba de leer_log autonoma (funciona siempre, con o sin mediciones.log externo)
    contenido_muestra = (
        "# Cabecera de prueba\n"
        "\n"
        "2026-09-08 09:14:00 ADS3202 CH1 FREQ 9.993761E+02\n"
        "2026-09-08\t09:17:31\tADS3202\tCH1\tFREQ\t1.001000E+03\n"
        "2026-09-08 09:16:01 ADS3202 CH2 CYCRMS NaN\n"
        "2026-09-08 25:61:00 ADS3202 CH2 FREQ 2.500000E+03\n"
    )
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".log") as tmp:
        tmp.write(contenido_muestra)
        ruta_tmp = tmp.name

    try:
        series_tmp, rechazadas_tmp = leer_log(ruta_tmp)
        assert len(series_tmp[("ADS3202", "CH1", "FREQ")]) == 2
        assert len(rechazadas_tmp) == 2
    finally:
        os.remove(ruta_tmp)

    # 6. Si mediciones.log ya esta en la carpeta, valida tambien contra el archivo real
    ruta_real = _buscar_archivo("mediciones.log")
    if os.path.exists(ruta_real):
        series_log, rechazadas_log = leer_log(ruta_real)
        assert len(rechazadas_log) == 8
        assert len(series_log[("ADS3202", "CH1", "FREQ")]) == 21

    print("pruebas OK")