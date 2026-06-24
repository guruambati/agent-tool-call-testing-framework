# Interview Notes — Agent Tool Call Testing Framework

## What I Built

A pytest-based testing framework for AI agents that call external tools. Includes
four mock tools (calculator, weather, email, database), an AgentRunner with retry
and session memory, and a PlanExecutor for multi-step workflows. 75 tests across
6 test files.

Built to develop the practical understanding needed to QA agentic AI systems —
understanding how agents fail when calling tools, and how to write systematic tests
that catch those failures.

## How I Would Explain It in an Interview

> "Modern AI agents don't just generate text — they call real tools: APIs, databases,
> search engines, email services. Testing these agents is fundamentally different from
> testing a REST API because you're not just validating the response format. You need
> to test tool selection, parameter validity, retry behavior, idempotency, side-effect
> isolation, and session state.
>
> I built a framework that tests all of these. Four mock tools simulate real integrations
> without network calls. The AgentRunner implements configurable retry with exponential
> back-off and distinguishes retryable errors — like ConnectionError — from non-retryable
> errors — like ValueError — which should fail immediately.
>
> Key insight: the email tool is intentionally non-idempotent — each call generates a
> new message ID. The database tool is idempotent. The tests verify both behaviors
> explicitly, which is something you'd miss if you only tested the happy path."

## What QA Problem It Solves

1. **Tool parameter validation** — agents can pass wrong types, missing fields,
   out-of-range values. Each tool has explicit validation and tests for all error paths.
2. **Retry coverage** — transient network failures shouldn't cause agent crashes.
   Tests verify the agent retries the right number of times on the right error types.
3. **Side-effect isolation** — tests for email tool verify instance isolation so
   one test's sends don't pollute another test's assertions.
4. **Audit trail** — every tool call is recorded in session.tool_calls_made.
   Tests verify this log is accurate and complete.
5. **Multi-step plan testing** — PlanExecutor tests verify abort-on-failure stops
   correctly and abort_on_failure=False continues past errors.

## Key Design Decisions Worth Discussing

**Why separate BaseTool from tool implementations?**
All call history, reset(), and _record() logic lives once in BaseTool. Adding a new
tool means implementing only the business logic — no boilerplate. Same pattern used
in LangChain's BaseTool.

**Why distinguish retryable vs non-retryable errors?**
ConnectionError and TimeoutError are transient — worth retrying. ValueError means bad
parameters — retrying won't help. Conflating them would either retry forever on bad
inputs or give up too early on network blips.

**Why is email non-idempotent?**
Real email sends aren't idempotent — sending the same email twice creates two deliveries.
Testing that message IDs are unique verifies this contract is enforced.

**Why mock tools instead of real API calls?**
Tests run in CI without API keys, no rate limits, fully deterministic. The trade-off:
you still need integration tests against real APIs before production. These unit tests
give fast feedback on agent logic.

## What I Would Add Next

1. **Real LangGraph agent integration** — replace the mock runner with a LangGraph
   graph (nodes, edges, conditional routing) and test against that
2. **OpenAI function calling** — add a test that sends a real function-calling request
   to GPT-4o-mini and validates the tool_calls in the response
3. **Tool call trace validation** — assert that for a given prompt, the agent called
   tools in the correct sequence with the correct parameters
4. **Rate limit simulation** — add a `RateLimitError` that triggers retry with longer
   back-off, testing that agents handle 429 responses gracefully
5. **Parallel tool call testing** — some agents call multiple tools concurrently;
   test thread-safety of the call history recording
