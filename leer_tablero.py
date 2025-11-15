# leer_tablero.py
# Autor: Katheryn Guasca
# Descripción: Lee un archivo de texto que define un tablero NumberLink.

import sys
import os

# ESTAS FUNCIONES DEBEN ESTAR FUERA DEL if __name__ == "__main__"
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


def imprimir_tablero(tablero):
    """Imprime el tablero en formato legible."""
    for fila in tablero:
        print(''.join(fila))


# --- Ejecución principal ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python leer_tablero.py <ruta_del_archivo>")
        sys.exit(1)

    ruta = sys.argv[1]

    try:
        tablero = leer_tablero(ruta)
        print(f"Tablero leído correctamente desde: {ruta}\n")
        imprimir_tablero(tablero)
    except Exception as e:
        print(f"Error al leer el archivo: {e}")