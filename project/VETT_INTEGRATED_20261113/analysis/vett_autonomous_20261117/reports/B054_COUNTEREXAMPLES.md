# B054 counterexamples

- accuracy: 0.5333 (16/30)
- task accuracy: 0.4667

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0075 | 2 | qwen2.5 | O | inn2.total_runs | 116 | 246 |
| match_0075 | 2 | qwen2.5 | O | inn2.total_wickets | 6 | 9 |
| match_0075 | 2 | llama3.1 | O | inn2.total_runs | 116 | 246 |
| match_0075 | 2 | llama3.1 | O | inn2.total_wickets | 6 | 9 |
| match_0075 | 2 | gemma2 | O | inn2.total_runs | 116 | 246 |
| match_0075 | 2 | gemma2 | O | inn2.total_wickets | 6 | 9 |
| match_0076 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 9 |
| match_0076 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 9 |
| match_0076 | 2 | qwen2.5 | O | inn2.total_runs | 182 | 181 |
| match_0076 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 10 |
| match_0076 | 2 | llama3.1 | O | inn2.total_runs | 182 | 181 |
| match_0076 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 9 |
| match_0076 | 2 | gemma2 | O | inn2.total_runs | 182 | 181 |
| match_0076 | 2 | gemma2 | O | inn2.total_wickets | 3 | 10 |

## Paired

- E vs O: n=6 gain=0 loss=0 net=0
