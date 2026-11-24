const fs = require("fs");
const path = require("path");

const METHOD = "t3_paper_direct_integration_variant";
const outDir = __dirname;

const table = (table_type, innings, columns, rows) => ({
  table_type,
  innings,
  columns,
  rows,
});

const batter = (batter, dismissal, runs, balls, fours, sixes) => ({
  batter,
  dismissal,
  runs,
  balls,
  fours,
  sixes,
});

const bowler = (bowler, overs, maidens, runs, wickets, wides, no_balls) => ({
  bowler,
  overs,
  maidens,
  runs,
  wickets,
  wides,
  no_balls,
});

const fow = (wicket, score, batter, over) => ({ wicket, score, batter, over });

const partnership = (
  partnership,
  batter_1,
  batter_2,
  runs,
  extras,
  batter_1_runs,
  batter_1_balls,
  batter_2_runs,
  batter_2_balls,
  overs,
  end
) => ({
  partnership,
  batter_1,
  batter_2,
  runs,
  extras,
  batter_1_runs,
  batter_1_balls,
  batter_2_runs,
  batter_2_balls,
  overs,
  end,
});

const matchTable = (venue, toss_winner, toss_decision, result, player_of_the_match) =>
  table(
    "match_summary",
    "match",
    ["venue", "toss_winner", "toss_decision", "result", "player_of_the_match"],
    [{ venue, toss_winner, toss_decision, result, player_of_the_match }]
  );

const inningsTable = (innings, team, total, wickets, overs) =>
  table("innings_summary", innings, ["team", "total", "wickets", "overs"], [
    { team, total, wickets, overs },
  ]);

const extrasTable = (innings, byes, leg_byes, no_balls, wides) =>
  table("extras", innings, ["byes", "leg_byes", "no_balls", "wides", "total"], [
    { byes, leg_byes, no_balls, wides, total: byes + leg_byes + no_balls + wides },
  ]);

const battingTable = (innings, rows) =>
  table("batting", innings, ["batter", "dismissal", "runs", "balls", "fours", "sixes"], rows);

const bowlingTable = (innings, rows) =>
  table(
    "bowling",
    innings,
    ["bowler", "overs", "maidens", "runs", "wickets", "wides", "no_balls"],
    rows
  );

const fowTable = (innings, rows) =>
  table("fall_of_wickets", innings, ["wicket", "score", "batter", "over"], rows);

const partnershipsTable = (innings, rows) =>
  table(
    "partnerships",
    innings,
    [
      "partnership",
      "batter_1",
      "batter_2",
      "runs",
      "extras",
      "batter_1_runs",
      "batter_1_balls",
      "batter_2_runs",
      "batter_2_balls",
      "overs",
      "end",
    ],
    rows
  );

