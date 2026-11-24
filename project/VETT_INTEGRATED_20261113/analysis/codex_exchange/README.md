# Codex exchange v1

DSH writes Ollama and workflow.db; Codex reads sealed material and returns score corrections.

1. Codex freezes a manifest (sample ids + prompt hashes + model config).
2. DSH integrates at the next batch boundary, reuses verifiable historical results.
3. DSH seals each finished batch here (tasks, raw answers, request metadata, scores).
4. Codex recomputes offline; DSH re-runs only if model input was wrong or a matching condition is missing.

Layout:
- MANIFEST_v1.json: protocol, models, 8 events, pilot design, file hashes.
- SEALED_B019_B022/: 72 adjudication tasks with exact prompts, raw answers, scores.
- PUBLISHED_D_RUNS/: O/M/E run rows; prompts must be rebuilt and hash-checked.
- PILOT_B209Z/: exact prompts for the 24-request two-match pilot.
