from collections import deque
import sys
from leer_tablero import NumberLinkBoardIO


class NumberLinkVerifier:
    """Valida la estructura y conectividad de rutas en un tablero NumberLink."""

    DIRECCIONES = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    @staticmethod
    def obtener_rutas(tablero):
        """Agrupa coordenadas por símbolo, ignorando espacios y puntos."""
        rutas = {}
        for i, fila in enumerate(tablero):
            for j, celda in enumerate(fila):
                if celda != ' ' and celda != '.':
                    rutas.setdefault(celda, []).append((i, j))
        return rutas

    @classmethod
    def grado(cls, tablero, i, j):
        """Devuelve el grado (vecinos con mismo símbolo) de una celda."""
        filas = len(tablero)
        cols = len(tablero[0])
        simbolo = tablero[i][j]
        g = 0

        for di, dj in cls.DIRECCIONES:
            ni, nj = i + di, j + dj
            if 0 <= ni < filas and 0 <= nj < cols:
                if tablero[ni][nj] == simbolo:
                    g += 1
        return g

    @classmethod
    def ruta_conectada(cls, tablero, simbolo, posiciones):
        """Comprueba si todas las celdas de un símbolo forman una ruta continua."""
        inicio = posiciones[0]
        visitado = set([inicio])
        q = deque([inicio])
        filas = len(tablero)
        cols = len(tablero[0])

        while q:
            i, j = q.popleft()
            for di, dj in cls.DIRECCIONES:
                ni, nj = i + di, j + dj
                if 0 <= ni < filas and 0 <= nj < cols:
                    if tablero[ni][nj] == simbolo and (ni, nj) not in visitado:
                        visitado.add((ni, nj))
                        q.append((ni, nj))

        return len(visitado) == len(posiciones)

    @classmethod
    def verificar_tablero(cls, tablero):
        """Valida grados, extremos y continuidad de cada ruta en el tablero."""
        rutas = cls.obtener_rutas(tablero)

        for simbolo, posiciones in rutas.items():
            if len(posiciones) < 2:
                print(f"Ruta '{simbolo}' no tiene suficientes celdas.")
                return False

            grados = [cls.grado(tablero, i, j) for (i, j) in posiciones]
            extremos = sum(1 for g in grados if g == 1)

            if extremos != 2:
                print(f"Ruta '{simbolo}' tiene {extremos} extremos. Debe tener 2.")
                return False

            if any(g > 2 for g in grados):
                print(f"Ruta '{simbolo}' tiene intersecciones (grado > 2).")
                return False

            if not cls.ruta_conectada(tablero, simbolo, posiciones):
                print(f"La ruta '{simbolo}' está interrumpida o no forma un camino continuo.")
                return False

        print("El tablero es válido.")
        return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python verificar_tablero.py <ruta_del_archivo>")
        sys.exit(1)

    ruta = sys.argv[1]

    try:
        tablero = NumberLinkBoardIO.leer_tablero(ruta)
        print(f"Tablero leído correctamente desde: {ruta}\n")
        NumberLinkBoardIO.imprimir_tablero(tablero)
        NumberLinkVerifier.verificar_tablero(tablero)
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
