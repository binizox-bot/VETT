# DSH 消费说明

1. 只读取 `model_inputs.jsonl`。每行的 `condition_code` 是不含语义的稳定代码；不要把 `private_gold.jsonl` 发送给模型。
2. 对每行分别运行三个冻结模型。保存 JSONL：`sample_id`、`model`、`raw_output`，可附 `model_digest`、decode、耗时和终止原因。
3. 模型/条件比较必须使用相同 model tag、digest、temperature、seed、context 和输出上限。期望矩阵为 5 个输入 × 3 模型 = 15 个原始回答。
4. 评分：`python score_frozen.py --predictions <raw.jsonl> --gold private_gold.jsonl --out <scores.jsonl>`。
5. 本目录已冻结。任何提示、别名、字段顺序或金标修改都必须新建版本目录。
