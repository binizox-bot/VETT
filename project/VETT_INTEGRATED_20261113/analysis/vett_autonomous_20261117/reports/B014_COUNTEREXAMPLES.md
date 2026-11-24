# B014 counterexamples

- accuracy: 0.8333 (10/12)
- task accuracy: 0.6667

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0184 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 7 |
| match_0184 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 25 |

## Paired

- single-condition batch; no paired comparison
