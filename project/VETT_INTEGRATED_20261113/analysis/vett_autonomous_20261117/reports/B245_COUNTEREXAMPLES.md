# B245 counterexamples

- accuracy: 0.6562 (63/96)
- task accuracy: 0.5694

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0003 | 1 | gemma2 | q1_batter | batter | Brandon Hale | Gareth Bishop |
| match_0008 | 2 | gemma2 | q1_batter | batter | Noah Brooks | Dylan Price |
| match_0008 | 2 | gemma2 | q2_original | original_bowler | Luke Barrett | Dylan Price |
| match_0010 | 2 | gemma2 | q1_batter | batter | Caleb Marsh | Aiden Price |
| match_0012 | 1 | gemma2 | q1_batter | batter | Dylan Grant | Mason Clarke |
| match_0015 | 2 | gemma2 | q1_batter | batter | Owen Hayes | Luca Barrett |
| match_0015 | 2 | gemma2 | q2_original | original_bowler | Noah Grant | Evan Turner |
| match_0017 | 2 | gemma2 | q1_batter | batter | Liam Reed | Miles Carter |
| match_0026 | 2 | gemma2 | q1_batter | batter | Ryan Hale | Leo Marsh |
| match_0030 | 1 | gemma2 | q1_batter | batter | Ben Carter | Evan Reid |
| match_0003 | 1 | llama3.1 | q1_batter | batter | Brandon Hale | Marcus Drake |
| match_0008 | 2 | llama3.1 | q1_batter | batter | Noah Brooks | Lucas Hart |
| match_0010 | 2 | llama3.1 | q1_batter | batter | Caleb Marsh | Aaron Vale |
| match_0012 | 1 | llama3.1 | q1_batter | batter | Dylan Grant | Adrian Stone |
| match_0015 | 2 | llama3.1 | q1_batter | batter | Owen Hayes | Toby Grant |
| match_0015 | 2 | llama3.1 | q4_old | Noah Grant_wickets | 4 | None |
| match_0015 | 2 | llama3.1 | q4_old | Caleb Rourke_wickets | 2 | None |
| match_0017 | 2 | llama3.1 | q1_batter | batter | Liam Reed | Miles Carter |
| match_0026 | 2 | llama3.1 | q1_batter | batter | Ryan Hale | Milo Grant |
| match_0030 | 1 | llama3.1 | q1_batter | batter | Ben Carter | Leo Turner |
| match_0030 | 1 | llama3.1 | q2_original | original_bowler | Logan Vale | Connor Blake |
| match_0030 | 1 | llama3.1 | q4_old | Logan Vale_wickets | 4 | None |
| match_0030 | 1 | llama3.1 | q4_old | Owen Price_wickets | 2 | None |
| match_0003 | 1 | qwen2.5 | q1_batter | batter | Brandon Hale | Aiden Cole |
| match_0008 | 2 | qwen2.5 | q1_batter | batter | Noah Brooks | Evan Price |
| match_0008 | 2 | qwen2.5 | q2_original | original_bowler | Luke Barrett | Dylan Price |
| match_0010 | 2 | qwen2.5 | q1_batter | batter | Caleb Marsh | Aaron Vale |
| match_0012 | 1 | qwen2.5 | q1_batter | batter | Dylan Grant | Caleb Brooks |
| match_0015 | 2 | qwen2.5 | q1_batter | batter | Owen Hayes | Bennett |
| match_0017 | 2 | qwen2.5 | q1_batter | batter | Liam Reed | Miles Carter |
| match_0026 | 2 | qwen2.5 | q1_batter | batter | Ryan Hale | Leo Marsh |
| match_0030 | 1 | qwen2.5 | q1_batter | batter | Ben Carter | Connor |
| match_0030 | 1 | qwen2.5 | q2_original | original_bowler | Logan Vale | Connor Blake |

## Paired

- q2_original vs q1_batter: n=0 gain=0 loss=0 net=0
- q4_old vs q1_batter: n=0 gain=0 loss=0 net=0
