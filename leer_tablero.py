# leer_tablero.py
# Autor: Katheryn Guasca
# Descripción: Lee un archivo de texto que define un tablero NumberLink.

import sys
import os

class NumberLinkBoardIO:
    """Utilidades para leer e imprimir tableros NumberLink."""

    @staticmethod
    def leer_tablero(ruta_archivo):
        """
        Lee un archivo de texto con el formato del tablero Numberlink.
        Retorna una lista de listas con los caracteres del tablero.

        Formato esperado:
        - Primera línea: 'filas columnas'
        - Siguientes líneas: contenido del tablero (puede tener espacios)
        """
        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo}")

        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            primera = archivo.readline().strip()
            while primera == '':
                primera = archivo.readline().strip()

            partes = primera.split()
            if len(partes) != 2:
                raise ValueError("La primera línea debe contener dos enteros: filas y columnas.")
            filas, columnas = map(int, partes)

            tablero = []
            for _ in range(filas):
                linea = archivo.readline()
                if not linea:
                    linea = ''
                linea = linea.rstrip('\n')
                if len(linea) < columnas:
                    linea += ' ' * (columnas - len(linea))
                tablero.append(list(linea[:columnas]))

        return tablero

    @staticmethod
    def imprimir_tablero(tablero):
        """Imprime el tablero en formato legible."""
        for fila in tablero:
            print(''.join(fila))

    @staticmethod
    def tablero_a_texto(tablero):
        return '\n'.join(''.join(fila) for fila in tablero)

    @staticmethod
    def guardar_resultado(tablero, ruta_salida, nombre_solver, tiempo_segundos, completa):
        if not ruta_salida:
            return
        directorio = os.path.dirname(ruta_salida)
        if directorio:
            os.makedirs(directorio, exist_ok=True)
        contenido = [
            f"Solver: {nombre_solver}",
            f"Tiempo: {tiempo_segundos:.4f} s",
            f"Completado: {'sí' if completa else 'no'}",
            "",
            NumberLinkBoardIO.tablero_a_texto(tablero)
        ]
        with open(ruta_salida, 'w', encoding='utf-8') as archivo:
            archivo.write('\n'.join(contenido))


# --- Ejecución principal ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python leer_tablero.py <ruta_del_archivo>")
        sys.exit(1)

    ruta = sys.argv[1]

    try:
        tablero = NumberLinkBoardIO.leer_tablero(ruta)
        print(f"Tablero leído correctamente desde: {ruta}\n")
        NumberLinkBoardIO.imprimir_tablero(tablero)
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
