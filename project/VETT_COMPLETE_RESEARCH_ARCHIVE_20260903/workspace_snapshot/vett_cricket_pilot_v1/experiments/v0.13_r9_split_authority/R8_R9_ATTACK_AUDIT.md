# R8-to-R9 Construction-Fingerprint Attack Audit

## Finding

R8 passes its mechanical gates, but its 170 same-event recaps create a density that is too conspicuous for corpus-scale use. R9 deliberately accepts a slightly lower controlled error in exchange for a less artificial surface and a harder evidence-composition requirement.

| Measure | R8 | R9 | Change |
| --- | ---: | ---: | ---: |
| Words | 14789 | 16131 | +1342 |
| Segments | 607 | 599 | -8 |
| Recaps | 170 | 102 | -68 |
| Most-common recap-gap share | 76.33% | 46.53% | -29.80 pp |
| Long exact repeated sentences | 0 | 0 | 0 |
| Revision + recap error | 62.24% | 59.18% | -3.06 pp |
| Three-state controlled error | 65.31% | 62.93% | -2.38 pp |

## Structural gain

- R9 removes 68 of R8's 170 recaps.
- Every one of the 60 revisions now requires two nonadjacent authority fragments.
- The first fragment establishes event category and legal-ball status while withholding the number.
- The later fragment supplies only the accepted magnitude and refers back by production cue.
- Missing either half causes a measurable, independently reported error pattern.
- R9 is a discourse variant of `match_0122`, not a fourth independent root.
- The same four partnership-ball repairs remain blocked on human support review.
