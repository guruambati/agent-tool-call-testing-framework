"""conftest.py — shared fixtures for agent tool tests."""

import pytest
from src.tools.calculator  import CalculatorTool
from src.tools.weather     import WeatherTool
from src.tools.email_sender import EmailSenderTool
from src.tools.database    import DatabaseLookupTool
from src.agent.runner      import AgentRunner
from src.agent.planner     import PlanExecutor


@pytest.fixture
def calc():
    return CalculatorTool()

@pytest.fixture
def weather():
    return WeatherTool()

@pytest.fixture
def email():
    return EmailSenderTool()

@pytest.fixture
def db():
    return DatabaseLookupTool()

@pytest.fixture
def runner():
    r = AgentRunner(max_retries=3, retry_delay_s=0.01)
    r.start_session("test-session")
    return r

@pytest.fixture
def wired_runner():
    """Runner pre-loaded with all four tools."""
    r = AgentRunner(max_retries=3, retry_delay_s=0.01)
    r.start_session("wired-session")
    r.register_tool("calculator",      CalculatorTool().run)
    r.register_tool("weather",         WeatherTool().run)
    r.register_tool("email_sender",    EmailSenderTool().run)
    r.register_tool("database_lookup", DatabaseLookupTool().run)
    return r

@pytest.fixture
def planner(wired_runner):
    return PlanExecutor(wired_runner)
