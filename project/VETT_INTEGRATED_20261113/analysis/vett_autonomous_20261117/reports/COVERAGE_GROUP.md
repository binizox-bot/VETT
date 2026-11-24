# Coverage group report (separate from diagnostic group)

- generated: 2026-11-18T15:51:41+08:00
- sweep results: 426
- sweep cells: 852
- sweep accuracy: 0.6819
- diagnostic cells: 669; accuracy: 0.6816

## By condition

- E: 206/216 = 0.9537
- O: 262/480 = 0.5458
- OI: 80/108 = 0.7407
- WI: 33/48 = 0.6875

## By model

- gemma2:9b: 204/284 = 0.7183
- llama3.1:8b: 197/284 = 0.6937
- qwen2.5:7b-instruct-q4_K_M: 180/284 = 0.6338

## Worst roots (>=6 cells)

- match_0020: 5/12 = 0.4167
- match_0030: 5/12 = 0.4167
- match_0041: 5/12 = 0.4167
- match_0022: 6/12 = 0.5
- match_0023: 6/12 = 0.5
- match_0024: 6/12 = 0.5
- match_0025: 6/12 = 0.5
- match_0026: 6/12 = 0.5
- match_0027: 6/12 = 0.5
- match_0028: 6/12 = 0.5
- match_0029: 6/12 = 0.5
- match_0031: 6/12 = 0.5

## Note

- This is a coverage group, not a hard-case group; do not merge its rate with B002–B022.
- E/O/OI/WI availability differs by root, so condition rates are not balanced samples.
