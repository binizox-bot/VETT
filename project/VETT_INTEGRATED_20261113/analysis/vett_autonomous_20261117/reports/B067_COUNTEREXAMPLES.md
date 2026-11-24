# B067 counterexamples

- accuracy: 0.381 (16/42)
- task accuracy: 0.2857

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0101 | 2 | qwen2.5 | O | inn2.total_runs | 111 | 142 |
| match_0101 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0101 | 2 | llama3.1 | O | inn2.total_runs | 111 | 142 |
| match_0101 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0101 | 2 | gemma2 | O | inn2.total_runs | 111 | 142 |
| match_0101 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0102 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 4 |
| match_0102 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 20 |
| match_0102 | 1 | qwen2.5 | E | inn1.total_runs | 118 | None |
| match_0102 | 1 | qwen2.5 | E | inn1.total_wickets | 10 | None |
| match_0102 | 1 | llama3.1 | E | inn1.total_runs | 118 | 121 |
| match_0102 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 4 |
| match_0102 | 1 | gemma2 | E | inn1.total_runs | 118 | 121 |
| match_0102 | 1 | gemma2 | E | inn1.total_wickets | 10 | 4 |
| match_0102 | 2 | qwen2.5 | O | inn2.total_runs | 121 | 118 |
| match_0102 | 2 | llama3.1 | O | inn2.total_runs | 121 | 118 |
| match_0102 | 2 | llama3.1 | O | inn2.total_wickets | 4 | 10 |
| match_0102 | 2 | gemma2 | O | inn2.total_runs | 121 | 118 |
| match_0102 | 2 | gemma2 | O | inn2.total_wickets | 4 | 10 |
| match_0102 | 2 | qwen2.5 | E | inn2.total_runs | 121 | None |
| match_0102 | 2 | qwen2.5 | E | inn2.total_wickets | 4 | None |
| match_0102 | 2 | qwen2.5 | OI | inn2.total_runs | 121 | 118 |
| match_0102 | 2 | llama3.1 | OI | inn2.total_runs | 121 | 118 |
| match_0102 | 2 | llama3.1 | OI | inn2.total_wickets | 4 | 20 |
| match_0102 | 2 | gemma2 | OI | inn2.total_runs | 121 | 118 |
| match_0102 | 2 | gemma2 | OI | inn2.total_wickets | 4 | 10 |

## Paired

- E vs O: n=12 gain=4 loss=5 net=-1
- OI vs O: n=6 gain=0 loss=0 net=0
