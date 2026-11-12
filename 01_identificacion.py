# NOTA: 01_identificacion



def parsear_idn(respuesta):
    """
    Parsea la respuesta de identificación (*IDN?) de un instrumento.
    Recibe un string con campos separados por comas y devuelve un diccionario
    con las claves: 'fabricante', 'modelo', 'serie', 'version'.
    Retorna None si la respuesta es vacía, inválida, contiene errores o tiene menos de 4 campos.
    """
    if not respuesta or not isinstance(respuesta, str):
        return None
    
    # Si el instrumento devuelve un mensaje de error, no es una identificación válida
    if "ERROR" in respuesta.upper():
        return None
        
    # Separar por comas y limpiar los espacios en blanco alrededor de cada campo
    campos = [c.strip() for c in respuesta.split(",")]
    
    # El osciloscopio devuelve 4 campos y el multímetro 5; se exigen al menos 4
    if len(campos) < 4:
        return None
        
    return {
        "fabricante": campos[0],
        "modelo": campos[1],
        "serie": campos[2],
        "version": campos[3]
    }


# ---- pruebas ----
if __name__ == "__main__":
    # 1. Caso normal de osciloscopio (4 campos)
    res_osc = parsear_idn("OWON,ADS3202,25470803,V1.2.0")
    assert res_osc == {
        "fabricante": "OWON", 
        "modelo": "ADS3202", 
        "serie": "25470803", 
        "version": "V1.2.0"
    }

    # 2. Caso normal de multímetro (5 campos, el 5to se descarta automáticamente)
    res_mult = parsear_idn("OWON,XDM1041,25470803,V4.4.0,3")
    assert res_mult == {
        "fabricante": "OWON", 
        "modelo": "XDM1041", 
        "serie": "25470803", 
        "version": "V4.4.0"
    }

    # 3. Caso con espacios en exceso alrededor de los campos
    res_espacios = parsear_idn("  OWON, ADS3202 , 25470803 , V1.2.0  ")
    assert res_espacios["modelo"] == "ADS3202"

    # 4. Caso raro: Menos de cuatro campos (falla)
    assert parsear_idn("OWON,ADS3202,25470803") is None

    # 5. Caso raro: Cadena vacía (falla)
    assert parsear_idn("") is None

    # 6. Caso raro: Respuesta de error del instrumento (falla)
    assert parsear_idn("ERROR: comando desconocido") is None

    print("pruebas OK")