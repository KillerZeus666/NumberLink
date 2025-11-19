# solucionador_backtracking.py
# Autor: Katheryn Guasca
# Descripción: Resuelve tableros NumberLink usando backtracking con heurística de bordes

import copy
from collections import deque
from itertools import islice

MAX_CAMINOS_PAR = 10000
MAX_CANDIDATOS_PARES = 3
MAX_CAMINOS_CHECK = 10000
mem_tablero = {}

"""
Estrategia: En cada paso elige el siguiente par más “restringido” (el que tiene menos 
caminos disponibles en el tablero actual), genera hasta 10 000 caminos para ese par 
y antes de seguir recursando verifica conectividad y paridad de componentes libres, además 
de que los pares restantes aún tengan al menos un camino accesible. Poda estados que dejan 
extremos en componentes distintas o islas sin extremos.
"""

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


def encontrar_todos_caminos(tablero_trabajo, inicio, fin, numero, max_caminos=MAX_CAMINOS_PAR):
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


def generar_caminos_incremental(tablero_trabajo, inicio, fin, max_caminos=MAX_CAMINOS_PAR):
    """
    Generador BFS que produce caminos desde origen a destino priorizando los más cortos.
    """
    filas = len(tablero_trabajo)
    cols = len(tablero_trabajo[0])
    cola = deque([[inicio]])
    generados = 0

    while cola and generados < max_caminos:
        camino = cola.popleft()
        pos_actual = camino[-1]

        if pos_actual == fin:
            generados += 1
            yield camino
            continue

        for vecino in obtener_vecinos(pos_actual, filas, cols):
            if vecino in camino:
                continue
            celda = tablero_trabajo[vecino[0]][vecino[1]]
            if celda == ' ' or vecino == fin:
                cola.append(camino + [vecino])


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


def analizar_componentes(tablero, pares_restantes):
    """
    Poda por componentes: las celdas transitables son espacios y los extremos pendientes.
    - Cada componente debe tener un número par de extremos y no quedarse sin extremos si hay huecos.
    - Los extremos de cada par deben estar en la misma componente.
    """
    filas, cols = len(tablero), len(tablero[0])
    extremos = set()
    for _, p1, p2 in pares_restantes:
        extremos.add(p1)
        extremos.add(p2)

    comp_id = [[-1] * cols for _ in range(filas)]
    comp_info = []

    def es_transitable(pos):
        return tablero[pos[0]][pos[1]] == ' ' or pos in extremos

    def bfs(inicio, comp_idx):
        q = deque([inicio])
        comp_id[inicio[0]][inicio[1]] = comp_idx
        libres = 0
        ends = 0
        while q:
            i, j = q.popleft()
            if (i, j) in extremos:
                ends += 1
            elif tablero[i][j] == ' ':
                libres += 1
            for ni, nj in obtener_vecinos((i, j), filas, cols):
                if comp_id[ni][nj] != -1:
                    continue
                if es_transitable((ni, nj)):
                    comp_id[ni][nj] = comp_idx
                    q.append((ni, nj))
        comp_info.append({"libres": libres, "extremos": ends})

    comp_idx = 0
    for i in range(filas):
        for j in range(cols):
            if comp_id[i][j] == -1 and es_transitable((i, j)):
                bfs((i, j), comp_idx)
                comp_idx += 1

    # Reglas de paridad y alcance de pares
    for info in comp_info:
        if info["libres"] > 0 and info["extremos"] == 0:
            return False
        if info["extremos"] % 2 == 1:
            return False

    # Cada extremo de un par debe estar en la misma componente
    for _, p1, p2 in pares_restantes:
        if comp_id[p1[0]][p1[1]] != comp_id[p2[0]][p2[1]]:
            return False

    return True


