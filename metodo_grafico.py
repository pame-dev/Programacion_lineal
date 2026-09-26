# Método gráfico (solo para problemas de 2 variables).
# Versión simplificada: se usan números float directamente, sin clases
# de fracciones ni de conversión.

import math

try:
    from .numeros import fmt, EPS
except ImportError:
    from numeros import fmt, EPS

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


def _graficar(factibles, restricciones, mejor):
    # Solo dibuja lo que ya se calculó en metodo_grafico(). No hace cálculos.
    if plt is None:
        print("\nNo se pudo mostrar la gráfica porque matplotlib no está instalado.")
        return
    if not factibles:
        return

    puntos = [(x, y) for x, y, _ in factibles]

    # Límite de los ejes: un poco más grande que el punto más lejano.
    x_max = max(p[0] for p in puntos + [(1, 1)]) * 1.5
    y_max = max(p[1] for p in puntos + [(1, 1)]) * 1.5

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.set_xlim(0, x_max)
    ax.set_ylim(0, y_max)
    ax.set_xlabel('x1')
    ax.set_ylabel('x2')
    ax.set_title('Región factible y solución óptima')
    ax.grid(True, alpha=0.25)

    # Se dibuja cada restricción como una recta: a1*x1 + a2*x2 = b.
    for (a1, a2, signo, b) in restricciones:
        if a2 != 0:
            x_vals = [0, x_max]
            y_vals = [(b - a1 * x) / a2 for x in x_vals]
            ax.plot(x_vals, y_vals, linestyle='--', color='gray')
        else:
            ax.axvline(x=b / a1, linestyle='--', color='gray')

    # Para pintar el área factible, se ordenan los vértices alrededor de
    # su punto central (así el relleno queda en el orden correcto).
    if len(puntos) >= 3:
        cx = sum(p[0] for p in puntos) / len(puntos)
        cy = sum(p[1] for p in puntos) / len(puntos)
        puntos_ordenados = sorted(puntos, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
        xs, ys = zip(*puntos_ordenados)
        ax.fill(xs, ys, color='skyblue', alpha=0.5)

    ax.scatter([p[0] for p in puntos], [p[1] for p in puntos], color='navy', zorder=3, label='Vértices factibles')
    ax.scatter([mejor[0]], [mejor[1]], color='red', s=120, zorder=4, label='Óptimo')
    ax.annotate(f'({fmt(mejor[0])}, {fmt(mejor[1])})', (mejor[0], mejor[1]),
                xytext=(8, 8), textcoords='offset points', color='red')

    ax.legend(loc='best')
    plt.tight_layout()
    plt.savefig('grafico_programacion_lineal.png', dpi=200, bbox_inches='tight')
    print("\nGráfica guardada en: grafico_programacion_lineal.png")
    plt.show()


def metodo_grafico(c, restricciones, tipo):
    assert len(c) == 2, "El método gráfico solo aplica a problemas de 2 variables."
    c1, c2 = c[0], c[1]

    # Cada restricción se ve como a1*x1 + a2*x2 = b. Se agregan también
    # los dos ejes (x1 = 0 y x2 = 0) para poder cortar con ellos.
    rectas = [(r[0], r[1], r[3]) for r in restricciones]
    rectas.append((1, 0, 0))
    rectas.append((0, 1, 0))

    print("\n===== MÉTODO GRÁFICO =====")
    print(f"Z = {fmt(c1)}·x1 + {fmt(c2)}·x2   ({tipo})")
    print("Nota: este método asume que la región factible es acotada.")

    # Se calcula la intersección de cada par de rectas (sistema 2x2 con
    # la regla de Cramer). Cada intersección es un posible vértice.
    vertices = []
    n = len(rectas)
    for i in range(n):
        for j in range(i + 1, n):
            a1, a2, b1 = rectas[i]
            a3, a4, b2 = rectas[j]
            det = a1 * a4 - a2 * a3
            if abs(det) < EPS:
                # Rectas paralelas: no se cortan en un solo punto.
                continue
            x1 = (b1 * a4 - b2 * a2) / det
            x2 = (a1 * b2 - a3 * b1) / det
            vertices.append((x1, x2))

    print("\nIntersecciones encontradas:")
    factibles = []
    vistos = set()
    for (x1, x2) in vertices:
        # Se redondea la clave para no repetir el mismo punto por errores
        # mínimos de precisión.
        clave = (round(x1, 6), round(x2, 6))
        if clave in vistos:
            continue
        vistos.add(clave)

        # Un punto es factible si está en el primer cuadrante y cumple
        # todas las restricciones del problema.
        es_factible = x1 >= -EPS and x2 >= -EPS
        if es_factible:
            for (a1, a2, signo, b) in restricciones:
                val = a1 * x1 + a2 * x2
                if signo == '<=' and val > b + EPS:
                    es_factible = False
                elif signo == '>=' and val < b - EPS:
                    es_factible = False
                elif signo == '=' and abs(val - b) > EPS:
                    es_factible = False
                if not es_factible:
                    break

        print(f"  ({fmt(x1)}, {fmt(x2)})  ->  {'FACTIBLE' if es_factible else 'no factible'}")
        if es_factible:
            factibles.append((x1, x2, c1 * x1 + c2 * x2))

    if not factibles:
        print("\n>>> El problema NO TIENE SOLUCIÓN FACTIBLE (región vacía).")
        return None

    print("\nEvaluación de Z en cada vértice factible:")
    for (x1, x2, z) in factibles:
        print(f"  Z({fmt(x1)}, {fmt(x2)}) = {fmt(z)}")

    # Se elige el vértice con mayor Z (max) o menor Z (min).
    mejor = max(factibles, key=lambda t: t[2]) if tipo == 'max' else min(factibles, key=lambda t: t[2])
    x1o, x2o, zo = mejor
    print(f"\n>>> Solución óptima: x1 = {fmt(x1o)}, x2 = {fmt(x2o)}, Z = {fmt(zo)}")
    _graficar(factibles, restricciones, mejor)
    return {"x1": x1o, "x2": x2o, "Z": zo}