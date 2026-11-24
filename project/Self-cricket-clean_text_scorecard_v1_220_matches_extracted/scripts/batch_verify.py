import sys; sys.path.insert(0,'.')
from scripts.verify_candidate import verify
for m in sys.argv[1:]:
    r = verify(m)
    print(f'{m}: {r["status"]} errors={r["error_count"]}')
    for e in r["errors"]:
        print(f'  {e}')
