# B255 counterexamples

- accuracy: 0.4921 (31/63)
- task accuracy: 0.4921

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0008 | 2 | gemma2 | T2_N0 | bowlers | ['Luke Barrett', 'Ryan Frost'] | ['Ryan Frost', 'Luke Barrett'] |
| match_0008 | 2 | gemma2 | T2_N1 | bowlers | ['Luke Barrett', 'Ryan Frost'] | ['Dylan Price', 'Aaron Wells'] |
| match_0008 | 2 | gemma2 | T2_N2 | bowlers | ['Ryan Frost', 'Evan Reed'] | ['Ryan Frost', 'Luke Barrett'] |
| match_0010 | 2 | gemma2 | T2_N2 | bowlers | ['Evan Turner', 'Luke Barrett'] | ['Aaron Vale', 'Ryan Foster'] |
| match_0012 | 1 | gemma2 | T2_N2 | bowlers | ['Lucas Vale', 'Caleb Brooks'] | ['Caleb Brooks', 'Lucas Vale'] |
| match_0015 | 2 | gemma2 | T2_N1 | bowlers | ['Noah Grant', 'Caleb Rourke'] | ['Caleb Rourke', 'Noah Grant'] |
| match_0030 | 1 | gemma2 | T2_N2 | bowlers | ['Owen Price', 'Logan Vale'] | ['Logan Vale', 'Owen Price'] |
| match_0008 | 2 | llama3.1 | T2_N0 | bowlers | ['Luke Barrett', 'Ryan Frost'] | ['Dylan Price', 'Aaron Wells'] |
| match_0008 | 2 | llama3.1 | T2_N1 | bowlers | ['Luke Barrett', 'Ryan Frost'] | ['Dylan Price', 'Aaron Wells'] |
| match_0008 | 2 | llama3.1 | T2_N2 | bowlers | ['Ryan Frost', 'Evan Reed'] | ['Dylan Price', 'Aaron Wells'] |
| match_0010 | 2 | llama3.1 | T2_N0 | bowlers | ['Ryan Foster', 'Evan Turner'] | ['Ryan Foster', 'Luke Barrett'] |
| match_0010 | 2 | llama3.1 | T2_N1 | bowlers | ['Ryan Foster', 'Evan Turner'] | ['Ryan Foster', 'Luke Barrett'] |
| match_0010 | 2 | llama3.1 | T2_N2 | bowlers | ['Evan Turner', 'Luke Barrett'] | ['Aaron Vale', 'Ryan Foster'] |
| match_0012 | 1 | llama3.1 | T2_N2 | bowlers | ['Lucas Vale', 'Caleb Brooks'] | ['Caleb Brooks', 'Lucas Vale'] |
| match_0015 | 2 | llama3.1 | T2_N0 | bowlers | ['Noah Grant', 'Caleb Rourke'] | ['Caleb Rourke', 'Noah Grant'] |
| match_0015 | 2 | llama3.1 | T2_N1 | bowlers | ['Noah Grant', 'Caleb Rourke'] | ['Caleb Rourke', 'Noah Grant'] |
| match_0030 | 1 | llama3.1 | T2_N0 | bowlers | ['Logan Vale', 'Owen Price'] | ['Connor Blake', 'Logan Vale'] |
| match_0030 | 1 | llama3.1 | T2_N1 | bowlers | ['Logan Vale', 'Owen Price'] | ['Connor Blake', 'Logan Vale'] |
| match_0030 | 1 | llama3.1 | T2_N2 | bowlers | ['Owen Price', 'Logan Vale'] | ['Logan Vale', 'Connor Blake'] |
| match_0008 | 2 | qwen2.5 | T2_N0 | bowlers | ['Luke Barrett', 'Ryan Frost'] | ['Dylan Price', 'Aaron Wells'] |
| match_0008 | 2 | qwen2.5 | T2_N1 | bowlers | ['Luke Barrett', 'Ryan Frost'] | ['Dylan Price', 'Aaron Wells'] |
| match_0008 | 2 | qwen2.5 | T2_N2 | bowlers | ['Ryan Frost', 'Evan Reed'] | ['Dylan Price', 'Aaron Wells'] |
| match_0010 | 2 | qwen2.5 | T2_N1 | bowlers | ['Ryan Foster', 'Evan Turner'] | ['Ryan Foster', 'Mason Hart'] |
| match_0010 | 2 | qwen2.5 | T2_N2 | bowlers | ['Evan Turner', 'Luke Barrett'] | ['Evan Turner', 'Ryan Foster'] |
| match_0012 | 1 | qwen2.5 | T2_N1 | bowlers | ['Caleb Brooks', 'Lucas Vale'] | ['Liam Frost', 'Caleb Brooks'] |
| match_0015 | 2 | qwen2.5 | T2_N1 | bowlers | ['Noah Grant', 'Caleb Rourke'] | ['Caleb Rourke', 'Noah Grant'] |
| match_0017 | 2 | qwen2.5 | T2_N2 | bowlers | ['Miles Carter', 'Liam Brooks'] | ['Liam Brooks', 'Miles Carter'] |
| match_0026 | 2 | qwen2.5 | T2_N1 | bowlers | ['Dylan Cole', 'Ben Carter'] | ['Nathan Wells', 'Leo Marsh'] |
| match_0026 | 2 | qwen2.5 | T2_N2 | bowlers | ['Dylan Cole', 'Ben Carter'] | ['Ben Carter', 'Dylan Cole'] |
| match_0030 | 1 | qwen2.5 | T2_N0 | bowlers | ['Logan Vale', 'Owen Price'] | ['Connor Blake', 'Logan Vale'] |
| match_0030 | 1 | qwen2.5 | T2_N1 | bowlers | ['Logan Vale', 'Owen Price'] | ['Connor Blake', 'Logan Vale'] |
| match_0030 | 1 | qwen2.5 | T2_N2 | bowlers | ['Owen Price', 'Logan Vale'] | ['Connor Blake', 'Logan Vale'] |

## Paired

- T2_N1 vs T2_N0: n=21 gain=0 loss=5 net=-5
- T2_N2 vs T2_N0: n=21 gain=1 loss=7 net=-6
