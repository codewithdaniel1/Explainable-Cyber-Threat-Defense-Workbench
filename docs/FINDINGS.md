# Explainable Cyber Threat Defense Workbench: findings

## Research question and data

Can three simple detection tracks provide useful signals to explainable network-flow classifiers, and do track alerts find attack-labeled flows missed by the selected model without an excessive increase in review work?

The [UNSW-NB15 published partition](https://research.unsw.edu.au/projects/unsw-nb15-dataset) contains **175,341 training flows** (119,341 attack-labeled; 68.1%) and **82,332 test flows** (45,332 attack-labeled; 55.1%). Exact input-feature overlap removes 8,541 rows from the primary test, leaving **73,791 flows** with 38,263 attack labels (51.9%). A grouped split of the published training data supplies fit and validation periods; the CSVs lack timestamps, so these are **not** chronological periods.

## Three standalone detection tracks

Rules are fixed readable conditions. The Isolation Forest learns from normal-labeled fit rows. The concentration track summarizes dataset-provided recent-connection counts. The two scored tracks use cutoffs set at the validation 90th percentile.

| Track | Primary-test alerts | Attack-labeled | Normal-labeled | Precision | Recall |
| --- | ---: | ---: | ---: | ---: | ---: |
| Rules union | 27,973 | 22,578 | 5,395 | 80.7% | 59.0% |
| Isolation Forest | 5,889 | 4,039 | 1,850 | 68.6% | 10.6% |
| Connection concentration | 7,157 | 7,157 | 0 | 100.0% | 18.7% |

The connection result is exceptionally clean in this benchmark and should be treated as a **dataset-specific pattern**, not evidence of a zero-false-alert detector in real traffic. The Isolation Forest's modest recall shows that abnormality alone is not a substitute for a labeled attack model.

## Three trained classifiers

Logistic regression, XGBoost, and EBM used the same base information and track signals. XGBoost had the highest validation AP (**0.9950**) and was selected before the test comparison. On the primary test:

| Model | AP | ROC AUC | Brier score |
| --- | ---: | ---: | ---: |
| Logistic regression | 0.9696 | 0.9654 | 0.1088 |
| **XGBoost** | **0.9825** | **0.9796** | **0.0929** |
| EBM | 0.9746 | 0.9710 | 0.1049 |

The validation 90th-percentile XGBoost cutoff produced only **1,831 test alerts**, catching 1,831 attack-labeled flows (4.8% recall). Its validation score distribution did not transfer into the same alert rate on test. At an explicit 10% test review budget (7,379 flows), XGBoost caught 7,379 attack-labeled flows (19.3% recall). These two policies answer different questions: a frozen score cutoff versus a fixed-size ranked queue.

## Equal-workload rule comparison

The rules union alerts **27,973** flows. At the *same* number of alerts, the selected XGBoost model finds more attack-labeled flows and sends fewer normal-labeled flows for review:

| Alert source | Alerts | Attack-labeled | Normal-labeled | Precision | Recall |
| --- | ---: | ---: | ---: | ---: | ---: |
| Rules union | 27,973 | 22,578 | 5,395 | 80.7% | 59.0% |
| **XGBoost, same alert count** | **27,973** | **27,899** | **74** | **99.7%** | **72.9%** |

Adding rule alerts beyond that equal-budget XGBoost queue finds **1,626 additional attack-labeled flows**, but also adds **5,373 normal-labeled flows**. The OR union grows to **34,972 alerts** and 77.2% recall. Adding Isolation Forest finds 857 additional attack-labeled flows with 1,830 additional normal-labeled flows; concentration adds no new alerts at this model budget. These are diagnostic comparisons, not a recommended combined policy.

## Missed attack labels and explanations

At the rule-matched model alert budget, XGBoost misses **10,364** of 38,263 attack-labeled test flows. Its largest missed categories are **Fuzzers (4,747)**, **Exploits (2,607)**, and **Reconnaissance (1,619)**. The notebook charts global importance for all three models and a local XGBoost SHAP contribution view for one missed attack-labeled flow. An explanation describes the model's score; it does not establish why the traffic occurred.

## Limits

- The dataset was generated in a cyber range, and attack labels are unusually common. Precision and false-alert counts cannot be transferred to a live SOC queue with a much lower attack base rate.
- The published train/test CSVs have no timestamps. Grouping exact duplicate inputs and excluding exact test overlap reduces one leakage risk, but cannot establish future-period generalization.
- **74,301** training rows and **28,386** published test rows repeat an earlier row's input fields within their respective files. **229** training input groups have conflicting labels. These features of the data can affect learned patterns and benchmark metrics.
- Dataset-provided recent-connection counts cannot be independently reconstructed from these two split CSVs. This project does not claim a production feature pipeline.
- The three rules and one concentration formula are explanatory examples. There is no live sensor, case-management queue, analyst feedback, or automatic containment.

**Dataset citation:** Moustafa and Slay, “UNSW-NB15: a comprehensive data set for network intrusion detection systems,” *MilCIS 2015*, DOI [10.1109/MilCIS.2015.7348942](https://doi.org/10.1109/MilCIS.2015.7348942). The [UNSW dataset page](https://research.unsw.edu.au/projects/unsw-nb15-dataset) provides the release description and citation guidance.

