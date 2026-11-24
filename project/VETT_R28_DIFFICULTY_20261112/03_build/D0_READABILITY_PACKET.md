# D0 可读性盲测包（t7）

每题给出**改动后的事实集**与两条候选 12 字段记录（A/B 顺序已随机化）。
请判断哪条记录能由这些事实推出。**本文件不含答案**；答案键在 `D0_READABILITY_KEY.json`，判读者在作答前不得打开。

## D0-C1  (item `r28q_0121`, FACTOR)

**改动后事实集**

```json
{
 "appeal_in_time": true,
 "appeal_made": true,
 "award_run_in_progress": true,
 "boundary_allowance": 6,
 "boundary_mode": "OVERTHROW",
 "completed_runs": 3,
 "contact": "BAT",
 "crossed_at_throw": true,
 "dismissal_candidate": "NONE",
 "penalty_runs_batting": 0,
 "wicket_fair": true,
 "wilful_deception": false
}
```

**候选 A**：`{"batter_runs": 11, "bowler_runs": 11, "counts_in_over": true, "delivery_status": "LEGAL", "dismissal": "NONE", "ledger.BATTER": 11, "ledger.BYE": 0, "ledger.LEG_BYE": 0, "ledger.NO_BALL_EXTRA": 0, "ledger.PENALTY": 5, "ledger.WIDE_EXTRA": 0, "total_runs": 16}`

**候选 B**：`{"batter_runs": 11, "bowler_runs": 11, "counts_in_over": true, "delivery_status": "LEGAL", "dismissal": "NONE", "ledger.BATTER": 11, "ledger.BYE": 0, "ledger.LEG_BYE": 0, "ledger.NO_BALL_EXTRA": 0, "ledger.PENALTY": 0, "ledger.WIDE_EXTRA": 0, "total_runs": 11}`

请回答：A 还是 B 能由上面的改动后事实集推出？

## D0-C2  (item `r28q_0161`, D1)

**改动后事实集**

```json
{
 "appeal_in_time": true,
 "appeal_made": true,
 "award_run_in_progress": true,
 "boundary_allowance": 0,
 "boundary_mode": "NONE",
 "completed_runs": 0,
 "contact": "NONE",
 "crossed_at_throw": false,
 "dismissal_candidate": "OBSTRUCTING_FIELD",
 "no_ball_called": true,
 "penalty_runs_batting": 5,
 "wicket_fair": true,
 "wilful_deception": true
}
```

**候选 A**：`{"batter_runs": 0, "bowler_runs": 1, "counts_in_over": false, "delivery_status": "NO_BALL", "dismissal": "NONE", "ledger.BATTER": 0, "ledger.BYE": 2, "ledger.LEG_BYE": 0, "ledger.NO_BALL_EXTRA": 1, "ledger.PENALTY": 10, "ledger.WIDE_EXTRA": 0, "total_runs": 13}`

**候选 B**：`{"batter_runs": 0, "bowler_runs": 1, "counts_in_over": false, "delivery_status": "NO_BALL", "dismissal": "NONE", "ledger.BATTER": 0, "ledger.BYE": 1, "ledger.LEG_BYE": 0, "ledger.NO_BALL_EXTRA": 1, "ledger.PENALTY": 10, "ledger.WIDE_EXTRA": 0, "total_runs": 12}`

请回答：A 还是 B 能由上面的改动后事实集推出？

## D0-C3  (item `r28q_0209`, D2)

**改动后事实集**

```json
{
 "appeal_in_time": true,
 "appeal_made": true,
 "attempting_run": false,
 "award_run_in_progress": true,
 "boundary_allowance": 6,
 "boundary_mode": "NONE",
 "completed_runs": 2,
 "contact": "NONE",
 "crossed_at_throw": true,
 "dismissal_candidate": "STUMPED_OR_RUN_OUT",
 "keeper_only": true,
 "out_of_ground": true,
 "penalty_runs_batting": 0,
 "wicket_fair": true,
 "wilful_deception": true
}
```

