# B097 counterexamples

- accuracy: 0.5417 (13/24)
- task accuracy: 0.4167

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0202 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 5 |
| match_0202 | 2 | qwen2.5 | O | inn2.total_runs | 183 | 182 |
| match_0202 | 2 | qwen2.5 | O | inn2.total_wickets | 6 | 5 |
| match_0202 | 2 | gemma2 | O | inn2.total_runs | 183 | 182 |
| match_0202 | 2 | gemma2 | O | inn2.total_wickets | 6 | 10 |
| match_0203 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 5 |
| match_0203 | 2 | qwen2.5 | O | inn2.total_runs | 176 | 174 |
| match_0203 | 2 | llama3.1 | O | inn2.total_runs | 176 | 174 |
| match_0203 | 2 | llama3.1 | O | inn2.total_wickets | 5 | 10 |
| match_0203 | 2 | gemma2 | O | inn2.total_runs | 176 | 174 |
| match_0203 | 2 | gemma2 | O | inn2.total_wickets | 5 | 10 |

## Paired

- single-condition batch; no paired comparison
