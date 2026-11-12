#NOTA: 09_estadistica.py

import importlib
import math
import os
import sys

# Asegura que Python encuentre 08_log.py en esta misma carpeta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def resumen(valores):
    """
    Recibe una lista de valores numericos y devuelve un diccionario con:
    n, minimo, maximo, promedio y desvio (muestral, dividiendo por n - 1).
    Devuelve None si la lista esta vacia o contiene elementos invalidos.
    """
    if not valores or not isinstance(valores, (list, tuple)):
        return None

    try:
        lista_num = [float(v) for v in valores]
    except (ValueError, TypeError):
        return None

    n = len(lista_num)
    if n == 0:
        return None

    minimo = min(lista_num)
    maximo = max(lista_num)
    promedio = sum(lista_num) / n

    # Desvio estandar de la muestra (divide por n - 1)
    if n == 1:
        desvio = 0.0
    else:
        suma_cuadrados = sum((v - promedio) ** 2 for v in lista_num)
        desvio = math.sqrt(suma_cuadrados / (n - 1))

    return {
        "n": n,
        "minimo": minimo,
        "maximo": maximo,
        "promedio": promedio,
        "desvio": desvio,
    }


def fuera_de_rango(valores, minimo, maximo):
    """
    Recibe una lista de valores y los limites del rango [minimo, maximo].
    Devuelve las posiciones (indices 0-based) de los valores que se salen
    del rango. Los dos extremos cuentan como adentro.
    """
    posiciones = []
    for i, v in enumerate(valores):
        try:
            val = float(v)
            if val < minimo or val > maximo:
                posiciones.append(i)
        except (ValueError, TypeError):
            posiciones.append(i)
    return posiciones


# ---- pruebas ----
if __name__ == "__main__":
    # 1. Prueba de resumen con una serie normal
    serie_prueba = [10.0, 12.0, 23.0, 23.0, 16.0, 23.0, 21.0, 16.0]
    res = resumen(serie_prueba)
    assert res["n"] == 8
    assert res["minimo"] == 10.0
    assert res["maximo"] == 23.0
    assert math.isclose(res["promedio"], 18.0, rel_tol=1e-5)

    # 2. Casos raros: lista vacia y lista con un unico valor (no debe dividir por cero)
    assert resumen([]) is None
    res_uno = resumen([42.5])
    assert res_uno["n"] == 1
    assert res_uno["desvio"] == 0.0

    # 3. Pruebas de fuera_de_rango (los extremos cuentan como adentro)
    datos = [5.0, 10.0, 15.0, 20.0, 25.0]
    assert fuera_de_rango(datos, 10.0, 20.0) == [0, 4]
    assert fuera_de_rango([], 0.0, 10.0) == []

    # 4. Control obligatorio con la serie real de frecuencias de CH1 en mediciones.log
    mod_log = importlib.import_module("08_log")
    ruta_log = mod_log._buscar_archivo("mediciones.log")
    if os.path.exists(ruta_log):
        series, _ = mod_log.leer_log(ruta_log)
        frecuencias_ch1 = series[("ADS3202", "CH1", "FREQ")]
        est_ch1 = resumen(frecuencias_ch1)

        # Promedio a menos del 0,5 % de 1000 Hz y desvio menor que 5 Hz
        error_relativo = abs(est_ch1["promedio"] - 1000.0) / 1000.0
        assert error_relativo < 0.005
        assert est_ch1["desvio"] < 5.0

    print("pruebas OK")