# dfa_cli_compacto.py — Versión optimizada para la App de Delivery
import sys
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import FancyArrowPatch

# === Definición del DFA (7 estados, alfabeto a/b/c) ===
states = {"q0", "q1", "q2", "q3", "q4", "q5", "q6"}
alphabet = {"a", "b", "c"}

delta = {
    # q0: Búsqueda
    ("q0", "a"): "q1",  # Avanza a Carrito
    ("q0", "b"): "q0",  # Bucle: sigue buscando

    # q1: Carrito
    ("q1", "a"): "q2",  # Avanza a Verificación de Dirección
    ("q1", "b"): "q1",  # Bucle: agrega más productos

    # q2: Verificación de Dirección
    ("q2", "a"): "q3",  # Avanza a Proceso de Pago
    ("q2", "c"): "q1",  # Regresa a Carrito (corregir)

    # q3: Proceso de Pago
    ("q3", "a"): "q4",  # Avanza a Preparación en Restaurante
    ("q3", "c"): "q2",  # Regresa a Verificación (tarjeta rechazada)

    # q4: Preparación en Restaurante
    ("q4", "a"): "q5",  # Avanza a Envío en Camino
    ("q4", "b"): "q4",  # Bucle: la comida se está cocinando

    # q5: Envío en Camino
    ("q5", "a"): "q6",  # Avanza a Entregado
    ("q5", "b"): "q5",  # Bucle: el repartidor va viajando
}

q0, F = "q0", {"q6"}  # Estado inicial y final (q6 = Entregado)


# === Simulación de la Cadena ===
def run(s):
    q, steps = q0, [q0]
    for i, ch in enumerate(s):
        if (q, ch) not in delta:
            raise ValueError(f"Transición inválida (Ø) desde {q} con '{ch}' en pos {i}")
        q = delta[(q, ch)]
        steps.append(q)
    return steps, q in F


# === Construcción del Grafo Estructurado ===
G = nx.MultiDiGraph()
G.add_nodes_from(sorted(list(states)))  # Ordenado para consistencia visual
for (q, a), p in delta.items():
    G.add_edge(q, p, key=a, label=a)

# Usamos shell_layout para distribuir los 7 estados en forma circular limpia
pos = nx.shell_layout(G)


# === Función de Cálculo de Posición de Etiquetas ===
def _mid(p1, p2, o=0.12):
    (x1, y1), (x2, y2) = p1, p2
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    nx_, ny_ = -dy, dx
    L = (nx_ ** 2 + ny_ ** 2) ** 0.5 or 1
    return mx + o * nx_ / L, my + o * ny_ / L


# === Renderizado Dinámico por Pasos ===
def draw_step(current, idx, sym=None):
    plt.clf()
    nodes = list(G.nodes())

    # 1. Dibujar todos los nodos (El nodo actual resalta en tamaño)
    nx.draw_networkx_nodes(
        G, pos,
        nodelist=nodes,
        node_size=[1000 if n == current else 650 for n in nodes],
        node_color=["#FFCDD2" if n == current else "#BBDEFB" for n in nodes],
        edgecolors="black"
    )

    # 2. Representación Teórica Formal: Doble círculo para los estados finales (F)
    nx.draw_networkx_nodes(
        G, pos,
        nodelist=list(F),
        node_size=[1150 if n == current else 800 for n in F],
        node_color="none",
        edgecolors="black",
        linewidths=2
    )

    # Textos de los identificadores de estados
    nx.draw_networkx_labels(G, pos, font_weight="bold", font_size=10)

    # 3. Dibujar transiciones (Aristas)
    seen = {}
    for u, v, k, d in G.edges(keys=True, data=True):
        # Caso especial: Bucles sobre sí mismos (Self-loops)
        if u == v:
            x, y = pos[u]
            plt.gca().add_patch(
                FancyArrowPatch(
                    (x, y), (x + 1e-4, y + 1e-4),
                    connectionstyle="arc3,rad=0.5",
                    arrowstyle='-|>',
                    mutation_scale=15,
                    color="gray"
                )
            )
            plt.text(x, y + 0.16, d['label'], fontsize=11, ha='center', color="darkred", weight="bold")
            continue

        # Caso: Flechas curvas entre estados distintos
        i = seen.get((u, v), 0)
        seen[(u, v)] = i + 1
        rad = 0.25 if i % 2 == 0 else -0.25

        nx.draw_networkx_edges(
            G, pos,
            edgelist=[(u, v)],
            connectionstyle=f"arc3,rad={rad}",
            arrows=True,
            arrowstyle='-|>',
            arrowsize=20
        )

        # Etiqueta del símbolo de transición en el punto medio (con desplazamiento)
        lx, ly = _mid(pos[u], pos[v], o=0.12 * (1 if rad > 0 else -1))
        plt.text(lx, ly, d['label'], fontsize=11, ha='center', color="darkred", weight="bold")

    titulo = f"Paso {idx}: Estado actual = {current}"
    if sym is not None:
        titulo += f"  (símbolo leído: '{sym}')"
    plt.title(titulo)
    plt.axis("off")


# === Punto de entrada CLI ===
def main():
    if len(sys.argv) > 1:
        cadena = sys.argv[1]
    else:
        cadena = input("Ingresa la cadena (alfabeto a/b/c): ").strip()

    for ch in cadena:
        if ch not in alphabet:
            print(f"Error: el símbolo '{ch}' no pertenece al alfabeto {alphabet}")
            sys.exit(1)

    try:
        steps, aceptada = run(cadena)
    except ValueError as e:
        print(f"Error de simulación: {e}")
        sys.exit(1)

    print("Secuencia de estados:", " -> ".join(steps))
    print("Cadena ACEPTADA" if aceptada else "Cadena RECHAZADA")

    plt.figure(figsize=(8, 8))
    draw_step(steps[0], 0)
    plt.pause(1.0)
    for idx, (st, sym) in enumerate(zip(steps[1:], cadena), start=1):
        draw_step(st, idx, sym)
        plt.pause(1.0)

    plt.show()


if __name__ == "__main__":
    main()