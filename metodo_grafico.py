# se resuelve con metodo gráfico 

import math

try:
    from .aritmetica import Frac, fmt
except ImportError:
    from aritmetica import Frac, fmt

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


def _to_float(value):
    if hasattr(value, 'num') and hasattr(value, 'den'):
        return float(value.num / value.den)
    return float(value)


def _graficar_region(factibles, restricciones, mejor, tipo):
    if plt is None:
        print("\nNo se pudo mostrar la gráfica porque matplotlib no está instalado.")
        return

    if not factibles:
        return

    puntos = [(_to_float(x), _to_float(y)) for x, y, _ in factibles]
    x0, y0 = sum(p[0] for p in puntos) / len(puntos), sum(p[1] for p in puntos) / len(puntos)

    def angulo(p):
        dx = p[0] - x0
        dy = p[1] - y0
        return math.atan2(dy, dx)

    hull = sorted(set(puntos), key=angulo)
    if len(hull) < 3:
        hull = puntos

    x_max = max(max(p[0] for p in puntos), 1)
    y_max = max(max(p[1] for p in puntos), 1)
    for a1, a2, signo, b in restricciones:
        a1f = _to_float(a1)
        a2f = _to_float(a2)
        bf = _to_float(b)
        if a2f != 0:
            x_intercept = bf / a1f if a1f != 0 else 0
            if x_intercept > 0:
                x_max = max(x_max, x_intercept)
        if a1f != 0:
            y_intercept = bf / a2f if a2f != 0 else 0
            if y_intercept > 0:
                y_max = max(y_max, y_intercept)

    x_max *= 1.5
    y_max *= 1.5

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.axhline(0, color='black', linewidth=0.8)
    ax.axvline(0, color='black', linewidth=0.8)
    ax.set_xlim(0, x_max)
    ax.set_ylim(0, y_max)
    ax.set_xlabel('x1')
    ax.set_ylabel('x2')
    ax.set_title('Región factible y solución óptima')
    ax.grid(True, alpha=0.25)

    for a1, a2, signo, b in restricciones:
        a1f = _to_float(a1)
        a2f = _to_float(a2)
        bf = _to_float(b)
        x_vals = [0, x_max]
        y_vals = [((bf - a1f * x) / a2f) if a2f != 0 else 0 for x in x_vals]
        if a2f == 0:
            ax.axvline(x=bf / a1f if a1f != 0 else 0, linestyle='--', color='gray', linewidth=1.5, alpha=0.8)
        else:
            ax.plot(x_vals, y_vals, linestyle='--', color='gray', linewidth=1.5, alpha=0.8)
        label = f'{fmt(a1)}x1 + {fmt(a2)}x2 {signo} {fmt(b)}'
        if len(ax.lines) <= len(restricciones):
            ax.text(x_max * 0.6, max(y_max * 0.9 - (len(ax.lines) * 0.1 * y_max), 0.2), label, fontsize=8, color='dimgray')

    xs, ys = zip(*hull)
    ax.fill(xs, ys, color='skyblue', alpha=0.5)
    ax.scatter([p[0] for p in puntos], [p[1] for p in puntos], color='navy', s=35, label='Vértices factibles', zorder=3)

    mejor_x = _to_float(mejor[0])
    mejor_y = _to_float(mejor[1])
    ax.scatter([mejor_x], [mejor_y], color='red', s=120, zorder=4, label='Óptimo')
    ax.annotate(f'Óptimo\n({fmt(mejor[0])}, {fmt(mejor[1])})', (mejor_x, mejor_y), xytext=(8, 8), textcoords='offset points', color='red', fontsize=9)

    ax.legend(loc='best')
    plt.tight_layout()
    plt.savefig('grafico_programacion_lineal.png', dpi=220, bbox_inches='tight')
    print("\nGráfica guardada en: grafico_programacion_lineal.png")
    plt.show()


def metodo_grafico(c, restricciones, tipo):
    # El método gráfico solo sirve para 2 variables. La idea es sustituir cada
    # restricción por una línea recta y luego buscar el polígono de soluciones factibles.
    assert len(c) == 2, "El método gráfico solo aplica a problemas de 2 variables."
    c1, c2 = c[0], c[1]

    # Cada restricción se representa como a1*x1 + a2*x2 = b.
    rectas = [(r[0], r[1], r[3]) for r in restricciones]
    # Se agregan los ejes x1=0 y x2=0 para analizar la región no negativa.
    rectas.append((Frac(1), Frac(0), Frac(0)))
    rectas.append((Frac(0), Frac(1), Frac(0)))

    print("\n===== MÉTODO GRÁFICO =====")
    print(f"Z = {fmt(c1)}·x1 + {fmt(c2)}·x2   ({tipo})")
    print("Nota: este método asume que la región factible es acotada.")

    # Se hallan intersecciones entre pares de rectas. Cada una representa un posible
    # vértice de la región factible.
    vertices = []
    n = len(rectas)
    for i in range(n):
        for j in range(i + 1, n):
            a1, a2, b1 = rectas[i]
            a3, a4, b2 = rectas[j]
            det = a1 * a4 - a2 * a3
            if det == Frac(0):
                continue
            x1 = (b1 * a4 - b2 * a2) / det
            x2 = (a1 * b2 - a3 * b1) / det
            vertices.append((x1, x2))

    print("\nIntersecciones encontradas:")
    # Se filtran solo los puntos que cumplen todas las restricciones y no son negativos.
    factibles = []
    vistos = set()
    for (x1, x2) in vertices:
        clave = (x1.num, x1.den, x2.num, x2.den)
        if clave in vistos:
            continue
        vistos.add(clave)

        es_factible = (x1 >= Frac(0)) and (x2 >= Frac(0))
        if es_factible:
            for (a1, a2, signo, b) in restricciones:
                val = a1 * x1 + a2 * x2
                if signo == '<=' and not (val <= b):
                    es_factible = False
                elif signo == '>=' and not (val >= b):
                    es_factible = False
                elif signo == '=' and not (val == b):
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

    # En un problema de maximización se escoge el punto con mayor valor de Z;
    # en minimización, el menor valor.
    mejor = max(factibles, key=lambda t: t[2]) if tipo == 'max' else min(factibles, key=lambda t: t[2])
    x1o, x2o, zo = mejor
    print(f"\n>>> Solución óptima: x1 = {fmt(x1o)}, x2 = {fmt(x2o)}, Z = {fmt(zo)}")
    _graficar_region(factibles, restricciones, mejor, tipo)
    return {"x1": x1o, "x2": x2o, "Z": zo}
