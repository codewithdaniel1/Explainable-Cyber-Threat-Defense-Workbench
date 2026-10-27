# Findings and limitations

## Status

No full-dataset experiment has been run yet. This document will contain observed results only after the dataset is prepared and the notebook has been executed. Development fixtures and capped smoke runs are not evidence of detection performance.

## First measurements to record

| Measure | Result |
| --- | --- |
| Authentication events processed | Pending data run |
| Distinct known red-team keys matched | Pending data run |
| Known events by chronological period | Pending data run |
| Rule alert volume by day | Pending data run |
| Known-event coverage at a fixed review budget | Pending model run |

## Interpretation guardrails

An unlisted authentication event is not confirmed benign. A known-event alert is an exact match to LANL's red-team event file, not proof that the project has detected every compromise. The dataset is de-identified and historical; any measured performance will describe this research setting and selected time window, not a bank's live environment.

