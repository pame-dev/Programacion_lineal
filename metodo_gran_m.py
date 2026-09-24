# metodo de la gran M

try:
    from .aritmetica import Frac, fmt, to_frac
    from .tablas import imprimir_tabla
except ImportError:
    from aritmetica import Frac, fmt, to_frac
    from tablas import imprimir_tabla


class MExpr:
    """Representa m*M + c."""

    def __init__(self, m=0, c=0):
        # Se guardan por separado el coeficiente de M y la parte constante.
        # Así se puede comparar M como una cantidad muy grande sin usar floats.
        self.m = to_frac(m)
        self.c = to_frac(c)

    def __add__(self, o):
        # La suma se hace componente a componente: (m1*M+c1)+(m2*M+c2).
        o = o if isinstance(o, MExpr) else MExpr(0, o)
        return MExpr(self.m + o.m, self.c + o.c)

    __radd__ = __add__

    def __sub__(self, o):
        # La resta también conserva por separado los términos con M y constantes.
        o = o if isinstance(o, MExpr) else MExpr(0, o)
        return MExpr(self.m - o.m, self.c - o.c)

    def __mul__(self, esc):
        # Al multiplicar por un número, se multiplican ambos componentes.
        esc = to_frac(esc)
        return MExpr(self.m * esc, self.c * esc)

    __rmul__ = __mul__

    def __truediv__(self, esc):
        # La división por un escalar se aplica a M y a la constante.
        esc = to_frac(esc)
        return MExpr(self.m / esc, self.c / esc)

    def __neg__(self):
        return MExpr(-self.m, -self.c)

    def __gt__(self, o):
        # Se compara primero el coeficiente de M y después la constante.
        o = o if isinstance(o, MExpr) else MExpr(0, o)
        return (self.m, self.c) > (o.m, o.c)

    def __lt__(self, o):
        o = o if isinstance(o, MExpr) else MExpr(0, o)
        return (self.m, self.c) < (o.m, o.c)

    def __eq__(self, o):
        o = o if isinstance(o, MExpr) else MExpr(0, o)
        return self.m == o.m and self.c == o.c

    def __repr__(self):
        if self.m == Frac(0):
            return fmt(self.c)
        parte_m = f"{fmt(self.m)}M" if self.m != Frac(1) else "M"
        if self.c == Frac(0):
            return parte_m
        signo = "+" if self.c > Frac(0) else "-"
        return f"{parte_m}{signo}{fmt(abs(self.c))}"


