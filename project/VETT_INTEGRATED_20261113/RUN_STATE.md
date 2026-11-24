# RUN_STATE（2026-11-13 19:25）

## 完成
- H1、闭合审计、pilot10、预注册。
- pilot 实验：qwen/llama × direct/closure/guided × 8 变体 + oracle 诊断，约 700 次本地调用，¥0。
- 结果文档：PILOT_RESULTS.md；论文骨架：PAPER_SKELETON.md。

## 三个核心发现
1. 换序 对→错 17–29%（重测 0/294）。
2. 缺证 UNKNOWN 正确率 0（100% 编造）。
3. closure 只修账不补抽取（hard 修订 0.529=0.529）；oracle 证据反而更差 → 瓶颈在聚合/状态维护。

## 未完成
- panel_v2 完整 320×3（停在 qwen 182/320；已主动停止，重跑 `python scripts/panel_v2.py` 可续）。
- gemma2 pilot。
- 事件级账本实现（若决定升级 RQ3）。
- 30 场扩展。

## 决策点（需用户）
- RQ3：升级事件账本 vs 收窄为“闭合修复边界”负结果。
- V4.1 Flash 预算上限（是否跑 60 次强模型锚点）。
- 人工可读性标注。
