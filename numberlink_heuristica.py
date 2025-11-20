# solucionador_backtracking.py
# Autor: Katheryn Guasca, Simon Diaz y Melissa Ruiz 
# Descripción: Resuelve tableros NumberLink usando backtracking con heurística de bordes

import copy
import os
import time
from collections import deque
from itertools import islice


class NumberLinkHeuristicSolver:
    """
    Estrategia: En cada paso elige el siguiente par más “restringido” (el que tiene menos
    caminos disponibles en el tablero actual), genera hasta MAX_CAMINOS_PAR caminos para ese par
    y antes de seguir recursando verifica conectividad, paridad de componentes libres y la inexistencia
    de cuellos de botella (celdas libres no-extremo con grado <= 1). También valida que los pares
    restantes sigan teniendo algún camino accesible y usa una tabla de memoización (MEMO_TABLERO)
    para recordar los caminos ya calculados por tablero.
    """

    MAX_CAMINOS_PAR = 10000
    MAX_CANDIDATOS_PARES = 3
    MAX_CAMINOS_CHECK = 10000
    MEMO_TABLERO = {}

    @staticmethod
    def tablero_a_clave(tablero): # esta no
        """Convierte el tablero en una cadena lineal para usar como clave del tablero de memoización."""
        return ''.join(''.join(fila) for fila in tablero)

    @staticmethod
    def encontrar_pares(tablero): # esta si 
        """Devuelve un dict de pares válidos (dos ocurrencias) por símbolo."""
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

        return {k: v for k, v in pares.items() if len(v) == 2}

    @staticmethod
    def contar_posiciones_borde(pos1, pos2, filas, cols): # esta si pero en ordenar_pares_por_heuristica
        """Cuenta cuántos extremos caen en el borde del tablero."""
        count = 0
        if NumberLinkHeuristicSolver.esta_en_borde(pos1[0], pos1[1], filas, cols): # aca se pone la funcion que se llama para el pseucodigo 
            count += 1
        if NumberLinkHeuristicSolver.esta_en_borde(pos2[0], pos2[1], filas, cols):
            count += 1
        return count

    @staticmethod
    def esta_en_borde(fila, col, filas, cols):
        """Indica si una celda está en el borde exterior del tablero."""
        return fila == 0 or fila == filas - 1 or col == 0 or col == cols - 1

    @staticmethod
    def calcular_distancia_manhattan(pos1, pos2): # esta si pero en ordenar_pares_por_heuristica
        """Distancia Manhattan entre dos posiciones."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    @staticmethod
    def contar_esquinas(pos1, pos2, filas, cols): # esta si pero en ordenar_pares_por_heuristica
        """Cuenta cuántos extremos están en esquinas."""
        count = 0
        if NumberLinkHeuristicSolver.es_esquina(pos1[0], pos1[1], filas, cols):# aca se pone la funcion que se llama para el pseucodigo
            count += 1
        if NumberLinkHeuristicSolver.es_esquina(pos2[0], pos2[1], filas, cols):
            count += 1
        return count

    @staticmethod
    def es_esquina(fila, col, filas, cols):
        """Indica si una celda es una esquina del tablero."""
        return ((fila == 0 or fila == filas - 1) and (col == 0 or col == cols - 1))

    @classmethod #FUNCION GRANDE QUE SI VA (1) Melissa 
    def ordenar_pares_por_heuristica(cls, tablero): # esta si 
        """Ordena pares priorizando esquinas, bordes y distancias cortas."""
        pares = cls.encontrar_pares(tablero)
        filas = len(tablero)
        cols = len(tablero[0]) if filas > 0 else 0

        pares_con_prioridad = []

        for numero, posiciones in pares.items():
            pos1, pos2 = posiciones

            bordes = cls.contar_posiciones_borde(pos1, pos2, filas, cols) # aca se pone la funcion que se llama para el pseucodigo
            esquinas = cls.contar_esquinas(pos1, pos2, filas, cols)
            distancia = cls.calcular_distancia_manhattan(pos1, pos2)

            prioridad = esquinas * 1000 + bordes * 100 + (100 - distancia)
            pares_con_prioridad.append((numero, pos1, pos2, prioridad))

        pares_con_prioridad.sort(key=lambda x: x[3], reverse=True)

        return [(num, p1, p2) for num, p1, p2, _ in pares_con_prioridad]

    @staticmethod
    def obtener_vecinos(pos, filas, cols): # esta si pero en _dfs_rutas y en generar_caminos_incremental y en detectar_cuellos y en _bfs_component y en existe_camino_basico
        """Retorna vecinos ortogonales dentro del tablero."""
        fila, col = pos
        vecinos = []
        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for df, dc in direcciones:
            nf, nc = fila + df, col + dc
            if 0 <= nf < filas and 0 <= nc < cols:
                vecinos.append((nf, nc))

        return vecinos

    @classmethod
    def encontrar_todos_caminos(cls, tablero_trabajo, inicio, fin, numero, max_caminos=None): # esta si pero en generar_caminos_incremental
        """Enumera caminos posibles entre dos extremos, ordenados por longitud."""
        limite = max_caminos if max_caminos is not None else cls.MAX_CAMINOS_PAR
        filas = len(tablero_trabajo)
        cols = len(tablero_trabajo[0])
        todos_caminos = []
        cls._dfs_rutas(tablero_trabajo, fin, filas, cols, limite, inicio, [inicio], {inicio}, todos_caminos)
        todos_caminos.sort(key=lambda c: len(c))
        return todos_caminos

    @classmethod
    #SEGUNDA FUNCION GRANDE QUE SI VA (2) Melissa
    def _dfs_rutas(cls, tablero, fin, filas, cols, limite, pos_actual, camino, visitados, todos_caminos): # esta si 
        """DFS auxiliar para construir rutas completas."""
        if len(todos_caminos) >= limite:
            return

        if pos_actual == fin:
            todos_caminos.append(list(camino))
            return

        for vecino in cls.obtener_vecinos(pos_actual, filas, cols): # aca se pone la funcion que se llama para el pseucodigo
            if vecino in visitados:
                continue

            celda = tablero[vecino[0]][vecino[1]]
            if celda == ' ' or vecino == fin:
                visitados.add(vecino)
                camino.append(vecino)
                cls._dfs_rutas(tablero, fin, filas, cols, limite, vecino, camino, visitados, todos_caminos) # aca se pone la funcion que se llama para el pseucodigo
                camino.pop()
                visitados.remove(vecino)

    @classmethod
    # TERCERA FUNCION GRANDE QUE SI VA (3) Melissa
    def generar_caminos_incremental(cls, tablero_trabajo, inicio, fin, max_caminos=None): # esta si 
        """Generador BFS que produce primero las rutas más cortas."""
        limite = max_caminos if max_caminos is not None else cls.MAX_CAMINOS_PAR
        filas = len(tablero_trabajo)
        cols = len(tablero_trabajo[0])
        cola = deque([[inicio]])
        generados = 0

        while cola and generados < limite:
            camino = cola.popleft()
            pos_actual = camino[-1]

            if pos_actual == fin:
                generados += 1
                yield camino
                continue

            for vecino in cls.obtener_vecinos(pos_actual, filas, cols): # aca se pone la funcion que se llama para el pseucodigo
                if vecino in camino:
                    continue
                celda = tablero_trabajo[vecino[0]][vecino[1]]
                if celda == ' ' or vecino == fin:
                    cola.append(camino + [vecino])

    @staticmethod
    def marcar_camino(tablero, camino, numero): # esta si pero en _backtrack Simón
        """Pinta el camino en el tablero salvo en los extremos."""
        for i, pos in enumerate(camino):
            if i == 0 or i == len(camino) - 1:
                continue
            tablero[pos[0]][pos[1]] = numero.lower()

    @staticmethod
    def desmarcar_camino(tablero, camino, numero): # esta si pero en _backtrack Simón
        """Borra un camino previamente pintado."""
        for i, pos in enumerate(camino):
            if i == 0 or i == len(camino) - 1:
                continue
            tablero[pos[0]][pos[1]] = ' '

    @staticmethod
    def _recolectar_extremos(pares_restantes): # esta si pero en analizar_componentes  y detectar_cuellos Simón
        """Devuelve el conjunto de extremos pendientes."""
        extremos = set()
        for _, p1, p2 in pares_restantes:
            extremos.add(p1)
            extremos.add(p2)
        return extremos

    @staticmethod
    def _es_transitable(tablero, extremos, pos): # esta si pero en _bfs_component
        """Indica si una celda puede ser parte de un camino."""
        return tablero[pos[0]][pos[1]] == ' ' or pos in extremos

    @classmethod
    # CUARTA FUNCION GRANDE QUE SI VA (4)
    def _bfs_component(cls, tablero, comp_id, inicio, comp_idx, extremos, filas, cols): # esta si 
        """Explora una componente de celdas transitables y resume libres/extremos."""
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
            for ni, nj in cls.obtener_vecinos((i, j), filas, cols): # aca se pone la funcion que se llama para el pseucodigo
                if comp_id[ni][nj] != -1:
                    continue
                if cls._es_transitable(tablero, extremos, (ni, nj)): # aca se pone la funcion que se llama para el pseucodigo
                    comp_id[ni][nj] = comp_idx
                    q.append((ni, nj))

        return {"libres": libres, "extremos": extremos_comp}

    @classmethod
    # QUINTA FUNCION GRANDE QUE SI VA (5) Simón
    def analizar_componentes(cls, tablero, pares_restantes):
        """Valida componentes: paridad de extremos y conectividad de cada par."""
        if not pares_restantes:
            return True

        filas, cols = len(tablero), len(tablero[0])
        extremos = cls._recolectar_extremos(pares_restantes) # aca se pone la funcion que se llama para el pseucodigo
        comp_id = [[-1] * cols for _ in range(filas)]
        comp_info = []
        comp_idx = 0

        for i in range(filas):
            for j in range(cols):
                if comp_id[i][j] == -1 and cls._es_transitable(tablero, extremos, (i, j)): # aca se pone la funcion que se llama para el pseucodigo
                    comp_info.append(cls._bfs_component(tablero, comp_id, (i, j), comp_idx, extremos, filas, cols)) # aca se pone la funcion que se llama para el pseucodigo
                    comp_idx += 1

        for info in comp_info:
            if info["libres"] > 0 and info["extremos"] == 0:
                return False
            if info["extremos"] % 2 == 1:
                return False

        for _, p1, p2 in pares_restantes:
            if comp_id[p1[0]][p1[1]] != comp_id[p2[0]][p2[1]]:
                return False

        return True

    @classmethod
    # SEXTA FUNCION GRANDE QUE SI VA (6)
    def detectar_cuellos(cls, tablero, pares_restantes): # esta si
        """Detecta celdas libres de grado 0/1 (no extremos) que anulan la solución."""
        if not pares_restantes:
            return False

        filas, cols = len(tablero), len(tablero[0])
        extremos = cls._recolectar_extremos(pares_restantes) #aca se pone la funcion que se llama para el pseucodigo

        for i in range(filas):
            for j in range(cols):
                if tablero[i][j] != ' ' or (i, j) in extremos:
                    continue

                vecinos_libres = 0
                for ni, nj in cls.obtener_vecinos((i, j), filas, cols): # aca se pone la funcion que se llama para el pseucodigo
                    if tablero[ni][nj] == ' ' or (ni, nj) in extremos:
                        vecinos_libres += 1
                if vecinos_libres <= 1:
                    return True
        return False

    @classmethod
    # SEPTIMA FUNCION GRANDE QUE SI VA (7)
    def existe_camino_basico(cls, tablero, inicio, fin): # esta si 
        """Comprueba conectividad simple entre dos extremos mediante BFS."""
        filas = len(tablero)
        cols = len(tablero[0])
        visitados = set([inicio])
        cola = deque([inicio])

        while cola:
            i, j = cola.popleft()
            if (i, j) == fin:
                return True
            for ni, nj in cls.obtener_vecinos((i, j), filas, cols): # aca se pone la funcion que se llama para el pseucodigo
                if (ni, nj) in visitados:
                    continue
                celda = tablero[ni][nj]
                if celda == ' ' or (ni, nj) == fin:
                    visitados.add((ni, nj))
                    cola.append((ni, nj))
        return False

    @classmethod
    def hay_camino_para_pares(cls, tablero, pares): # esta si pero en _backtrack Simón
        """Valida que cada par pendiente conserve al menos un camino alcanzable."""
        for _, pos1, pos2 in pares[:cls.MAX_CAMINOS_CHECK]:
            if not cls.existe_camino_basico(tablero, pos1, pos2): # aca se pone la funcion que se llama para el pseucodigo
                return False
        return True

    @classmethod
    def obtener_candidatos_pares(cls, tablero, pares, max_candidatos=None, max_caminos=None): # esta si pero en _backtrack
        """Selecciona pares más restringidos y sus rutas candidatas, usando tablero de memoización."""
        max_candidatos = max_candidatos if max_candidatos is not None else cls.MAX_CANDIDATOS_PARES
        max_caminos = max_caminos if max_caminos is not None else cls.MAX_CAMINOS_PAR
        clave_tablero = cls.tablero_a_clave(tablero) 
        mem_tablero = cls.MEMO_TABLERO.setdefault(clave_tablero, {})
        opciones = []

        for idx, (numero, p1, p2) in enumerate(pares):
            if numero in mem_tablero:
                caminos = mem_tablero[numero]
            else:
                generador = cls.generar_caminos_incremental(tablero, p1, p2, max_caminos=max_caminos) # aca se pone la funcion que se llama para el pseucodigo
                caminos = list(islice(generador, max_caminos))
                mem_tablero[numero] = caminos

            if not caminos:
                continue
            opciones.append((len(caminos), idx, caminos))

        opciones.sort(key=lambda x: x[0])
        return [(idx, caminos) for _, idx, caminos in opciones[:max_candidatos]]

    @classmethod
    # OCTAVA FUNCION GRANDE QUE SI VA (8) Simón
    def resolver_numberlink_backtracking(cls, tablero_original, verbose=True, max_caminos_por_par=None): # esta si
        """Backtracking guiado que prueba caminos por pares hasta completar el tablero."""
        tablero = copy.deepcopy(tablero_original)
        pares_ordenados = cls.ordenar_pares_por_heuristica(tablero_original)# aca se pone la funcion que se llama para el pseucodigo
        limite = max_caminos_por_par if max_caminos_por_par is not None else cls.MAX_CAMINOS_PAR

        if verbose:
            print("\n=== ESTRATEGIA: BACKTRACKING CON HEURÍSTICA DE BORDES ===")
            print(f"Total de pares a conectar: {len(pares_ordenados)}\n")

        intentos = [0]

        if cls._backtrack(tablero, pares_ordenados, pares_ordenados, intentos, limite, verbose): # aca se pone la funcion que se llama para el pseucodigo
            if verbose:
                print(f"\n✓ Solución encontrada en {intentos[0]} intentos")
            return tablero, True

        if verbose:
            print(f"\n✗ No se encontró solución después de {intentos[0]} intentos")
        return tablero, False

    @classmethod
    def _backtrack(cls, tablero, pares_restantes, pares_ordenados, intentos, limite, verbose): # esta si pero en resolver_numberlink_backtracking Simón
        """Recursión principal que intenta conectar pares con podas agresivas."""
        intentos[0] += 1

        if not pares_restantes:
            return all(' ' not in fila for fila in tablero)

        candidatos = cls.obtener_candidatos_pares(tablero, pares_restantes, max_candidatos=cls.MAX_CANDIDATOS_PARES, max_caminos=limite) # aca se pone la funcion que se llama para el pseucodigo
        if not candidatos:
            return False

        for idx_sel, caminos in candidatos:
            if verbose and len(pares_restantes) == len(pares_ordenados):
                print(f"Conectando '{pares_restantes[idx_sel][0]}': {len(caminos)} caminos candidatos")

            numero, _, _ = pares_restantes[idx_sel]
            restantes = pares_restantes[:idx_sel] + pares_restantes[idx_sel + 1:]

            for camino in caminos[:limite]:
                cls.marcar_camino(tablero, camino, numero) # aca se pone la funcion que se llama para el pseucodigo
                if (not cls.detectar_cuellos(tablero, restantes) and # aca se pone la funcion que se llama para el pseucodigo
                        cls.analizar_componentes(tablero, restantes) and# aca se pone la funcion que se llama para el pseucodigo
                        cls.hay_camino_para_pares(tablero, restantes)):# aca se pone la funcion que se llama para el pseucodigo
                    if cls._backtrack(tablero, restantes, pares_ordenados, intentos, limite, verbose):# aca se pone la funcion que se llama para el pseucodigo
                        return True
                cls.desmarcar_camino(tablero, camino, numero)# aca se pone la funcion que se llama para el pseucodigo
        return False

    @staticmethod
    def imprimir_tablero(tablero):
        """Imprime el tablero en formato legible."""
        for fila in tablero:
            print(''.join(fila))


if __name__ == "__main__":
    from leer_tablero import NumberLinkBoardIO
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python solucionador_backtracking.py <ruta_del_archivo>")
        sys.exit(1)
    
    ruta = sys.argv[1]
    
    try:
        tablero = NumberLinkBoardIO.leer_tablero(ruta)
        
        print("=== TABLERO ORIGINAL ===")
        NumberLinkBoardIO.imprimir_tablero(tablero)
        
        pares = NumberLinkHeuristicSolver.encontrar_pares(tablero)
        print(f"\nPares a conectar: {len(pares)}")
        for num, posiciones in sorted(pares.items()):
            print(f"  '{num}': {posiciones[0]} ↔ {posiciones[1]}")

        filas = len(tablero)
        cols = len(tablero[0]) if filas else 0
        ruta_salida = os.path.join("tablerosSalida", f"salida{filas}x{cols}.txt")

        inicio = time.perf_counter()
        solucion, completa = NumberLinkHeuristicSolver.resolver_numberlink_backtracking(tablero, verbose=True)
        duracion = time.perf_counter() - inicio
        
        if completa:
            print("\n=== TABLERO RESUELTO ===")
            NumberLinkHeuristicSolver.imprimir_tablero(solucion)
        else:
            print("\n=== SOLUCIÓN PARCIAL ===")
            NumberLinkHeuristicSolver.imprimir_tablero(solucion)
            print("\nNo se pudo encontrar una solución completa.")

        NumberLinkBoardIO.guardar_resultado(solucion, ruta_salida, "Backtracking Heurístico", duracion, completa)
        print(f"\nTiempo de resolución: {duracion:.4f} s")
        print(f"Resultado guardado en: {ruta_salida}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
