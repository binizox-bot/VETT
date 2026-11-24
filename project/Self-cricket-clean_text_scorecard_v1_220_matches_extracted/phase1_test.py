"""Phase 1: Test upgrade on match_0050."""
import sys; sys.path.insert(0,'.')
from src.upgrader import *

mid = 'match_0050'
original = read_original(mid)
sc = read_scorecard(mid)
evidence = extract_canonical_values(sc)
audit_before = audit_commentary(original, evidence)

print('=== match_0050 BEFORE ===')
print(f'Length: {len(original)} chars')
print_audit(audit_before, 'BEFORE')
print(f'Noise: {audit_before["noise_numbers"][:15]}')
print(f'Missing: {audit_before["missing_evidence"][:10]}')
print()
print('Protected evidence:')
for k,v in sorted(evidence.items()):
    print(f'  {k}: {v}')

# Also check regenerated version
print()
print('=== match_0050 REGENERATED ===')
reg_path = f'output/regenerated/{mid}/commentary.txt'
reg = open(reg_path, encoding='utf-8').read()
audit_regen = audit_commentary(reg, evidence)
print(f'Length: {len(reg)} chars')
print_audit(audit_regen, 'REGEN')
noise = audit_regen.get('noise_numbers', [])
missing = audit_regen.get('missing_evidence', [])
print(f'Noise: {noise[:15]}')
print(f'Missing: {missing[:10]}')

# Check upgraded version
print()
print('=== match_0050 UPGRADED ===')
upg_path = f'output/upgraded/{mid}/commentary.txt'
upg = open(upg_path, encoding='utf-8').read()
audit_upg = audit_commentary(upg, evidence)
print(f'Length: {len(upg)} chars')
print_audit(audit_upg, 'UPGD')
print(f'Noise: {audit_upg.get("noise_numbers",[])[:15]}')
print(f'Missing: {audit_upg.get("missing_evidence",[])[:10]}')
