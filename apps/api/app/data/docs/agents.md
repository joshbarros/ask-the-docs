# Agent harnesses: the model is the engine, the harness is the car

An agent is a model in a loop. A harness is everything around that loop that makes it safe, observable and debuggable. Most agent failures in production are harness failures: missing validation, no approval gate, no trace, no evals.

## Components

1. **Typed tools.** Every tool is a schema plus a handler. Arguments are validated before execution; errors are returned as data, not crashes.
2. **MCP.** The Model Context Protocol standardizes tool exposure so integrations are reusable across agents instead of hard-coded.
3. **Approval gates.** Autonomy scales with reversibility. Read-only actions run automatically; irreversible actions (pay, delete, email a customer) require human approval until evals prove reliability.
4. **Bounded loops.** Cap tool steps, retry transient failures with backoff, and on exhaustion force a final tool-free answer.
5. **Tracing.** Record messages, tool calls, arguments, results, tokens, cost and latency. A trace should let you replay a failure deterministically.
6. **Evals.** Score tool-call accuracy, unsafe-action block rate, recovery rate and steps-to-resolution, not just the final prose.

## The habit

Autonomy should grow only as evals prove reliability. Start conservative, widen the lane with data. The teams that ship agents to customers all have one thing in common: they can replay and explain any failure.
