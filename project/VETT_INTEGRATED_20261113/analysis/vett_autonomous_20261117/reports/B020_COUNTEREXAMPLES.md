# B020 counterexamples

- accuracy: 0.7708 (37/48)
- task accuracy: 0.75

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0009 | 2 | qwen2.5 | OI | inn2.total_runs | 187 | 185 |
| match_0009 | 2 | qwen2.5 | OI | inn2.total_wickets | 5 | 8 |
| match_0009 | 2 | llama3.1 | OI | inn2.total_runs | 187 | 185 |
| match_0009 | 2 | llama3.1 | OI | inn2.total_wickets | 5 | 10 |
| match_0009 | 2 | gemma2 | OI | inn2.total_runs | 187 | 185 |
| match_0009 | 2 | gemma2 | OI | inn2.total_wickets | 5 | 10 |
| match_0011 | 2 | qwen2.5 | OI | inn2.total_runs | 132 | 179 |
| match_0011 | 2 | qwen2.5 | OI | inn2.total_wickets | 6 | 10 |
| match_0011 | 2 | llama3.1 | OI | inn2.total_runs | 132 | 179 |
| match_0011 | 2 | gemma2 | OI | inn2.total_runs | 132 | 265 |
| match_0011 | 2 | gemma2 | OI | inn2.total_wickets | 6 | 10 |

## Paired

- E vs O: n=12 gain=0 loss=0 net=0
- OI vs O: n=0 gain=0 loss=0 net=0
