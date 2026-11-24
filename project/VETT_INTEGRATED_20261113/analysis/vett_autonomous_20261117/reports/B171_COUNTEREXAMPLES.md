# B171 counterexamples

- accuracy: 0.5833 (28/48)
- task accuracy: 0.5

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0168 | 2 | gemma2 | O | inn2.total_runs | 177 | 174 |
| match_0169 | 2 | gemma2 | O | inn2.total_runs | 116 | 292 |
| match_0169 | 2 | gemma2 | O | inn2.total_runs | 116 | 292 |
| match_0168 | 2 | llama3.1 | O | inn2.total_runs | 177 | 174 |
| match_0168 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 20 |
| match_0168 | 2 | llama3.1 | O | inn2.total_runs | 177 | 174 |
| match_0168 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 46.2 |
| match_0169 | 1 | llama3.1 | O | inn1.total_wickets | 10 | None |
| match_0169 | 2 | llama3.1 | O | inn2.total_runs | 116 | 292 |
| match_0169 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 116 |
| match_0169 | 2 | llama3.1 | O | inn2.total_runs | 116 | 292 |
| match_0170 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 183 |
| match_0168 | 2 | qwen2.5 | O | inn2.total_runs | 177 | 174 |
| match_0168 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 10 |
| match_0168 | 2 | qwen2.5 | O | inn2.total_runs | 177 | 174 |
| match_0168 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 7 |
| match_0169 | 2 | qwen2.5 | O | inn2.total_runs | 116 | 292 |
| match_0169 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 11 |
| match_0169 | 2 | qwen2.5 | O | inn2.total_runs | 116 | 292 |
| match_0170 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 8 |

## Paired

- single-condition batch; no paired comparison

## Parse failures

- match_0169 llama3.1 O
