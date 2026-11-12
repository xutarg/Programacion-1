#NOTA: 10_informe.py



import importlib
import os
import sys

# Asegura que Python encuentre los demas archivos del TFI en esta misma carpeta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

mod_idn = importlib.import_module("01_identificacion")
mod_mag = importlib.import_module("02_magnitudes")
mod_cli = importlib.import_module("05_cliente")
mod_bar = importlib.import_module("06_barrido")
mod_ver = importlib.import_module("07_verificacion")
mod_log = importlib.import_module("08_log")
mod_est = importlib.import_module("09_estadistica")

parsear_idn = mod_idn.parsear_idn
con_unidad = mod_mag.con_unidad
Instrumento = mod_cli.Instrumento
barrer = mod_bar.barrer
verificar_canal = mod_ver.verificar_canal
leer_log = mod_log.leer_log
resumen = mod_est.resumen


UNIDADES_MAGNITUD = {
    "FREQ": "Hz",
    "PKPK": "V",
    "CYCRMS": "V",
}


def armar_informe(idn, series, verificaciones):
    """
    Funcion pura: recibe el diccionario idn, el diccionario de series
    y la lista de verificaciones, y devuelve el informe completo como string.
    No imprime nada ni abre archivos.
    """
    lineas = []
    lineas.append("============================================================")
    lineas.append("INFORME DEL BANCO DE MEDICIONES AUTOMATIZADO")
    lineas.append("============================================================")

    # 1. Identificacion del instrumento
    if idn and isinstance(idn, dict):
        fabricante = idn.get("fabricante", "N/A")
        modelo = idn.get("modelo", "N/A")
        serie_eq = idn.get("serie", "N/A")
        version = idn.get("version", "N/A")
        lineas.append(
            f"Instrumento: {fabricante} {modelo} (Serie: {serie_eq}, Firmware: {version})"
        )
    else:
        lineas.append("Instrumento: No identificado")

    lineas.append("")
    lineas.append("SERIES REGISTRADAS:")

    # 2. Una linea por serie con n, promedio, minimo y maximo con unidades legibles
    if not series:
        lineas.append("  Sin series registradas.")
    else:
        for clave, valores in series.items():
            if isinstance(clave, tuple) and len(clave) == 3:
                equipo, canal, magnitud = clave
                etiqueta = f"{equipo} {canal} {magnitud}"
            else:
                magnitud = str(clave)
                etiqueta = str(clave)

            unidad = UNIDADES_MAGNITUD.get(magnitud, "")
            est = resumen(valores)
            if est is None:
                lineas.append(f"  - {etiqueta}: sin datos validos (n=0)")
            else:
                prom_txt = con_unidad(est["promedio"], unidad)
                min_txt = con_unidad(est["minimo"], unidad)
                max_txt = con_unidad(est["maximo"], unidad)
                lineas.append(
                    f"  - {etiqueta}: n={est['n']} | "
                    f"promedio={prom_txt} | min={min_txt} | max={max_txt}"
                )

    lineas.append("")
    lineas.append("VERIFICACIONES EN VIVO:")

    # 3. Resultado de cada verificacion
    if not verificaciones:
        lineas.append("  Sin verificaciones realizadas.")
    else:
        for ver in verificaciones:
            canal = ver.get("canal", "N/A")
            estado = "OK (COINCIDE)" if ver.get("coincide") else "FALLO (NO COINCIDE)"
            v_med = ver.get("vrms_medido")
            v_teo = ver.get("vrms_teorico")

            if v_med is not None and v_teo is not None:
                med_txt = con_unidad(v_med, "V")
                teo_txt = con_unidad(v_teo, "V")
                lineas.append(
                    f"  - {canal}: {estado} | Vrms medido={med_txt} vs Vrms teorico={teo_txt}"
                )
            else:
                motivo = ver.get("motivo", "Datos insuficientes")
                lineas.append(f"  - {canal}: {estado} ({motivo})")

    lineas.append("============================================================")
    return "\n".join(lineas)


# ---- pruebas ----
if __name__ == "__main__":
    # 1. Prueba normal de armar_informe (funcion pura, sin red ni archivos)
    idn_prueba = {
        "fabricante": "OWON",
        "modelo": "ADS3202",
        "serie": "25470803",
        "version": "V1.2.0",
    }
    series_prueba = {
        ("ADS3202", "CH1", "FREQ"): [1000.0, 1000.0, 1000.0],
        ("ADS3202", "CH1", "PKPK"): [2.0, 2.0, 2.0],
    }
    verificaciones_prueba = [
        {
            "canal": "CH1",
            "vrms_medido": 0.707,
            "vrms_teorico": 0.7071,
            "coincide": True,
        }
    ]
    texto_inf = armar_informe(idn_prueba, series_prueba, verificaciones_prueba)
    assert isinstance(texto_inf, str)
    assert "ADS3202" in texto_inf
    assert "n=3" in texto_inf
    assert "1 kHz" in texto_inf
    assert "2 V" in texto_inf
    assert "707 mV" in texto_inf
    assert "OK (COINCIDE)" in texto_inf

    # 2. Caso raro: canal cuya verificacion da que NO coincide
    verif_fallida = [
        {
            "canal": "CH2",
            "vrms_medido": 1.0,
            "vrms_teorico": 0.7071,
            "coincide": False,
        }
    ]
    texto_fallo = armar_informe(idn_prueba, series_prueba, verif_fallida)
    assert "FALLO (NO COINCIDE)" in texto_fallo

    # 3. Caso raro: datos vacios (idn None, sin series ni verificaciones)
    texto_vacio = armar_informe(None, {}, [])
    assert "No identificado" in texto_vacio
    assert "Sin series registradas" in texto_vacio
    assert "Sin verificaciones realizadas" in texto_vacio

    print("pruebas OK")

    # ---- Ejecucion del banco de mediciones completo ----
    try:
        equipo = Instrumento()
    except OSError:
        equipo = None

    if equipo is not None:
        try:
            idn_vivo = parsear_idn(equipo.preguntar("*IDN?"))
            barrido_vivo = barrer(equipo, ["CH1", "CH2"])
            verificaciones_vivas = [
                verificar_canal(barrido_vivo, "CH1"),
                verificar_canal(barrido_vivo, "CH2"),
            ]
        finally:
            equipo.cerrar()

        ruta_log = mod_log._buscar_archivo("mediciones.log")
        if os.path.exists(ruta_log):
            series_archivo, _ = leer_log(ruta_log)
            informe_final = armar_informe(idn_vivo, series_archivo, verificaciones_vivas)
            print()
            print(informe_final)