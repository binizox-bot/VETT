# Method self-test trace

## T³

### Text-to-Tuple

Every event-like mention becomes a flat
`(batter, bowler, outcome)` tuple. Source, scope, replay status, finality,
arrival order and event identity are not present in the tuple.

### Integration

- Variant A counts every tuple.
- Variant B removes exact duplicate tuples, then counts.

### Tuple-to-Table

Summary, batting and bowling aggregates are generated. Canonical event order is
not recoverable from the flat multiset, so FOW and partnerships remain absent.

## Map&Make

### Atomization

Every target-linked mention becomes an atomic outcome proposition. For this
optimistic diagnostic, hidden event alignment is supplied.

### Schema

Summary, batting, bowling, FOW and partnership schemas are correctly inferred.

### Table filling

- Variant A retains the first proposition aligned to an event.
- Variant B retains the last proposition aligned to an event.

Neither policy represents a version graph or authoritative-source hierarchy.
Independent propositions also do not recover canonical event ordering.
