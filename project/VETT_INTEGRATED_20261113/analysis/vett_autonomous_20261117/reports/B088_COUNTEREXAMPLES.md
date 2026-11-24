# B088 counterexamples

- accuracy: 0.2083 (5/24)
- task accuracy: 0.0833

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0183 | 2 | qwen2.5 | O | inn2.total_runs | 101 | 306 |
| match_0183 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 7 |
| match_0183 | 2 | llama3.1 | O | inn2.total_runs | 101 | 306 |
| match_0183 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 7 |
| match_0183 | 2 | gemma2 | O | inn2.total_runs | 101 | 306 |
| match_0183 | 2 | gemma2 | O | inn2.total_wickets | 10 | 7 |
| match_0184 | 2 | qwen2.5 | O | inn2.total_runs | 73 | 72 |
| match_0184 | 2 | llama3.1 | O | inn2.total_runs | 73 | 72 |
| match_0184 | 2 | llama3.1 | O | inn2.total_wickets | 7 | 25 |
| match_0184 | 2 | gemma2 | O | inn2.total_runs | 73 | 72 |
| match_0184 | 2 | gemma2 | O | inn2.total_wickets | 7 | 10 |
| match_0185 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 4 |
| match_0185 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 9 |
| match_0185 | 2 | qwen2.5 | O | inn2.total_runs | 37 | 36 |
| match_0185 | 2 | qwen2.5 | O | inn2.total_wickets | 1 | 4 |
| match_0185 | 2 | llama3.1 | O | inn2.total_runs | 37 | 36 |
| match_0185 | 2 | llama3.1 | O | inn2.total_wickets | 1 | 9 |
| match_0185 | 2 | gemma2 | O | inn2.total_runs | 37 | 36 |
| match_0185 | 2 | gemma2 | O | inn2.total_wickets | 1 | 10 |

## Paired

- single-condition batch; no paired comparison
