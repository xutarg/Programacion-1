# Bitácora de uso de IA — Trabajo Final Integrador

Registro de las consultas hechas a la inteligencia artificial durante el armado del trabajo, qué cambios hicimos y cómo probamos que todo funcione bien.

---

### 1. Ejercicios 1 y 2 (`01_identificacion.py` y `02_magnitudes.py`)
* **El prompt:**
  > "Escribe el código completo en Python para el ejercicio 1 (parsear_idn) y el ejercicio 2 (a_numero y con_unidad) incluyendo las pruebas con assert requeridas por la consigna."
* **Qué contestó:**
  Me dio las funciones para separar los datos del equipo con `.split(",")` y limpiar espacios con `.strip()`. Para el ejercicio 2 armó una lista con las escalas (`p`, `n`, `u`, `m`, `k`, `M`, `G`) que divide el valor hasta dejarlo entre 1 y 999.
* **Qué cambiaste:**
  En el ejercicio 2 al principio me tiraba error de sintaxis porque al copiar del chat se pegó un texto extra al final. Lo borré y además unifiqué el último mensaje de todos los archivos para que diga `print("pruebas OK")`.
* **Cómo lo verificaste:**
  Probé con `assert` que funcione tanto con los 4 datos del osciloscopio como con los 5 del multímetro, y en el ejercicio 2 agregué la prueba trampa `assert con_unidad(999.9999, "Hz") == "1 kHz"` para asegurarme de que al redondear no devuelva `"1000 Hz"`.

---

### 2. Ejercicios 3 y 4 (`03_comandos.py` y `04_configurar.py`)
* **El prompt:**
  > "Escribe el código completo en Python para el ejercicio 3 (es_consulta y validar) y el ejercicio 4 (comandos_de_canal) incluyendo las pruebas con assert."
* **Qué contestó:**
  Me armó la función `es_consulta` mirando si el texto termina en `?`, la función `validar` revisando cada regla con `if` (que no esté vacío, que empiece con `:` o `*`, que no tenga espacios dobles, etc.) y `comandos_de_canal` que devuelve la lista con las 4 órdenes de configuración.
* **Qué cambiaste:**
  Revisé que los mensajes de error fueran claros y que si el canal no es `CH1` ni `CH2` devuelva `None` enseguida.
* **Cómo lo verificaste:**
  Puse un `assert` por cada regla rota de la tabla de la consigna y en el ejercicio 4 agregué un ciclo `for` que pasa los 4 comandos generados por la validación del ejercicio 3 para confirmar que estén bien escritos.

---

### 3. Ejercicios 5 y 6 (`05_cliente.py` y `06_barrido.py`)
* **El prompt:**
  > "Escribe el código completo de 05_cliente.py y 06_barrido.py con todas sus pruebas assert."
* **Qué contestó:**
  Armó la clase `Instrumento` usando `socket` para conectarse a `127.0.0.1:5555`, agregando el salto de línea `"\n"` al enviar comandos. Para el ejercicio 6 hizo la función `barrer` y una clase cortita llamada `InstrumentoMentira` que devuelve valores fijos para probar sin red.
* **Qué cambiaste:**
  Como los nombres de los archivos empiezan con números (como `01_identificacion.py`), Python no me dejaba usar `import` común. Lo resolvimos usando `importlib.import_module` y agregando la ruta de la carpeta para que encuentre los archivos siempre.
* **Cómo lo verificaste:**
  En `06_barrido.py` probé con `InstrumentoMentira` qué pasa si el equipo responde `"ERROR: comando desconocido"`, verificando con `assert` que `valor` quede en `None` pero `crudo` guarde el error. También abrí otra terminal con `instrumento_virtual.py` y comprobé que `*IDN?` devuelva el modelo `ADS3202`.

---

### 4. Ejercicio 7 (`07_verificacion.py`)
* **El prompt:**
  > "Ayúdame a armar el código del ejercicio 7 (vrms_teorico, coincide y verificar_canal) con sus pruebas."
* **Qué contestó:**
  Me dio las tres funciones aplicando la fórmula de la señal senoidal `(vpp / 2) / math.sqrt(2)` y calculando el error relativo `abs(medido - teorico) / abs(teorico) <= tolerancia` con 2% por defecto.
* **Qué cambiaste:**
  Agregué validaciones para que si `vpp` es negativo o cero, o si falta algún dato en el barrido, devuelva `None` o `False` sin que el programa se rompa por dividir por cero.
* **Cómo lo verificaste:**
  Además de probar con valores normales de una senoide, armé el `assert` de una onda cuadrada (`Vpp = 2.0` y `Vrms = 1.0`) y verifiqué que `verificar_canal` devuelva `coincide == False`.

---

### 5. Ejercicios 8, 9 y 10 (`08_log.py`, `09_estadistica.py` y `10_informe.py`)
* **El prompt:**
  > "Muéstrame el ajuste de NaN en 08_log.py, el control con mediciones.log en 09_estadistica.py y el código completo de 10_informe.py."
* **Qué contestó:**
  Me dio las funciones para leer `mediciones.log` usando `linea.split()` (sin comillas adentro de los paréntesis para que acepte la línea con tabulaciones), el cálculo de promedio y desvío estándar en el 9, y la función `armar_informe` en el 10 que devuelve todo el texto armado sin usar `print` adentro.
* **Qué cambiaste:**
  Al probar con el archivo `mediciones.log` real vimos dos cosas: primero, había una línea con valor `NaN` que `float()` dejaba pasar, así que agregamos `math.isfinite(valor)` para rechazarla; segundo, al principio me daba error `FileNotFoundError` porque la terminal buscaba el archivo en otra carpeta, así que agregamos una función que busca `mediciones.log` en la misma carpeta del script.
* **Cómo lo verificaste:**
  Comprobé con `assert` que `leer_log` encuentre exactamente 21 mediciones buenas en `CH1 FREQ` y 8 rechazadas, que el promedio en el ejercicio 9 dé a menos de 0,5% de 1000 Hz con desvío menor a 5 Hz, y que `10_informe.py` imprima el informe completo con el instrumento virtual prendido.