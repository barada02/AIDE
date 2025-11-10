"""
Agent definitions for AIDE Manager Agent.
"""

from google.adk.agents import Agent
from .config import MODEL


# Create the root agent (Manager Agent)
manager_agent = Agent(
    name="ManagerAgent",
    description="""You are the Manager Agent for AIDE (Autonomous Intelligent Data Engine). 
    Your role is to:
    1. Receive file processing requests via PubSub messages
    2. Analyze file types and project requirements
    3. Route files to appropriate expert agents (CSV, PDF, Generic)
    4. Coordinate the data preparation workflow
    5. Ensure proper project ID management and data isolation
    
    You work with expert agents as function tools to process different file types and manage the overall data preparation pipeline.""",
    model=MODEL,
    
)

root_agent = manager_agent