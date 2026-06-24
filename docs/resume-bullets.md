# Resume Bullets — Agent Tool Call Testing Framework

## Option A — AI QA Engineer / GenAI QA focus

- Built a pytest-based agent tool testing framework with 75 tests covering tool
  parameter validation, retry behavior, idempotency contracts, side-effect isolation,
  and multi-step plan execution across four mock tools (calculator, weather, email,
  database lookup)

## Option B — AI SDET focus

- Designed and implemented an AgentRunner with configurable retry logic and session
  memory (Python, pytest); tests distinguish retryable transient errors from
  non-retryable parameter errors and verify call audit logs are complete and accurate

## Option C — LLM Evaluation / AI Quality Engineer focus

- Developed a framework for testing AI agent tool-call behavior including
  non-idempotent side-effect validation, SMTP failure simulation, database row
  isolation, and multi-step plan abort/continue logic; integrated with GitHub
  Actions CI for automated quality gates

## Notes on Usage

- Talking point: "This tests the agent's tool-dispatch layer independently of any
  LLM. The same test suite can be adapted to validate real function-calling responses
  from OpenAI or Anthropic — you'd replace the mock runner with a real API call and
  assert on the tool_calls field."
- Pair with agent-related interview questions about LangChain, LangGraph, or
  OpenAI function calling to show you understand how these tools fit the real stack.
