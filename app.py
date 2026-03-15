from __future__ import annotations

import math
from dataclasses import dataclass

from flask import Flask, jsonify, render_template, request

from numerical_methods import FUNCTIONS, METHODS, integrate_with_runge
from improper_integrals import IMPROPER_INTEGRALS, improper_integral_numeric


app = Flask(__name__)


@dataclass
class IntegrationRequest:
    function_key: str
    method_key: str
    a: float
    b: float
    eps: float


def parse_integration_request(data):
    try:
        function_key = str(data["function_key"])
        method_key = str(data["method_key"])
        a_str = data.get("a")
        if a_str is None or str(a_str).strip() == "":
            raise ValueError("Поле 'a' не заполнено")
        a = float(a_str)
        b_str = data.get("b")
        if b_str is None or str(b_str).strip() == "":
            raise ValueError("Поле 'b' не заполнено")
        b = float(b_str)
        eps_str = data.get("eps")
        if eps_str is None or str(eps_str).strip() == "":
            raise ValueError("Поле 'eps' не заполнено")
        eps = float(eps_str)
    except (KeyError, TypeError, ValueError):
        raise ValueError("Некорректные входные данные")

    if eps <= 0:
        raise ValueError("Точность должна быть положительной")

    return IntegrationRequest(function_key, method_key, a, b, eps)


@app.route("/")
def index():
    return render_template(
        "index.html",
        functions=FUNCTIONS,
        methods=METHODS,
        improper_integrals=IMPROPER_INTEGRALS,
    )


@app.route("/api/integrate", methods=["POST"])
def api_integrate():
    try:
        data = request.get_json(force=True)
        params = parse_integration_request(data)

        f_info = FUNCTIONS[params.function_key]
        f = f_info["func"]

        result, n, err = integrate_with_runge(
            f, params.a, params.b, params.method_key, params.eps
        )

        if err is None:
            raise ValueError("Точность не достигнута: превышено максимальное число разбиений (n_max = 16777216)")

        if math.isnan(err):
            err = None

        exact_value = None
        exact_error = None
        if (exact := f_info.get("exact")) is not None:
            exact_value = exact(params.a, params.b)
            exact_error = abs(result - exact_value)
            if math.isnan(exact_error):
                exact_error = None

        return jsonify(
            {
                "ok": True,
                "result": result,
                "n": n,
                "runge_error": err,
                "exact_value": exact_value,
                "exact_error": exact_error,
            }
        )
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.route("/api/improper", methods=["POST"])
def api_improper():
    try:
        data = request.get_json(force=True)
        key_str = data.get("key")
        if key_str is None or str(key_str).strip() == "":
            raise ValueError("Поле 'key' не заполнено")
        key = str(key_str)
        method_key_str = data.get("method_key")
        if method_key_str is None or str(method_key_str).strip() == "":
            raise ValueError("Поле 'method_key' не заполнено")
        method_key = str(method_key_str)
        eps_str = data.get("eps")
        if eps_str is None or str(eps_str).strip() == "":
            raise ValueError("Поле 'eps' не заполнено")
        eps = float(eps_str)
        a_override = data.get("a")
        b_override = data.get("b")

        if eps <= 0:
            raise ValueError("Точность должна быть положительной")

        info = IMPROPER_INTEGRALS[key]

        if not info.convergent:
            return jsonify(
                {
                    "ok": True,
                    "exists": False,
                    "message": "Интеграл не существует (расходится)",
                }
            )

        a_val = float(a_override) if a_override is not None and str(a_override).strip() != "" else None
        b_val = float(b_override) if b_override is not None and str(b_override).strip() != "" else None

        value, _ = improper_integral_numeric(
            key,
            method_key,
            eps,
            a_override=a_val,
            b_override=b_val,
        )
        if math.isnan(value):
            value = None
        exact_error = None
        if value is not None and info.exact_value is not None:
            exact_error = abs(value - info.exact_value)
            if math.isnan(exact_error):
                exact_error = None
        if value is None:
            raise ValueError("Не удалось вычислить значение интеграла")

        return jsonify(
            {
                "ok": True,
                "exists": True,
                "value": value,
                "exact_value": info.exact_value,
                "exact_error": exact_error,
            }
        )
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
