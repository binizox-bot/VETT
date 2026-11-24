# VETT workflow status

- time: 2026-11-23T19:17:38+08:00
- workflow state: idle_no_valid_tasks
- batch state: idle
- task state: {"done": 10369, "failed": 8, "queued": 0, "claimed": 0}
- schema: 2; planning: rule_template
- external API calls: 0
- supervisor: 7096 alive=True
- worker: 31180 alive=True heartbeat=12611.2s restarts=40
- queue: {"done": 10369, "failed": 8, "queued": 0, "claimed": 0}

- run elapsed: 8.73 h
- load/inference/scoring ms: 45578751.8 / 36337054.9 / 5271.3
- plan/wait ms: 22382.3 / 0.0
- attempts: 11425; uncertain: 28

## Batches

| batch | template | status | accuracy | cells | raw |
|---|---|---|---:|---|---|
| B001 | T1_baseline_o | scored | 1.0 | 12/12 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B001.jsonl |
| B002 | T2_hard_excerpt | scored | 0.8333 | 10/12 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B002.jsonl |
| B003 | T3_matched_deletion | scored | 0.1667 | 3/18 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B003.jsonl |
| B004 | T4_full_table | scored | 0.1938 | 25/129 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B004.jsonl |
| B005 | T2_hard_excerpt | scored | 0.8333 | 5/6 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B005.jsonl |
| B006 | T3_matched_deletion | scored | 0.0 | 0/6 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B006.jsonl |
| B007 | T5_hard_fulltext | scored | 0.0 | 0/12 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B007.jsonl |
| B008 | T1_baseline_o | scored | 0.9167 | 11/12 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B008.jsonl |
| B009 | T5_hard_fulltext | scored | 0.0 | 0/12 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B009.jsonl |
| B010 | T1_baseline_o | scored | 1.0 | 12/12 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B010.jsonl |
| B011 | T5_hard_fulltext | scored | 0.0 | 0/6 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B011.jsonl |
| B012 | A_field_probe | scored | 0.9167 | 22/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B012.jsonl |
| B013 | B_cross_innings | scored | 0.0 | 0/6 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B013.jsonl |
| B014 | T1_baseline_o | scored | 0.8333 | 10/12 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B014.jsonl |
| B015 | T3_matched_deletion | scored | 0.2222 | 4/18 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B015.jsonl |
| B016 | S_coverage_sweep | scored | 0.8125 | 78/96 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B016.jsonl |
| B017 | S_coverage_sweep | scored | 0.7667 | 46/60 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B017.jsonl |
| B018 | S_coverage_sweep | scored | 0.85 | 51/60 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B018.jsonl |
| B019 | C_adjudication | scored | 0.9778 | 176/180 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B019.jsonl |
| B020 | S_coverage_sweep | scored | 0.7708 | 37/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B020.jsonl |
| B021 | B2_matched_control | scored | 0.0 | 0/12 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B021.jsonl |
| B022 | C_adjudication | scored | 0.9222 | 166/180 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B022.jsonl |
| B023 | S_coverage_sweep | scored | 0.8167 | 49/60 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B023.jsonl |
| B024 | S_coverage_sweep | scored | 0.8667 | 52/60 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B024.jsonl |
| B025 | S_coverage_sweep | scored | 0.6458 | 31/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B025.jsonl |
| B026 | S_coverage_sweep | scored | 0.6389 | 23/36 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B026.jsonl |
| B027 | S_coverage_sweep | scored | 0.619 | 26/42 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B027.jsonl |
| B028 | S_coverage_sweep | scored | 0.5 | 12/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B028.jsonl |
| B029 | S_coverage_sweep | scored | 0.5 | 12/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B029.jsonl |
| B030 | S_coverage_sweep | scored | 0.4583 | 11/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B030.jsonl |
| B031 | S_coverage_sweep | scored | 0.5 | 12/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B031.jsonl |
| B032 | S_coverage_sweep | scored | 0.5 | 12/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B032.jsonl |
| B033 | S_coverage_sweep | scored | 0.5 | 12/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B033.jsonl |
| B034 | S_coverage_sweep | scored | 0.5417 | 13/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B034.jsonl |
| B035 | S_coverage_sweep | scored | 0.5 | 12/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B035.jsonl |
| B036 | S_coverage_sweep | scored | 0.5 | 12/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B036.jsonl |
| B037 | S_coverage_sweep | scored | 0.4583 | 11/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B037.jsonl |
| B038 | S_coverage_sweep | scored | 0.75 | 45/60 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B038.jsonl |
| B039 | S_coverage_sweep | scored | 0.5714 | 24/42 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B039.jsonl |
| B040 | S_coverage_sweep | scored | 0.641 | 50/78 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B040.jsonl |
| B041 | S_coverage_sweep | scored | 0.5833 | 42/72 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B041.jsonl |
| B042 | S_coverage_sweep | scored | 0.6667 | 32/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B042.jsonl |
| B043 | S_coverage_sweep | scored | 0.6333 | 19/30 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B043.jsonl |
| B044 | S_coverage_sweep | scored | 0.5417 | 13/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B044.jsonl |
| B045 | S_coverage_sweep | scored | 0.5 | 12/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B045.jsonl |
| B046 | S_coverage_sweep | scored | 0.625 | 15/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B046.jsonl |
| B047 | S_coverage_sweep | scored | 0.4167 | 10/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B047.jsonl |
| B048 | S_coverage_sweep | scored | 0.5833 | 14/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B048.jsonl |
| B049 | S_coverage_sweep | scored | 0.7222 | 26/36 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B049.jsonl |
| B050 | S_coverage_sweep | scored | 0.5 | 12/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B050.jsonl |
| B051 | S_coverage_sweep | scored | 0.5 | 12/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B051.jsonl |
| B052 | S_coverage_sweep | scored | 0.5 | 12/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B052.jsonl |
| B053 | S_coverage_sweep | scored | 0.5667 | 17/30 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B053.jsonl |
| B054 | S_coverage_sweep | scored | 0.5333 | 16/30 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B054.jsonl |
| B055 | S_coverage_sweep | scored | 0.5 | 12/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B055.jsonl |
| B056 | S_coverage_sweep | scored | 0.4583 | 11/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B056.jsonl |
| B057 | S_coverage_sweep | scored | 0.5 | 12/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B057.jsonl |
| B058 | S_coverage_sweep | scored | 0.4583 | 11/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B058.jsonl |
| B059 | S_coverage_sweep | scored | 0.6786 | 57/84 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B059.jsonl |
| B060 | S_coverage_sweep | scored | 0.6111 | 33/54 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B060.jsonl |
| B061 | S_coverage_sweep | scored | 0.375 | 9/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B061.jsonl |
| B062 | S_coverage_sweep | scored | 0.375 | 9/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B062.jsonl |
| B063 | S_coverage_sweep | scored | 0.5 | 12/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B063.jsonl |
| B064 | S_coverage_sweep | scored | 0.625 | 30/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B064.jsonl |
| B065 | S_coverage_sweep | scored | 0.5 | 12/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B065.jsonl |
| B066 | S_coverage_sweep | scored | 0.6667 | 24/36 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B066.jsonl |
| B067 | S_coverage_sweep | scored | 0.381 | 16/42 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B067.jsonl |
| B068 | S_coverage_sweep | scored | 0.6 | 18/30 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B068.jsonl |
| B069 | S_coverage_sweep | scored | 0.4167 | 10/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B069.jsonl |
| B070 | S_coverage_sweep | scored | 0.25 | 6/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B070.jsonl |
| B071 | S_coverage_sweep | scored | 0.4167 | 10/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B071.jsonl |
| B072 | S_coverage_sweep | scored | 0.5 | 12/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B072.jsonl |
| B073 | S_coverage_sweep | scored | 0.5 | 12/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B073.jsonl |
| B074 | S_coverage_sweep | scored | 0.5 | 12/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B074.jsonl |
| B075 | S_coverage_sweep | scored | 0.5 | 12/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B075.jsonl |
| B076 | S_coverage_sweep | scored | 0.5 | 12/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B076.jsonl |
| B077 | S_coverage_sweep | scored | 0.5417 | 13/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B077.jsonl |
| B078 | S_coverage_sweep | scored | 0.625 | 15/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B078.jsonl |
| B079 | S_coverage_sweep | scored | 0.6667 | 48/72 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B079.jsonl |
| B080 | S_coverage_sweep | scored | 0.7222 | 52/72 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B080.jsonl |
| B081 | S_coverage_sweep | scored | 0.6389 | 46/72 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B081.jsonl |
| B082 | S_coverage_sweep | scored | 0.7083 | 68/96 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B082.jsonl |
| B083 | S_coverage_sweep | scored | 0.6282 | 49/78 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B083.jsonl |
| B084 | S_coverage_sweep | scored | 0.6146 | 59/96 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B084.jsonl |
| B085 | S_coverage_sweep | scored | 0.6667 | 64/96 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B085.jsonl |
| B086 | S_coverage_sweep | scored | 0.5972 | 43/72 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B086.jsonl |
| B087 | S_coverage_sweep | scored | 0.6167 | 37/60 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B087.jsonl |
| B088 | S_coverage_sweep | scored | 0.2083 | 5/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B088.jsonl |
| B089 | S_coverage_sweep | scored | 0.4167 | 10/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B089.jsonl |
| B090 | S_coverage_sweep | scored | 0.4583 | 11/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B090.jsonl |
| B091 | S_coverage_sweep | scored | 0.4167 | 10/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B091.jsonl |
| B092 | S_coverage_sweep | scored | 0.4583 | 11/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B092.jsonl |
| B093 | S_coverage_sweep | scored | 0.5417 | 13/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B093.jsonl |
| B094 | S_coverage_sweep | scored | 0.5 | 12/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B094.jsonl |
| B095 | S_coverage_sweep | scored | 0.4167 | 10/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B095.jsonl |
| B096 | S_coverage_sweep | scored | 0.4583 | 11/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B096.jsonl |
| B097 | S_coverage_sweep | scored | 0.5417 | 13/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B097.jsonl |
| B098 | S_coverage_sweep | scored | 0.375 | 9/24 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B098.jsonl |
| B099 | S_coverage_sweep | scored | 0.5208 | 25/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B099.jsonl |
| B100 | S_coverage_sweep | scored | 0.6667 | 40/60 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B100.jsonl |
| B101 | S_coverage_sweep | scored | 0.625 | 60/96 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B101.jsonl |
| B102 | S_coverage_sweep | scored | 0.5 | 39/78 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B102.jsonl |
| B103 | S_coverage_sweep | scored | 0.5833 | 56/96 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B103.jsonl |
| B104 | S_coverage_sweep | scored | 0.7273 | 48/66 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B104.jsonl |
| B105 | S_coverage_sweep | scored | 0.4167 | 20/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B105.jsonl |
| B106 | S_coverage_sweep | scored | 0.5 | 6/12 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B106.jsonl |
| B107 | P_field_sweep | scored | 0.4583 | 22/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B107.jsonl |
| B108 | P_field_sweep | scored | 0.5 | 24/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B108.jsonl |
| B109 | P_field_sweep | scored | 0.5208 | 25/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B109.jsonl |
| B110 | P_field_sweep | scored | 0.4583 | 22/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B110.jsonl |
| B111 | P_field_sweep | scored | 0.5 | 24/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B111.jsonl |
| B112 | P_field_sweep | scored | 0.4583 | 22/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B112.jsonl |
| B113 | P_field_sweep | scored | 0.5 | 24/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B113.jsonl |
| B114 | P_field_sweep | scored | 0.4583 | 22/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B114.jsonl |
| B115 | P_field_sweep | scored | 0.4792 | 23/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B115.jsonl |
| B116 | P_field_sweep | scored | 0.4375 | 21/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B116.jsonl |
| B117 | P_field_sweep | scored | 0.4792 | 23/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B117.jsonl |
| B118 | P_field_sweep | scored | 0.5 | 24/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B118.jsonl |
| B119 | P_field_sweep | scored | 0.4583 | 22/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B119.jsonl |
| B120 | P_field_sweep | scored | 0.4792 | 23/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B120.jsonl |
| B121 | P_field_sweep | scored | 0.4583 | 22/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B121.jsonl |
| B122 | P_field_sweep | scored | 0.5 | 24/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B122.jsonl |
| B123 | P_field_sweep | scored | 0.5417 | 26/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B123.jsonl |
| B124 | P_field_sweep | scored | 0.5 | 24/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B124.jsonl |
| B125 | P_field_sweep | scored | 0.5 | 24/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B125.jsonl |
| B126 | P_field_sweep | scored | 0.4583 | 22/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B126.jsonl |
| B127 | P_field_sweep | scored | 0.625 | 30/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B127.jsonl |
| B128 | P_field_sweep | scored | 0.5 | 24/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B128.jsonl |
| B129 | P_field_sweep | scored | 0.6042 | 29/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B129.jsonl |
| B130 | P_field_sweep | scored | 0.5625 | 27/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B130.jsonl |
| B131 | P_field_sweep | scored | 0.5 | 24/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B131.jsonl |
| B132 | P_field_sweep | scored | 0.5417 | 26/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B132.jsonl |
| B133 | P_field_sweep | scored | 0.5417 | 26/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B133.jsonl |
| B134 | P_field_sweep | scored | 0.4583 | 22/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B134.jsonl |
| B135 | P_field_sweep | scored | 0.5833 | 28/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B135.jsonl |
| B136 | P_field_sweep | scored | 0.4375 | 21/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B136.jsonl |
| B137 | P_field_sweep | scored | 0.5208 | 25/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B137.jsonl |
| B138 | P_field_sweep | scored | 0.6042 | 29/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B138.jsonl |
| B139 | P_field_sweep | scored | 0.7292 | 35/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B139.jsonl |
| B140 | P_field_sweep | scored | 0.5 | 24/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B140.jsonl |
| B141 | P_field_sweep | scored | 0.4792 | 23/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B141.jsonl |
| B142 | P_field_sweep | scored | 0.3958 | 19/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B142.jsonl |
| B143 | P_field_sweep | scored | 0.5208 | 25/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B143.jsonl |
| B144 | P_field_sweep | scored | 0.3958 | 19/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B144.jsonl |
| B145 | P_field_sweep | scored | 0.5208 | 25/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B145.jsonl |
| B146 | P_field_sweep | scored | 0.5 | 24/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B146.jsonl |
| B147 | P_field_sweep | scored | 0.4583 | 22/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B147.jsonl |
| B148 | P_field_sweep | scored | 0.5 | 24/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B148.jsonl |
| B149 | P_field_sweep | scored | 0.4792 | 23/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B149.jsonl |
| B150 | P_field_sweep | scored | 0.375 | 18/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B150.jsonl |
| B151 | ACC_llama_p320 | scored | 0.6667 | 2/3 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B151.jsonl |
| B152 | P_field_sweep | scored | 0.3125 | 15/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B152.jsonl |
| B153 | P_field_sweep | scored | 0.5417 | 26/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B153.jsonl |
| B154 | P_field_sweep | scored | 0.5 | 24/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B154.jsonl |
| B155 | P_field_sweep | scored | 0.5417 | 26/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B155.jsonl |
| B156 | P_field_sweep | scored | 0.5 | 24/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B156.jsonl |
| B157 | P_field_sweep | scored | 0.4167 | 20/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B157.jsonl |
| B158 | P_field_sweep | scored | 0.5208 | 25/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B158.jsonl |
| B159 | P_field_sweep | scored | 0.25 | 12/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B159.jsonl |
| B160 | P_field_sweep | scored | 0.2917 | 14/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B160.jsonl |
| B161 | P_field_sweep | scored | 0.4583 | 22/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B161.jsonl |
| B162 | P_field_sweep | scored | 0.4792 | 23/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B162.jsonl |
| B163 | P_field_sweep | scored | 0.5208 | 25/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B163.jsonl |
| B164 | P_field_sweep | scored | 0.5417 | 26/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B164.jsonl |
| B165 | P_field_sweep | scored | 0.5435 | 25/46 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B165.jsonl |
| B166 | P_field_sweep | scored | 0.4792 | 23/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B166.jsonl |
| B167 | P_field_sweep | scored | 0.3958 | 19/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B167.jsonl |
| B168 | P_field_sweep | scored | 0.6667 | 32/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B168.jsonl |
| B169 | P_field_sweep | scored | 0.4792 | 23/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B169.jsonl |
| B170 | P_field_sweep | scored | 0.4375 | 21/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B170.jsonl |
| B171 | P_field_sweep | scored | 0.5833 | 28/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B171.jsonl |
| B172 | P_field_sweep | scored | 0.5833 | 28/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B172.jsonl |
| B173 | P_field_sweep | scored | 0.375 | 18/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B173.jsonl |
| B174 | P_field_sweep | scored | 0.5 | 24/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B174.jsonl |
| B175 | P_field_sweep | scored | 0.5 | 24/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B175.jsonl |
| B176 | P_field_sweep | scored | 0.5417 | 26/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B176.jsonl |
| B177 | P_field_sweep | scored | 0.4792 | 23/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B177.jsonl |
| B178 | P_field_sweep | scored | 0.4167 | 20/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B178.jsonl |
| B179 | P_field_sweep | scored | 0.3958 | 19/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B179.jsonl |
| B180 | P_field_sweep | scored | 0.3958 | 19/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B180.jsonl |
| B181 | P_field_sweep | scored | 0.5 | 24/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B181.jsonl |
| B182 | P_field_sweep | scored | 0.4583 | 22/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B182.jsonl |
| B183 | P_field_sweep | scored | 0.4375 | 21/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B183.jsonl |
| B184 | P_field_sweep | scored | 0.5625 | 27/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B184.jsonl |
| B185 | P_field_sweep | scored | 0.4167 | 20/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B185.jsonl |
| B186 | P_field_sweep | scored | 0.4375 | 21/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B186.jsonl |
| B187 | P_field_sweep | scored | 0.375 | 18/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B187.jsonl |
| B188 | P_field_sweep | scored | 0.5 | 24/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B188.jsonl |
| B189 | P_field_sweep | scored | 0.3125 | 15/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B189.jsonl |
| B190 | P_field_sweep | scored | 0.4792 | 23/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B190.jsonl |
| B191 | P_field_sweep | scored | 0.5833 | 28/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B191.jsonl |
| B192 | P_field_sweep | scored | 0.4583 | 22/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B192.jsonl |
| B193 | P_field_sweep | scored | 0.4583 | 22/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B193.jsonl |
| B194 | P_field_sweep | scored | 0.4583 | 22/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B194.jsonl |
| B195 | P_field_sweep | scored | 0.4167 | 20/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B195.jsonl |
| B196 | P_field_sweep | scored | 0.3958 | 19/48 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B196.jsonl |
| B197 | P_field_sweep | scored | 0.3333 | 4/12 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B197.jsonl |
| B198 | T4_full_table_scale | scored | 0.2677 | 2072/7740 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B198.jsonl |
| B199 | T4_full_table_scale2 | scored | 0.2358 | 1825/7740 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B199.jsonl |
| B200 | T4_full_table_O_scale | scored | 0.1299 | 338/2603 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B200.jsonl |
| B201 | T4_full_table_O_scale | failed | None | None | None |
| B202 | T4_full_table_O_scale | failed | None | None | None |
| B203 | T4_full_table_O_scale | failed | None | None | None |
| B204 | T4_full_table_E_scale | failed | None | None | None |
| B205 | T4_full_table_E_scale | failed | None | None | None |
| B206 | T4_full_table_OI_scale | failed | None | None | None |
| B207 | T4_full_table_E_used | scored | 0.1081 | 381/3526 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B207.jsonl |
| B208 | T4_full_table_OI_used | scored | 0.2483 | 993/3999 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B208.jsonl |
| B209 | B_cross_innings_scale | scored | 0.5862 | 102/174 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B209.jsonl |
| B209Z | X_codex_abc_pilot | scored | 0.8021 | 77/96 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B209Z.jsonl |
| B210 | P_E_probe | scored | 0.8851 | 701/792 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B210.jsonl |
| B211 | P_OI_probe | scored | 0.649 | 405/624 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B211.jsonl |
| B212 | X_codex_frozen_v1 | scored | 1.0 | 57/57 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B212.jsonl |
| B213 | X_night_core_event | scored | 0.9667 | 87/90 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B213.jsonl |
| B221 | X_night_core_event | scored | 0.8556 | 77/90 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B221.jsonl |
| B222 | X_night_core_event | scored | 0.8333 | 75/90 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B222.jsonl |
| B223 | X_night_core_event | scored | 0.9222 | 83/90 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B223.jsonl |
| B224 | X_night_core_event | scored | 0.7222 | 65/90 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B224.jsonl |
| B225 | X_night_core_event | scored | 0.9 | 81/90 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B225.jsonl |
| B226 | X_night_core_event | scored | 0.9333 | 84/90 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B226.jsonl |
| B227 | X_night_core_event | scored | 0.7444 | 67/90 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B227.jsonl |
| B228 | X_night_fulltable | scored | 0.2752 | 71/258 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B228.jsonl |
| B229 | X_night_fulltable | scored | 0.2171 | 56/258 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B229.jsonl |
| B230 | X_night_fulltable | scored | 0.2364 | 61/258 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B230.jsonl |
| B231 | X_night_fulltable | scored | 0.2907 | 75/258 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B231.jsonl |
| B232 | X_night_fulltable | scored | 0.186 | 48/258 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B232.jsonl |
| B233 | X_night_fulltable | scored | 0.155 | 40/258 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B233.jsonl |
| B234 | X_night_fulltable | scored | 0.2248 | 58/258 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B234.jsonl |
| B235 | X_night_fulltable | scored | 0.2442 | 63/258 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B235.jsonl |
| B236 | X_night_fallback | scored | 0.9667 | 58/60 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B236.jsonl |
| B237 | X_night_ft_ordinary | scored | 0.191 | 51/267 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B237.jsonl |
| B238 | X_night_ft_ordinary | scored | 0.2783 | 718/2580 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B238.jsonl |
| B239 | X_night_ft_ordinary | scored | 0.2109 | 272/1290 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B239.jsonl |
| B240 | X_night_ft_ordinary | scored | 0.2659 | 343/1290 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B240.jsonl |
| B241 | X_night_ft_ordinary | scored | 0.2512 | 2577/10260 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B241.jsonl |
| B242 | X_night_ft_ordinary | scored | 0.2387 | 1478/6192 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B242.jsonl |
| B243 | X_night_diag | scored | 0.4667 | 56/120 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B243.jsonl |
| B244 | X_night_diag | scored | 0.5938 | 57/96 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B244.jsonl |
| B245 | X_night_diag | scored | 0.6562 | 63/96 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B245.jsonl |
| B246 | X_night_diag | scored | 0.7788 | 243/312 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B246.jsonl |
| B247 | X_night_fulltable | scored | 0.2607 | 269/1032 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B247.jsonl |
| B248 | X_night_partial | scored | 0.7333 | 176/240 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B248.jsonl |
| B249 | X_night_partial | scored | 0.2833 | 68/240 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B249.jsonl |
| B250 | X_night_fulltable | scored | 0.1003 | 207/2064 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B250.jsonl |
| B251 | X_night_field | scored | 0.2208 | 106/480 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B251.jsonl |
| B252 | X_night_field | scored | 0.2208 | 53/240 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B252.jsonl |
| B253 | X_night_partial | scored | 0.2 | 48/240 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B253.jsonl |
| B254 | X_top2_membership | scored | 0.6667 | 6/9 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B254.jsonl |
| B255 | X_top2_membership | scored | 0.4921 | 31/63 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B255.jsonl |
| B256 | X_q4_neutral | scored | 0.5104 | 49/96 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B256.jsonl |
| B257 | X_ft_hint | scored | 0.2403 | 31/129 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B257.jsonl |
| B258 | X_ft_direct_4root | scored | 0.2301 | 243/1056 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B258.jsonl |
| B259 | X_ft_hint_4root | scored | 0.2267 | 234/1032 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B259.jsonl |
| B260 | X_rank_evidence | scored | 0.0 | 0/12 | D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\runs\B260.jsonl |

