#NOTA: 04_configurar



def validar_comando_simple(comando):
    """
    Función auxiliar de validación basada en el Ejercicio 3
    para asegurar que los comandos generados cumplan con la sintaxis SCPI.
    """
    if not comando or not isinstance(comando, str):
        return False
    if not comando.startswith(':'):
        return False
    if "  " in comando:
        return False
    if comando.count('?') > 1:
        return False
    if '?' in comando and not comando.endswith('?'):
        return False
    partes = comando.split()
    if len(partes) != 2:
        return False
    return True


def comandos_de_canal(canal, display, acoplamiento, sonda, escala):
    """
    Genera la lista de cuatro órdenes SCPI para configurar un canal (CH1 o CH2).
    Retorna None si el canal no es válido.
    """
    if canal not in ["CH1", "CH2"]:
        return None
        
    return [
        f":{canal}:DISPlay {display}",
        f":{canal}:COUPling {acoplamiento}",
        f":{canal}:PROBe {sonda}",
        f":{canal}:SCALe {escala}"
    ]


# ---- pruebas ----
if __name__ == "__main__":
    # 1. Caso correcto para CH1 con los parámetros exactos de la consigna
    comandos_ch1 = comandos_de_canal("CH1", "ON", "DC", "10X", "1v")
    assert comandos_ch1 == [
        ":CH1:DISPlay ON",
        ":CH1:COUPling DC",
        ":CH1:PROBe 10X",
        ":CH1:SCALe 1v"
    ]

    # 2. Caso correcto para CH2
    comandos_ch2 = comandos_de_canal("CH2", "OFF", "AC", "1X", "500mV")
    assert comandos_ch2 == [
        ":CH2:DISPlay OFF",
        ":CH2:COUPling AC",
        ":CH2:PROBe 1X",
        ":CH2:SCALe 500mV"
    ]

    # 3. Caso inválido: canal incorrecto (debe retornar None)
    assert comandos_de_canal("CH3", "ON", "DC", "10X", "1v") is None

    # 4. Prueba de integración: comprobar que todos los comandos generados pasan la validación
    for cmd in comandos_ch1:
        assert validar_comando_simple(cmd) is True, f"El comando '{cmd}' no pasó la validación"

    print("pruebas OK")