# 归属更正新样本：作答核对（ANSWER KEY）

你的三问回答与仓库中的 gold 完全一致：**3/3 正确**。

## 1. 改判的是哪次出局

- 正确：第二局（Sandbank Spirits Women 的追分 innings），Lina Fox 得 0 分时的出局；原记 Nora Vale，改判给 Ruby North。
- 证据句（attribution_named，char 1239）：
  "The chase took a hit when Lina Fox fell to Ruby North for 0."
- 对照句（control，char 1239）：
  "The chase took a hit when Lina Fox fell to Nora Vale for 0."

## 2. 两位投手的 wicket 数

| 字段 | control | attribution_named | 你的回答 |
|---|---:|---:|---|
| inn2.bowl1_Nora Vale.figures | 4/6 | 3/6 | 3 个 wickets（3/6）✓ |
| inn2.bowl2_Ruby North.figures | 3/7 | 4/7 | 4 个 wickets（4/7）✓ |

- 证据句（attribution_named，char 3337）："Nora Vale, whose 3 for 6 made the deepest incisions."
- 证据句（attribution_named，char 3390）："Ruby North kept the pressure on with 4 for 7..."

## 3. 全队 wicket 总数

- 正确：第二局仍是 10。
- 证据句（attribution_named，char 2888）：
  "Sandbank Spirits Women closed on 55 for 10 from 16.5 overs, the 164 runs margin reflecting a chase that had been tested but never broken.."
- 一减一加：Nora 4→3，Ruby 3→4，总和不变。

## 三项评分检查

| 检查 | 结果 |
|---|---|
| Nora 比 control 少 1 个 wicket | 通过（4→3） |
| Ruby 比 control 多 1 个 wicket | 通过（3→4） |
| 全队 total_wickets 与 control 相同 | 通过（10→10） |

## 你可能需要知道的两个细节

1. 你提到的 "55 for 10 from 16.5 overs" 确实在文本中（char 2888），不是只在 scorecard 里；所以全队总数是可从题面直接核对的。
2. 当前样本用 **batter + 比分（Lina Fox, 0/1）** 定位这次出局，没有写 over 号。若下一轮要求“明确标出局号/over 号”，需要在改判句里补 over（例如 "in the 4th over"），否则只能定位到“Lina Fox 这次出局”，不能定位到某一球。

## 附件缺口

你提到 attribution_named 的完整正文未随附件提供；仓库中该文件存在：
- attribution_case/control/commentary.txt
- attribution_case/attribution_named/commentary.txt

两份全文也已汇总到 attribution_case/FULL_TEXT.md，便于独立复核。
