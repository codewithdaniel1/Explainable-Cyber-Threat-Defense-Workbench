# Explainable Cyber Threat Defense Workbench

An explainable cyber defense research project modeled on [Explainable AML Transaction Monitoring](https://github.com/codewithdaniel1/Explainable-AML-Transaction-Monitoring). The central question is whether transparent rules, behavior signals, and trained models can surface known malicious identity activity at a review volume a security team could handle.

## Start here

| File | Purpose |
| --- | --- |
| [docs/PROJECT_GUIDE.md](docs/PROJECT_GUIDE.md) | Research question, architecture, dataset, leakage controls, and phased design. |
| [cyber_threat_modeling.ipynb](cyber_threat_modeling.ipynb) | Main research notebook. The first stage audits prepared events, labels, time splits, and rule signals. |
| [docs/FINDINGS.md](docs/FINDINGS.md) | Results and limitations. It records only findings actually measured. |
| [scripts/prepare_lanl.py](scripts/prepare_lanl.py) | Streaming parser and past-only feature preparation. |

The current milestone is **data preparation and initial investigation**, not a finished detection system. The notebook's model comparison, AI investigation assistant, response simulation, and serving layer are subsequent milestones. The [project guide](docs/PROJECT_GUIDE.md) states the intended order and evaluation gates.

## Data

The primary source is Los Alamos National Laboratory's [Comprehensive, Multi-Source Cyber-Security Events dataset](https://csr.lanl.gov/data/cyber1/). Download `auth.txt.gz` and `redteam.txt.gz` from the source and place them in `data/raw/`. The full authentication file is large (7.2 GB compressed), so begin with a capped development run and move to longer periods only after checking memory, time, and label coverage. Raw and prepared data are excluded from Git.

The red-team file identifies particular known compromise events in the authentication stream. An authentication event absent from that file is **unlabeled**, not verified benign. The project will report recall against known events and alert workload; any conventional precision estimate must be described as a proxy with this limitation.

## Prepare the first event table

The preparation script uses only Python's standard library. This example writes the first 100,000 events for a smoke run:

```bash
python3 scripts/prepare_lanl.py \
  --auth data/raw/auth.txt.gz \
  --redteam data/raw/redteam.txt.gz \
  --max-events 100000
```

The output is `data/processed/auth_features.csv.gz` plus `auth_features.csv.manifest.json`. The manifest records the event cap, rows written, and exact red-team keys matched. A capped run is useful for checking parsing and features; **it is not a valid final evaluation**. For a complete run, omit `--max-events` and `--max-day`. A complete run will be compute and storage intensive.

To run the notebook after preparing data, use Python 3.11 or newer and install the research dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m ipykernel install --user --name cyber-workbench --display-name "Python (cyber workbench)"
```

Then open `cyber_threat_modeling.ipynb`, select the project kernel, and run in order. The notebook refuses to treat a capped run as final results. A 100,000-row smoke sample may contain no red-team events; that is expected and does not establish detector performance.

## Verify the feature builder

```bash
python3 -m unittest discover -s tests -v
```

The tests cover exact red-team event matching, malformed input, ordered timestamps, and the rule that events at the same second cannot see each other in historical features.

## Research boundaries

This is an educational workbench using de-identified research data. It does not connect to a live SIEM, execute containment actions, or claim that a model score proves compromise. Its future LLM workflow will ground answers in retrieved events and approved reference text and will require human approval for simulated response actions.

