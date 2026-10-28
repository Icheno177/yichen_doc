"""Independent model recalculation; formulas are never evaluated with eval()."""
from __future__ import annotations

import ast
import math
from typing import Any

INPUT_CLASSES = {"VERIFIED_EXTERNAL", "VERIFIED_INTERNAL", "USER_PROVIDED_UNVERIFIED", "ASSUMPTION", "DEMONSTRATION", "MISSING"}


class _Arithmetic(ast.NodeVisitor):
    def __init__(self, names: dict[str, float]): self.names = names
    def visit_Expression(self, node): return self.visit(node.body)
    def visit_Constant(self, node):
        if isinstance(node.value, (int, float)): return float(node.value)
        raise ValueError("Only numeric constants are supported")
    def visit_Name(self, node):
        if node.id not in self.names: raise ValueError(f"Unknown model input: {node.id}")
        return float(self.names[node.id])
    def visit_BinOp(self, node):
        a, b = self.visit(node.left), self.visit(node.right)
        if isinstance(node.op, ast.Add): return a + b
        if isinstance(node.op, ast.Sub): return a - b
        if isinstance(node.op, ast.Mult): return a * b
        if isinstance(node.op, ast.Div): return a / b
        if isinstance(node.op, ast.Pow): return a ** b
        raise ValueError("Unsupported arithmetic operator")
    def visit_UnaryOp(self, node):
        value = self.visit(node.operand)
        if isinstance(node.op, ast.USub): return -value
        if isinstance(node.op, ast.UAdd): return value
        raise ValueError("Unsupported unary operator")
    def generic_visit(self, node): raise ValueError(f"Unsupported formula syntax: {type(node).__name__}")


def evaluate_expression(expression: str, values: dict[str, float]) -> float:
    tree = ast.parse(expression, mode="eval")
    return float(_Arithmetic(values).visit(tree))


def _irr(cashflows: list[float]) -> float | None:
    if not cashflows or not (any(x < 0 for x in cashflows) and any(x > 0 for x in cashflows)):
        return None
    def npv(rate): return sum(cf / ((1 + rate) ** i) for i, cf in enumerate(cashflows))
    low, high = -0.9999, 10.0
    if npv(low) * npv(high) > 0: return None
    for _ in range(300):
        mid = (low + high) / 2
        val = npv(mid)
        if abs(val) < 1e-10: return mid
        if npv(low) * val <= 0: high = mid
        else: low = mid
    return (low + high) / 2