const predictions = [
  {
    instance_id: "match_0185.V4SDC",
    method: METHOD,
    tables: [
      matchTable(
        "Brookside Training Oval, Eastmere",
        "Tidehaven",
        "bat",
        "Ridgefield won by 9 wickets",
        "Noah Vance (Ridgefield)"
      ),
      inningsTable("I1", "Tidehaven", 36, 10, "20.3"),
      extrasTable("I1", 0, 1, 1, 12),
      battingTable("I1", [
        batter("Harvey Lane", "b Noah Vance", 0, 2, 0, 0),
        batter("Rohan Blake", "c Arlo Finch b Noah Vance", 8, 18, 1, 0),
        batter("Miles Sharp", "b Noah Vance", 0, 3, 0, 0),
        batter("Nolan Reed (c)", "b Noah Vance", 1, 10, 0, 0),
        batter("Caleb Frost", "lbw Arjun Wells", 2, null, 0, 0),
        batter("Owen Marsh", "b Arjun Wells", 7, null, 1, 0),
        batter("Dylan Pierce", "b Arjun Wells", 0, 7, 0, 0),
        batter("Theo Grant (wk)", "c Ben Cole b Elias Grant", 1, 5, 0, 0),
        batter("Arun Cole", "b Arjun Wells", 2, 11, 0, 0),
        batter("Kian Stone", "not out", 1, 7, 0, 0),
        batter("Vikram Holt", "b Arjun Wells", 0, 9, 0, 0),
      ]),
      bowlingTable("I1", [
        bowler("Noah Vance", "6", 3, 9, 4, 4, 0),
        bowler("Arjun Wells", "9.3", 4, 15, 5, 6, 1),
        bowler("Elias Grant", "2", 1, 5, 1, 0, 0),
        bowler("Ben Cole", "3", 0, 6, 0, 2, 0),
      ]),
      fowTable("I1", [
        fow(1, 0, "Harvey Lane", "0.2"),
        fow(2, 1, "Miles Sharp", "1.1"),
        fow(3, 11, "Rohan Blake", "5.4"),
        fow(4, 12, "Nolan Reed", "7.3"),
        fow(5, 24, "Owen Marsh", "13.2"),
        fow(6, 24, "Dylan Pierce", "14.5"),
        fow(7, 26, "Caleb Frost", "16.1"),
        fow(8, 30, "Theo Grant", "17.3"),
        fow(9, 35, "Arun Cole", "19.1"),
        fow(10, 36, "Vikram Holt", "20.3"),
      ]),
      partnershipsTable("I1", [
        partnership(1, "Harvey Lane", "Rohan Blake", 0, 0, 0, 2, 0, 0, "0.1-0.2", "Bowled (Harvey Lane)"),
        partnership(2, "Miles Sharp", "Rohan Blake", 1, 1, 0, 3, 0, 0, "0.3-1.1", "Bowled (Miles Sharp)"),
        partnership(3, "Rohan Blake", "Nolan Reed", 10, 1, 8, 18, 1, 10, "1.2-5.4", "Caught (Rohan Blake)"),
        partnership(4, "Nolan Reed", "Caleb Frost", 1, 1, 0, 0, 0, 9, "5.5-7.3", "Bowled (Nolan Reed)"),
        partnership(5, "Caleb Frost", "Owen Marsh", 12, 3, 2, null, 7, null, "7.4-13.2", "Bowled (Owen Marsh)"),
        partnership(6, "Dylan Pierce", "Caleb Frost", 0, 0, 0, 7, 0, 0, "13.3-14.5", "Bowled (Dylan Pierce)"),
        partnership(7, "Theo Grant", "Caleb Frost", 2, 1, 1, 3, 0, 0, "14.6-16.1", "Leg Before Wicket (Caleb Frost)"),
        partnership(8, "Theo Grant", "Arun Cole", 4, 2, 0, 2, 2, 6, "16.2-17.3", "Caught (Theo Grant)"),
        partnership(9, "Kian Stone", "Arun Cole", 5, 4, 1, 5, 0, 5, "17.4-19.1", "Bowled (Arun Cole)"),
        partnership(10, "Kian Stone", "Vikram Holt", 1, 1, 0, 2, 0, 9, "19.2-20.3", "Bowled (Vikram Holt)"),
      ]),
      inningsTable("I2", "Ridgefield", 37, 1, "3.3"),
      extrasTable("I2", 0, 0, 2, 7),
      battingTable("I2", [
        batter("Arlo Finch (wk)", "not out", 19, null, 3, 0),
        batter("Ben Cole", "c Rohan Blake b Owen Marsh", 7, 5, 0, 1),
        batter("Noah Vance", "not out", 2, null, 0, 0),
        batter("Mason Dale", "did not bat", 0, 0, 0, 0),
        batter("Ethan Vale (c)", "did not bat", 0, 0, 0, 0),
        batter("Arjun Wells", "did not bat", 0, 0, 0, 0),
        batter("Isaac Rowe", "did not bat", 0, 0, 0, 0),
        batter("Connor Hayes", "did not bat", 0, 0, 0, 0),
        batter("Elias Grant", "did not bat", 0, 0, 0, 0),
        batter("Sam Brooks", "did not bat", 0, 0, 0, 0),
        batter("Jack Morris", "did not bat", 0, 0, 0, 0),
      ]),
      bowlingTable("I2", [
        bowler("Owen Marsh", "2", 0, 19, 1, 2, 1),
        bowler("Arun Cole", "1", 0, 13, 0, 5, 0),
        bowler("Caleb Frost", "0.3", 0, 5, 0, 0, 1),
      ]),
      fowTable("I2", [fow(1, 18, "Ben Cole", "1.5")]),
      partnershipsTable("I2", [
        partnership(1, "Arlo Finch", "Ben Cole", 18, 1, 10, 6, 7, 5, "0.1-1.5", "Caught (Ben Cole)"),
        partnership(2, "Noah Vance", "Arlo Finch", 19, 8, 2, null, 9, null, "1.6-3.3", "innings completion"),
      ]),
    ],
  },
  {
    instance_id: "match_0106.V4SDC",
    method: METHOD,
    tables: [
      matchTable(
        "Brookhaven Cricket Oval, Eastmoor",
        "Coral Bay Tides Women",
        "field",
        "Meadowridge Spirits Women won by 88 runs",
        "Jade Sinclair"
      ),
      inningsTable("I1", "Meadowridge Spirits Women", 132, 8, "20.0"),
      extrasTable("I1", 2, 4, 5, 18),
      battingTable("I1", [
        batter("Elena Cross (wk)", "b Aila Rowan", 10, 12, 1, 0),
        batter("Mira Vale", "lbw Nia Brooke", 8, 18, 0, 0),
        batter("Tara Quinn", "c Maris Vale b Aila Rowan", 7, 8, 1, 0),
        batter("Rowan Hayes", "b Celeste Reed", 21, null, 1, 0),
        batter("Nora Finch (c)", "c Bella Marsh b Celeste Reed", 41, null, 4, 0),
        batter("Lena Moss", "run out (Emilia Shaw)", 4, 7, 0, 0),
        batter("Jade Sinclair", "b Celeste Reed", 0, 2, 0, 0),
        batter("Pippa Lane", "b Nia Brooke", 6, 7, 0, 0),
        batter("Ivy Stone", "not out", 6, 5, 1, 0),
        batter("Clara Bell", "not out", 0, 0, 0, 0),
        batter("Ruby North", "did not bat", 0, 0, 0, 0),
      ]),
      bowlingTable("I1", [
        bowler("Sienna Park", "3", 0, 13, 0, 2, 0),
        bowler("Aila Rowan", "4", 1, 21, 2, 3, 0),
        bowler("Nia Brooke", "4", 0, 25, 2, 2, 3),
        bowler("Lara Holt", "2", 0, 11, 0, 2, 0),
        bowler("Celeste Reed", "4", 0, 27, 3, 4, 0),
        bowler("Emilia Shaw", "2", 0, 16, 0, 3, 1),
        bowler("Faye Turner", "1", 0, 13, 0, 2, 1),
      ]),
      fowTable("I1", [
        fow(1, 18, "Elena Cross", "3.6"),
        fow(2, 29, "Tara Quinn", "5.5"),
        fow(3, 39, "Mira Vale", "7.5"),
        fow(4, 97, "Rowan Hayes", "15.3"),
        fow(5, 111, "Lena Moss", "17.1"),
        fow(6, 111, "Jade Sinclair", "17.3"),
        fow(7, 120, "Pippa Lane", "18.5"),
        fow(8, 130, "Nora Finch", "19.5"),
      ]),
      partnershipsTable("I1", [
        partnership(1, "Elena Cross", "Mira Vale", 18, 5, 10, 12, 3, 8, "0.1-3.6", "Bowled (Elena Cross)"),
        partnership(2, "Tara Quinn", "Mira Vale", 11, 2, 7, 8, 2, 4, "4.1-5.5", "Caught (Tara Quinn)"),
        partnership(3, "Rowan Hayes", "Mira Vale", 10, 3, 4, 5, 3, 6, "5.6-7.5", "Leg Before Wicket (Mira Vale)"),
        partnership(4, "Rowan Hayes", "Nora Finch", 58, 12, 17, null, 29, null, "7.6-15.3", "Bowled (Rowan Hayes)"),
        partnership(5, "Lena Moss", "Nora Finch", 14, 4, 4, 7, 6, 6, "15.4-17.1", "Run Out (Lena Moss)"),
        partnership(6, "Jade Sinclair", "Nora Finch", 0, 0, 0, 2, 0, 0, "17.2-17.3", "Bowled (Jade Sinclair)"),
        partnership(7, "Pippa Lane", "Nora Finch", 9, 1, 6, 7, 2, 3, "17.4-18.5", "Bowled (Pippa Lane)"),
        partnership(8, "Ivy Stone", "Nora Finch", 10, 1, 5, 4, 4, 2, "18.6-19.5", "Caught (Nora Finch)"),
        partnership(9, "Ivy Stone", "Clara Bell", 2, 1, 1, 1, 0, 0, "19.6-19.6", "innings completion"),
      ]),
      inningsTable("I2", "Coral Bay Tides Women", 44, 10, "17.4"),
      extrasTable("I2", 0, 1, 0, 8),
      battingTable("I2", [
        batter("Aila Rowan", "b Jade Sinclair", 0, 4, 0, 0),
        batter("Maris Vale", "b Jade Sinclair", 2, 13, 0, 0),
        batter("Nia Brooke", "lbw Jade Sinclair", 0, 1, 0, 0),
        batter("Emilia Shaw (c)", "c Jade Sinclair b Mira Vale", 19, 47, 2, 0),
        batter("Lara Holt", "c Nora Finch b Tara Quinn", 1, 8, 0, 0),
        batter("Sienna Park", "b Ivy Stone", 4, null, 0, 0),
        batter("Faye Turner", "b Ivy Stone", 0, 2, 0, 0),
        batter("Bella Marsh (wk)", "b Ivy Stone", 0, 3, 0, 0),
        batter("Celeste Reed", "c Rowan Hayes b Tara Quinn", 1, 5, 0, 0),
        batter("Ruth Elms", "b Mira Vale", 3, 7, 0, 0),
        batter("Priya Cove", "not out", 5, 1, 1, 0),
      ]),
      bowlingTable("I2", [
        bowler("Jade Sinclair", "4", 2, 5, 3, 1, 0),
        bowler("Mira Vale", "3.4", 0, 9, 2, 2, 0),
        bowler("Tara Quinn", "4", 1, 11, 2, 2, 0),
        bowler("Ivy Stone", "4", 1, 8, 3, 1, 0),
        bowler("Clara Bell", "1", 0, 5, 0, 2, 0),
        bowler("Nora Finch", "1", 0, 5, 0, 0, 0),
      ]),
      fowTable("I2", [
        fow(1, 1, "Aila Rowan", "0.4"),
        fow(2, 1, "Nia Brooke", "0.5"),
        fow(3, 5, "Maris Vale", "3.6"),
        fow(4, 7, "Lara Holt", "6.2"),
        fow(5, 24, "Sienna Park", "12.1"),
        fow(6, 24, "Faye Turner", "12.3"),
        fow(7, 25, "Bella Marsh", "12.6"),
        fow(8, 28, "Celeste Reed", "14.2"),
        fow(9, 38, "Ruth Elms", "16.5"),
        fow(10, 44, "Emilia Shaw", "17.4"),
      ]),
      partnershipsTable("I2", [
        partnership(1, "Aila Rowan", "Maris Vale", 1, 1, 0, 4, 0, 0, "0.1-0.4", "Bowled (Aila Rowan)"),
        partnership(2, "Nia Brooke", "Maris Vale", 0, 0, 0, 1, 0, 0, "0.5-0.5", "Leg Before Wicket (Nia Brooke)"),
        partnership(3, "Emilia Shaw", "Maris Vale", 4, 1, 1, 3, 2, 13, "0.6-3.6", "Bowled (Maris Vale)"),
        partnership(4, "Emilia Shaw", "Lara Holt", 2, 0, 1, 11, 1, 8, "4.1-6.2", "Caught (Lara Holt)"),
        partnership(5, "Sienna Park", "Emilia Shaw", 17, 4, 4, null, 9, null, "6.3-12.1", "Bowled (Sienna Park)"),
        partnership(6, "Faye Turner", "Emilia Shaw", 0, 0, 0, 2, 0, 0, "12.2-12.3", "Bowled (Faye Turner)"),
        partnership(7, "Bella Marsh", "Emilia Shaw", 1, 1, 0, 3, 0, 0, "12.4-12.6", "Bowled (Bella Marsh)"),
        partnership(8, "Celeste Reed", "Emilia Shaw", 3, 1, 1, 5, 1, 2, "13.1-14.2", "Caught (Celeste Reed)"),
        partnership(9, "Ruth Elms", "Emilia Shaw", 10, 1, 3, 7, 6, 9, "14.3-16.5", "Bowled (Ruth Elms)"),
        partnership(10, "Priya Cove", "Emilia Shaw", 6, 0, 5, 1, 1, 4, "16.6-17.4", "Caught (Emilia Shaw)"),
      ]),
    ],
  },
  {
    instance_id: "match_0178.V4SDC",
    method: METHOD,
    tables: [
      matchTable(
        "South Meridian Institute Ground, Westhaven",
        "Shoreline Rangers",
        "bat",
        "Shoreline Rangers won by 208 runs",
        "Aaron Miles (Shoreline Rangers)"
      ),
      inningsTable("I1", "Shoreline Rangers", 282, 10, "47.2"),
      extrasTable("I1", 2, 1, 1, 17),
      battingTable("I1", [
        batter("Finn Archer", "c Arin Wells b Miles Benton", 74, null, 9, 1),
        batter("Leo Marsh", "c Aiden Scott b Zane Cooper", 18, 21, 2, 0),
        batter("Rory Blake", "b Zane Cooper", 0, 2, 0, 0),
        batter("Miles Carter", "c Julian Vale b Aiden Scott", 36, null, 1, 1),
        batter("Dylan Vale", "c Isaac Vale b Miles Benton", 63, 60, 6, 1),
        batter("Connor Wells", "b Zane Cooper", 12, 15, 1, 0),
        batter("Evan Price", "b Aiden Scott", 6, 12, 1, 0),
        batter("Noah Grant", "c Arin Wells b Miles Benton", 24, 28, 2, 0),
        batter("Aaron Miles", "b Miles Benton", 4, 5, 0, 0),
        batter("Toby Reed", "not out", 19, 15, 1, 0),
        batter("Logan Shaw", "b Cameron Ellis", 5, 5, 0, 0),
      ]),
      bowlingTable("I1", [
        bowler("Tyler Quinn", "5", 0, 43, 0, 3, 0),
        bowler("Zane Cooper", "10", 0, 49, 3, 2, 0),
        bowler("Miles Benton", "10", 0, 56, 4, 3, 0),
        bowler("Blake Morgan", "5", 0, 32, 0, 0, 0),
        bowler("Evan Carter", "7", 0, 43, 0, 2, 0),
        bowler("Aiden Scott", "8", 1, 24, 2, 3, 0),
        bowler("Cameron Ellis", "2.2", 0, 32, 1, 4, 1),
      ]),
      fowTable("I1", [
        fow(1, 62, "Leo Marsh", "8.4"),
        fow(2, 62, "Rory Blake", "8.6"),
        fow(3, 138, "Miles Carter", "23.4"),
        fow(4, 144, "Finn Archer", "24.2"),
        fow(5, 169, "Connor Wells", "28.6"),
        fow(6, 184, "Evan Price", "32.4"),
        fow(7, 252, "Dylan Vale", "42.2"),
        fow(8, 258, "Aaron Miles", "43.1"),
        fow(9, 265, "Noah Grant", "44.5"),
        fow(10, 282, "Logan Shaw", "47.2"),
      ]),
      partnershipsTable("I1", [
        partnership(1, "Finn Archer", "Leo Marsh", 62, 5, 39, 33, 18, 21, "0.1-8.4", "Caught (Leo Marsh)"),
        partnership(2, "Rory Blake", "Finn Archer", 0, 0, 0, 2, 0, 0, "8.5-8.6", "Bowled (Rory Blake)"),
        partnership(3, "Finn Archer", "Miles Carter", 76, 5, 35, null, 36, null, "9.1-23.4", "Caught (Miles Carter)"),
        partnership(4, "Finn Archer", "Dylan Vale", 6, 2, 0, 0, 4, 4, "23.5-24.2", "Caught (Finn Archer)"),
        partnership(5, "Dylan Vale", "Connor Wells", 25, 0, 13, 12, 12, 15, "24.3-28.6", "Bowled (Connor Wells)"),
        partnership(6, "Dylan Vale", "Evan Price", 15, 0, 9, 9, 6, 12, "29.1-32.4", "Bowled (Evan Price)"),
        partnership(7, "Dylan Vale", "Noah Grant", 68, 7, 37, 35, 24, 28, "32.5-42.2", "Caught (Dylan Vale)"),
        partnership(8, "Aaron Miles", "Noah Grant", 6, 2, 4, 5, 0, 0, "42.3-43.1", "Bowled (Aaron Miles)"),
        partnership(9, "Toby Reed", "Noah Grant", 7, 0, 7, 3, 0, 0, "43.2-44.5", "Caught (Noah Grant)"),
        partnership(10, "Toby Reed", "Logan Shaw", 17, 0, 12, 12, 5, 5, "44.6-47.2", "Bowled (Logan Shaw)"),
      ]),
      inningsTable("I2", "Meridian Strikers", 74, 10, "24.4"),
      extrasTable("I2", 0, 3, 1, 12),
      battingTable("I2", [
        batter("Arin Wells (wk)", "b Connor Reed", 24, null, 2, 0),
        batter("Isaac Vale", "lbw Caleb Turner", 0, 1, 0, 0),
        batter("Evan Carter (c)", "b Logan Shaw", 7, null, 0, 0),
        batter("Tyler Quinn", "c Dylan Vale b Aaron Miles", 13, 25, 2, 0),
        batter("Aiden Scott", "c Finn Archer b Tyler Quinn", 6, 13, 0, 0),
        batter("Blake Morgan", "b Aaron Miles", 0, 3, 0, 0),
        batter("Julian Vale", "b Connor Reed", 0, 6, 0, 0),
        batter("Leo Foster", "b Aaron Miles", 2, 25, 0, 0),
        batter("Cameron Ellis", "st Owen Hayes b Aaron Miles", 1, 10, 0, 0),
        batter("Miles Benton", "b Tyler Quinn", 1, 12, 0, 0),
        batter("Zane Cooper", "not out", 4, 10, 1, 0),
      ]),
      bowlingTable("I2", [
        bowler("Caleb Turner", "5", 0, 31, 1, 6, 0),
        bowler("Finn Archer", "2", 0, 7, 0, 1, 0),
        bowler("Logan Shaw", "5", 0, 14, 1, 0, 0),
        bowler("Connor Reed", "4", 1, 8, 2, 2, 1),
        bowler("Aaron Miles", "5", 2, 4, 4, 2, 0),
        bowler("Tyler Quinn", "3.4", 1, 7, 2, 1, 0),
      ]),
      fowTable("I2", [
        fow(1, 1, "Isaac Vale", "0.4"),
        fow(2, 27, "Evan Carter", "6.2"),
        fow(3, 45, "Arin Wells", "11.4"),
        fow(4, 54, "Tyler Quinn", "14.5"),
        fow(5, 54, "Blake Morgan", "15.2"),
        fow(6, 54, "Julian Vale", "16.3"),
        fow(7, 58, "Aiden Scott", "18.1"),
        fow(8, 67, "Leo Foster", "21.5"),
        fow(9, 70, "Cameron Ellis", "23.2"),
        fow(10, 74, "Miles Benton", "24.4"),
      ]),
      partnershipsTable("I2", [
        partnership(1, "Arin Wells", "Isaac Vale", 1, 0, 1, 3, 0, 1, "0.1-0.4", "Leg Before Wicket (Isaac Vale)"),
        partnership(2, "Arin Wells", "Evan Carter", 26, 6, 13, null, 7, null, "0.5-6.2", "Bowled (Evan Carter)"),
        partnership(3, "Tyler Quinn", "Arin Wells", 18, 2, 6, 10, 10, 2, "6.3-11.4", "Bowled (Arin Wells)"),
        partnership(4, "Tyler Quinn", "Aiden Scott", 9, 0, 7, 15, 2, 5, "11.5-14.5", "Caught (Tyler Quinn)"),
        partnership(5, "Blake Morgan", "Aiden Scott", 0, 0, 0, 3, 0, 0, "14.6-15.2", "Bowled (Blake Morgan)"),
        partnership(6, "Julian Vale", "Aiden Scott", 0, 0, 0, 6, 0, 0, "15.3-16.3", "Bowled (Julian Vale)"),
        partnership(7, "Aiden Scott", "Leo Foster", 4, 0, 4, 8, 0, 3, "16.4-18.1", "Caught (Aiden Scott)"),
        partnership(8, "Leo Foster", "Cameron Ellis", 9, 6, 2, 12, 1, 10, "18.2-21.5", "Bowled (Leo Foster)"),
        partnership(9, "Miles Benton", "Cameron Ellis", 3, 2, 1, 12, 0, 0, "21.6-23.2", "Stumped (Cameron Ellis)"),
        partnership(10, "Zane Cooper", "Miles Benton", 4, 0, 4, 10, 0, 0, "23.3-24.4", "Bowled (Miles Benton)"),
      ]),
    ],
  },
];

