# 🧩 Proyecto NumberLink — Lectura de Tablero

Este proyecto implementa la primera parte del solucionador del rompecabezas **NumberLink**.  
En esta etapa, el programa **lee correctamente un tablero desde un archivo de texto** y lo muestra por pantalla.

---

## 📘 Descripción del problema

El juego **NumberLink**, inventado por *Sam Loyd en 1897*, consiste en conectar pares de números o letras iguales en un tablero,  
trazando líneas que no se crucen entre sí y llenando todas las celdas del tablero.

En esta versión inicial, **solo se implementa la lectura del tablero desde un archivo de entrada**.

---

## Ejecución

Cada script se puede ejecutar por separado desde la carpeta `NumberLink` pasando la ruta del archivo de tablero:

- `leer_tablero.py`: Lee y muestra el tablero.  
  ```bash
  python leer_tablero.py tablerosEntrada/tableroSimple.txt
  ```

- `numberlink.py`: Resuelve el tablero con backtracking y muestra el resultado.  
  ```bash
  python numberlink.py tablerosEntrada/tableroSimple.txt
  ```

- `verificar_tablero.py`: Valida que un tablero (solución propuesta) cumpla las reglas.  
  ```bash
  python verificar_tablero.py tablerosSalida/solucion1_ejemplo.txt
  ```

