"""
AgentRunner class for managing ADK agent execution with session management.
"""

import logging
from typing import Any, Optional
import asyncio

from google.adk import Runner
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService, Session
from google.genai import types


class AgentRunner:
    """
    A reusable class for running ADK agents with session management.
    """
    
    def __init__(self, agent, app_name: str, user_id: str = "default_user"):
        """
        Initialize the AgentRunner.
        
        Args:
            agent: The ADK agent to run
            app_name: Name of the application
            user_id: Default user ID (can be overridden per request)
        """
        self.agent = agent
        self.app_name = app_name
        self.default_user_id = user_id
        
        # Initialize session service
        self.session_service = InMemorySessionService()
        
        # Store runners per session to avoid recreating
        self.runners = {}
        self.sessions = {}
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    async def prepare_session(self, user_id: str, session_id: str = None) -> str:
        """
        Prepare a session for the user.
        
        Args:
            user_id: User identifier
            session_id: Session identifier (auto-generated if None)
        
        Returns:
            str: The session ID that was created/used
        """
        if session_id is None:
            session_id = f"session_{user_id}_{len(self.sessions) + 1}"
        
        session_key = f"{user_id}_{session_id}"
        
        # Check if session already exists
        if session_key in self.sessions:
            self.logger.info(f"Using existing session: {session_key}")
            return session_id
        
        try:
            # Create new session
            session = await self.session_service.create_session(
                app_name=self.app_name,
                user_id=user_id,
                session_id=session_id
            )
            
            # Create runner for this session
            runner = Runner(
                agent=self.agent,
                app_name=self.app_name,
                session_service=self.session_service
            )
            
            # Store session and runner
            self.sessions[session_key] = session
            self.runners[session_key] = runner
            
            self.logger.info(f"Session created: App='{self.app_name}', User='{user_id}', Session='{session_id}'")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Failed to create session for {user_id}: {e}")
            raise
    
    async def run_agent(self, prompt: str, user_id: str = None, session_id: str = None) -> str:
        """
        Run the agent with the given prompt.
        
        Args:
            prompt: User's input prompt
            user_id: User identifier (uses default if None)
            session_id: Session identifier (auto-generated if None)
        
        Returns:
            str: Agent's response
        """
        if user_id is None:
            user_id = self.default_user_id
        
        # Ensure session is prepared
        session_id = await self.prepare_session(user_id, session_id)
        session_key = f"{user_id}_{session_id}"
        
        # Get the runner for this session
        runner = self.runners[session_key]
        
        self.logger.info(f"User Query: {prompt}")
        
        try:
            # Prepare the user's message in ADK format
            content = types.Content(role='user', parts=[types.Part(text=prompt)])
            
            final_response_text = "Agent did not produce a final response."
            
            # Execute the agent and process events
            async for event in runner.run_async(
                user_id=user_id, 
                session_id=session_id, 
                new_message=content
            ):
                # Check for final response
                if event.is_final_response():
                    if event.content and event.content.parts:
                        # Get text response from the first part
                        final_response_text = event.content.parts[0].text
                    elif event.actions and event.actions.escalate:
                        # Handle potential errors/escalations
                        final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                    break
            
            self.logger.info(f"Agent Response: {final_response_text}")
            return final_response_text
            
        except Exception as e:
            self.logger.error(f"Error running agent for {user_id}: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    async def get_session_info(self, user_id: str) -> dict:
        """
        Get information about user's sessions.
        
        Args:
            user_id: User identifier
        
        Returns:
            dict: Session information
        """
        user_sessions = [
            key.split('_', 1)[1] for key in self.sessions.keys() 
            if key.startswith(f"{user_id}_")
        ]
        
        return {
            "user_id": user_id,
            "active_sessions": user_sessions,
            "total_sessions": len(user_sessions)
        }


# Convenience function for simple usage
async def run_single_prompt(agent, prompt: str, app_name: str = "simple_app") -> str:
    """
    Simple function to run a single prompt with an agent.
    
    Args:
        agent: The ADK agent
        prompt: User's prompt
        app_name: Application name
    
    Returns:
        str: Agent's response
    """
    runner = AgentRunner(agent, app_name)
    return await runner.run_agent(prompt)


# Example usage in main block
if __name__ == "__main__":
    from manager.agent import root_agent

    # Option 1: Using asyncio.run() with the convenience function
    try:
        response = asyncio.run(run_single_prompt(
            agent=root_agent,
            prompt="Tell me about your favorite movie role",
            app_name="bradPittApp"
        ))
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error running agent: {e}")

    print("--------------------------------")

    # Option 2: Using asyncio.run() with AgentRunner class
    async def test_agent_runner():
        try:
            runner = AgentRunner(
                agent=root_agent,
                app_name="bradPittApp",
                user_id="test_user"
            )
            response = await runner.run_agent(
                prompt="What's your favorite movie role?",
                user_id="test_user",
                session_id="test_session"
            )
            print(f"Class Response: {response}")
            
            # Test another prompt in the same session
            response2 = await runner.run_agent(
                prompt="Tell me more about that role",
                user_id="test_user",
                session_id="test_session"
            )
            print(f"Follow-up Response: {response2}")
            
        except Exception as e:
            print(f"Error with AgentRunner: {e}")
    
    # Uncomment to test the class version
    asyncio.run(test_agent_runner())
    
   
  