from collections import deque
import os
import sys
from leer_tablero import leer_tablero, imprimir_tablero

def obtener_rutas(tablero):
    rutas = {}
    for i, fila in enumerate(tablero):
        for j, celda in enumerate(fila):
            if celda != ' ' and celda != '.':
                rutas.setdefault(celda, []).append((i, j))
    return rutas

def grado(tablero, i, j):
    filas = len(tablero)
    cols = len(tablero[0])
    simbolo = tablero[i][j]
    g = 0
    
    for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
        ni, nj = i + di, j + dj
        if 0 <= ni < filas and 0 <= nj < cols:
            if tablero[ni][nj] == simbolo:
                g += 1
    return g

def ruta_conectada(tablero, simbolo, posiciones):
    # escoger el primer extremo
    inicio = posiciones[0]
    visitado = set([inicio])
    q = deque([inicio])
    filas = len(tablero)
    cols = len(tablero[0])

    while q:
        i, j = q.popleft()
        """
        La búsqueda solo considera movimientos en 4 direcciones:
          (-1, 0) → arriba
          ( 1, 0) → abajo
          ( 0,-1) → izquierda
          ( 0, 1) → derecha
        """
        for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
            ni, nj = i + di, j + dj
            if 0 <= ni < filas and 0 <= nj < cols:
                """
                Para cada dirección, verifica si:
                    1. La celda está dentro del tablero.
                    2. Contiene el mismo símbolo.
                    3. Aún no fue visitada.
                """
                if tablero[ni][nj] == simbolo and (ni, nj) not in visitado:
                    visitado.add((ni, nj))
                    q.append((ni, nj))

    return len(visitado) == len(posiciones)

def verificar_tablero(tablero):
    rutas = obtener_rutas(tablero)

    for simbolo, posiciones in rutas.items():
        # 1. debe haber al menos dos celdas del mismo símbolo
        if len(posiciones) < 2:
            print(f"Ruta '{simbolo}' no tiene suficientes celdas.")
            return False

        # 2. calcular grados
        grados = [grado(tablero, i, j) for (i, j) in posiciones]

        # extremos = grado 1, interiores = grado 2
        extremos = sum(1 for g in grados if g == 1)

        # a) debe haber exactamente dos extremos
        if extremos != 2:
            print(f"Ruta '{simbolo}' tiene {extremos} extremos. Debe tener 2.")
            return False
        
        # b) ninguna celda puede tener grado > 2
        if any(g > 2 for g in grados):
            print(f"Ruta '{simbolo}' tiene intersecciones (grado > 2).")
            return False

        # 3. comprobar conectividad
        if not ruta_conectada(tablero, simbolo, posiciones):
            print(f"La ruta '{simbolo}' está interrumpida o no forma un camino continuo.")
            return False

    print( "El tablero es válido.")
    return True


# --- Ejecución principal ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python verificar_tablero.py <ruta_del_archivo>")
        sys.exit(1)

    ruta = sys.argv[1]

    try:
        tablero = leer_tablero(ruta)
        print(f"Tablero leído correctamente desde: {ruta}\n")
        imprimir_tablero(tablero)
        verificar_tablero(tablero)
    except Exception as e:
        print(f"Error al leer el archivo: {e}")