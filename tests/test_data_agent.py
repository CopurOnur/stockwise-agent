import pytest
from src.agents.data_agent import DataAgent

def test_data_agent_runs():
    # Use a longer period to ensure we get enough data
    agent = DataAgent(period='5d', interval='1d')
    out = agent.run()
    assert 'AAPL' in out  # Try a different ticker to see if it's specific to NVDA
    assert 'latest_price' in out['AAPL']
    assert isinstance(out['NVDA']['latest_price'], float)
    assert 'indicators' in out['NVDA']
    assert 'SMA20' in out['NVDA']['indicators']
