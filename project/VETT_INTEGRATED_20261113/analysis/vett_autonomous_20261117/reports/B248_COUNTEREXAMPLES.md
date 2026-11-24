# B248 counterexamples

- accuracy: 0.7333 (176/240)
- task accuracy: 0.3125

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0008 | 2 | gemma2 | N1_F_partial | innings_total_wickets | 10 | 8 |
| match_0008 | 2 | gemma2 | N2_F_partial | innings_total_wickets | 10 | 8 |
| match_0010 | 2 | gemma2 | N1_F_partial | innings_total_wickets | 10 | 8 |
| match_0010 | 2 | gemma2 | N2_F_partial | Ryan Foster_wickets | 2 | 3 |
| match_0012 | 1 | gemma2 | N2_F_partial | Caleb Brooks_wickets | 3 | 4 |
| match_0012 | 1 | gemma2 | N2_F_partial | Lucas Vale_wickets | 3 | 2 |
| match_0015 | 2 | gemma2 | N2_F_partial | Noah Grant_wickets | 3 | 4 |
| match_0017 | 2 | gemma2 | N2_F_partial | Miles Carter_wickets | 4 | 5 |
| match_0026 | 2 | gemma2 | N1_F_partial | innings_total_wickets | 10 | 251 |
| match_0030 | 1 | gemma2 | N2_F_partial | Logan Vale_wickets | 3 | 4 |
| match_0003 | 1 | llama3.1 | N2_F_partial | Evan Clarke_wickets | 3 | 4 |
| match_0008 | 2 | llama3.1 | N1_F_partial | Luke Barrett_runs | 30 | 0 |
| match_0008 | 2 | llama3.1 | N1_F_partial | Ryan Frost_runs | 37 | 0 |
| match_0008 | 2 | llama3.1 | N2_F_partial | Luke Barrett_runs | 30 | 0 |
| match_0008 | 2 | llama3.1 | N2_F_partial | Ryan Frost_runs | 37 | 0 |
| match_0010 | 2 | llama3.1 | N1_F_partial | Ryan Foster_runs | 48 | 0 |
| match_0010 | 2 | llama3.1 | N1_F_partial | Evan Turner_runs | 38 | 0 |
| match_0010 | 2 | llama3.1 | N2_F_partial | Ryan Foster_wickets | 2 | 4 |
| match_0010 | 2 | llama3.1 | N2_F_partial | Ryan Foster_runs | 48 | 0 |
| match_0010 | 2 | llama3.1 | N2_F_partial | Evan Turner_runs | 38 | 0 |
| match_0012 | 1 | llama3.1 | N2_F_partial | Caleb Brooks_wickets | 3 | 5 |
| match_0015 | 2 | llama3.1 | N1_F_partial | Noah Grant_runs | 62 | 0 |
| match_0015 | 2 | llama3.1 | N1_F_partial | Caleb Rourke_runs | 41 | 74 |
| match_0015 | 2 | llama3.1 | N2_F_partial | Noah Grant_wickets | 3 | 6 |
| match_0015 | 2 | llama3.1 | N2_F_partial | Noah Grant_runs | 62 | 0 |
| match_0015 | 2 | llama3.1 | N2_F_partial | Caleb Rourke_wickets | 3 | 4 |
| match_0015 | 2 | llama3.1 | N2_F_partial | Caleb Rourke_runs | 41 | 0 |
| match_0017 | 2 | llama3.1 | N1_F_partial | Miles Carter_runs | 18 | 48 |
| match_0017 | 2 | llama3.1 | N2_F_partial | Miles Carter_wickets | 4 | 5 |
| match_0017 | 2 | llama3.1 | N2_F_partial | Miles Carter_runs | 18 | 48 |
| match_0026 | 2 | llama3.1 | N2_F_partial | Dylan Cole_wickets | 4 | 6 |
| match_0026 | 2 | llama3.1 | N2_F_partial | Dylan Cole_runs | 5 | 0 |
| match_0026 | 2 | llama3.1 | N2_F_partial | Ben Carter_runs | 5 | 0 |
| match_0030 | 1 | llama3.1 | N2_F_partial | Logan Vale_wickets | 3 | 4 |
| match_0003 | 1 | qwen2.5 | N2_F_partial | Evan Clarke_runs | 28 | None |
| match_0003 | 1 | qwen2.5 | N2_F_partial | Connor Reed_runs | 28 | None |
| match_0008 | 2 | qwen2.5 | N2_F_partial | Luke Barrett_wickets | 2 | 4 |
| match_0008 | 2 | qwen2.5 | N2_F_partial | Luke Barrett_runs | 30 | None |
| match_0008 | 2 | qwen2.5 | N2_F_partial | Ryan Frost_runs | 37 | None |
| match_0010 | 2 | qwen2.5 | N2_F_partial | Ryan Foster_runs | 48 | None |
| match_0010 | 2 | qwen2.5 | N2_F_partial | Evan Turner_wickets | 3 | 4 |
| match_0010 | 2 | qwen2.5 | N2_F_partial | Evan Turner_runs | 38 | None |
| match_0012 | 1 | qwen2.5 | N1_F_partial | Caleb Brooks_runs | 56 | None |
| match_0012 | 1 | qwen2.5 | N1_F_partial | Lucas Vale_runs | 44 | None |
| match_0012 | 1 | qwen2.5 | N2_F_partial | Caleb Brooks_wickets | 3 | 4 |
| match_0012 | 1 | qwen2.5 | N2_F_partial | Caleb Brooks_runs | 56 | None |
| match_0012 | 1 | qwen2.5 | N2_F_partial | Lucas Vale_runs | 44 | None |
| match_0015 | 2 | qwen2.5 | N1_F_partial | innings_total_wickets | 10 | 8 |
| match_0015 | 2 | qwen2.5 | N2_F_partial | Noah Grant_wickets | 3 | 4 |
| match_0015 | 2 | qwen2.5 | N2_F_partial | Noah Grant_runs | 62 | None |
| match_0015 | 2 | qwen2.5 | N2_F_partial | Caleb Rourke_runs | 41 | None |
| match_0017 | 2 | qwen2.5 | N2_F_partial | Miles Carter_wickets | 4 | 5 |
| match_0017 | 2 | qwen2.5 | N2_F_partial | Miles Carter_runs | 18 | None |
| match_0017 | 2 | qwen2.5 | N2_F_partial | Liam Brooks_wickets | 4 | 3 |
| match_0017 | 2 | qwen2.5 | N2_F_partial | Liam Brooks_runs | 27 | None |
| match_0026 | 2 | qwen2.5 | N1_F_partial | Dylan Cole_runs | 5 | None |
| match_0026 | 2 | qwen2.5 | N1_F_partial | Ben Carter_runs | 5 | None |
| match_0026 | 2 | qwen2.5 | N2_F_partial | Dylan Cole_runs | 5 | None |
| match_0026 | 2 | qwen2.5 | N2_F_partial | Ben Carter_runs | 5 | None |
| match_0030 | 1 | qwen2.5 | N1_F_partial | Logan Vale_runs | 10 | None |

## Paired

- N2_F_partial vs N1_F_partial: n=120 gain=3 loss=33 net=-30
