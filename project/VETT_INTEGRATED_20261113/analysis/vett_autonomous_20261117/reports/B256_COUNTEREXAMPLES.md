# B256 counterexamples

- accuracy: 0.5104 (49/96)
- task accuracy: 0.3958

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0003 | 1 | gemma2 | q4_old_neutral_N2 | Evan Clarke_wickets | 4 | 3 |
| match_0003 | 1 | gemma2 | q4_old_neutral_N2 | Connor Reed_wickets | 1 | 2 |
| match_0008 | 2 | gemma2 | q4_old_neutral_N2 | Luke Barrett_wickets | 3 | 2 |
| match_0008 | 2 | gemma2 | q4_old_neutral_N2 | Ryan Frost_wickets | 3 | 4 |
| match_0010 | 2 | gemma2 | q4_old_neutral_N2 | Evan Turner_wickets | 2 | 3 |
| match_0012 | 1 | gemma2 | q4_old_neutral_N2 | Caleb Brooks_wickets | 4 | 3 |
| match_0012 | 1 | gemma2 | q4_old_neutral_N2 | Lucas Vale_wickets | 2 | 3 |
| match_0015 | 2 | gemma2 | q4_old_neutral_N2 | Caleb Rourke_wickets | 2 | 3 |
| match_0017 | 2 | gemma2 | q4_old_neutral_N2 | Miles Carter_wickets | 5 | 4 |
| match_0017 | 2 | gemma2 | q4_old_neutral_N2 | Liam Brooks_wickets | 3 | 4 |
| match_0026 | 2 | gemma2 | q4_old_neutral_N2 | Dylan Cole_wickets | 5 | 4 |
| match_0026 | 2 | gemma2 | q4_old_neutral_N2 | Ben Carter_wickets | 2 | 3 |
| match_0030 | 1 | gemma2 | q4_old_neutral_N2 | Logan Vale_wickets | 4 | 3 |
| match_0030 | 1 | gemma2 | q4_old_neutral_N2 | Owen Price_wickets | 2 | 3 |
| match_0008 | 2 | llama3.1 | q4_old_neutral_N2 | Luke Barrett_wickets | 3 | 2 |
| match_0008 | 2 | llama3.1 | q4_old_neutral_N2 | Ryan Frost_wickets | 3 | 4 |
| match_0010 | 2 | llama3.1 | q4_old_neutral_N2 | Ryan Foster_wickets | 3 | 2 |
| match_0010 | 2 | llama3.1 | q4_old_neutral_N2 | Evan Turner_wickets | 2 | 4 |
| match_0012 | 1 | llama3.1 | q4_old_neutral_N2 | Caleb Brooks_wickets | 4 | 3 |
| match_0012 | 1 | llama3.1 | q4_old_neutral_N2 | Lucas Vale_wickets | 2 | 3 |
| match_0012 | 1 | llama3.1 | q4_old_neutral_N2 | Caleb Brooks_wickets | 4 | 3 |
| match_0012 | 1 | llama3.1 | q4_old_neutral_N2 | Lucas Vale_wickets | 2 | 4 |
| match_0015 | 2 | llama3.1 | q4_old_neutral_N2 | Noah Grant_wickets | 4 | None |
| match_0015 | 2 | llama3.1 | q4_old_neutral_N2 | Caleb Rourke_wickets | 2 | None |
| match_0015 | 2 | llama3.1 | q4_old_neutral_N2 | Noah Grant_wickets | 4 | 3 |
| match_0015 | 2 | llama3.1 | q4_old_neutral_N2 | Caleb Rourke_wickets | 2 | 3 |
| match_0017 | 2 | llama3.1 | q4_old_neutral_N2 | Miles Carter_wickets | 5 | 4 |
| match_0017 | 2 | llama3.1 | q4_old_neutral_N2 | Liam Brooks_wickets | 3 | 4 |
| match_0026 | 2 | llama3.1 | q4_old_neutral_N2 | Ben Carter_wickets | 2 | 3 |
| match_0026 | 2 | llama3.1 | q4_old_neutral_N2 | Dylan Cole_wickets | 5 | 4 |
| match_0026 | 2 | llama3.1 | q4_old_neutral_N2 | Ben Carter_wickets | 2 | 3 |
| match_0030 | 1 | llama3.1 | q4_old_neutral_N2 | Logan Vale_wickets | 4 | None |
| match_0030 | 1 | llama3.1 | q4_old_neutral_N2 | Owen Price_wickets | 2 | None |
| match_0030 | 1 | llama3.1 | q4_old_neutral_N2 | Logan Vale_wickets | 4 | None |
| match_0030 | 1 | llama3.1 | q4_old_neutral_N2 | Owen Price_wickets | 2 | None |
| match_0003 | 1 | qwen2.5 | q4_old_neutral_N2 | Evan Clarke_wickets | 4 | 3 |
| match_0003 | 1 | qwen2.5 | q4_old_neutral_N2 | Connor Reed_wickets | 1 | 2 |
| match_0003 | 1 | qwen2.5 | q4_old_neutral_N2 | Connor Reed_wickets | 1 | 2 |
| match_0008 | 2 | qwen2.5 | q4_old_neutral_N2 | Ryan Frost_wickets | 3 | 4 |
| match_0008 | 2 | qwen2.5 | q4_old_neutral_N2 | Ryan Frost_wickets | 3 | 4 |
| match_0010 | 2 | qwen2.5 | q4_old_neutral_N2 | Evan Turner_wickets | 2 | 3 |
| match_0012 | 1 | qwen2.5 | q4_old_neutral_N2 | Caleb Brooks_wickets | 4 | None |
| match_0012 | 1 | qwen2.5 | q4_old_neutral_N2 | Lucas Vale_wickets | 2 | None |
| match_0015 | 2 | qwen2.5 | q4_old_neutral_N2 | Caleb Rourke_wickets | 2 | 3 |
| match_0015 | 2 | qwen2.5 | q4_old_neutral_N2 | Caleb Rourke_wickets | 2 | 3 |
| match_0026 | 2 | qwen2.5 | q4_old_neutral_N2 | Ben Carter_wickets | 2 | 3 |
| match_0030 | 1 | qwen2.5 | q4_old_neutral_N2 | Owen Price_wickets | 2 | 3 |

## Paired

- q4_old_neutral_N2_W vs q4_old_neutral_N2_F: n=0 gain=0 loss=0 net=0