def detectar_cuellos(tablero, pares_restantes):
    """
    Detecta celdas libres con grado <= 1 que no son extremos pendientes.
    """
    if not pares_restantes:
        return False

    filas, cols = len(tablero), len(tablero[0])
    extremos = set()
    for _, p1, p2 in pares_restantes:
        extremos.add(p1)
        extremos.add(p2)

    for i in range(filas):
        for j in range(cols):
            if tablero[i][j] != ' ':
                continue
            if (i, j) in extremos:
                continue
            vecinos_libres = 0
            for ni, nj in obtener_vecinos((i, j), filas, cols):
                if tablero[ni][nj] == ' ' or (ni, nj) in extremos:
                    vecinos_libres += 1
            if vecinos_libres <= 1:
                return True
    return False


def existe_camino_basico(tablero, inicio, fin):
    """Comprueba conectividad simple mediante BFS."""
    filas = len(tablero)
    cols = len(tablero[0])
    visitados = set([inicio])
    cola = deque([inicio])

    while cola:
        i, j = cola.popleft()
        if (i, j) == fin:
            return True
        for ni, nj in obtener_vecinos((i, j), filas, cols):
            if (ni, nj) in visitados:
                continue
            celda = tablero[ni][nj]
            if celda == ' ' or (ni, nj) == fin:
                visitados.add((ni, nj))
                cola.append((ni, nj))
    return False


def hay_camino_para_pares(tablero, pares):
    """
    Verifica que cada par pendiente tenga al menos un camino posible mediante BFS.
    """
    for _, pos1, pos2 in pares[:MAX_CAMINOS_CHECK]:
        if not existe_camino_basico(tablero, pos1, pos2):
            return False
    return True


def tablero_a_clave(tablero):
    return ''.join(''.join(fila) for fila in tablero)


def obtener_candidatos_pares(tablero, pares, max_candidatos=MAX_CANDIDATOS_PARES, max_caminos=MAX_CAMINOS_PAR):
    """
    Obtiene hasta max_candidatos pares ordenados por cantidad de caminos disponibles.
    Cada camino se genera incrementalmente para priorizar rutas cortas.
    """
    clave_tablero = tablero_a_clave(tablero)
    cache_tablero = mem_tablero.setdefault(clave_tablero, {})
    opciones = []
    for idx, (numero, p1, p2) in enumerate(pares):
        if numero in cache_tablero:
            caminos = cache_tablero[numero]
        else:
            generador = generar_caminos_incremental(tablero, p1, p2, max_caminos=max_caminos)
            caminos = list(islice(generador, max_caminos))
            cache_tablero[numero] = caminos
        if not caminos:
            continue
        opciones.append((len(caminos), idx, caminos))

    opciones.sort(key=lambda x: x[0])
    candidatos = []
    for _, idx, caminos in opciones[:max_candidatos]:
        candidatos.append((idx, caminos))
    return candidatos


def resolver_numberlink_backtracking(tablero_original, verbose=True, max_caminos_por_par=10000):
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
    
    def backtrack(pares_restantes):
        intentos[0] += 1
        
        if not pares_restantes:
            # Verificar que todas las celdas estén llenas
            for fila in tablero:
                if ' ' in fila:
                    return False
            return True
        
        candidatos = obtener_candidatos_pares(tablero, pares_restantes, max_candidatos=MAX_CANDIDATOS_PARES, max_caminos=max_caminos_por_par)
        if not candidatos:
            return False

        for idx_sel, caminos in candidatos:
            if verbose and len(pares_restantes) == len(pares_ordenados):
                print(f"Conectando '{pares_restantes[idx_sel][0]}': {len(caminos)} caminos candidatos")

            numero, pos1, pos2 = pares_restantes[idx_sel]
            restantes = pares_restantes[:idx_sel] + pares_restantes[idx_sel+1:]

            limite_caminos = min(len(caminos), max_caminos_por_par)
            for camino in caminos[:limite_caminos]:
                marcar_camino(tablero, camino, numero)
                # Poda: asegurar que los pares pendientes sigan conectables
                if analizar_componentes(tablero, restantes) and hay_camino_para_pares(tablero, restantes):
                    if backtrack(restantes):
                        return True
                desmarcar_camino(tablero, camino, numero)
        return False
    
    if backtrack(pares_ordenados):
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
