# Financial and Operating Model Audit

Supported structured calculations are arithmetic expressions, ROI, TCO, NPV, DCF (with optional terminal value), IRR, payback, CAGR, GMV, TAM/SAM/SOM expressions, Bear/Base/Bull scenarios, and one-parameter sensitivity sweeps. Inputs record value, unit, period, classification, source ID and limitation. Classifications: `VERIFIED_EXTERNAL`, `VERIFIED_INTERNAL`, `USER_PROVIDED_UNVERIFIED`, `ASSUMPTION`, `DEMONSTRATION`, and `MISSING`.

The safe expression evaluator allows numeric constants, named inputs, parentheses, unary signs, and `+ - * / **`; it rejects arbitrary code and function calls. NPV/DCF requires period-0 and subsequent cash flows plus a discount rate. IRR is solved by bisection only for a bracketed root. Payback is interpolated over sequential cash flows.

Recalculation verifies arithmetic only. It does not validate source quality, input reasonableness, tax, working capital, currency, units or economic classification. Scenario overrides and sensitivity values default to assumptions and remain conditional unless explicitly classified. Unknown inputs remain missing. Work-hour savings are not cash savings without an evidenced avoidable-cost bridge. Arbitrary workbook formulas are inventoried but not recalculated by openpyxl; report unsupported functions as `NOT_RUN`.

Forecasts that affect decisions should include Bear/Base/Bull inputs, source/classification, results, sensitivity, risks and Stop/Go effect. Missing inputs are not grounds to invent estimates.
