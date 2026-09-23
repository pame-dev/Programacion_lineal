# aqui se piden los datos del problema y se elige el método de resolución
try:
    from .aritmetica import Frac, texto_a_frac
    from .metodo_grafico import metodo_grafico
    from .metodo_simplex import metodo_simplex
    from .metodo_gran_m import metodo_gran_m
except ImportError:
    from aritmetica import Frac, texto_a_frac
    from metodo_grafico import metodo_grafico
    from metodo_simplex import metodo_simplex
    from metodo_gran_m import metodo_gran_m


# Funciones auxiliares para leer datos del usuario con validación.
def pedir_entero(mensaje, minimo=1):
    # Se repite hasta que el usuario ingrese un entero válido.
    while True:
        try:
            valor = int(input(mensaje))
            if valor < minimo:
                print(f"  Debe ser un entero >= {minimo}.")
                continue
            return valor
        except ValueError:
            print("  Entrada inválida, escribe un número entero.")


def pedir_frac(mensaje):
    while True:
        texto = input(mensaje)
        try:
            return texto_a_frac(texto)
        except Exception:
            print("  Entrada inválida. Usa un entero, decimal (2.5) o fracción (3/4).")


def pedir_signo(mensaje):
    while True:
        s = input(mensaje).strip()
        if s in ('<=', '>=', '='):
            return s
        print("  Signo inválido. Escribe exactamente <=, >= o =.")


def pedir_tipo(mensaje):
    while True:
        s = input(mensaje).strip().lower()
        if s in ('max', 'min'):
            return s
        print("  Escribe 'max' o 'min'.")


def leer_problema():
    # Esta función recoge la estructura del problema: variables, objetivo y restricciones.
    print("\n===== Definición del problema de Programación Lineal =====")
    n = pedir_entero("Número de variables de decisión: ", 1)
    tipo = pedir_tipo("¿Maximizar o minimizar Z? (max/min): ")

    print(f"\nCoeficientes de la función objetivo Z (forma estándar):")
    # Se convierte cada valor a Frac para usar aritmética exacta.
    c = [pedir_frac(f"  c{i+1}  (coeficiente de x{i+1}): ") for i in range(n)]

    m = pedir_entero("\nNúmero de restricciones: ", 1)
    restricciones = []
    print("\nPara cada restricción escribe sus coeficientes, el signo y el lado derecho b.")
    for i in range(m):
        print(f"\nRestricción {i+1}:")
        coefs = [pedir_frac(f"  a{i+1}{j+1}  (coeficiente de x{j+1}): ") for j in range(n)]
        signo = pedir_signo("  signo (<=, >=, =): ")
        b = pedir_frac("  b (lado derecho): ")
        restricciones.append(tuple(coefs) + (signo, b))

    return n, c, tipo, restricciones


def metodos_disponibles(n, restricciones):
    # Antes de resolver, se valida qué algoritmo aplica al problema.
    disponibles = []
    # Regla: Simplex estándar solo acepta restricciones del tipo <= y b >= 0.
    solo_le = all(r[-2] == '<=' for r in restricciones)
    b_no_negativo = all(r[-1] >= Frac(0) for r in restricciones)

    if n == 2:
        disponibles.append('grafico')
    if solo_le and b_no_negativo:
        disponibles.append('simplex')
    # Gran M puede resolver casos más generales, así que casi siempre está disponible.
    disponibles.append('granm')
    return disponibles, solo_le, b_no_negativo


def elegir_metodo(disponibles):
    nombres = {
        'grafico': 'Método Gráfico (solo problemas de 2 variables)',
        'simplex': 'Método Simplex estándar',
        'granm': 'Método de la Gran M',
    }
    print("\nMétodos disponibles para este problema:")
    for i, met in enumerate(disponibles):
        print(f"  {i+1}. {nombres[met]}")

    while True:
        try:
            op = int(input("Elige el número del método a usar: "))
            if 1 <= op <= len(disponibles):
                return disponibles[op - 1]
        except ValueError:
            pass
        print("  Opción inválida.")


def main():
    # Flujo principal del programa: entra el problema, se elige el método y se resuelve.
    print("##################################################################")
    print("#   SOLUCIONADOR DE PROGRAMACIÓN LINEAL - Gráfico / Simplex / Gran M")
    print("##################################################################")

    while True:
        n, c, tipo, restricciones = leer_problema()
        disponibles, solo_le, b_no_negativo = metodos_disponibles(n, restricciones)

        if 'simplex' not in disponibles:
            print("\nNota: el método Simplex estándar NO está disponible porque el problema")
            print("tiene alguna restricción '=' o '>=' (o algún lado derecho b negativo).")
            print("En ese caso se necesitan variables artificiales -> usa el método de la Gran M.")
        if 'grafico' not in disponibles:
            print("\nNota: el método Gráfico solo está disponible para problemas de 2 variables.")

        metodo = elegir_metodo(disponibles)

        if metodo == 'grafico':
            metodo_grafico(c, restricciones, tipo)
        elif metodo == 'simplex':
            metodo_simplex(c, restricciones, tipo)
        elif metodo == 'granm':
            metodo_gran_m(c, restricciones, tipo)

        de_nuevo = input("\n¿Deseas resolver otro problema? (s/n): ").strip().lower()
        if de_nuevo != 's':
            print("\n¡Hasta luego!")
            break


if __name__ == "__main__":
    main()
