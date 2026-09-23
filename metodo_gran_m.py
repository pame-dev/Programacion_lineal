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
        self.m = to_frac(m)
        self.c = to_frac(c)

    def __add__(self, o):
        o = o if isinstance(o, MExpr) else MExpr(0, o)
        return MExpr(self.m + o.m, self.c + o.c)

    __radd__ = __add__

    def __sub__(self, o):
        o = o if isinstance(o, MExpr) else MExpr(0, o)
        return MExpr(self.m - o.m, self.c - o.c)

    def __mul__(self, esc):
        esc = to_frac(esc)
        return MExpr(self.m * esc, self.c * esc)

    __rmul__ = __mul__

    def __truediv__(self, esc):
        esc = to_frac(esc)
        return MExpr(self.m / esc, self.c / esc)

    def __neg__(self):
        return MExpr(-self.m, -self.c)

    def __gt__(self, o):
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
    c_obj = [(-v if es_min else v) for v in c]

    nombres = [f"x{i+1}" for i in range(n_vars)]
    costos = [MExpr(0, c_obj[i]) for i in range(n_vars)]
    columnas_extra = []

    for i, (*coefs, signo, b) in enumerate(restricciones):
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
        nombres.append(nom)
        costos.append(MExpr(-1, 0) if tp == 'a' else MExpr(0, 0))

    n_total = len(nombres)
    tabla = [[Frac(0)] * n_total for _ in range(m)]
    b_col = [Frac(0)] * m
    for i, (*coefs, signo, b) in enumerate(restricciones):
        for k in range(n_vars):
            tabla[i][k] = coefs[k]
        b_col[i] = b

    base = [None] * m
    for idx, (nom, tp, fila) in enumerate(columnas_extra):
        j = n_vars + idx
        if tp == 's':
            tabla[fila][j] = Frac(1)
            base[fila] = j
        elif tp == 'e':
            tabla[fila][j] = Frac(-1)
        elif tp == 'a':
            tabla[fila][j] = Frac(1)
            base[fila] = j

    for i in range(m):
        if b_col[i] < Frac(0):
            b_col[i] = -b_col[i]
            tabla[i] = [-v for v in tabla[i]]

    print("\n===== MÉTODO DE LA GRAN M =====")
    print(f"Z = " + " + ".join(f"{fmt(c[i])}·x{i+1}" for i in range(n_vars)) + f"   ({tipo})")

    iteracion = 0
    MAX_ITER = 200
    while True:
        if iteracion > MAX_ITER:
            print("\n>>> El método no convergió tras muchas iteraciones (posible ciclado).")
            return None

        cb = [costos[base[i]] for i in range(m)]
        z_j = [sum((cb[i] * tabla[i][j] for i in range(m)), MExpr(0, 0)) for j in range(n_total)]
        cj_zj = [costos[j] - z_j[j] for j in range(n_total)]
        z_actual = sum((cb[i] * b_col[i] for i in range(m)), MExpr(0, 0))

        encabezados = ["Base"] + nombres + ["b"]
        filas_tabla = [[nombres[base[i]]] + [fmt(v) for v in tabla[i]] + [fmt(b_col[i])] for i in range(m)]
        filas_tabla.append(["Cj-Zj"] + [fmt(v) for v in cj_zj] + [fmt(z_actual)])
        imprimir_tabla(encabezados, filas_tabla, titulo=f"Iteración {iteracion}")

        col_entra = None
        mejor_val = MExpr(0, 0)
        for j in range(n_total):
            if cj_zj[j] > mejor_val:
                mejor_val = cj_zj[j]
                col_entra = j
        if col_entra is None:
            break

        fila_sale = None
        mejor_razon = None
        for i in range(m):
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
        tabla[fila_sale] = [v / piv for v in tabla[fila_sale]]
        b_col[fila_sale] = b_col[fila_sale] / piv
        for i in range(m):
            if i != fila_sale and tabla[i][col_entra] != Frac(0):
                factor = tabla[i][col_entra]
                tabla[i] = [tabla[i][j] - factor * tabla[fila_sale][j] for j in range(n_total)]
                b_col[i] = b_col[i] - factor * b_col[fila_sale]

        base[fila_sale] = col_entra
        iteracion += 1

    for i in range(m):
        if nombres[base[i]].startswith('a') and b_col[i] != Frac(0):
            print("\n>>> El problema NO TIENE SOLUCIÓN FACTIBLE.")
            print("    (una variable artificial quedó positiva en la base óptima)")
            return None

    solucion = {nombres[j]: Frac(0) for j in range(n_total)}
    for i in range(m):
        solucion[nombres[base[i]]] = b_col[i]

    z_final_expr = sum((costos[base[i]] * b_col[i] for i in range(m)), MExpr(0, 0))
    z_num = z_final_expr.c
    if es_min:
        z_num = -z_num

    print("\n>>> SOLUCIÓN ÓPTIMA ENCONTRADA:")
    for k in range(n_vars):
        print(f"    x{k+1} = {fmt(solucion[f'x{k+1}'])}")
    print(f"    Z = {fmt(z_num)}")
    return {"variables": solucion, "Z": z_num}