def audit_models(models: list[dict]) -> dict:
    results, issues = [], []
    for idx, model in enumerate(models, 1):
        mid = str(model.get("model_id", f"MODEL-{idx:03d}"))
        inputs = model.get("inputs", {})
        values, input_rows = {}, []
        for key, item in inputs.items():
            if not isinstance(item, dict): item = {"value": item}
            classification = str(item.get("classification", "MISSING")).upper()
            if classification not in INPUT_CLASSES:
                issues.append({"issue_id": f"MODEL-CLASS-{mid}-{key}", "severity": "HIGH", "description": f"Invalid input classification for {key}: {classification}", "status": "OPEN"})
            value = item.get("value")
            if value is None or classification == "MISSING":
                issues.append({"issue_id": f"MODEL-MISSING-{mid}-{key}", "severity": "HIGH", "description": f"Required model input missing: {key}", "status": "OPEN"})
            else:
                values[key] = float(value)
            if classification not in {"VERIFIED_EXTERNAL", "VERIFIED_INTERNAL"}:
                issues.append({"issue_id": f"MODEL-UNVERIFIED-{mid}-{key}", "severity": "MEDIUM", "description": f"Input {key} is classified {classification}; model output is conditional.", "status": "OPEN"})
            input_rows.append({"input_id": key, "value": value, "unit": item.get("unit", ""), "period": item.get("period", ""), "classification": classification, "source_id": item.get("source_id", ""), "limitations": item.get("limitations", "")})
        output = None; error = None; formula = model.get("formula", "")
        try:
            kind = str(model.get("model_type", "expression")).lower()
            if kind == "roi":
                benefit, cost = values[model.get("benefit_input", "incremental_benefit")], values[model.get("cost_input", "incremental_cost")]
                if cost == 0: raise ValueError("ROI cost denominator is zero")
                formula = "(incremental_benefit - incremental_cost) / incremental_cost"
                output = (benefit - cost) / cost
            elif kind == "tco":
                cost_keys = model.get("cost_inputs", list(values))
                if not cost_keys: raise ValueError("TCO requires at least one classified cost input")
                output = sum(values[key] for key in cost_keys)
                formula = "sum(classified lifecycle cost inputs)"
            elif kind == "cagr":
                start = float(values[model.get("start_input", "start")])
                end = float(values[model.get("end_input", "end")])
                periods = float(model.get("periods", values.get("periods", 0)))
                if start <= 0 or end < 0 or periods <= 0: raise ValueError("CAGR requires start > 0, end >= 0 and periods > 0")
                output = (end / start) ** (1 / periods) - 1
                formula = "(ending_value / beginning_value)^(1 / periods) - 1"
            elif kind == "gmv":
                quantity = float(values[model.get("quantity_input", "transaction_count")])
                value = float(values[model.get("value_input", "average_order_value")])
                output = quantity * value
                formula = "transaction_count * average_order_value"
            elif kind in {"tam", "sam", "som"}:
                expression = model.get("expression", "eligible_customers * annual_spend")
                output = evaluate_expression(expression, values)
                formula = expression
            elif kind in {"npv", "dcf"}:
                flows = [float(x) for x in model.get("cashflows", [])]
                rate = float(model.get("discount_rate", values.get("discount_rate")))
                if not flows: raise ValueError("cashflows must include period 0 and following periods")
                if rate <= -1: raise ValueError("discount_rate must be greater than -100%")
                formula = "sum(cashflow_t / (1 + discount_rate)^t), t=0..n"
                output = sum(cf / ((1 + rate) ** t) for t, cf in enumerate(flows))
                terminal = model.get("terminal_value")
                if kind == "dcf" and terminal is not None:
                    output += float(terminal) / ((1 + rate) ** (len(flows) - 1))
                    formula += " + terminal_value / (1 + discount_rate)^n"
            elif kind == "irr":
                flows = [float(x) for x in model.get("cashflows", [])]
                formula = "rate r such that sum(cashflow_t/(1+r)^t)=0"
                output = _irr(flows)
                if output is None: raise ValueError("IRR is undefined or not bracketed for the supplied cash flows")
            elif kind == "payback":
                flows = [float(x) for x in model.get("cashflows", [])]
                if not flows: raise ValueError("cashflows must include period 0 and following periods")
                cumulative = 0.0; output = None
                for i, cf in enumerate(flows):
                    previous = cumulative; cumulative += cf
                    if cumulative >= 0 and i > 0 and cf > 0:
                        output = (i - 1) + (-previous / cf); break
                formula = "first period where cumulative incremental cash flows recover initial outflow"
                if output is None: raise ValueError("Payback is not reached in the provided period")
            elif kind in {"scenarios", "sensitivity"}:
                expression = model.get("expression", formula)
                if not expression: raise ValueError(f"{kind} requires an expression")
                rows = []
                if kind == "scenarios":
                    for scenario in model.get("scenarios", []):
                        scenario_values = dict(values)
                        for key, item in scenario.get("inputs", {}).items():
                            record = item if isinstance(item, dict) else {"value": item, "classification": "ASSUMPTION"}
                            classification = str(record.get("classification", "ASSUMPTION")).upper()
                            if classification not in INPUT_CLASSES:
                                issues.append({"issue_id": f"MODEL-CLASS-{mid}-{scenario.get('name','case')}-{key}", "severity": "HIGH", "description": f"Invalid scenario input classification for {key}: {classification}", "status": "OPEN"})
                            if classification not in {"VERIFIED_EXTERNAL", "VERIFIED_INTERNAL"}:
                                issues.append({"issue_id": f"MODEL-UNVERIFIED-{mid}-{scenario.get('name','case')}-{key}", "severity": "MEDIUM", "description": f"Scenario input {key} is classified {classification}; result is conditional.", "status": "OPEN"})
                            scenario_values[key] = float(record.get("value"))
                        rows.append({"case": scenario.get("name", f"Scenario {len(rows)+1}"), "inputs": scenario.get("inputs", {}),
                                     "independent_output": evaluate_expression(expression, scenario_values), "reported_output": scenario.get("reported_output")})
                else:
                    parameter = model.get("parameter")
                    if not parameter: raise ValueError("Sensitivity model requires a parameter name")
                    for value in model.get("values", []):
                        scenario_values = dict(values); scenario_values[parameter] = float(value)
                        classification = str(model.get("parameter_classification", "ASSUMPTION")).upper()
                        if classification not in {"VERIFIED_EXTERNAL", "VERIFIED_INTERNAL"}:
                            issues.append({"issue_id": f"MODEL-UNVERIFIED-{mid}-{parameter}", "severity": "MEDIUM", "description": f"Sensitivity values for {parameter} are classified {classification}; results are conditional.", "status": "OPEN"})
                        rows.append({"parameter": parameter, "value": value, "classification": classification,
                                     "independent_output": evaluate_expression(expression, scenario_values)})
                if not rows: raise ValueError(f"{kind} requires at least one case")
                output = rows
                formula = expression
            else:
                expression = model.get("expression", formula)
                if not expression: raise ValueError("model needs an expression or supported model_type")
                output = evaluate_expression(expression, values)
        except (ValueError, TypeError, KeyError, ZeroDivisionError, OverflowError, SyntaxError) as exc:
            error = str(exc)
            issues.append({"issue_id": f"MODEL-RECALC-{mid}", "severity": "HIGH", "description": error, "status": "OPEN"})
        expected = model.get("reported_output")
        delta = None if not isinstance(output, (int, float)) or expected is None else output - float(expected)
        if delta is not None and not math.isclose(output, float(expected), rel_tol=float(model.get("tolerance", 1e-6)), abs_tol=float(model.get("absolute_tolerance", 1e-8))):
            issues.append({"issue_id": f"MODEL-MISMATCH-{mid}", "severity": "CRITICAL", "description": f"Independent recalculation {output} differs from reported output {expected}.", "status": "OPEN"})
        results.append({"model_id": mid, "model_type": model.get("model_type", "expression"), "formula": formula,
                        "inputs": input_rows, "independent_output": output, "reported_output": expected,
                        "difference": delta, "unit": model.get("unit", ""), "period": model.get("period", ""),
                        "limitations": model.get("limitations", ""), "error": error,
                        "result_status": "RECALCULATED_CONDITIONAL" if output is not None else "NOT_RECALCULATED"})
    return {"model_count": len(results), "models": results, "issues": issues,
            "limitations": ["An independently reproducible formula does not validate the source or classification of its inputs.", "ROI/NPV/IRR results are not business outcomes unless cash flows and input evidence are verified."]}
