from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.googlesearch import GoogleSearchTools
from pydantic import StrictInt, StrictStr

agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    tools=[GoogleSearchTools()],
    description="You are a news agent that helps users find the latest news.",
    instructions=[
        "Given a topic by the user, respond with 4 latest news items about that topic.",
        "Search for 10 news items and select the top 4 unique items.",
        "Search in English and in French.",
    ],
    show_tool_calls=True,
    debug_mode=True,
)

if __name__ == "__main__":
    agent.print_response(
        message="Mistral AI",
        markdown=True,
        show_full_reasoning=True,
    )
