from langchain_core.tools import InjectedToolArg,tool
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
import requests
import json
import os
from typing import Annotated


os.environ.get("GROQ_API_KEY")

# Creating tools


@tool
def get_conversion_factor(base_currency:str,target_currency:str)->float:
    """This function fetches the currency conversion factor between a given base currency and a target currency."""
    url = f"https://v6.exchangerate-api.com/v6/0c9b47848ab6337d34254882/pair/{base_currency}/{target_currency}"
    response = requests.get(url)
    print("Response: ",response)
    data = response.json()
    # conversion_factor = data["rates"][target_currency]
    print("Json data: ",data)
    return data

@tool
def convert(base_currency_value: int, conversion_factor: Annotated[float, InjectedToolArg])-> float:
    """This function converts the currency using the conversion factor."""
    return base_currency_value * conversion_factor

print(convert.args)

# tool binding
llm=ChatGroq(model="llama-3.3-70b-versatile")
llm_with_tools=llm.bind_tools([get_conversion_factor,convert]) # binding the tools to the llm

# tool calling 
messages=[]
messages.append(HumanMessage("What is the conversion factor between USD and INR, and based on that can you convert 100 USD to INR")) # passing the query to the llm with tools to get the response
print(messages)
print("----------------------------------------------------")
result=llm_with_tools.invoke(messages) # passing the query to the llm with tools to get the response
messages.append(result) # appending the result to the messages list
print(messages)
print("----------------------------------------------------")
print("Tool call: ",result.tool_calls) # tool call is a list of dictionaries



for tool_call in result.tool_calls:
  # execute the 1st tool and get the value of conversion factor
  if tool_call['name'] == 'get_conversion_factor':
    tool_message1 = get_conversion_factor.invoke(tool_call)
    # fetch this conversion factor
    conversion_factor = json.loads(tool_message1.content)['conversion_rate']
    # append this tool message to messages list
    messages.append(tool_message1)
  # execute the 2nd tool using the conversion factor from tool 1
  if tool_call['name'] == 'convert':
    # fetch the current arg
    tool_call['args']['conversion_factor'] = conversion_factor
    tool_message2 = convert.invoke(tool_call)
    messages.append(tool_message2)

print("Final meessage send to llm: ",messages)
final_answer=llm_with_tools.invoke(messages).content
print("Final response from LLM: ",final_answer)

