#NOTA: 02_magnitudes



def a_numero(texto):
    """
    Convierte un string en notación científica a número flotante.
    Devuelve None si el texto no es un número válido.
    """
    try:
        return float(texto)
    except (ValueError, TypeError):
        return None


def con_unidad(valor, unidad):
    """
    Convierte un valor numérico a un string con el prefijo métrico adecuado
    para que el número quede entre 1 y 999.
    """
    if valor == 0.0:
        return f"0 {unidad}"
    
    escalas = [
        ("p", 1e-12),
        ("n", 1e-9),
        ("u", 1e-6),
        ("m", 1e-3),
        ("", 1.0),
        ("k", 1e3),
        ("M", 1e6),
        ("G", 1e9)
    ]
    
    for i, (prefijo, factor) in enumerate(escalas):
        val_esc = valor / factor
        if 1.0 <= abs(val_esc) < 1000.0:
            redondeado = round(val_esc, 3)
            if abs(redondeado) >= 1000.0 and i + 1 < len(escalas):
                prefijo_sig, factor_sig = escalas[i + 1]
                val_esc_sig = valor / factor_sig
                redondeado_sig = round(val_esc_sig, 3)
                if redondeado_sig.is_integer():
                    val_str = str(int(redondeado_sig))
                else:
                    val_str = str(redondeado_sig).rstrip('0').rstrip('.')
                return f"{val_str} {prefijo_sig}{unidad}"
            
            if redondeado.is_integer():
                val_str = str(int(redondeado))
            else:
                val_str = str(redondeado).rstrip('0').rstrip('.')
            return f"{val_str} {prefijo}{unidad}"
            
    return f"{valor} {unidad}"


# ---- pruebas ----
if __name__ == "__main__":
    # 1. Pruebas de conversión con a_numero
    assert a_numero("1.000000E+03") == 1000.0
    assert a_numero("texto_invalido") is None

    # 2. Pruebas de con_unidad según la tabla de la consigna
    assert con_unidad(1000.0, "Hz") == "1 kHz"
    assert con_unidad(2500.0, "Hz") == "2.5 kHz"
    assert con_unidad(2.0, "V") == "2 V"
    assert con_unidad(0.707, "V") == "707 mV"
    assert con_unidad(0.0005, "s") == "500 us"
    assert con_unidad(0.0, "V") == "0 V"

    # 3. Caso especial de redondeo crítico (999.9999 Hz debe dar 1 kHz y no 1000 Hz)
    assert con_unidad(999.9999, "Hz") == "1 kHz"

    print("pruebas OK")