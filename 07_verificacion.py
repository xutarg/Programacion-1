#NOTA: verificacion.py



import math

def vrms_teorico(vpp):
    """
    Calcula el Vrms teórico para una señal senoidal a partir de Vpp.
    Retorna None si el valor de Vpp no es válido (menor o igual a cero).
    """
    try:
        val = float(vpp)
        if val <= 0:
            return None
        return (val / 2.0) / math.sqrt(2)
    except (ValueError, TypeError):
        return None


def coincide(medido, teorico, tolerancia=0.02):
    """
    Devuelve True si el valor medido cae dentro de la tolerancia relativa del teórico.
    """
    try:
        m = float(medido)
        t = float(teorico)
        if t == 0:
            return False
        error = abs(m - t) / abs(t)
        return error <= tolerancia
    except (ValueError, TypeError):
        return False


def verificar_canal(filas, canal):
    """
    Busca el PKPK y el CYCRMS de un canal específico en el resultado del barrido,
    calcula el Vrms teórico y verifica si coincide con el medido.
    """
    pkpk = None
    vrms_medido = None

    for fila in filas:
        # Supone que cada fila es un diccionario con claves: canal, magnitud, valor, etc.
        if fila.get("canal") == canal:
            if fila.get("magnitud") == "PKPK":
                pkpk = fila.get("valor")
            elif fila.get("magnitud") == "CYCRMS":
                vrms_medido = fila.get("valor")

    if pkpk is None or vrms_medido is None:
        return {"canal": canal, "coincide": False, "motivo": "Faltan datos de PKPK o CYCRMS"}

    teorico = vrms_teorico(pkpk)
    if teorico is None:
        return {"canal": canal, "coincide": False, "motivo": "Vpp inválido para cálculo teórico"}

    resultado = coincide(vrms_medido, teorico)
    return {
        "canal": canal,
        "vrms_medido": vrms_medido,
        "vrms_teorico": teorico,
        "coincide": resultado
    }


# ---- pruebas ----
if __name__ == "__main__":
    # 1. Pruebas de vrms_teorico
    assert math.isclose(vrms_teorico(2.0), 0.70710678, rel_tol=1e-5)
    assert vrms_teorico(-2.0) is None

    # 2. Pruebas de coincide con tolerancia
    assert coincide(0.705, 0.7071, 0.02) is True
    assert coincide(0.800, 0.7071, 0.02) is False

    # 3. Prueba trampa del Ejercicio 7: Señal cuadrada de 2V Vpp tiene Vrms = 1V, no 0.707V
    # Pasar un barrido simulado de onda cuadrada debe dar que NO coincide.
    barrido_cuadrada = [
        {"canal": "CH1", "magnitud": "PKPK", "valor": 2.0},
        {"canal": "CH1", "magnitud": "CYCRMS", "valor": 1.0}
    ]
    res_verificacion = verificar_canal(barrido_cuadrada, "CH1")
    assert res_verificacion["coincide"] is False

    print("pruebas OK")