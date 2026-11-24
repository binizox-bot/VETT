# B079 counterexamples

- accuracy: 0.6667 (48/72)
- task accuracy: 0.6389

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0165 | 2 | qwen2.5 | O | inn2.total_runs | 38 | 142 |
| match_0165 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 5 |
| match_0165 | 2 | llama3.1 | O | inn2.total_runs | 38 | 142 |
| match_0165 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 5 |
| match_0165 | 2 | gemma2 | O | inn2.total_runs | 38 | 142 |
| match_0165 | 2 | gemma2 | O | inn2.total_wickets | 10 | 5 |
| match_0165 | 2 | qwen2.5 | E | inn2.total_wickets | 10 | 6 |
| match_0165 | 2 | qwen2.5 | WI | inn2.total_runs | 38 | 151 |
| match_0165 | 2 | qwen2.5 | WI | inn2.total_wickets | 10 | 5 |
| match_0165 | 2 | llama3.1 | WI | inn2.total_runs | 38 | 142 |
| match_0165 | 2 | llama3.1 | WI | inn2.total_wickets | 10 | 5 |
| match_0165 | 2 | gemma2 | WI | inn2.total_runs | 38 | 142 |
| match_0165 | 2 | gemma2 | WI | inn2.total_wickets | 10 | 5 |
| match_0165 | 2 | qwen2.5 | OI | inn2.total_runs | 38 | 115 |
| match_0165 | 2 | qwen2.5 | OI | inn2.total_wickets | 10 | 5 |
| match_0165 | 2 | llama3.1 | OI | inn2.total_runs | 38 | 82 |
| match_0165 | 2 | llama3.1 | OI | inn2.total_wickets | 10 | 5 |
| match_0165 | 2 | gemma2 | OI | inn2.total_runs | 38 | 142 |
| match_0166 | 2 | qwen2.5 | O | inn2.total_runs | 32 | 91 |
| match_0166 | 2 | qwen2.5 | O | inn2.total_wickets | 0 | 9 |
| match_0166 | 2 | llama3.1 | O | inn2.total_runs | 32 | 91 |
| match_0166 | 2 | llama3.1 | O | inn2.total_wickets | 0 | 9 |
| match_0166 | 2 | gemma2 | O | inn2.total_runs | 32 | 91 |
| match_0166 | 2 | gemma2 | O | inn2.total_wickets | 0 | 9 |

## Paired

- E vs O: n=12 gain=5 loss=0 net=5
- OI vs O: n=12 gain=1 loss=0 net=1
- WI vs O: n=12 gain=0 loss=0 net=0
