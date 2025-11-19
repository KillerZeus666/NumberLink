"""
 Implementa una búsqueda en profundidad con poda alfa‑beta, pero sin adversario 
 (ambos niveles maximizan la misma función de evaluación). Para cada par genera 
 muchos caminos, marca uno y calcula un valor heurístico: premia estados con más 
 caminos disponibles para los pares pendientes y penaliza distancias mínimas altas 
 y espacios vacíos. Alfa‑beta evita explorar ramas que ya no pueden superar la mejor 
 puntuación encontrada, acelerando la DFS.
"""

import copy
import heapq
from collections import deque
import math

MAX_CAMINOS_POR_PAR = 10000  # para búsqueda estándar
MAX_CAMINOS_MINIMAX = 6000   # para búsqueda max/max (sin adversario)
PUNTUACION_SOLUCION = 1_000_000

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


def heuristica_restante(pares_ordenados, idx):
    """Suma una cota inferior de celdas a rellenar para los pares restantes."""
    h = 0
    for _, p1, p2 in pares_ordenados[idx:]:
        h += max(0, calcular_distancia_manhattan(p1, p2) - 1)
    return h


def contar_celdas_ocupadas(tablero):
    return sum(1 for fila in tablero for celda in fila if celda != ' ')


def tablero_a_clave(tablero):
    return ''.join(''.join(fila) for fila in tablero)


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

    g0 = contar_celdas_ocupadas(tablero_inicial)
    h0 = heuristica_restante(pares_ordenados, 0)
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
        caminos = encontrar_todos_caminos(tablero, pos1, pos2, numero, max_caminos=max_caminos_por_par)

        if verbose and idx == 0:
            print(f"Conectando '{numero}' con {len(caminos)} caminos candidatos (A*)")

        for camino in caminos:
            # Crear nuevo tablero con el camino marcado
            nuevo_tablero = copy.deepcopy(tablero)
            nuevas_celdas = 0
            for pos in camino[1:-1]:
                if nuevo_tablero[pos[0]][pos[1]] == ' ':
                    nuevas_celdas += 1
            marcar_camino(nuevo_tablero, camino, numero)

            nuevo_idx = idx + 1
            nuevo_g = g_actual + nuevas_celdas
            nuevo_h = heuristica_restante(pares_ordenados, nuevo_idx)
            nueva_clave = tablero_a_clave(nuevo_tablero)

            clave_estado = (nuevo_idx, nueva_clave)
            if clave_estado in mejor_g and nuevo_g >= mejor_g[clave_estado]:
                continue
            mejor_g[clave_estado] = nuevo_g

            estado_id += 1
            heapq.heappush(heap, (nuevo_g + nuevo_h, nuevo_h, estado_id, nuevo_idx, nuevo_g, nuevo_tablero))

    if verbose:
        print("\n✗ A* no encontró solución")
    return tablero_original, False



# --- Minimax con poda alfa-beta ---
def contar_caminos_restantes(tablero, pares_ordenados, idx, limite_por_par):
    """Cuenta cuántos caminos legales quedan para cada par restante (corto)."""
    total = 0
    for numero, p1, p2 in pares_ordenados[idx:]:
        total += len(encontrar_todos_caminos(tablero, p1, p2, numero, max_caminos=limite_por_par))
    return total


def evaluar_estado(tablero, pares_ordenados, idx):
    """Evalúa un estado: más caminos disponibles y menor heurística es mejor."""
    caminos = contar_caminos_restantes(tablero, pares_ordenados, idx, limite_por_par=20)
    h = heuristica_restante(pares_ordenados, idx)
    libres = sum(1 for fila in tablero for celda in fila if celda == ' ')
    # Premia opciones futuras, penaliza distancia mínima y espacios vacíos
    return caminos * 100 - h * 10 - libres


def minimax(tablero, pares_ordenados, idx, profundidad, alpha, beta, max_caminos_por_par):
    """Búsqueda max/max (sin adversario) con poda alfa-beta."""
    if idx == len(pares_ordenados):
        # Si ya colocamos todos los pares, solo es victoria si no hay espacios.
        if all(' ' not in fila for fila in tablero):
            return PUNTUACION_SOLUCION, tablero
        return -PUNTUACION_SOLUCION // 2, tablero

    if profundidad == 0:
        return evaluar_estado(tablero, pares_ordenados, idx), tablero

    numero, pos1, pos2 = pares_ordenados[idx]
    caminos = encontrar_todos_caminos(tablero, pos1, pos2, numero, max_caminos=max_caminos_por_par)

    if not caminos:
        # Si no hay movimientos, es un estado muerto.
        return -PUNTUACION_SOLUCION, tablero

    mejor_val = -math.inf
    mejor_tablero = None
    for camino in caminos:
        nuevo_tablero = copy.deepcopy(tablero)
        marcar_camino(nuevo_tablero, camino, numero)
        val, tablero_hijo = minimax(nuevo_tablero, pares_ordenados, idx + 1, profundidad - 1, alpha, beta, max_caminos_por_par)
        if val > mejor_val:
            mejor_val = val
            mejor_tablero = tablero_hijo
        alpha = max(alpha, mejor_val)
        if beta <= alpha:
            break
    return mejor_val, mejor_tablero


def resolver_numberlink_minimax(tablero_original, verbose=True, profundidad=None, max_caminos_por_par=MAX_CAMINOS_MINIMAX):
    """
    Resuelve buscando rutas con minimax (MAX elige, MIN adversario hipotético).
    Profundidad limitada para evitar explosión combinatoria.
    """
    tablero = copy.deepcopy(tablero_original)
    pares_ordenados = ordenar_pares_por_heuristica(tablero)

    if profundidad is None:
        profundidad = len(pares_ordenados)  # cubrir todos los pares

    if verbose:
        print("\n=== ESTRATEGIA: MINIMAX CON PODA ===")
        print(f"Total de pares a conectar: {len(pares_ordenados)}\n")

    val, tablero_resultado = minimax(tablero, pares_ordenados, 0, profundidad, -math.inf, math.inf, max_caminos_por_par)
    completa = tablero_resultado is not None and all(' ' not in fila for fila in tablero_resultado) and val >= PUNTUACION_SOLUCION

    if verbose:
        if completa:
            print(f"\n✓ Minimax encontró solución (valor={val})")
        else:
            print(f"\n✗ Minimax sin solución completa. Mejor valor encontrado={val}")

    return tablero_resultado if tablero_resultado else tablero_original, completa


def imprimir_tablero(tablero):
    """Imprime el tablero en formato legible."""
    for fila in tablero:
        print(''.join(fila))


# --- Ejemplo de uso ---
if __name__ == "__main__":
    from leer_tablero import leer_tablero
    from verificar_tablero import verificar_tablero
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python numberlink_minmax.py <ruta_del_archivo>")
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
        
        # Resolver con minimax
        solucion, completa = resolver_numberlink_minimax(tablero, verbose=True, profundidad=None, max_caminos_por_par=MAX_CAMINOS_MINIMAX)
        
        print("\n=== TABLERO RESULTADO (MINIMAX) ===")
        imprimir_tablero(solucion)
        
        print("\n=== VERIFICACIÓN ===")
        verificar_tablero(solucion)
        
        if not completa:
            print("\nNo se encontró solución completa con minimax.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
