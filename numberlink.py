# solucionador_backtracking.py
# Autor: Katheryn Guasca
# Descripción: Resuelve tableros NumberLink usando backtracking con heurística de bordes

import copy
from collections import deque

def encontrar_pares(tablero):
    """Encuentra todos los pares de números en el tablero."""
    pares = {}
    filas = len(tablero)
    cols = len(tablero[0]) if filas > 0 else 0
    
    for i in range(filas):
        for j in range(cols):
            celda = tablero[i][j]
            if celda != ' ':
                if celda not in pares:
                    pares[celda] = []
                pares[celda].append((i, j))
    
    pares_validos = {k: v for k, v in pares.items() if len(v) == 2}
    return pares_validos


def contar_posiciones_borde(pos1, pos2, filas, cols):
    """Cuenta cuántas de las dos posiciones están en el borde."""
    def esta_en_borde(fila, col):
        return fila == 0 or fila == filas - 1 or col == 0 or col == cols - 1
    
    count = 0
    if esta_en_borde(pos1[0], pos1[1]):
        count += 1
    if esta_en_borde(pos2[0], pos2[1]):
        count += 1
    return count


def calcular_distancia_manhattan(pos1, pos2):
    """Calcula la distancia Manhattan entre dos posiciones."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def contar_esquinas(pos1, pos2, filas, cols):
    """Cuenta cuántas posiciones están en una esquina."""
    def es_esquina(fila, col):
        return ((fila == 0 or fila == filas - 1) and 
                (col == 0 or col == cols - 1))
    
    count = 0
    if es_esquina(pos1[0], pos1[1]):
        count += 1
    if es_esquina(pos2[0], pos2[1]):
        count += 1
    return count


def ordenar_pares_por_heuristica(tablero):
    """Ordena los pares según la heurística de bordes."""
    pares = encontrar_pares(tablero)
    filas = len(tablero)
    cols = len(tablero[0]) if filas > 0 else 0
    
    pares_con_prioridad = []
    
    for numero, posiciones in pares.items():
        pos1, pos2 = posiciones
        
        bordes = contar_posiciones_borde(pos1, pos2, filas, cols)
        esquinas = contar_esquinas(pos1, pos2, filas, cols)
        distancia = calcular_distancia_manhattan(pos1, pos2)
        
        prioridad = esquinas * 1000 + bordes * 100 + (100 - distancia)
        
        pares_con_prioridad.append((numero, pos1, pos2, prioridad))
    
    pares_con_prioridad.sort(key=lambda x: x[3], reverse=True)
    
    return [(num, p1, p2) for num, p1, p2, _ in pares_con_prioridad]


def obtener_vecinos(pos, filas, cols):
    """Retorna las posiciones vecinas válidas."""
    fila, col = pos
    vecinos = []
    # Priorizar bordes: arriba, abajo, izq, der
    direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    for df, dc in direcciones:
        nf, nc = fila + df, col + dc
        if 0 <= nf < filas and 0 <= nc < cols:
            vecinos.append((nf, nc))
    
    return vecinos


def encontrar_todos_caminos(tablero_trabajo, inicio, fin, numero, max_caminos=50):
    """
    Encuentra TODOS los caminos posibles desde inicio hasta fin.
    Retorna una lista de caminos ordenados por longitud.
    """
    filas = len(tablero_trabajo)
    cols = len(tablero_trabajo[0])
    
    todos_caminos = []
    
    def dfs(pos_actual, camino, visitados):
        if len(todos_caminos) >= max_caminos:
            return
        
        if pos_actual == fin:
            todos_caminos.append(list(camino))
            return
        
        for vecino in obtener_vecinos(pos_actual, filas, cols):
            if vecino in visitados:
                continue
            
            celda = tablero_trabajo[vecino[0]][vecino[1]]
            
            if celda == ' ' or vecino == fin:
                visitados.add(vecino)
                camino.append(vecino)
                dfs(vecino, camino, visitados)
                camino.pop()
                visitados.remove(vecino)
    
    visitados_inicial = {inicio}
    dfs(inicio, [inicio], visitados_inicial)
    
    # Ordenar por longitud (preferir caminos cortos)
    todos_caminos.sort(key=lambda c: len(c))
    
    return todos_caminos


def marcar_camino(tablero, camino, numero):
    """Marca un camino en el tablero."""
    for i, pos in enumerate(camino):
        if i == 0 or i == len(camino) - 1:
            continue
        tablero[pos[0]][pos[1]] = numero.lower()


def desmarcar_camino(tablero, camino, numero):
    """Desmarca un camino del tablero."""
    for i, pos in enumerate(camino):
        if i == 0 or i == len(camino) - 1:
            continue
        tablero[pos[0]][pos[1]] = ' '


def resolver_numberlink_backtracking(tablero_original, verbose=True):
    """
    Resuelve el tablero NumberLink usando backtracking.
    Prueba diferentes caminos hasta encontrar una solución completa.
    """
    tablero = copy.deepcopy(tablero_original)
    pares_ordenados = ordenar_pares_por_heuristica(tablero_original)
    
    if verbose:
        print("\n=== ESTRATEGIA: BACKTRACKING CON HEURÍSTICA DE BORDES ===")
        print(f"Total de pares a conectar: {len(pares_ordenados)}\n")
    
    intentos = [0]  # Contador de intentos
    
    def backtrack(idx, caminos_usados):
        intentos[0] += 1
        
        if idx == len(pares_ordenados):
            # Verificar que todas las celdas estén llenas
            for fila in tablero:
                if ' ' in fila:
                    return False
            return True
        
        numero, pos1, pos2 = pares_ordenados[idx]
        
        # Encontrar todos los caminos posibles
        caminos = encontrar_todos_caminos(tablero, pos1, pos2, numero)
        
        if verbose and idx == 0:
            print(f"Conectando '{numero}': encontrados {len(caminos)} caminos posibles")
        
        # Probar cada camino
        for camino in caminos:
            # Marcar el camino
            marcar_camino(tablero, camino, numero)
            
            # Recursión
            if backtrack(idx + 1, caminos_usados + [camino]):
                return True
            
            # Deshacer (backtrack)
            desmarcar_camino(tablero, camino, numero)
        
        return False
    
    if backtrack(0, []):
        if verbose:
            print(f"\n✓ Solución encontrada en {intentos[0]} intentos")
        return tablero, True
    else:
        if verbose:
            print(f"\n✗ No se encontró solución después de {intentos[0]} intentos")
        return tablero, False


def imprimir_tablero(tablero):
    """Imprime el tablero en formato legible."""
    for fila in tablero:
        print(''.join(fila))


# --- Ejemplo de uso ---
if __name__ == "__main__":
    from leer_tablero import leer_tablero
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python solucionador_backtracking.py <ruta_del_archivo>")
        sys.exit(1)
    
    ruta = sys.argv[1]
    
    try:
        tablero = leer_tablero(ruta)
        
        print("=== TABLERO ORIGINAL ===")
        imprimir_tablero(tablero)
        
        # Mostrar información de pares
        pares = encontrar_pares(tablero)
        print(f"\nPares a conectar: {len(pares)}")
        for num, posiciones in sorted(pares.items()):
            print(f"  '{num}': {posiciones[0]} ↔ {posiciones[1]}")
        
        # Resolver con backtracking
        solucion, completa = resolver_numberlink_backtracking(tablero, verbose=True)
        
        if completa:
            print("\n=== TABLERO RESUELTO ===")
            imprimir_tablero(solucion)
        else:
            print("\n=== SOLUCIÓN PARCIAL ===")
            imprimir_tablero(solucion)
            print("\nNo se pudo encontrar una solución completa.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()