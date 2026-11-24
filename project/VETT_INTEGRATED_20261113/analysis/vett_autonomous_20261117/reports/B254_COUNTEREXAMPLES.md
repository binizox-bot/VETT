# B254 counterexamples

- accuracy: 0.6667 (6/9)
- task accuracy: 0.6667

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0003 | 1 | llama3.1 | T2_N0 | bowlers | ['Evan Clarke', 'Connor Reed'] | ['Evan Clarke', 'Isaac Wells'] |
| match_0003 | 1 | llama3.1 | T2_N1 | bowlers | ['Evan Clarke', 'Connor Reed'] | ['Evan Clarke', 'Isaac Wells'] |
| match_0003 | 1 | llama3.1 | T2_N2 | bowlers | ['Evan Clarke', 'Connor Reed'] | ['Evan Clarke', 'Isaac Wells'] |

## Paired

- T2_N1 vs T2_N0: n=3 gain=0 loss=0 net=0
- T2_N2 vs T2_N0: n=3 gain=0 loss=0 net=0
