# B002 counterexamples

- accuracy: 0.8333 (10/12)
- task accuracy: 0.6667

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0002 | 2 | qwen2.5 | E | inn2.total_wickets | 10 | None |
| match_0002 | 2 | llama3.1 | E | inn2.total_wickets | 10 | 18.4 |

## Paired

- single-condition batch; no paired comparison
