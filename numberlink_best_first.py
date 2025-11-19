# solucionador_backtracking.py
# Autor: Katheryn Guasca
# Descripción: Resuelve tableros NumberLink usando backtracking con heurística de bordes

"""
 Usa A* como motor principal. Genera muchos caminos posibles para cada par, 
 los ordena con una heurística que prioriza pares en esquinas/bordes y distancias 
 cortas, y luego explora estados (tableros parciales) con A*. En A*, g es el número 
 de celdas ya ocupadas y h es la suma de distancias Manhattan mínimas que quedan por
 cubrir; con f=g+h el algoritmo siempre expande el estado aparentemente más prometedor
"""

import copy
import heapq
import os
import time
from collections import deque

MAX_CAMINOS_POR_PAR = 2000

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


def encontrar_todos_caminos(tablero_trabajo, inicio, fin, numero, max_caminos=MAX_CAMINOS_POR_PAR):
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


def generar_caminos_incremental(tablero_trabajo, inicio, fin, max_caminos=MAX_CAMINOS_POR_PAR):
    """
    Genera caminos utilizando BFS para obtener primero los más cortos.
    Evita crear toda la lista en memoria.
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


def evaluar_componentes(tablero, pares_restantes):
    """
    Obtiene información de componentes.
    Retorna (es_valido, penalización_por_componentes).
    """
    if not pares_restantes:
        completo = all(' ' not in fila for fila in tablero)
        return completo, 0 if completo else float('inf')

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
        extremos_comp = 0
        while q:
            i, j = q.popleft()
            if (i, j) in extremos:
                extremos_comp += 1
            elif tablero[i][j] == ' ':
                libres += 1
            for ni, nj in obtener_vecinos((i, j), filas, cols):
                if comp_id[ni][nj] != -1:
                    continue
                if es_transitable((ni, nj)):
                    comp_id[ni][nj] = comp_idx
                    q.append((ni, nj))
        comp_info.append({"libres": libres, "extremos": extremos_comp})

    comp_idx = 0
    for i in range(filas):
        for j in range(cols):
            if comp_id[i][j] == -1 and es_transitable((i, j)):
                bfs((i, j), comp_idx)
                comp_idx += 1

    componentes_con_extremos = 0
    for info in comp_info:
        if info["libres"] > 0 and info["extremos"] == 0:
            return False, float('inf')
        if info["extremos"] % 2 == 1:
            return False, float('inf')
        if info["extremos"] > 0:
            componentes_con_extremos += 1

    for _, p1, p2 in pares_restantes:
        if comp_id[p1[0]][p1[1]] != comp_id[p2[0]][p2[1]]:
            return False, float('inf')

    penalizacion = max(0, componentes_con_extremos - 1)
    return True, penalizacion


def analizar_componentes(tablero, pares_restantes):
    """
    Analiza componentes de celdas libres + extremos pendientes y retorna si el estado es válido.
    """
    valido, _ = evaluar_componentes(tablero, pares_restantes)
    return valido



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
        caminos = encontrar_todos_caminos(tablero, pos1, pos2, numero, max_caminos=max_caminos_por_par)
        
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


def heuristica_distancia(pares_restantes):
    """Suma una cota inferior de celdas a rellenar para los pares restantes."""
    return sum(max(0, calcular_distancia_manhattan(p1, p2) - 1) for _, p1, p2 in pares_restantes)


def contar_celdas_libres(tablero):
    return sum(1 for fila in tablero for celda in fila if celda == ' ')


def heuristica_total(tablero, pares_restantes, penalizacion_componentes=0):
    """Combina distancia mínima con penalizaciones suaves."""
    return (heuristica_distancia(pares_restantes) +
            penalizacion_componentes * 5 +
            contar_celdas_libres(tablero))


def contar_celdas_ocupadas(tablero):
    return sum(1 for fila in tablero for celda in fila if celda != ' ')


def tablero_a_clave(tablero):
    return ''.join(''.join(fila) for fila in tablero)


def pares_con_camino(tablero, pares, limite=200):
    """Verifica rápidamente que cada par tenga al menos un camino posible."""
    for numero, p1, p2 in pares:
        caminos = encontrar_todos_caminos(tablero, p1, p2, numero, max_caminos=limite)
        if not caminos:
            return False
    return True


def resolver_numberlink_a_star(tablero_original, verbose=True, max_caminos_por_par=10000):
    """
    Resuelve el tablero usando A*.
    f = g + h, con g = celdas ocupadas y h = Manhattan mínima restante.
    """
    tablero_inicial = copy.deepcopy(tablero_original)
    pares_ordenados = ordenar_pares_por_heuristica(tablero_inicial)

    if verbose:
        print("\n=== ESTRATEGIA: A* CON HEURÍSTICA DE DISTANCIA ===")
        print(f"Total de pares a conectar: {len(pares_ordenados)}\n")

    heap = []
    mejor_g = {}
    estado_id = 0

    if not analizar_componentes(tablero_inicial, pares_ordenados):
        if verbose:
            print("Estado inicial inválido por componentes.")
        return tablero_original, False

    if not pares_con_camino(tablero_inicial, pares_ordenados):
        if verbose:
            print("Estado inicial inválido: algún par no tiene caminos.")
        return tablero_original, False

    g0 = contar_celdas_ocupadas(tablero_inicial)
    component_cache = {}

    def validar_componentes(idx_local, tablero_actual, pares_restantes):
        clave = (idx_local, tablero_a_clave(tablero_actual))
        if clave in component_cache:
            return component_cache[clave]
        valido, penalizacion = evaluar_componentes(tablero_actual, pares_restantes)
        component_cache[clave] = (valido, penalizacion)
        return component_cache[clave]

    valido_inicial, penalizacion_inicial = validar_componentes(0, tablero_inicial, pares_ordenados)
    if not valido_inicial:
        if verbose:
            print("Estado inicial inválido tras evaluación detallada.")
        return tablero_original, False

    h0 = heuristica_total(tablero_inicial, pares_ordenados, penalizacion_inicial)
    heapq.heappush(heap, (g0 + h0, h0, estado_id, 0, g0, tablero_inicial))
    mejor_g[(0, tablero_a_clave(tablero_inicial))] = g0

    while heap:
        f, h_actual, _, idx, g_actual, tablero = heapq.heappop(heap)

        if idx == len(pares_ordenados):
            if all(' ' not in fila for fila in tablero):
                if verbose:
                    print(f"\n✓ Solución encontrada con A* (g={g_actual}, h={h_actual})")
                return tablero, True
            continue

        numero, pos1, pos2 = pares_ordenados[idx]
        caminos_iter = generar_caminos_incremental(tablero, pos1, pos2, max_caminos=max_caminos_por_par)
        caminos_procesados = 0

        for camino in caminos_iter:
            caminos_procesados += 1
            # Crear nuevo tablero con el camino marcado
            nuevo_tablero = copy.deepcopy(tablero)
            nuevas_celdas = 0
            for pos in camino[1:-1]:
                if nuevo_tablero[pos[0]][pos[1]] == ' ':
                    nuevas_celdas += 1
            marcar_camino(nuevo_tablero, camino, numero)

            nuevo_idx = idx + 1
            restantes = pares_ordenados[nuevo_idx:]

            valido_componentes, penalizacion_componentes = validar_componentes(nuevo_idx, nuevo_tablero, restantes)
            if not valido_componentes:
                continue

            nuevo_g = g_actual + nuevas_celdas
            nuevo_h = heuristica_total(nuevo_tablero, restantes, penalizacion_componentes)
            nueva_clave = tablero_a_clave(nuevo_tablero)

            clave_estado = (nuevo_idx, nueva_clave)
            if clave_estado in mejor_g and nuevo_g >= mejor_g[clave_estado]:
                continue
            mejor_g[clave_estado] = nuevo_g

            estado_id += 1
            heapq.heappush(heap, (nuevo_g + nuevo_h, nuevo_h, estado_id, nuevo_idx, nuevo_g, nuevo_tablero))

        if verbose and idx == 0:
            print(f"Conectando '{numero}' con {caminos_procesados} caminos candidatos (A*)")

    if verbose:
        print("\n✗ A* no encontró solución")
    return tablero_original, False


def imprimir_tablero(tablero):
    """Imprime el tablero en formato legible."""
    for fila in tablero:
        print(''.join(fila))


# --- Ejemplo de uso ---
if __name__ == "__main__":
    from leer_tablero import NumberLinkBoardIO
    from verificar_tablero import NumberLinkVerifier
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python numberlink.py <ruta_del_archivo>")
        sys.exit(1)
    
    ruta = sys.argv[1]
    
    try:
        tablero = NumberLinkBoardIO.leer_tablero(ruta)
        
        print("=== TABLERO ORIGINAL ===")
        imprimir_tablero(tablero)
        
        # Mostrar información de pares
        pares = encontrar_pares(tablero)
        print(f"\nPares a conectar: {len(pares)}")
        for num, posiciones in sorted(pares.items()):
            print(f"  '{num}': {posiciones[0]} ↔ {posiciones[1]}")
        
        # Resolver con A*
        filas = len(tablero)
        cols = len(tablero[0]) if filas else 0
        ruta_salida = os.path.join("tablerosSalida", f"salida{filas}x{cols}.txt")

        inicio = time.perf_counter()
        solucion, completa = resolver_numberlink_a_star(tablero, verbose=True, max_caminos_por_par=MAX_CAMINOS_POR_PAR)
        duracion = time.perf_counter() - inicio
        
        print("\n=== TABLERO RESULTADO (A*) ===")
        imprimir_tablero(solucion)
        
        print("\n=== VERIFICACIÓN ===")
        NumberLinkVerifier.verificar_tablero(solucion)
        
        NumberLinkBoardIO.guardar_resultado(solucion, ruta_salida, "A* Best-First", duracion, completa)
        print(f"\nTiempo de resolución: {duracion:.4f} s")
        print(f"Resultado guardado en: {ruta_salida}")
        if not completa:
            print("\nNo se encontró solución completa con A*.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
