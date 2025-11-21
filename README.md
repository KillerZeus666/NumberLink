# 🧩 Proyecto NumberLink — Lectura, Verificación y Resolución

Herramientas para trabajar con el rompecabezas **NumberLink**: lectura de tableros, verificación de soluciones y un solucionador por backtracking con heurísticas.

---

## 📘 Descripción del problema

El juego **NumberLink** consiste en conectar pares de símbolos iguales en un tablero ortogonal, trazando líneas que no se crucen ni se bifurquen y llenando todas las celdas.

---

## Formato de entrada

- Primera línea: `<filas> <columnas>`
- Siguientes líneas: contenido del tablero (símbolos para extremos, espacios en blanco para celdas vacías).

---

## Scripts principales

- `leer_tablero.py`: lee y muestra un tablero desde archivo.  
  ```bash
  python leer_tablero.py tablerosEntrada/entrada9_2x3.txt
  ```

- `numberlink_heuristica.py`: resuelve con backtracking heurístico.  
  Estrategia: prioriza el par más restringido, genera rutas (DFS/BFS) con límites, y poda por cuellos de botella, conectividad de componentes y conectividad simple.  
  Guarda el resultado en `tablerosSalida/salida<filas>x<columnas>.txt`.  
  ```bash
  python numberlink_heuristica.py tablerosEntrada/entrada9_2x3.txt
  ```

- `verificar_tablero.py`: valida que un tablero cumpla las reglas (dos extremos por símbolo, sin intersecciones y camino continuo para cada ruta).  
  ```bash
  python verificar_tablero.py tablerosSalida/salida9x9.txt
  ```

Ejecuta cada script desde la carpeta `NumberLink` pasando la ruta del archivo de tablero correspondiente.
