# Metodo simplex (convención Zj - Cj)
# Se sigue iterando mientras exista algún valor NEGATIVO en la fila Zj-Cj.
# Cuando todos son >= 0, la tabla es óptima.

try:
    from .numeros import fmt, EPS
    from .tablas import imprimir_tabla
except ImportError:
    from numeros import fmt, EPS
    from tablas import imprimir_tabla


# Valida restricciones
def validar(restricciones):
    for (*_, signo, b) in restricciones:
        if signo != '<=' or b < -EPS:
            raise ValueError("El simplex estándar requiere restricciones '<=' con b >= 0.")


# Tabla inicial
def tabla_inicial(restricciones, m):
    tabla = []
    for i, (*coefs, signo, b) in enumerate(restricciones):  # cada restriccion se vuelve de igualdad agregando una variable de holgura
        holguras = [1.0 if k == i else 0.0 for k in range(m)]
        tabla.append(list(coefs) + holguras + [b])
    return tabla


# Calcula Zj - Cj y Z
def calcular_zj_cj(tabla, base, c_ext):
    cb = [c_ext[k] for k in base]
    filas = range(len(tabla))
    zj_cj = [sum(cb[i] * tabla[i][j] for i in filas) - c_ext[j] for j in range(len(c_ext))]
    z = sum(cb[i] * tabla[i][-1] for i in filas)
    return zj_cj, z  # ultima fila de la tabla (Zj-Cj) y valor de Z actual


# Fila que sale (razón mínima)
def fila_que_sale(tabla, col):
    candidatas = [i for i in range(len(tabla)) if tabla[i][col] > EPS]  # Filas con elementos positivos en la columna
    if not candidatas:
        print(">>> No hay filas con elementos positivos en la columna.")
        return None  # el problema es no acotado
    return min(candidatas, key=lambda i: tabla[i][-1] / tabla[i][col])


# Pivoteo Gauss-Jordan
def pivotear(tabla, fila, col):
    piv = tabla[fila][col]
    tabla[fila] = [v / piv for v in tabla[fila]]  # divide la fila pivote por el pivote para que quede en 1
    for i in range(len(tabla)):
        factor = tabla[i][col]
        if i != fila and abs(factor) > EPS:
            tabla[i] = [v - factor * p for v, p in zip(tabla[i], tabla[fila])]
# fila nueva = fila vieja - factor * fila pivote, para que el elemento de la columna pivote sea 0


# Resuelve con simplex
def metodo_simplex(c, restricciones, tipo):
    validar(restricciones)

    n_vars = len(c)
    m = len(restricciones)
    n_total = n_vars + m
    es_min = (tipo == 'min')

    # Minimizar: se maximiza -Z
    c_obj = [-v for v in c] if es_min else list(c)
    c_ext = c_obj + [0.0] * m
    nombres = [f"x{i+1}" for i in range(n_vars)] + [f"s{i+1}" for i in range(m)]

    tabla = tabla_inicial(restricciones, m)
    base = [n_vars + i for i in range(m)]

    print("\n===== MÉTODO SIMPLEX ESTÁNDAR =====")
    print("Z = " + " + ".join(f"{fmt(c[i])}·x{i+1}" for i in range(n_vars)) + f"   ({tipo})")

    iteracion = 0
    MAX_ITER = 200
    while True:
        if iteracion > MAX_ITER:
            print("\n>>> El método no convergió tras muchas iteraciones (posible ciclado).")
            return None

        zj_cj, z_actual = calcular_zj_cj(tabla, base, c_ext)

        encabezados = ["Base"] + nombres + ["b"]
        filas_tabla = [[nombres[base[i]]] + [fmt(v) for v in tabla[i]] for i in range(m)]
        filas_tabla.append(["Zj-Cj"] + [fmt(v) for v in zj_cj] + [fmt(z_actual)])
        imprimir_tabla(encabezados, filas_tabla, titulo=f"Iteración {iteracion}")

        # Entra la columna con el Zj-Cj MÁS NEGATIVO.
        col_entra = min(range(n_total), key=lambda j: zj_cj[j])
        if zj_cj[col_entra] >= -EPS:
            break  # ya no hay negativos: óptimo

        fila_sale = fila_que_sale(tabla, col_entra)
        if fila_sale is None:
            print(">>> El problema es NO ACOTADO (Z puede crecer/decrecer sin límite). No tiene solución óptima finita.")
            return None

        print(f"Entra: {nombres[col_entra]}   |   Sale: {nombres[base[fila_sale]]}   |   "
              f"Pivote: {fmt(tabla[fila_sale][col_entra])}")

        pivotear(tabla, fila_sale, col_entra)
        base[fila_sale] = col_entra
        iteracion += 1

    solucion = {nombre: 0.0 for nombre in nombres}
    for i, k in enumerate(base):
        solucion[nombres[k]] = tabla[i][-1]

    z_final = -z_actual if es_min else z_actual

    print("\n>>> SOLUCIÓN ÓPTIMA ENCONTRADA:")
    for k in range(n_vars):
        print(f"    x{k+1} = {fmt(solucion[f'x{k+1}'])}")
    print(f"    Z = {fmt(z_final)}")
    return {"variables": solucion, "Z": z_final}