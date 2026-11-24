# B019 counterexamples

- accuracy: 0.9778 (176/180)
- task accuracy: 0.8889

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0003 | 1 | qwen2.5 | C_change | Evan Clarke_wickets | 3 | 4 |
| match_0017 | 1 | qwen2.5 | C_change | Liam Brooks_wickets | 4 | 6 |
| match_0026 | 1 | qwen2.5 | C_change | Ben Carter_wickets | 3 | 4 |
| match_0026 | 1 | llama3.1 | C_change | Ben Carter_wickets | 3 | 4 |

## Paired

- C_maintain vs C_change: n=60 gain=4 loss=0 net=4
- C_no_notice vs C_change: n=60 gain=4 loss=0 net=4
