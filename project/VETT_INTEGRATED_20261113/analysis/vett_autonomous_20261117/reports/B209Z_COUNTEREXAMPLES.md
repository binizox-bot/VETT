# B209Z counterexamples

- accuracy: 0.8021 (77/96)
- task accuracy: 0.5714

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0003 | 1 | gemma2 | C_no_notice_full | Evan Clarke_wickets | 4 | 3 |
| match_0003 | 1 | gemma2 | C_no_notice_full | Connor Reed_wickets | 1 | 2 |
| match_0003 | 1 | gemma2 | C_no_notice_full | innings_total_wickets | 8 | 7 |
| match_0003 | 1 | gemma2 | C_maintain_full | Evan Clarke_wickets | 4 | 3 |
| match_0003 | 1 | gemma2 | C_maintain_full | Connor Reed_wickets | 1 | 2 |
| match_0003 | 1 | gemma2 | C_maintain_full | innings_total_wickets | 8 | 7 |
| match_0003 | 1 | gemma2 | C_change_full | innings_total_wickets | 8 | 10 |
| match_0003 | 1 | llama3.1 | C_no_notice_full | Evan Clarke_wickets | 4 | 3 |
| match_0003 | 1 | llama3.1 | C_no_notice_full | Connor Reed_wickets | 1 | 2 |
| match_0003 | 1 | llama3.1 | C_no_notice_full | innings_total_wickets | 8 | 164 |
| match_0003 | 1 | llama3.1 | C_maintain_full | Evan Clarke_wickets | 4 | 3 |
| match_0003 | 1 | llama3.1 | C_maintain_full | Connor Reed_wickets | 1 | 2 |
| match_0003 | 1 | llama3.1 | C_maintain_full | innings_total_wickets | 8 | 164 |
| match_0003 | 1 | llama3.1 | C_change_full | innings_total_wickets | 8 | 164 |
| match_0003 | 1 | qwen2.5 | C_no_notice_full | Evan Clarke_wickets | 4 | 3 |
| match_0003 | 1 | qwen2.5 | C_no_notice_full | Connor Reed_wickets | 1 | 2 |
| match_0003 | 1 | qwen2.5 | C_maintain_full | Evan Clarke_wickets | 4 | 3 |
| match_0003 | 1 | qwen2.5 | C_maintain_full | Connor Reed_wickets | 1 | 2 |
| match_0003 | 1 | qwen2.5 | C_change_full | innings_total_wickets | 8 | 7 |

## Paired

- C_change_window vs C_change_full: n=15 gain=3 loss=0 net=3
- C_maintain_full vs C_change_full: n=15 gain=1 loss=6 net=-5
- C_maintain_window vs C_change_full: n=15 gain=3 loss=0 net=3
- C_no_notice_full vs C_change_full: n=15 gain=1 loss=6 net=-5
- C_no_notice_window vs C_change_full: n=15 gain=3 loss=0 net=3
- X_full vs C_change_full: n=0 gain=0 loss=0 net=0
- X_window vs C_change_full: n=0 gain=0 loss=0 net=0
