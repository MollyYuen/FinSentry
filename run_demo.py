"""Run the sample's offline Skill 1 demonstration from any working directory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.screening import read_financial_data, screen


ROOT = Path(__file__).resolve().parent
SAMPLE = ROOT / "data" / "sample"


def main() -> None:
    parser = argparse.ArgumentParser(description="FinSentry Skill 1 offline sample")
    parser.add_argument("--offline", action="store_true", help="仅运行离线规则演示")
    args = parser.parse_args()
    if not args.offline:
        parser.error("起步包仅支持 --offline；尚未接入 PDF、Skill 2 或 DeepSeek")

    actual = screen(read_financial_data(SAMPLE / "financial_data.csv"))
    expected = json.loads((SAMPLE / "expected_screening_result.json").read_text(encoding="utf-8"))
    if actual != expected:
        raise SystemExit("结果与样例预期不符：请先检查数据、单位和规则；未保存结果。")
    output = ROOT / "outputs" / "screening_result.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(actual, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for rule in actual["results"]:
        print(rule["rule_id"], rule["status"])
    print(f"样例验收通过。输出文件：{output}")
    print("注意：来源页码尚未对照原 PDF 核验，不能作为正式引用。")


if __name__ == "__main__":
    main()
