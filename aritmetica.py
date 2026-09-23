# este archivo define fracciones exactas para evitar errores con decimales

# El programa no usa float para los cálculos importantes porque los decimales
# pueden producir errores de precisión. Por eso todas las cantidades se guardan
# en fracciones exactas (numerador/denominador).
def gcd(a, b):
    """Máximo común divisor (algoritmo de Euclides, con un ciclo)."""
    a, b = abs(a), abs(b)
    while b != 0:
        a, b = b, a % b
    return a if a != 0 else 1


class Frac:
    """Fracción exacta num/den, siempre representada en su forma reducida."""

    def __init__(self, num, den=1):
        # Cada fracción se normaliza para que quede siempre reducida, por ejemplo:
        # 6/8 -> 3/4. Eso evita errores de comparación y de cálculo.
        if den == 0:
            raise ZeroDivisionError("El denominador no puede ser 0.")
        if den < 0:
            num, den = -num, -den
        g = gcd(num, den)
        self.num = num // g
        self.den = den // g

    def __add__(self, o):
        o = to_frac(o)
        return Frac(self.num * o.den + o.num * self.den, self.den * o.den)

    __radd__ = __add__

    def __sub__(self, o):
        o = to_frac(o)
        return Frac(self.num * o.den - o.num * self.den, self.den * o.den)

    def __rsub__(self, o):
        return to_frac(o) - self

    def __mul__(self, o):
        o = to_frac(o)
        return Frac(self.num * o.num, self.den * o.den)

    __rmul__ = __mul__

    def __truediv__(self, o):
        o = to_frac(o)
        if o.num == 0:
            raise ZeroDivisionError("División entre 0.")
        return Frac(self.num * o.den, self.den * o.num)

    def __neg__(self):
        return Frac(-self.num, self.den)

    def __abs__(self):
        return Frac(abs(self.num), self.den)

    def __eq__(self, o):
        o = to_frac(o)
        return self.num == o.num and self.den == o.den

    def __lt__(self, o):
        o = to_frac(o)
        return self.num * o.den < o.num * self.den

    def __le__(self, o):
        return self < o or self == o

    def __gt__(self, o):
        o = to_frac(o)
        return self.num * o.den > o.num * self.den

    def __ge__(self, o):
        return self > o or self == o

    def __hash__(self):
        return hash((self.num, self.den))

    def __repr__(self):
        if self.den == 1:
            return str(self.num)
        return f"{self.num}/{self.den}"


def to_frac(x):
    """Convierte int, str o Frac a Frac."""
    # Esta función permite mezclar enteros y fracciones sin tener que convertir
    # manualmente cada valor antes de operar.
    if isinstance(x, Frac):
        return x
    if isinstance(x, int):
        return Frac(x, 1)
    if isinstance(x, str):
        return texto_a_frac(x)
    raise TypeError(f"No se puede convertir a fracción: {x!r}")


def texto_a_frac(texto):
    """Convierte texto ingresado por el usuario a Frac."""
    # Acepta entradas como: 5, 2.5, -3/4, +4.
    texto = texto.strip().replace(" ", "")
    if texto == "":
        raise ValueError("Entrada vacía.")

    negativo = False
    if texto.startswith("-"):
        negativo = True
        texto = texto[1:]
    elif texto.startswith("+"):
        texto = texto[1:]

    if "/" in texto:
        n_txt, d_txt = texto.split("/")
        valor = Frac(int(n_txt), int(d_txt))
    elif "." in texto:
        entero_txt, decimal_txt = texto.split(".")
        entero_txt = entero_txt if entero_txt != "" else "0"
        decimal_txt = decimal_txt if decimal_txt != "" else "0"
        num = int(entero_txt) * (10 ** len(decimal_txt)) + int(decimal_txt)
        den = 10 ** len(decimal_txt)
        valor = Frac(num, den)
    else:
        valor = Frac(int(texto), 1)

    return -valor if negativo else valor


def fmt(x):
    """Texto legible de una fracción o de cualquier objeto con __repr__."""
    return str(x)
