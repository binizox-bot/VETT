# B246 counterexamples

- accuracy: 0.7788 (243/312)
- task accuracy: 0.7583

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0003 | 1 | gemma2 | q1_batter | batter | Brandon Hale | None |
| match_0003 | 1 | gemma2 | q1_batter | batter | Brandon Hale | Evan Clarke |
| match_0008 | 2 | gemma2 | q1_batter | batter | Noah Brooks | Caleb Hayes |
| match_0008 | 2 | gemma2 | q1_batter | batter | Noah Brooks | Mason Reid |
| match_0010 | 2 | gemma2 | q1_batter | batter | Caleb Marsh | Isaac |
| match_0010 | 2 | gemma2 | q1_batter | batter | Caleb Marsh | Isaac |
| match_0017 | 2 | gemma2 | q1_batter | batter | Liam Reed | Cole Bennett |
| match_0017 | 2 | gemma2 | q1_batter | batter | Liam Reed | Cole Bennett |
| match_0026 | 2 | gemma2 | q1_batter | batter | Ryan Hale | Nathan |
| match_0026 | 2 | gemma2 | q2_original | original_bowler | Dylan Cole | Ryan Hale |
| match_0026 | 2 | gemma2 | q1_batter | batter | Ryan Hale | Nathan |
| match_0003 | 1 | llama3.1 | q1_batter | batter | Brandon Hale | Evan Clarke |
| match_0003 | 1 | llama3.1 | q1_batter | batter | Brandon Hale | Aiden Cole |
| match_0003 | 1 | llama3.1 | q4_old | Evan Clarke_wickets | 4 | 3 |
| match_0003 | 1 | llama3.1 | q4_old | Connor Reed_wickets | 1 | 2 |
| match_0008 | 2 | llama3.1 | q1_batter | batter | Noah Brooks | Mason Reid |
| match_0008 | 2 | llama3.1 | q1_batter | batter | Noah Brooks | Mason Reid |
| match_0008 | 2 | llama3.1 | q4_old | Luke Barrett_wickets | 3 | 2 |
| match_0008 | 2 | llama3.1 | q4_old | Ryan Frost_wickets | 3 | 4 |
| match_0010 | 2 | llama3.1 | q1_batter | batter | Caleb Marsh | Isaac |
| match_0010 | 2 | llama3.1 | q1_batter | batter | Caleb Marsh | Isaac |
| match_0010 | 2 | llama3.1 | q2_original | original_bowler | Ryan Foster | Evan Turner |
| match_0010 | 2 | llama3.1 | q4_old | Ryan Foster_wickets | 3 | 2 |
| match_0010 | 2 | llama3.1 | q4_old | Evan Turner_wickets | 2 | 3 |
| match_0012 | 1 | llama3.1 | q4_old | Caleb Brooks_wickets | 4 | 3 |
| match_0012 | 1 | llama3.1 | q4_old | Lucas Vale_wickets | 2 | 4 |
| match_0015 | 2 | llama3.1 | q4_old | Noah Grant_wickets | 4 | None |
| match_0015 | 2 | llama3.1 | q4_old | Caleb Rourke_wickets | 2 | None |
| match_0015 | 2 | llama3.1 | q2_original | original_bowler | Noah Grant | Caleb Rourke |
| match_0015 | 2 | llama3.1 | q4_old | Noah Grant_wickets | 4 | None |
| match_0015 | 2 | llama3.1 | q4_old | Caleb Rourke_wickets | 2 | None |
| match_0017 | 2 | llama3.1 | q1_batter | batter | Liam Reed | Miles Carter |
| match_0017 | 2 | llama3.1 | q1_batter | batter | Liam Reed | Cole Bennett |
| match_0017 | 2 | llama3.1 | q2_original | original_bowler | Miles Carter | Liam Brooks |
| match_0017 | 2 | llama3.1 | q4_old | Miles Carter_wickets | 5 | 4 |
| match_0017 | 2 | llama3.1 | q4_old | Liam Brooks_wickets | 3 | 2 |
| match_0026 | 2 | llama3.1 | q1_batter | batter | Ryan Hale | Nathan |
| match_0026 | 2 | llama3.1 | q1_batter | batter | Ryan Hale | Nathan |
| match_0026 | 2 | llama3.1 | q4_old | Dylan Cole_wickets | 5 | 4 |
| match_0026 | 2 | llama3.1 | q4_old | Ben Carter_wickets | 2 | 3 |
| match_0030 | 1 | llama3.1 | q2_original | original_bowler | Logan Vale | Owen Price |
| match_0030 | 1 | llama3.1 | q4_old | Logan Vale_wickets | 4 | None |
| match_0030 | 1 | llama3.1 | q4_old | Owen Price_wickets | 2 | None |
| match_0003 | 1 | qwen2.5 | q1_batter | batter | Brandon Hale | None |
| match_0003 | 1 | qwen2.5 | q1_batter | batter | Brandon Hale | Connor Reed |
| match_0003 | 1 | qwen2.5 | q4_old | Connor Reed_wickets | 1 | 2 |
| match_0008 | 2 | qwen2.5 | q1_batter | batter | Noah Brooks | None |
| match_0008 | 2 | qwen2.5 | q1_batter | batter | Noah Brooks | Luke Barrett |
| match_0008 | 2 | qwen2.5 | q4_old | Ryan Frost_wickets | 3 | 4 |
| match_0010 | 2 | qwen2.5 | q1_batter | batter | Caleb Marsh | None |
| match_0010 | 2 | qwen2.5 | q2_original | original_bowler | Ryan Foster | Isaac |
| match_0010 | 2 | qwen2.5 | q1_batter | batter | Caleb Marsh | Isaac |
| match_0012 | 1 | qwen2.5 | q1_batter | batter | Dylan Grant | None |
| match_0012 | 1 | qwen2.5 | q1_batter | batter | Dylan Grant | None |
| match_0015 | 2 | qwen2.5 | q1_batter | batter | Owen Hayes | None |
| match_0015 | 2 | qwen2.5 | q1_batter | batter | Owen Hayes | Caleb Rourke |
| match_0015 | 2 | qwen2.5 | q4_old | Caleb Rourke_wickets | 2 | 3 |
| match_0017 | 2 | qwen2.5 | q1_batter | batter | Liam Reed | Miles Carter |
| match_0017 | 2 | qwen2.5 | q1_batter | batter | Liam Reed | Cole Bennett |
| match_0017 | 2 | qwen2.5 | q4_old | Miles Carter_wickets | 5 | 4 |

## Paired

- q2_original vs q1_batter: n=0 gain=0 loss=0 net=0
- q3_final vs q1_batter: n=0 gain=0 loss=0 net=0
- q4_old vs q1_batter: n=0 gain=0 loss=0 net=0
