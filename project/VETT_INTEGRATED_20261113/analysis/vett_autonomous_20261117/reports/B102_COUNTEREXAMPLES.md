# B102 counterexamples

- accuracy: 0.5 (39/78)
- task accuracy: 0.4359

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0212 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 4 |
| match_0212 | 2 | qwen2.5 | O | inn2.total_runs | 109 | 106 |
| match_0212 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 10 |
| match_0212 | 2 | llama3.1 | O | inn2.total_runs | 109 | 106 |
| match_0212 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 10 |
| match_0212 | 2 | gemma2 | O | inn2.total_runs | 109 | 106 |
| match_0212 | 2 | gemma2 | O | inn2.total_wickets | 3 | 10 |
| match_0212 | 2 | qwen2.5 | WI | inn2.total_runs | 109 | 106 |
| match_0212 | 2 | qwen2.5 | WI | inn2.total_wickets | 3 | 10 |
| match_0212 | 2 | llama3.1 | WI | inn2.total_runs | 109 | 106 |
| match_0212 | 2 | llama3.1 | WI | inn2.total_wickets | 3 | 10 |
| match_0212 | 2 | gemma2 | WI | inn2.total_runs | 109 | 106 |
| match_0212 | 2 | gemma2 | WI | inn2.total_wickets | 3 | 10 |
| match_0212 | 2 | qwen2.5 | OI | inn2.total_runs | 109 | 106 |
| match_0212 | 2 | qwen2.5 | OI | inn2.total_wickets | 3 | 10 |
| match_0212 | 2 | llama3.1 | OI | inn2.total_runs | 109 | 106 |
| match_0212 | 2 | llama3.1 | OI | inn2.total_wickets | 3 | 10 |
| match_0212 | 2 | gemma2 | OI | inn2.total_runs | 109 | 106 |
| match_0212 | 2 | gemma2 | OI | inn2.total_wickets | 3 | 10 |
| match_0213 | 2 | qwen2.5 | O | inn2.total_runs | 114 | 272 |
| match_0213 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0213 | 2 | llama3.1 | O | inn2.total_runs | 114 | 272 |
| match_0213 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0213 | 2 | gemma2 | O | inn2.total_runs | 114 | 272 |
| match_0213 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0213 | 2 | qwen2.5 | E | inn2.total_runs | 114 | None |
| match_0213 | 2 | qwen2.5 | E | inn2.total_wickets | 10 | None |
| match_0213 | 2 | llama3.1 | E | inn2.total_wickets | 10 | 34.2 |
| match_0213 | 2 | gemma2 | E | inn2.total_wickets | 10 | None |
| match_0213 | 2 | qwen2.5 | WI | inn2.total_runs | 114 | 272 |
| match_0213 | 2 | qwen2.5 | WI | inn2.total_wickets | 10 | 8 |
| match_0213 | 2 | llama3.1 | WI | inn2.total_runs | 114 | 272 |
| match_0213 | 2 | llama3.1 | WI | inn2.total_wickets | 10 | 8 |
| match_0213 | 2 | gemma2 | WI | inn2.total_runs | 114 | 272 |
| match_0213 | 2 | gemma2 | WI | inn2.total_wickets | 10 | 8 |
| match_0213 | 2 | qwen2.5 | OI | inn2.total_runs | 114 | 212 |
| match_0213 | 2 | qwen2.5 | OI | inn2.total_wickets | 10 | 8 |
| match_0213 | 2 | llama3.1 | OI | inn2.total_runs | 114 | 273 |
| match_0213 | 2 | gemma2 | OI | inn2.total_runs | 114 | 273 |

## Paired

- E vs O: n=18 gain=8 loss=0 net=8
- OI vs O: n=18 gain=2 loss=0 net=2
- WI vs O: n=18 gain=0 loss=0 net=0
