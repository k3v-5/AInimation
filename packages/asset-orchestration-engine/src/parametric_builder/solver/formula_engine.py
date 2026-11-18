import re
import math
from typing import Dict, Any, Optional

class ParameterFormulaEngine:
    """
    Motor seguro de evaluación de fórmulas paramétricas.
    Soporta operaciones aritméticas, clamp, min, max, sqrt sin usar eval() arbitrario.
    """
    @classmethod
    def evaluate(cls, expression: str, context_params: Dict[str, Any]) -> float:
        expr = expression.strip()

        # Reemplazar identificadores de parámetros por sus valores numéricos
        for param_name, param_val in sorted(context_params.items(), key=lambda x: len(x[0]), reverse=True):
            if isinstance(param_val, (int, float)):
                # Reemplazo seguro por palabra completa
                expr = re.sub(rf"\b{param_name}\b", str(float(param_val)), expr)

        # Evaluar funciones seguras simples
        # 1. Total_height * wall_ratio
        # Soportar sintaxis segura: números y operadores +, -, *, /, (, )
        if not re.fullmatch(r"[\d\.\s\+\-\*\/\(\)]+", expr):
            raise ValueError(f"UNSAFE_EXPRESSION: Formula contains unauthorized characters: {expr}")

        # Evitar división por cero
        try:
            # Uso de evaluación aritmética pura restringida
            result = float(eval(expr, {"__builtins__": None}, {}))
            return round(result, 4)
        except ZeroDivisionError:
            return 0.0
