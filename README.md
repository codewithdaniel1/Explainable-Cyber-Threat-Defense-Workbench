# Explainable Cyber Threat Defense Workbench

A **one-notebook MVP** using a public network-flow dataset. It compares three detection tracks, three alternative classifiers, held-out alerts, model explanations, and missed attack labels.

## Which file should I read?

| File | Purpose |
| --- | --- |
| [docs/PROJECT_GUIDE.md](docs/PROJECT_GUIDE.md) | Start here for the research question, architecture, data split, and metric definitions. |
| [cyber_threat_modeling.ipynb](cyber_threat_modeling.ipynb) | Run the full analysis in order. Code, tables, charts, and saved outputs are together. |
| [docs/FINDINGS.md](docs/FINDINGS.md) | Read the measured results, alert tradeoffs, missed attack categories, and limitations. |
| [docs/Cyber_Threat_Defense_Expert_Briefing.pdf](docs/Cyber_Threat_Defense_Expert_Briefing.pdf) | View the slide-style briefing on model results, alert workload, detection signals, and missed attack categories. |

The project asks: **Can readable rules, anomaly detection, and connection-count signals help explainable models identify attack-labeled network flows at a manageable review volume?** It uses [UNSW-NB15](https://research.unsw.edu.au/projects/unsw-nb15-dataset), a cyber-range dataset with normal and simulated attack traffic. This is a benchmark experiment, not a deployed security product.

The three **signals** are fixed rules, an Isolation Forest novelty score, and recent-connection concentration. Logistic regression, XGBoost, and an Explainable Boosting Machine (EBM) are three **alternative classifiers** trained on the same raw inputs plus those signals. Each classifier scores every evaluation flow. The notebook compares the standalone track alerts separately from the selected model's alerts.

## Set up

Use Python 3.11 or newer from the repository folder:

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

In VS Code, open `cyber_threat_modeling.ipynb`, choose `.venv/bin/python` as the notebook kernel, and run cells from top to bottom. The notebook in this repository includes the results of a full run on both published split files.

## Get the data

The [UNSW research page](https://research.unsw.edu.au/projects/unsw-nb15-dataset) describes the dataset and its published train/test partition. Place these files in `data/raw/`:

- `UNSW_NB15_training-set.csv` (175,341 flows)
- `UNSW_NB15_testing-set.csv` (82,332 flows)

The university's current download link may require Microsoft sign-in. The notebook run in this repository used a [public mirror of the same two named CSVs](https://huggingface.co/datasets/Mouwiya/UNSW-NB15-small/tree/6f5f54594dfc80c84264aec4c7cc3d9b162f1e2f):

```bash
mkdir -p data/raw
curl -L --fail -o data/raw/UNSW_NB15_training-set.csv 'https://huggingface.co/datasets/Mouwiya/UNSW-NB15-small/resolve/6f5f54594dfc80c84264aec4c7cc3d9b162f1e2f/UNSW_NB15_training-set.csv'
curl -L --fail -o data/raw/UNSW_NB15_testing-set.csv 'https://huggingface.co/datasets/Mouwiya/UNSW-NB15-small/resolve/6f5f54594dfc80c84264aec4c7cc3d9b162f1e2f/UNSW_NB15_testing-set.csv'
```

For the files used in the saved run, the SHA-256 hashes are `bec7dd5ec88dc2a0ccc7a07879d338395ed7421750f675fd0339e07dfe0648fa` (training) and `734fe6642edf758f7c94d7d9149426b49d202fe8e7bf0bef47392489c3c0a559` (testing). The raw CSVs are excluded from Git.

## Notebook order

| Sections | What happens |
| --- | --- |
| 1–4 | Load data, profile labels, audit exact train/test feature overlap, make a grouped validation split, define shared features. |
| 5–8 | Evaluate rules, Isolation Forest, and recent-connection concentration as standalone alert sources. |
| 9–12 | Train three classifiers, select one by validation average precision, and score held-out test flows. |
| 13–16 | Compare equal-size alert queues, audit missed attack types, explain model scores, and interpret limits. |

`id`, `label`, and `attack_cat` never enter classifier inputs. Exact test rows whose input features also occur in the published training file are excluded from the **primary** test scorecard. The official partition lacks timestamps, so this experiment cannot establish future-period performance. Attack labels are unusually common in this dataset; precision and alert volume are benchmark measurements, not estimates for a production SOC.

