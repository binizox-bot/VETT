# Published D runs: rebuild material

expand.jsonl stores prompt_sha256 and text_sha256 but NOT the prompt body. Rebuild the exact prompt with:

    python VETT_INTEGRATED_20261113/analysis/vett_overnight_20261114/expand.py

and verify each row's prompt_sha256 and text_sha256 before reuse. Source text is the published commentary under Self-cricket-clean_text_scorecard_v1_220_matches/match_*/commentary.txt.
