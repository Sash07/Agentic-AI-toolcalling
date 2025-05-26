from langchain_core.tools import tool
from pydantic import BaseModel
from typing import List
import os
import ast
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub

# Load environment variables
load_dotenv()
os.getenv("GROQ_API_KEY")

# Define input schema for tools
class NumberInput(BaseModel):
    nums: List[int]

@tool(args_schema=NumberInput)
def add(nums:str)->str:
    """Add the numbers"""
    converted_list = ast.literal_eval(nums)
    for num in converted_list:
        sum1+=num
    return str(num)

@tool (args_schema=NumberInput)
def multiply(nums:str)->str:
    """Multiply the given numbers"""
    product=1
    for num in nums:
        if not isinstance(num, int):
            raise ValueError("All inputs must be integers")
        else:
            product= product*num
    return product

# Define tools
@tool
def add(nums: str) -> int:
    """Add the numbers."""
    sum1=0
    converted_list = nums.split(",")
    for num in converted_list:
        sum1+=int(num)
    return sum1

@tool
def multiply(nums: str) -> str:
    """Multiply the given numbers."""
    result = 1
    converted_list = nums.split(",")
    for num in converted_list:
        result=result*int(num)
    return result

# List of tools
tools = [add, multiply]

# Load Groq LLM
llm = ChatGroq(model="llama-3.3-70b-versatile")

# Bind tools to LLM
llm_with_tools = llm.bind_tools(tools)

# Create ReAct agent
prompt = hub.pull("hwchase17/react")
agent = create_react_agent(llm=llm_with_tools, tools=tools, prompt=prompt)

# Create executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Invoke with chained logic
response = agent_executor.invoke({"input": "What is 4+2*9"})
print(response)