**候选 A**：`{"batter_runs": 0, "bowler_runs": 0, "counts_in_over": false, "delivery_status": "LEGAL", "dismissal": "NONE", "ledger.BATTER": 0, "ledger.BYE": 3, "ledger.LEG_BYE": 0, "ledger.NO_BALL_EXTRA": 0, "ledger.PENALTY": 5, "ledger.WIDE_EXTRA": 0, "total_runs": 8}`

**候选 B**：`{"batter_runs": 0, "bowler_runs": 0, "counts_in_over": false, "delivery_status": "LEGAL", "dismissal": "NONE", "ledger.BATTER": 0, "ledger.BYE": 10, "ledger.LEG_BYE": 0, "ledger.NO_BALL_EXTRA": 0, "ledger.PENALTY": 5, "ledger.WIDE_EXTRA": 0, "total_runs": 15}`

请回答：A 还是 B 能由上面的改动后事实集推出？

## D0-C4  (item `r28q_0257`, D3)

**改动后事实集**

```json
{
 "appeal_in_time": false,
 "appeal_made": true,
 "award_run_in_progress": false,
 "boundary_allowance": 6,
 "boundary_mode": "OVERTHROW",
 "completed_runs": 3,
 "contact": "PERSON",
 "crossed_at_throw": true,
 "dismissal_candidate": "OBSTRUCTING_FIELD",
 "no_ball_called": true,
 "penalty_runs_batting": 0,
 "wicket_fair": true,
 "wilful_deception": false
}
```

**候选 A**：`{"batter_runs": 0, "bowler_runs": 1, "counts_in_over": false, "delivery_status": "NO_BALL", "dismissal": "OBSTRUCTING_FIELD", "ledger.BATTER": 0, "ledger.BYE": 0, "ledger.LEG_BYE": 10, "ledger.NO_BALL_EXTRA": 1, "ledger.PENALTY": 0, "ledger.WIDE_EXTRA": 0, "total_runs": 11}`

**候选 B**：`{"batter_runs": 0, "bowler_runs": 1, "counts_in_over": false, "delivery_status": "NO_BALL", "dismissal": "NONE", "ledger.BATTER": 0, "ledger.BYE": 0, "ledger.LEG_BYE": 10, "ledger.NO_BALL_EXTRA": 1, "ledger.PENALTY": 0, "ledger.WIDE_EXTRA": 0, "total_runs": 11}`

请回答：A 还是 B 能由上面的改动后事实集推出？

## D0-C5  (item `r28q_0305`, D4)

**改动后事实集**

```json
{
 "appeal_in_time": true,
 "appeal_made": true,
 "attempting_run": false,
 "award_run_in_progress": true,
 "boundary_allowance": 0,
 "boundary_mode": "OVERTHROW",
 "completed_runs": 3,
 "contact": "NONE",
 "crossed_at_throw": false,
 "dismissal_candidate": "STUMPED_OR_RUN_OUT",
 "keeper_only": true,
 "no_ball_called": true,
 "out_of_ground": true,
 "penalty_runs_batting": 0,
 "wicket_fair": true,
 "wilful_deception": true
}
```

**候选 A**：`{"batter_runs": 0, "bowler_runs": 1, "counts_in_over": false, "delivery_status": "NO_BALL", "dismissal": "NONE", "ledger.BATTER": 0, "ledger.BYE": 8, "ledger.LEG_BYE": 0, "ledger.NO_BALL_EXTRA": 1, "ledger.PENALTY": 5, "ledger.WIDE_EXTRA": 0, "total_runs": 14}`

**候选 B**：`{"batter_runs": 0, "bowler_runs": 1, "counts_in_over": false, "delivery_status": "NO_BALL", "dismissal": "NONE", "ledger.BATTER": 0, "ledger.BYE": 4, "ledger.LEG_BYE": 0, "ledger.NO_BALL_EXTRA": 1, "ledger.PENALTY": 5, "ledger.WIDE_EXTRA": 0, "total_runs": 10}`

请回答：A 还是 B 能由上面的改动后事实集推出？
