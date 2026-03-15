import math

from numerical_methods import integrate_with_runge, METHODS


class ImproperIntegral:
    def __init__(self, func, a, b, singular_points, name, description, exact_value, convergent):
        self.func = func
        self.a = a
        self.b = b
        self.singular_points = singular_points
        self.name = name
        self.description = description
        self.exact_value = exact_value
        self.convergent = convergent


def g1(x):
    if x <= 0:
        return float("inf")
    return 1.0 / math.sqrt(x)


def g2(x):
    if x >= 1:
        return float("inf")
    return 1.0 / math.sqrt(1.0 - x)


def g3(x):
    if x == 0.5:
        return float("inf")
    return 1.0 / math.sqrt(abs(x - 0.5))


def g4(x):
    if x <= 0:
        return float("inf")
    return 1.0 / (x ** 1.5)


def g5(x):
    if x >= 1:
        return float("inf")
    return 1.0 / ((1.0 - x) ** 1.5)


def g6(x):
    if x == 0.5:
        return float("inf")
    return 1.0 / (abs(x - 0.5) ** 1.5)


IMPROPER_INTEGRALS = {
    "g1": ImproperIntegral(
        func=g1,
        a=0.0,
        b=1.0,
        singular_points=(0.0,),
        name="g₁(x) = 1/√x",
        description="Несобственный интеграл 2 рода: разрыв в левой границе",
        exact_value=2.0,
        convergent=True,
    ),
    "g2": ImproperIntegral(
        func=g2,
        a=0.0,
        b=1.0,
        singular_points=(1.0,),
        name="g₂(x) = 1/√(1-x)",
        description="Несобственный интеграл 2 рода: разрыв в правой границе",
        exact_value=2.0,
        convergent=True,
    ),
    "g3": ImproperIntegral(
        func=g3,
        a=0.0,
        b=1.0,
        singular_points=(0.5,),
        name="g₃(x) = 1/√|x-0.5|",
        description="Несобственный интеграл 2 рода: разрыв внутри интервала",
        exact_value=4 * math.sqrt(0.5),
        convergent=True,
    ),
    "g4": ImproperIntegral(
        func=g4,
        a=0.0,
        b=1.0,
        singular_points=(0.0,),
        name="g₄(x) = 1/x^{3/2}",
        description="Несобственный интеграл 2 рода: разрыв в левой границе, расходится",
        exact_value=None,
        convergent=False,
    ),
    "g5": ImproperIntegral(
        func=g5,
        a=0.0,
        b=1.0,
        singular_points=(1.0,),
        name="g₅(x) = 1/(1-x)^{3/2}",
        description="Несобственный интеграл 2 рода: разрыв в правой границе, расходится",
        exact_value=None,
        convergent=False,
    ),
    "g6": ImproperIntegral(
        func=g6,
        a=0.0,
        b=1.0,
        singular_points=(0.5,),
        name="g₆(x) = 1/|x-0.5|^{3/2}",
        description="Несобственный интеграл 2 рода: разрыв внутри интервала, расходится",
        exact_value=None,
        convergent=False,
    ),
}


def improper_integral_numeric(key, method_key, eps, n0=4, a_override=None, b_override=None):
    info = IMPROPER_INTEGRALS[key]
    a = info.a if a_override is None else a_override
    b = info.b if b_override is None else b_override
    f = info.func

    if len(info.singular_points) == 1:
        c = info.singular_points[0]
    else:
        raise NotImplementedError("Only one singular point is supported")

    if not info.convergent:
        raise ArithmeticError("Интеграл не существует (расходится)")

    eps_sing = 0.1
    value_prev = None
    for _ in range(10):
        parts = []
        if abs(c - a) < 1e-12:
            val, _, _ = integrate_with_runge(
                f, a + eps_sing, b, method_key, eps, n0=n0
            )
            parts.append(val)
        elif abs(c - b) < 1e-12:
            val, _, _ = integrate_with_runge(
                f, a, b - eps_sing, method_key, eps, n0=n0
            )
            parts.append(val)
        else:
            left, _, _ = integrate_with_runge(
                f, a, c - eps_sing, method_key, eps, n0=n0
            )
            right, _, _ = integrate_with_runge(
                f, c + eps_sing, b, method_key, eps, n0=n0
            )
            parts.extend([left, right])

        value = sum(parts)

        if value_prev is not None and abs(value - value_prev) < eps:
            return value, 0

        value_prev = value
        eps_sing *= 0.5

    return value_prev if value_prev is not None else None, 0
