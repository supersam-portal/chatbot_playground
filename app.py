from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import Runnable
from langchain_core.messages import AIMessage, HumanMessage
from langchain import hub
from langchain_core.prompts.chat import MessagesPlaceholder
from langchain.agents import AgentExecutor
from langchain.tools import tool
import pandas as pd
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
import chainlit as cl
from langchain_core.prompts import ChatPromptTemplate

# Instantiate the LLM

@tool
def get_google_ads_data():
    """Get Google Ads data."""
    data = pd.DataFrame({
        'Campaign': ['Campaign 1', 'Campaign 2', 'Campaign 3'],
        'Clicks': [100, 200, 300],
        'Impressions': [1000, 2000, 3000],
        'Cost': [1000, 2000, 3000],
        'Conversions': [10, 20, 30],
        'ConversionValue': [1000, 2000, 3000],
    
    })
    return data



@cl.on_chat_start
async def on_chat_start():

    template = ChatPromptTemplate.from_messages([
        ("system", "You are an assistant that will help business owner to audit their Google Ads performance. You have access to functions to retrieve their google ads data and generate reports."),
        ("ai", "Hi, I can help you look into your google ads campaign report!"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{user_input}"),
    ])
    # template = hub.pull(f"<prompt-id>")
    tools = [get_google_ads_data]
    llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0, streaming=True)
    agent = (
            {
                "user_input": lambda x: x["user_input"],
                "history": lambda x: x["history"],
            }
            | template
            | llm
            | OpenAIToolsAgentOutputParser()

    )
    agent_executor = AgentExecutor(agent=agent, tools=tools, prompt=template , verbose=True)
    cl.user_session.set("agent_executor", agent_executor)
    cl.user_session.set("history", [])

@cl.on_message
async def on_message(message: cl.Message):
    agent_executor = cl.user_session.get("agent_executor")  # type: Runnable
    history = cl.user_session.get("history")
    msg = cl.Message(content="")
    chunks = []
    
    for chunk in agent_executor.stream(
        {
            "user_input": message.content,
            "history": history,
        }
    ):
        # Agent Action
        chunks+=chunk
        if "actions" in chunk:
            for action in chunk["actions"]:
                await msg.stream_token(action.tool)
        # Observation
        elif "steps" in chunk:
            for step in chunk["steps"]:
                await msg.stream_token(step.observation)
        # Final result
        elif "output" in chunk:
            await msg.stream_token(chunk["output"])
        else:
            raise ValueError()
        print("---")


        await msg.stream_token(chunk["output"])
    history.extend([HumanMessage(content=message.content), AIMessage(content=chunks['output'])])
    await msg.send()
