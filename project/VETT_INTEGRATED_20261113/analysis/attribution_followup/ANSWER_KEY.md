# ANSWER_KEY：改判样本金标

## match_0003 — inn1 — Brandon Hale

| 字段 | 值 |
|---|---:|
| Evan Clarke_wickets | 3 |
| Evan Clarke_runs | 28 |
| Connor Reed_wickets | 2 |
| Connor Reed_runs | 28 |
| innings_total_wickets | 8 |

- 旧改判句：Brandon Hale fell to Evan Clarke
- 新改判句：Brandon Hale fell to Connor Reed
- 旧汇总 A：Evan Clarke, whose 4 for 28；旧汇总 B：Connor Reed kept the pressure on with 1 for 28
- 通知：Match review: the dismissal of Brandon Hale in the first innings was reassigned from Evan Clarke to Connor Reed.

## match_0008 — inn2 — Noah Brooks

| 字段 | 值 |
|---|---:|
| Luke Barrett_wickets | 2 |
| Luke Barrett_runs | 30 |
| Ryan Frost_wickets | 4 |
| Ryan Frost_runs | 37 |
| innings_total_wickets | 10 |

- 旧改判句：Noah Brooks fell to Luke Barrett
- 新改判句：Noah Brooks fell to Ryan Frost
- 旧汇总 A：Luke Barrett, whose 3 for 30；旧汇总 B：Ryan Frost kept the pressure on with 3 for 37
- 通知：Scorers' correction: Noah Brooks's dismissal, originally credited to Luke Barrett, now belongs to Ryan Frost.

## match_0010 — inn2 — Caleb Marsh

| 字段 | 值 |
|---|---:|
| Ryan Foster_wickets | 2 |
| Ryan Foster_runs | 48 |
| Evan Turner_wickets | 3 |
| Evan Turner_runs | 38 |
| innings_total_wickets | 10 |

- 旧改判句：Caleb Marsh fell to Ryan Foster
- 新改判句：Caleb Marsh fell to Evan Turner
- 旧汇总 A：Ryan Foster, whose 3 for 48；旧汇总 B：Evan Turner kept the pressure on with 2 for 38
- 通知：The review panel moved Caleb Marsh's dismissal from Ryan Foster to Evan Turner.

## match_0012 — inn1 — Dylan Grant

| 字段 | 值 |
|---|---:|
| Caleb Brooks_wickets | 3 |
| Caleb Brooks_runs | 56 |
| Lucas Vale_wickets | 3 |
| Lucas Vale_runs | 44 |
| innings_total_wickets | 10 |

- 旧改判句：Dylan Grant fell to Caleb Brooks
- 新改判句：Dylan Grant fell to Lucas Vale
- 旧汇总 A：Caleb Brooks, whose 4 for 56；旧汇总 B：Lucas Vale kept the pressure on with 2 for 44
- 通知：Match review: the dismissal of Dylan Grant in the first innings was reassigned from Caleb Brooks to Lucas Vale.

## match_0015 — inn2 — Owen Hayes

| 字段 | 值 |
|---|---:|
| Noah Grant_wickets | 3 |
| Noah Grant_runs | 62 |
| Caleb Rourke_wickets | 3 |
| Caleb Rourke_runs | 41 |
| innings_total_wickets | 10 |

- 旧改判句：Owen Hayes fell to Noah Grant
- 新改判句：Owen Hayes fell to Caleb Rourke
- 旧汇总 A：Noah Grant, whose 4 for 62；旧汇总 B：Caleb Rourke kept the pressure on with 2 for 41
- 通知：Scorers' correction: Owen Hayes's dismissal, originally credited to Noah Grant, now belongs to Caleb Rourke.

## match_0017 — inn2 — Liam Reed

| 字段 | 值 |
|---|---:|
| Miles Carter_wickets | 4 |
| Miles Carter_runs | 18 |
| Liam Brooks_wickets | 4 |
| Liam Brooks_runs | 27 |
| innings_total_wickets | 10 |

- 旧改判句：Liam Reed fell to Miles Carter
- 新改判句：Liam Reed fell to Liam Brooks
- 旧汇总 A：Miles Carter, whose 5 for 18；旧汇总 B：Liam Brooks kept the pressure on with 3 for 27
- 通知：The review panel moved Liam Reed's dismissal from Miles Carter to Liam Brooks.

## match_0026 — inn2 — Ryan Hale

| 字段 | 值 |
|---|---:|
| Dylan Cole_wickets | 4 |
| Dylan Cole_runs | 5 |
| Ben Carter_wickets | 3 |
| Ben Carter_runs | 5 |
| innings_total_wickets | 10 |

- 旧改判句：Ryan Hale fell to Dylan Cole
- 新改判句：Ryan Hale fell to Ben Carter
- 旧汇总 A：Dylan Cole, whose 5 for 5；旧汇总 B：Ben Carter kept the pressure on with 2 for 5
- 通知：Match review: the dismissal of Ryan Hale in the second innings was reassigned from Dylan Cole to Ben Carter.

## match_0030 — inn1 — Ben Carter

| 字段 | 值 |
|---|---:|
| Logan Vale_wickets | 3 |
| Logan Vale_runs | 10 |
| Owen Price_wickets | 3 |
| Owen Price_runs | 1 |
| innings_total_wickets | 10 |

- 旧改判句：Ben Carter fell to Logan Vale
- 新改判句：Ben Carter fell to Owen Price
- 旧汇总 A：Logan Vale, whose 4 for 10；旧汇总 B：Owen Price kept the pressure on with 2 for 1
- 通知：Scorers' correction: Ben Carter's dismissal, originally credited to Logan Vale, now belongs to Owen Price.

## Lina Fox 开发样例
- original: {'Nora_Vale_wickets': 4, 'Nora_Vale_runs': 6, 'Ruby_North_wickets': 3, 'Ruby_North_runs': 7, 'innings_total_wickets': 10}
- explicit: {'Nora_Vale_wickets': 3, 'Nora_Vale_runs': 6, 'Ruby_North_wickets': 4, 'Ruby_North_runs': 7, 'innings_total_wickets': 10}
- derivation: {'Nora_Vale_wickets': 3, 'Nora_Vale_runs': 6, 'Ruby_North_wickets': 4, 'Ruby_North_runs': 7, 'innings_total_wickets': 10}