## Next queued tasks

- none

## Recent events

- 2026-11-23T19:06:12+08:00 exhausted {"reason": "no_eligible_tasks", "coverage": ["C missing-evidence matrix", "D R28 low-old-value direction", "E temperature/seed randomness", "F held-out full-table validation"]}
- 2026-11-23T19:06:12+08:00 coverage_audit {"generated_at": "2026-11-23T19:06:12+08:00", "reason": "no_eligible_tasks", "matches_total": 220, "parsed_positions": 437, "u_full": {"responses": 1311, "json_scorable": 1304, "missing_positions": 3}, "evidence_index": 
- 2026-11-23T19:02:37+08:00 status_written {"batches": 254, "queue": {"done": 10369, "failed": 8, "queued": 0, "claimed": 0}}
- 2026-11-23T18:51:11+08:00 exhausted {"reason": "no_eligible_tasks", "coverage": ["C missing-evidence matrix", "D R28 low-old-value direction", "E temperature/seed randomness", "F held-out full-table validation"]}
- 2026-11-23T18:51:11+08:00 coverage_audit {"generated_at": "2026-11-23T18:51:11+08:00", "reason": "no_eligible_tasks", "matches_total": 220, "parsed_positions": 437, "u_full": {"responses": 1311, "json_scorable": 1304, "missing_positions": 3}, "evidence_index": 
- 2026-11-23T18:47:37+08:00 status_written {"batches": 254, "queue": {"done": 10369, "failed": 8, "queued": 0, "claimed": 0}}
- 2026-11-23T18:36:11+08:00 exhausted {"reason": "no_eligible_tasks", "coverage": ["C missing-evidence matrix", "D R28 low-old-value direction", "E temperature/seed randomness", "F held-out full-table validation"]}
- 2026-11-23T18:36:11+08:00 coverage_audit {"generated_at": "2026-11-23T18:36:11+08:00", "reason": "no_eligible_tasks", "matches_total": 220, "parsed_positions": 437, "u_full": {"responses": 1311, "json_scorable": 1304, "missing_positions": 3}, "evidence_index": 
- 2026-11-23T18:34:07+08:00 hourly_report {"path": "D:\\Download\\VETT_Cricket_Complete_Delivery_R19_20261017\\VETT_INTEGRATED_20261113\\analysis\\vett_autonomous_20261117\\reports\\HOURLY_20261123_183407.md", "elapsed_hours": 8.0}
- 2026-11-23T18:34:06+08:00 snapshot_written {"path": "D:\\Download\\VETT_Cricket_Complete_Delivery_R19_20261017\\VETT_INTEGRATED_20261113\\analysis\\vett_autonomous_20261117\\reports\\SNAPSHOT_20261123_183406.md"}
- 2026-11-23T18:32:36+08:00 status_written {"batches": 254, "queue": {"done": 10369, "failed": 8, "queued": 0, "claimed": 0}}
- 2026-11-23T18:21:11+08:00 exhausted {"reason": "no_eligible_tasks", "coverage": ["C missing-evidence matrix", "D R28 low-old-value direction", "E temperature/seed randomness", "F held-out full-table validation"]}
