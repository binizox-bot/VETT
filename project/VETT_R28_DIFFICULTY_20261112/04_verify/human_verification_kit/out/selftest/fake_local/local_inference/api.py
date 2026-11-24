def annotate(task_id, sample, caller='t24'):
    text = (sample.get('span_text') or sample.get('passage') or '').lower()
    topic = 'RUNS' if 'run' in text else 'BOWLING'
    return {'status': 'OK', 'annotation': {'topic': topic, 'supported': True}, 'degraded': None,
            'ledger_entry': {'model_tag': 'fake-local-for-selftest',
                            'prompt_template_version': 'S1.span_topic.v4',
                            'input_sha256': '0' * 64}}
