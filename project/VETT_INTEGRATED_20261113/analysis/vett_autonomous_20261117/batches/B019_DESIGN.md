# B019 C_adjudication

- hypothesis: Same event under formal reassignment, maintained original, and no notice; separates notification understanding, old-value extraction, and propagation.
- rationale: branch C dev batch before coverage sweep continues
- created: 2026-11-18T15:00:58+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; change gold=new, maintain/no_notice gold=old
- sources: attribution_followup/samples.json, scorecard-derived event

## Positions

- match_0003 innings 1
- match_0008 innings 1
- match_0017 innings 1
- match_0026 innings 1

## Conditions

C_change, C_maintain, C_no_notice

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0003 inn1 C_change qwen2.5:7b-instruct-q4_K_M (attribution) key=ade8dcfdb041
- match_0003 inn1 C_change llama3.1:8b (attribution) key=70ab09ca26a2
- match_0003 inn1 C_change gemma2:9b (attribution) key=a8f596ff47be
- match_0003 inn1 C_maintain qwen2.5:7b-instruct-q4_K_M (attribution) key=4944ae12cfd6
- match_0003 inn1 C_maintain llama3.1:8b (attribution) key=f6372d2d80dd
- match_0003 inn1 C_maintain gemma2:9b (attribution) key=163ad5594336
- match_0003 inn1 C_no_notice qwen2.5:7b-instruct-q4_K_M (attribution) key=31d7e41070f9
- match_0003 inn1 C_no_notice llama3.1:8b (attribution) key=e8ca773c41cc
- match_0003 inn1 C_no_notice gemma2:9b (attribution) key=f3da3a43c13f
- match_0008 inn1 C_change qwen2.5:7b-instruct-q4_K_M (attribution) key=d18e79ac7d61
- match_0008 inn1 C_change llama3.1:8b (attribution) key=866bc8e1d116
- match_0008 inn1 C_change gemma2:9b (attribution) key=f18595808cbe
- match_0008 inn1 C_maintain qwen2.5:7b-instruct-q4_K_M (attribution) key=6cb5b8aa6232
- match_0008 inn1 C_maintain llama3.1:8b (attribution) key=8efad965b396
- match_0008 inn1 C_maintain gemma2:9b (attribution) key=d897c83d6d24
- match_0008 inn1 C_no_notice qwen2.5:7b-instruct-q4_K_M (attribution) key=d52b72961125
- match_0008 inn1 C_no_notice llama3.1:8b (attribution) key=5d38918c1eef
- match_0008 inn1 C_no_notice gemma2:9b (attribution) key=a6e57a54cf08
- match_0017 inn1 C_change qwen2.5:7b-instruct-q4_K_M (attribution) key=90bb6de86770
- match_0017 inn1 C_change llama3.1:8b (attribution) key=0ff44673a2eb
- match_0017 inn1 C_change gemma2:9b (attribution) key=8440e8c86163
- match_0017 inn1 C_maintain qwen2.5:7b-instruct-q4_K_M (attribution) key=d21fa70b6bd0
- match_0017 inn1 C_maintain llama3.1:8b (attribution) key=06d81232c7e9
- match_0017 inn1 C_maintain gemma2:9b (attribution) key=96d8efac7ba6
- match_0017 inn1 C_no_notice qwen2.5:7b-instruct-q4_K_M (attribution) key=e80374b2d2ab
- match_0017 inn1 C_no_notice llama3.1:8b (attribution) key=b550ddc3a855
- match_0017 inn1 C_no_notice gemma2:9b (attribution) key=a1ad99d21eb5
- match_0026 inn1 C_change qwen2.5:7b-instruct-q4_K_M (attribution) key=3776ecb3acf3
- match_0026 inn1 C_change llama3.1:8b (attribution) key=896b0bc03702
- match_0026 inn1 C_change gemma2:9b (attribution) key=f644caa1625e
- match_0026 inn1 C_maintain qwen2.5:7b-instruct-q4_K_M (attribution) key=7f6e00c8291e
- match_0026 inn1 C_maintain llama3.1:8b (attribution) key=80f83d95cd8d
- match_0026 inn1 C_maintain gemma2:9b (attribution) key=57dd2224d17d
- match_0026 inn1 C_no_notice qwen2.5:7b-instruct-q4_K_M (attribution) key=8c96d3447a23
- match_0026 inn1 C_no_notice llama3.1:8b (attribution) key=cbaf4ddf58c8
- match_0026 inn1 C_no_notice gemma2:9b (attribution) key=1ad4879b9cd8

## Rejected candidates

- none
