# R13-C to R14 comparison

| Metric | R13-C | R14-B |
| --- | ---: | ---: |
| Scored atomic cells | 101 | 101 |
| Target rows | 17 | 17 |
| Independent decision components | 17 | 50 |
| Cells per decision component | 5.94 | 2.02 |
| Rows with mixed master/reserve truth | 0/17 | 17/17 |
| Formula-derived cells | not separately controlled | 78/101 |
| Joint multi-field cells including FOW tuples | 101 row-bundled | 86/101 |
| Best fixed source by field-name errors | not gated | 43/101 |
| Best fixed source by family errors | 46/101 | 50/101 |

R13-C tests whether a model can select the correct complete row through global cricket conservation. R14-B tests whether it can construct a row field by field after both scorer folios become internally mixed.

The R14 metric does not imply 50 statistically independent random variables. A decision component is the smallest set of fields jointly resolved by one public relation or event tuple. It is used to avoid treating several mechanically coupled cells as separate reasoning successes.

