# Level 3 Map&Make trace

## Stage 1 — atomic propositions

The propositions below preserve source order. They do not assign delivery IDs
or NEW/DUPLICATE/REVISE state labels.

1. Frost's over contains six legal balls.
2. Aaron scores 2, 4, 4, 3 and 6 from Frost on five legal balls.
3. Connor scores 3 from Frost on one legal ball.
4. The end-of-over Frost scoring list repeats the events already described.
5. Frost's previous-match figures are not part of the target innings.
6. Pike's over contains six legal balls.
7. Connor scores 2, 2, 2, 4 and 1 from Pike on five legal balls.
8. Aaron scores 3 from Pike on one legal ball.
9. The end-of-over Pike scoring list repeats the events already described.
10. Pike's previous-match figures are not part of the target innings.
11. Stone's over contains six legal balls.
12. Aaron is initially credited with 2, 3, 3 and 4 from Stone on four legal balls.
13. Connor is credited with 3 and 1 from Stone on two legal balls.
14. Connor faces one additional no-ball from Stone; its catch is void and it has no bat run.
15. Stone bowls one wide to Aaron.
16. The end-of-over Stone scoring list repeats the events already described.
17. Stone's previous-match figures are not part of the target innings.
18. Rowe's over contains six legal balls.
19. Rowe dismisses Connor for no run on a legal ball.
20. Dylan faces three legal dots and is then dismissed by Rowe for no run on a fourth legal ball.
21. Rowe bowls one wide to Ethan.
22. Ethan scores 4 from Rowe on one legal ball.
23. The end-of-over Rowe scoring list repeats the events already described.
24. Rowe's previous-match figures are not part of the target innings.
25. Shaw's over contains six legal balls.
26. Shaw bowls one wide to Aaron.
27. Aaron scores 4, 2 and 1 from Shaw on three legal balls.
28. Ethan scores 4 and 2 and then faces a dot from Shaw on three legal balls.
29. The end-of-over Shaw scoring list repeats the events already described.
30. Shaw's previous-match figures are not part of the target innings.
31. Hart's over contains six legal balls.
32. Aaron initially scores 2 and 6 and is then bowled by Hart for no run, using three legal balls.
33. Gavin faces a dot and then initially scores 3 from Hart, using two legal balls.
34. Ethan faces one legal dot from Hart.
35. The end-of-over Hart scoring list repeats the events already described.
36. Hart's previous-match figures are not part of the target innings.
37. The second scoring shot by Aaron in Stone's over is finally 3 leg-byes, not bat runs.
38. The second scoring shot by Aaron in Hart's over is finally 2 bat runs, not 6.
39. A provisional message suggests changing Gavin's third scoring shot in Hart's over from 3 to 2.
40. The final ruling rejects that provisional value and restores the shot to 3 bat runs.
41. The delayed recording that says 3 is stale audio, not a new event or ruling.
42. Final official rulings override provisional and repeated material.

## Stage 2 — iteratively constructed schema

- `summary(runs, wickets, legal_balls, wides, no_balls, byes, leg_byes)`
- `batting(player, runs, balls, out)`
- `bowling(player, legal_balls, runs_conceded, wickets)`
- `fall_of_wickets(wicket_number, batter, team_runs)`

## Stage 3 — table filling policy

The propositions are processed in source order. Statements explicitly marked
as repeat, archive or stale audio do not add rows. A final official proposition
replaces the earlier value that its natural-language description identifies.
No external event ledger, event-state classifier, rollback module or semantic
repair pass is used.
