"""
Agent definitions for Brad.
"""

from google.adk.agents import Agent
from .config import MODEL


# Create the root agent (LeadManagerAgent)
agent_brad = Agent(
    name="BradAgent",
    description="You will act like Brad pitt in all of your responses. You are to answer as Brad pitt would.",
    model=MODEL,
    
)

root_agent = agent_brad