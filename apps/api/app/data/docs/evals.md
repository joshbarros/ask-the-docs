# LLM evaluation: measure, gate, ship

An eval harness is a labeled set, metrics tied to real failures, and a threshold that blocks regressions. It is what separates a demo from a system.

## Build the ground-truth set

Collect 50-100 real questions with known-good answers and the passages that support them. Include out-of-scope questions on purpose: a system that answers everything is a system that hallucinates. Grow the set over time by promoting every real failure into a permanent case.

## Pick metrics that map to failure modes

- Groundedness: is the answer supported by the retrieved context?
- Answer relevance: does it address the question?
- Context recall: did retrieval find the right passage?
- Refusal precision: when it should decline, does it?
- Citation accuracy: do cited passages actually contain the claim?

Delete any metric that never changes a decision.

## Automate the gate

Run the harness in CI on every change to retrieval, prompts, models or chunking. Fail the build below the threshold. Report cost and latency next to quality: p95 latency and dollars per thousand queries are product requirements.

The loop is measure, gate, ship, promote failures, repeat. Teams that do this ship faster because they stop arguing about vibes and start reading a table.
