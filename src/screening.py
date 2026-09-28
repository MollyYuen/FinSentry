"""Deterministic MVP screening. No LLM call or PDF extraction occurs here."""

from __future__ import annotations

import csv
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path


FIELD_NAMES = (
    "metric", "year", "value_original", "original_unit", "value_yuan",
    "statement_scope", "source_file", "source_page", "page_verified",
)
UNITS = {"元": Decimal("1"), "千元": Decimal("1000"), "万元": Decimal("10000")}
RULE_METRICS = {
    "R1": ("营业收入", "归母净利润"),
    "R2": ("归母净利润", "经营活动现金流量净额"),
    "R3": ("归母净利润", "扣非后归母净利润"),
}
REASONS = {
    "R1": "营业收入下降而归母净利润增长，且增速差异达到暂定阈值，需核验利润改善来源",
    "R2": "归母净利润增长而经营现金流下降，且增速差异达到暂定阈值，需进一步核验",
    "R3": "归母净利润与扣非后归母净利润增速背离，需核验非经常性因素",
}
THRESHOLD_PP = Decimal("20")


def read_financial_data(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None or set(reader.fieldnames) != set(FIELD_NAMES):
            raise ValueError(f"CSV 表头必须为: {', '.join(FIELD_NAMES)}")
        return list(reader)


def _rate(value_now: Decimal, value_prev: Decimal) -> Decimal:
    if value_prev <= 0:
        raise ValueError("上期金额为零或负数，不能按本 MVP 的同比阈值直接判断")
    return (value_now - value_prev) / value_prev


def _decimal(value: str, name: str) -> Decimal:
    try:
        result = Decimal(value)
    except (InvalidOperation, TypeError):
        raise ValueError(f"{name} 不是有效数字") from None
    if not result.is_finite():
        raise ValueError(f"{name} 必须为有限数字")
    return result


def _extract_pair(rows: list[dict[str, str]], metric: str) -> tuple[Decimal, Decimal, list[int], bool]:
    pair = [r for r in rows if r.get("metric") == metric]
    current = [r for r in pair if r.get("year") == "2025"]
    previous = [r for r in pair if r.get("year") == "2024"]
    if len(current) != 1 or len(previous) != 1 or len(pair) != 2:
        raise ValueError(f"{metric} 必须恰有 2025/2024 两条记录")
    a, b = current[0], previous[0]
    if a["statement_scope"] != "合并" or b["statement_scope"] != "合并":
        raise ValueError(f"{metric} 不是同一合并报表口径")
    if a["original_unit"] not in UNITS or a["original_unit"] != b["original_unit"]:
        raise ValueError(f"{metric} 原始单位缺失、不支持或两期不一致")
    if not a["source_file"] or a["source_file"] != b["source_file"]:
        raise ValueError(f"{metric} 来源文件缺失或两期不一致")
    amounts = []
    for row in (a, b):
        original = _decimal(row["value_original"], f"{metric} value_original")
        normalized = _decimal(row["value_yuan"], f"{metric} value_yuan")
        if original * UNITS[row["original_unit"]] != normalized:
            raise ValueError(f"{metric} 原始金额与换算金额不相符")
        amounts.append(normalized)
    pages = []
    for row in (a, b):
        try:
            page = int(row["source_page"])
        except (TypeError, ValueError):
            raise ValueError(f"{metric} 缺少有效的来源页码") from None
        if page <= 0:
            raise ValueError(f"{metric} 页码必须是正整数")
        pages.append(page)
        if row["page_verified"].lower() not in ("true", "false"):
            raise ValueError(f"{metric} page_verified 必须是 true/false")
    verified = all(row["page_verified"].lower() == "true" for row in (a, b))
    return amounts[0], amounts[1], pages, verified


def _rounded(value: Decimal, digits: int) -> float:
    quantum = Decimal("1").scaleb(-digits)
    return float(value.quantize(quantum, rounding=ROUND_HALF_UP))


def _evaluate(rule_id: str, rows: list[dict[str, str]]) -> dict:
    values: dict[str, Decimal] = {}
    pages: list[int] = []
    verified = True
    try:
        for metric in RULE_METRICS[rule_id]:
            now, before, metric_pages, metric_verified = _extract_pair(rows, metric)
            values[metric] = _rate(now, before)
            pages.extend(metric_pages)
            verified = verified and metric_verified
    except ValueError as exc:
        return {
            "rule_id": rule_id, "status": "DATA_ISSUE", "calculation": {},
            "reason": str(exc), "source_pages": [], "source_verified": False,
        }

    first, second = (values[m] for m in RULE_METRICS[rule_id])
    if rule_id == "R1":
        triggered = first < 0 and second > 0 and (second - first) * 100 >= THRESHOLD_PP
        calc = {"revenue_yoy": _rounded(first, 4), "net_profit_yoy": _rounded(second, 4),
                "difference_pp": _rounded((second - first) * 100, 2)}
    elif rule_id == "R2":
        triggered = first > 0 and second < 0 and (first - second) * 100 >= THRESHOLD_PP
        calc = {"net_profit_yoy": _rounded(first, 4), "operating_cashflow_yoy": _rounded(second, 4),
                "difference_pp": _rounded((first - second) * 100, 2)}
    else:
        triggered = (first > 0 and second < 0) or abs(first - second) * 100 >= THRESHOLD_PP
        calc = {"net_profit_yoy": _rounded(first, 4), "adjusted_net_profit_yoy": _rounded(second, 4),
                "difference_pp": _rounded(abs(first - second) * 100, 2)}
    return {
        "rule_id": rule_id,
        "status": "REVIEW" if triggered else "PASS",
        "calculation": calc,
        "reason": REASONS[rule_id] if triggered else "未达到本规则的 MVP 暂定触发条件",
        "source_pages": sorted(set(pages)),
        "source_verified": verified,
    }


def screen(rows: list[dict[str, str]]) -> dict:
    return {
        "schema_version": "0.1",
        "case_id": "datang_2025_demo",
        "data_status": "SAMPLE_UNVERIFIED",
        "results": [_evaluate(rule_id, rows) for rule_id in ("R1", "R2", "R3")],
    }
