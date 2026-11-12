#NOTA: 03_comandos



def es_consulta(comando):
    """
    Devuelve True si el comando es una consulta (termina en '?').
    """
    if not isinstance(comando, str):
        return False
    return comando.endswith('?')


def validar(comando):
    """
    Valida un comando SCPI según las reglas de sintaxis.
    Retorna None si es correcto, o un string con el error correspondiente.
    """
    if not comando or not isinstance(comando, str):
        return "El comando no puede estar vacío"
        
    if not comando.startswith(':') and not comando.startswith('*'):
        return "El comando debe empezar con ':' o '*'"
        
    if "  " in comando:
        return "El comando no puede tener dos espacios seguidos"
        
    if comando.count('?') > 1:
        return "El comando no puede tener más de un signo de interrogación"
        
    if '?' in comando and not comando.endswith('?'):
        return "El signo de interrogación solo puede ir al final"
        
    partes = comando.split()
    if es_consulta(comando):
        if len(partes) > 1:
            return "Una consulta no lleva argumento"
    else:
        if len(partes) > 2:
            return "Una orden lleva un solo argumento"
            
    return None


# ---- pruebas ----
if __name__ == "__main__":
    # 1. Pruebas de es_consulta
    assert es_consulta(":MEASUrement:CH1:FREQuency?") is True
    assert es_consulta(":CH1:DISPlay ON") is False

    # 2. Pruebas de comandos válidos
    assert validar(":CH1:DISPlay ON") is None
    assert validar(":MEASUrement:CH1:FREQuency?") is None
    assert validar("*IDN?") is None

    # 3. Pruebas de casos inválidos (casos raros requeridos)
    assert validar("") is not None
    assert validar("CH1:DISPlay ON") is not None
    assert validar(":CH1:DISPlay  ON") is not None
    assert validar(":CH1:DISPlay??") is not None
    assert validar(":CH1:DIS?Play") is not None
    assert validar(":CH1:SCALe 1 v") is not None
    assert validar(":CH1:DISPlay ON?") is not None

    print("pruebas OK")