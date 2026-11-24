# B022 C_adjudication

- hypothesis: Same event under formal reassignment, maintained original, and no notice; separates notification understanding, old-value extraction, and propagation.
- rationale: full 8-event C batch after 4-event dev batch
- created: 2026-11-18T15:07:46+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; change gold=new, maintain/no_notice gold=old
- sources: attribution_followup/samples.json, scorecard-derived event

## Positions

- match_0010 innings 1
- match_0012 innings 1
- match_0015 innings 1
- match_0030 innings 1

## Conditions

C_change, C_maintain, C_no_notice

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0010 inn1 C_change qwen2.5:7b-instruct-q4_K_M (attribution) key=25957cb6c1ce
- match_0010 inn1 C_change llama3.1:8b (attribution) key=e049135de4a5
- match_0010 inn1 C_change gemma2:9b (attribution) key=4f35d2811758
- match_0010 inn1 C_maintain qwen2.5:7b-instruct-q4_K_M (attribution) key=a3df935e8d2e
- match_0010 inn1 C_maintain llama3.1:8b (attribution) key=60eee34a76a0
- match_0010 inn1 C_maintain gemma2:9b (attribution) key=453ef0bee3ae
- match_0010 inn1 C_no_notice qwen2.5:7b-instruct-q4_K_M (attribution) key=332c7ffbb5e5
- match_0010 inn1 C_no_notice llama3.1:8b (attribution) key=12ef67cab441
- match_0010 inn1 C_no_notice gemma2:9b (attribution) key=164063601569
- match_0012 inn1 C_change qwen2.5:7b-instruct-q4_K_M (attribution) key=f1eb3d2506cb
- match_0012 inn1 C_change llama3.1:8b (attribution) key=6a3931c1ad52
- match_0012 inn1 C_change gemma2:9b (attribution) key=24a471368dc3
- match_0012 inn1 C_maintain qwen2.5:7b-instruct-q4_K_M (attribution) key=8fe96570b1be
- match_0012 inn1 C_maintain llama3.1:8b (attribution) key=ae6ef3484f73
- match_0012 inn1 C_maintain gemma2:9b (attribution) key=402ddd0bb0c1
- match_0012 inn1 C_no_notice qwen2.5:7b-instruct-q4_K_M (attribution) key=687769aa4aea
- match_0012 inn1 C_no_notice llama3.1:8b (attribution) key=01792d926c98
- match_0012 inn1 C_no_notice gemma2:9b (attribution) key=61762e6f3f18
- match_0015 inn1 C_change qwen2.5:7b-instruct-q4_K_M (attribution) key=b12d971ea628
- match_0015 inn1 C_change llama3.1:8b (attribution) key=1aea0a8ba7f9
- match_0015 inn1 C_change gemma2:9b (attribution) key=67cf8b11c139
- match_0015 inn1 C_maintain qwen2.5:7b-instruct-q4_K_M (attribution) key=1e24b62518c0
- match_0015 inn1 C_maintain llama3.1:8b (attribution) key=eb9d1ac352da
- match_0015 inn1 C_maintain gemma2:9b (attribution) key=2097ec627f59
- match_0015 inn1 C_no_notice qwen2.5:7b-instruct-q4_K_M (attribution) key=113b4217868c
- match_0015 inn1 C_no_notice llama3.1:8b (attribution) key=2dbadf8aca25
- match_0015 inn1 C_no_notice gemma2:9b (attribution) key=a5a305bd22d3
- match_0030 inn1 C_change qwen2.5:7b-instruct-q4_K_M (attribution) key=65dade6ba5a9
- match_0030 inn1 C_change llama3.1:8b (attribution) key=4e41fcaa7e69
- match_0030 inn1 C_change gemma2:9b (attribution) key=2921bab5bd02
- match_0030 inn1 C_maintain qwen2.5:7b-instruct-q4_K_M (attribution) key=d202ce36f9a9
- match_0030 inn1 C_maintain llama3.1:8b (attribution) key=f5d8d59b3d22
- match_0030 inn1 C_maintain gemma2:9b (attribution) key=f139fa39600c
- match_0030 inn1 C_no_notice qwen2.5:7b-instruct-q4_K_M (attribution) key=fd3ae0e3611e
- match_0030 inn1 C_no_notice llama3.1:8b (attribution) key=10e7fd2a85b2
- match_0030 inn1 C_no_notice gemma2:9b (attribution) key=0741e7fd0be5

## Rejected candidates

- match_0003 C_change: duplicate_existing_task
- match_0003 C_change: duplicate_existing_task
- match_0003 C_change: duplicate_existing_task
- match_0003 C_maintain: duplicate_existing_task
- match_0003 C_maintain: duplicate_existing_task
- match_0003 C_maintain: duplicate_existing_task
- match_0003 C_no_notice: duplicate_existing_task
- match_0003 C_no_notice: duplicate_existing_task
- match_0003 C_no_notice: duplicate_existing_task
- match_0008 C_change: duplicate_existing_task
- match_0008 C_change: duplicate_existing_task
- match_0008 C_change: duplicate_existing_task
- match_0008 C_maintain: duplicate_existing_task
- match_0008 C_maintain: duplicate_existing_task
- match_0008 C_maintain: duplicate_existing_task
- match_0008 C_no_notice: duplicate_existing_task
- match_0008 C_no_notice: duplicate_existing_task
- match_0008 C_no_notice: duplicate_existing_task
- match_0017 C_change: duplicate_existing_task
- match_0017 C_change: duplicate_existing_task
- match_0017 C_change: duplicate_existing_task
- match_0017 C_maintain: duplicate_existing_task
- match_0017 C_maintain: duplicate_existing_task
- match_0017 C_maintain: duplicate_existing_task
- match_0017 C_no_notice: duplicate_existing_task
- match_0017 C_no_notice: duplicate_existing_task
- match_0017 C_no_notice: duplicate_existing_task
- match_0026 C_change: duplicate_existing_task
- match_0026 C_change: duplicate_existing_task
- match_0026 C_change: duplicate_existing_task
- match_0026 C_maintain: duplicate_existing_task
- match_0026 C_maintain: duplicate_existing_task
- match_0026 C_maintain: duplicate_existing_task
- match_0026 C_no_notice: duplicate_existing_task
- match_0026 C_no_notice: duplicate_existing_task
- match_0026 C_no_notice: duplicate_existing_task