def metodo_gran_m(c, restricciones, tipo):
    # Gran M sirve cuando hay restricciones >= o =, o cuando se necesita forzar
    # variables artificiales para construir una solución básica inicial.
    n_vars = len(c)
    m = len(restricciones)
    es_min = (tipo == 'min')
    # Gran M trabaja internamente como maximización. Por eso una minimización
    # cambia de signo y al final se vuelve a cambiar el resultado.
    c_obj = [(-v if es_min else v) for v in c]

    # Primero se registran las variables originales y sus costos en Z.
    nombres = [f"x{i+1}" for i in range(n_vars)]
    costos = [MExpr(0, c_obj[i]) for i in range(n_vars)]
    columnas_extra = []

    for i, (*coefs, signo, b) in enumerate(restricciones):
        # <= necesita una holgura; >= necesita exceso y artificial;
        # = necesita una variable artificial para formar una base inicial.
        if signo == '<=':
            columnas_extra.append((f"s{i+1}", 's', i))
        elif signo == '>=':
            columnas_extra.append((f"e{i+1}", 'e', i))
            columnas_extra.append((f"a{i+1}", 'a', i))
        elif signo == '=':
            columnas_extra.append((f"a{i+1}", 'a', i))
        else:
            raise ValueError(f"Signo no reconocido: {signo}")

    for (nom, tp, fila) in columnas_extra:
        # Las variables artificiales reciben -M para penalizarlas en la función
        # objetivo y forzarlas a salir de la solución final.
        nombres.append(nom)
        costos.append(MExpr(-1, 0) if tp == 'a' else MExpr(0, 0))

    n_total = len(nombres)
    # Se reserva la matriz de coeficientes de las restricciones y la columna b.
    tabla = [[Frac(0)] * n_total for _ in range(m)]
    b_col = [Frac(0)] * m
    for i, (*coefs, signo, b) in enumerate(restricciones):
        # Las primeras columnas corresponden a las variables originales.
        for k in range(n_vars):
            tabla[i][k] = coefs[k]
        b_col[i] = b

    base = [None] * m
    for idx, (nom, tp, fila) in enumerate(columnas_extra):
        j = n_vars + idx
        if tp == 's':
            # Una holgura forma la variable básica de una restricción <=.
            tabla[fila][j] = Frac(1)
            base[fila] = j
        elif tp == 'e':
            # Una variable de exceso se resta en una restricción >=.
            tabla[fila][j] = Frac(-1)
        elif tp == 'a':
            # La artificial permite tener un 1 en la columna básica inicial.
            tabla[fila][j] = Frac(1)
            base[fila] = j

    for i in range(m):
        # Se cambia el signo de una fila completa si su lado derecho es negativo.
        if b_col[i] < Frac(0):
            b_col[i] = -b_col[i]
            tabla[i] = [-v for v in tabla[i]]

    print("\n===== MÉTODO DE LA GRAN M =====")
    print(f"Z = " + " + ".join(f"{fmt(c[i])}·x{i+1}" for i in range(n_vars)) + f"   ({tipo})")

    iteracion = 0
    MAX_ITER = 200
    while True:
        # Cada vuelta del ciclo representa una iteración del método simplex.
        if iteracion > MAX_ITER:
            print("\n>>> El método no convergió tras muchas iteraciones (posible ciclado).")
            return None

        cb = [costos[base[i]] for i in range(m)]
        # Zj es la combinación de cada columna usando los costos de la base.
        z_j = [sum((cb[i] * tabla[i][j] for i in range(m)), MExpr(0, 0)) for j in range(n_total)]
        # Cj-Zj indica cuánto puede mejorar el objetivo si entra una columna.
        cj_zj = [costos[j] - z_j[j] for j in range(n_total)]
        # Este es el valor actual de Z usando los términos independientes.
        z_actual = sum((cb[i] * b_col[i] for i in range(m)), MExpr(0, 0))

        encabezados = ["Base"] + nombres + ["b"]
        filas_tabla = [[nombres[base[i]]] + [fmt(v) for v in tabla[i]] + [fmt(b_col[i])] for i in range(m)]
        filas_tabla.append(["Cj-Zj"] + [fmt(v) for v in cj_zj] + [fmt(z_actual)])
        imprimir_tabla(encabezados, filas_tabla, titulo=f"Iteración {iteracion}")

        col_entra = None
        mejor_val = MExpr(0, 0)
        for j in range(n_total):
            # Se elige la columna con el Cj-Zj más positivo.
            if cj_zj[j] > mejor_val:
                mejor_val = cj_zj[j]
                col_entra = j
        if col_entra is None:
            # Si no hay valores positivos, la tabla ya es óptima.
            break

        fila_sale = None
        mejor_razon = None
        for i in range(m):
            # La prueba de razón mínima indica qué fila debe salir de la base.
            if tabla[i][col_entra] > Frac(0):
                razon = b_col[i] / tabla[i][col_entra]
                if mejor_razon is None or razon < mejor_razon:
                    mejor_razon = razon
                    fila_sale = i

        if fila_sale is None:
            print(f"\nLa columna de '{nombres[col_entra]}' no tiene elementos positivos.")
            print(">>> El problema es NO ACOTADO. No tiene solución óptima finita.")
            return None

        print(f"Entra: {nombres[col_entra]}   |   Sale: {nombres[base[fila_sale]]}   |   "
              f"Pivote: {fmt(tabla[fila_sale][col_entra])}")

        piv = tabla[fila_sale][col_entra]
        # Se divide la fila pivote para convertir el pivote en 1.
        tabla[fila_sale] = [v / piv for v in tabla[fila_sale]]
        b_col[fila_sale] = b_col[fila_sale] / piv
        for i in range(m):
            if i != fila_sale and tabla[i][col_entra] != Frac(0):
                # Se hacen ceros en el resto de la columna pivote.
                factor = tabla[i][col_entra]
                tabla[i] = [tabla[i][j] - factor * tabla[fila_sale][j] for j in range(n_total)]
                b_col[i] = b_col[i] - factor * b_col[fila_sale]

        base[fila_sale] = col_entra
        # La columna entrante reemplaza a la variable que salió de la base.
        iteracion += 1

    for i in range(m):
        # Si una artificial sigue positiva, las restricciones no pueden
        # cumplirse simultáneamente.
        if nombres[base[i]].startswith('a') and b_col[i] != Frac(0):
            print("\n>>> El problema NO TIENE SOLUCIÓN FACTIBLE.")
            print("    (una variable artificial quedó positiva en la base óptima)")
            return None

    solucion = {nombres[j]: Frac(0) for j in range(n_total)}
    # Las variables básicas toman el valor de b; las no básicas valen cero.
    for i in range(m):
        solucion[nombres[base[i]]] = b_col[i]

    z_final_expr = sum((costos[base[i]] * b_col[i] for i in range(m)), MExpr(0, 0))
    # Solo se reporta la parte constante de Z; la parte con M debe desaparecer.
    z_num = z_final_expr.c
    if es_min:
        z_num = -z_num

    print("\n>>> SOLUCIÓN ÓPTIMA ENCONTRADA:")
    for k in range(n_vars):
        print(f"    x{k+1} = {fmt(solucion[f'x{k+1}'])}")
    print(f"    Z = {fmt(z_num)}")
    return {"variables": solucion, "Z": z_num}
