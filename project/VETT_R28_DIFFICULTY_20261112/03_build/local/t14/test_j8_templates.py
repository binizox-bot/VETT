"""J8 guard test: no non-frozen template on the main path, no choice residue in runs.

Run: ``python test_j8_templates.py`` (no GPU).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

T14_ROOT = Path(__file__).resolve().parent
LOCAL = T14_ROOT.parent
RUN_ROOT = LOCAL.parents[1]
for _p in (str(T14_ROOT), str(LOCAL), str(RUN_ROOT / "05_pipeline"),
           str(RUN_ROOT / "02_design" / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import t14_runner as R  # noqa: E402


def expect_raises(fn, label: str) -> None:
    try:
        fn()
    except RuntimeError:
        return
    raise AssertionError(f"expected RuntimeError for {label}")


def main() -> None:
    # 1) valid frozen config passes
    R.assert_frozen_templates({
        "t1_template_version": "T1.factor_visibility.v1",
        "s1_template_version": "S1.span_topic.v4",
        "t2_template_version": "T2.naturalness_pair.v1",
    })
    # 2) deprecated choice field is rejected even if value is innocent
    expect_raises(lambda: R.assert_frozen_templates(
        {"t2_choice_template_version": "DEPRECATED_NOT_USED"}), "deprecated key")
    expect_raises(lambda: R.assert_frozen_templates(
        {"t2_template_version": "T2.naturalness_pair.choice.v1"}), "choice template")
    expect_raises(lambda: R.assert_frozen_templates(
        {"t2_template_version": "T2.other.v1"}), "unknown template")
    # 3) actual main config is frozen and has no deprecated key
    main_cfg = json.loads((T14_ROOT / "runs" / "t14_main" / "config.json")
                          .read_text(encoding="utf-8"))
    assert "t2_choice_template_version" not in main_cfg
    assert main_cfg["t2_template_version"] == "T2.naturalness_pair.v1"
    R.assert_frozen_templates(main_cfg)
    # 4) main-path startup runs the guard
    runner = R.Runner(run_id="t14_main", execute=False, use_cache=False, limit=None)
    assert runner.config["t2_template_version"] == "T2.naturalness_pair.v1"
    # 5) no file under t14/runs carries the retired choice template string
    offenders = []
    for path in (T14_ROOT / "runs").rglob("*"):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "choice.v1" in text or "t2_choice_template_version" in text:
            offenders.append(str(path.relative_to(T14_ROOT)))
    assert not offenders, offenders
    # 6) quarantine is outside runs/ and retained
    quarantine = T14_ROOT / "quarantine"
    assert quarantine.exists()
    assert (quarantine / "t14_smoke_choice_v1").exists()
    assert (quarantine / "t14_dry_choice_v1").exists()
    print("J8 template guard test: PASS")


if __name__ == "__main__":
    main()