const flattenTables = (tables) => {
  const tuples = [];
  for (const t of tables) {
    for (let index = 0; index < t.rows.length; index += 1) {
      const row = t.rows[index];
      const entity =
        row.batter ??
        row.bowler ??
        row.team ??
        (row.wicket !== undefined ? `wicket_${row.wicket}` : `${t.table_type}_row_${index + 1}`);
      for (const column of t.columns) {
        tuples.push({
          entity,
          team_or_innings: t.innings,
          event_or_attribute: `${t.table_type}.${column}`,
          value: row[column],
        });
      }
    }
  }
  return tuples;
};

const conflictTuples = {
  "match_0185.V4SDC": [
    { entity: "Tidehaven", team_or_innings: "I1", event_or_attribute: "extras.total", value: 17 },
    { entity: "Rohan Blake", team_or_innings: "I1", event_or_attribute: "batting.runs", value: 9 },
    { entity: "wicket_5", team_or_innings: "I1", event_or_attribute: "fall_of_wickets.score", value: 25 },
    { entity: "Tidehaven", team_or_innings: "I1", event_or_attribute: "innings_summary.total", value: 37 },
  ],
  "match_0106.V4SDC": [
    { entity: "Meadowridge Spirits Women", team_or_innings: "I1", event_or_attribute: "extras.total", value: 32 },
    { entity: "Elena Cross", team_or_innings: "I1", event_or_attribute: "batting.runs", value: 11 },
    { entity: "partnership_4", team_or_innings: "I1", event_or_attribute: "partnerships.runs", value: 59 },
    { entity: "Celeste Reed", team_or_innings: "I1", event_or_attribute: "bowling.wickets", value: 4 },
    { entity: "partnership_5", team_or_innings: "I2", event_or_attribute: "partnerships.runs", value: 18 },
    { entity: "Emilia Shaw", team_or_innings: "I2", event_or_attribute: "batting.runs", value: 20 },
  ],
  "match_0178.V4SDC": [
    { entity: "Shoreline Rangers", team_or_innings: "I1", event_or_attribute: "extras.total", value: 24 },
    { entity: "Finn Archer", team_or_innings: "I1", event_or_attribute: "batting.runs", value: 75 },
    { entity: "partnership_3", team_or_innings: "I1", event_or_attribute: "partnerships.runs", value: 77 },
    { entity: "Dylan Vale", team_or_innings: "I1", event_or_attribute: "batting.runs", value: 64 },
    { entity: "Zane Cooper", team_or_innings: "I1", event_or_attribute: "bowling.wickets", value: 5 },
    { entity: "Shoreline Rangers", team_or_innings: "I1", event_or_attribute: "innings_summary.total", value: 283 },
    { entity: "partnership_2", team_or_innings: "I2", event_or_attribute: "partnerships.runs", value: 27 },
    { entity: "Arin Wells", team_or_innings: "I2", event_or_attribute: "batting.runs", value: 25 },
    { entity: "wicket_3", team_or_innings: "I2", event_or_attribute: "fall_of_wickets.score", value: 46 },
    { entity: "Tyler Quinn", team_or_innings: "I2", event_or_attribute: "batting.runs", value: 14 },
    { entity: "Aaron Miles", team_or_innings: "I2", event_or_attribute: "bowling.wickets", value: 3 },
    { entity: "Aaron Miles", team_or_innings: "I2", event_or_attribute: "bowling.wickets", value: 5 },
    { entity: "Meridian Strikers", team_or_innings: "I2", event_or_attribute: "extras.total", value: 17 },
  ],
};

const raw = predictions.map((prediction) => {
  const integrated = flattenTables(prediction.tables);
  return {
    instance_id: prediction.instance_id,
    method: METHOD,
    variant: "paper-style T3 direct-integration variant",
    stage_1_text_to_tuple: {
      tuple_fields: ["entity", "team_or_innings", "event_or_attribute", "value"],
      tuples: [...integrated, ...conflictTuples[prediction.instance_id]],
    },
    stage_2_direct_tuple_integration: {
      integration_mode: "direct",
      generated_code_used: false,
      tuples: integrated,
    },
    stage_3_tuple_to_table: {
      tables: prediction.tables,
    },
  };
});

const jsonl = (items) => `${items.map((item) => JSON.stringify(item)).join("\n")}\n`;

fs.writeFileSync(path.join(outDir, `${METHOD}.raw.jsonl`), jsonl(raw));
fs.writeFileSync(path.join(outDir, `${METHOD}.predictions.jsonl`), jsonl(predictions));
