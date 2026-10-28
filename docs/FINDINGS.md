# Findings: open-world network-flow triage

## Question and evaluation

When an attack category is absent from training, which ranking policy surfaces it within a fixed review budget, and how many benign flows does that queue include?

The notebook evaluates nine leave-one-attack-category-out folds on UNSW-NB15. The published files contain 175,341 training flows and 82,332 test flows. After excluding 8,541 test rows with exact input matches in training, the primary test set contains **73,791 flows**. For each fold, the XGBoost known-risk model trains on normal traffic and the remaining attack categories. An Isolation Forest is fit on normal training flows only. Both rank the same test set without access to test labels.

At a given budget, the policies select the same number of flows: known-risk only; novelty only; and a two-lane queue with 75% of slots from known-risk ranking and 25% from novelty ranking among rows not already chosen. The 10% budget (7,379 flows) is primary. Category-macro averages below include eight categories with at least 100 primary-test examples; `Worms` (44 examples) is excluded from the macro and reported separately.

## Primary result: the trade-off at a 10% budget

| Policy | Held-out-category recall | Known-category recall | Precision | Normal alerts per 1,000 normal flows | Held-out precision in novelty lane |
| --- | ---: | ---: | ---: | ---: | ---: |
| Known-risk only | 0.2% | 22.7% | 100.0% | 0.03 | — |
| Novelty only | **13.3%** | 13.1% | 67.6% | 67.2 | 8.4% |
| Two-lane 75/25 | 4.6% | **20.1%** | **91.1%** | 18.5 | 8.6% |

The novelty queue finds more withheld-category flows than the other two policies, at the cost of sending substantially more normal flows for review. The two-lane policy recovers part of the known-category performance while retaining some open-world recall and reducing the benign alert rate relative to novelty-only. It does **not** maximize held-out recall.

Known-risk-only has extremely high precision on this test set but almost no macro held-out-category recall. That result captures the central open-world tension: a policy can rank known attack patterns cleanly while failing to surface a category excluded from training.

## Review-budget sensitivity

| Budget | Policy | Held-out recall | Known-category recall | Precision | Normal alerts per 1,000 |
| ---: | --- | ---: | ---: | ---: | ---: |
| 5% | Known-risk only | 0.1% | 11.3% | 100.0% | 0.00 |
| 5% | Novelty only | 7.2% | 6.3% | 63.7% | 37.7 |
| 5% | Two-lane 75/25 | 2.5% | 10.3% | 93.2% | 7.1 |
| 10% | Known-risk only | 0.2% | 22.3% | 100.0% | 0.03 |
| 10% | Novelty only | 14.1% | 13.1% | 67.5% | 67.4 |
| 10% | Two-lane 75/25 | 4.6% | 19.8% | 91.1% | 18.5 |
| 20% | Known-risk only | 0.4% | 45.1% | 99.5% | 2.0 |
| 20% | Novelty only | 41.1% | 29.3% | 75.4% | 102.1 |
| 20% | Two-lane 75/25 | 8.1% | 39.6% | 90.2% | 40.7 |

Across all budgets, novelty-only leads held-out-category recall. The two-lane policy occupies a middle ground, with higher known-category recall and fewer normal alerts than novelty-only. The 75/25 setting is a transparent example, not an optimized split or a recommendation for a real team.

## Category variation

At 10%, novelty-only held-out-category recall ranges from **6.7% for Reconnaissance** to **21.0% for DoS** among categories with at least 100 examples. The two-lane policy ranges from **1.4% for Reconnaissance** to **11.2% for DoS**. Fuzzers, Exploits, and Generic have substantial test support but do not respond uniformly to the novelty ranking. This is why the category-level table in the notebook matters alongside the macro average.

`Worms` has only 44 primary-test examples. Novelty-only selects 9 of them (20.5% recall), while the two-lane policy selects 2 (4.5%). These small counts are descriptive, not stable estimates.

## Example model explanation

For one held-out `Exploits` flow, the known-risk model score is **0.8452** and the Isolation Forest score is **0.4596** (higher indicates more unusual). The notebook displays local XGBoost contributions for the score and compares selected flow values with normal-flow percentiles. This example helps inspect how the known-risk model ranks a flow; it does not explain the Isolation Forest score or establish that a feature caused an attack.

## What the results support

- Unknown-category evaluation changes the question from “does the model detect attacks represented in training?” to “does the queue surface a category omitted from training?”
- Novelty ranking can recover withheld-category examples that known-risk ranking misses, but it introduces more normal-flow review.
- A two-lane allocation makes the trade-off explicit and measurable; this benchmark does not prove that 75/25 is optimal.
- The experiment is a useful research MVP on an established open-world problem. It does not introduce a new detector or establish a new industry pattern.

## Limitations

- A withheld UNSW-NB15 category is only a controlled proxy for unknown behavior, not a zero-day attack.
- The published files have no timestamps. The experiment cannot evaluate temporal generalization or future drift.
- UNSW-NB15 is cyber-range generated and attack-heavy. Precision and normal-alert rates are dataset-specific, not estimates for production traffic.
- Exact input-overlap removal reduces one leakage path but cannot remove broader dependence among flows.
- `Worms` has very low support; its recall is unstable.
- The dataset's recent-connection-count features are supplied fields. They cannot be reconstructed from the two split files alone.
- This is a notebook benchmark. It has no live sensor, analyst workflow, case-management queue, feedback loop, or automatic response.

## References

- Moustafa and Slay, “UNSW-NB15: a comprehensive data set for network intrusion detection systems,” *MilCIS 2015*, [DOI 10.1109/MilCIS.2015.7348942](https://doi.org/10.1109/MilCIS.2015.7348942).
- “Toward Open-World Network Intrusion Detection via Open Recognition and Inspection,” IEEE 2025, [IEEE Xplore](https://ieeexplore.ieee.org/document/11159092/).
- “SPIDER: A Semi-Supervised Continual Learning-Based Network Intrusion Detection System,” IEEE INFOCOM 2024, [project page](https://newslab.iith.ac.in/publications/spider-a-semi-supervised-continual-learning-based-network-intrusion-detection-system/).
