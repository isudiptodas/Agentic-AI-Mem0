from openai import OpenAI
from mem0 import MemoryClient
from dotenv import load_dotenv
import os
from tools.tools import tools, tool_functions
from prompt import SYSTEM_PROMPT
import json

load_dotenv() 

memClient = MemoryClient(api_key=os.getenv("MEM0_API"))
client = OpenAI(
    base_url="http://localhost:12434/engines/v1",
    api_key="hello"
)

while True:
    userInput = input("Ask anything : ")

    if userInput.strip().lower() == 'exit':
        break
    else:
        messages = [
          { "role": "system", "content": SYSTEM_PROMPT },
          { "role": "user", "content": userInput }
        ]

        while True:
            response = client.chat.completions.create(
            model="qwen2.5:1.5B-F16",
            messages=messages,
            tools=tools,
            stream=False
            )

            assistant_message = response.choices[0].message

            if not assistant_message.tool_calls:
                final_text = assistant_message.content
                print(f"{final_text}\n")
                break

            messages.append(assistant_message)

            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name

                arguments = json.loads(
                    tool_call.function.arguments
                )

                print(f"\n Calling tool: {function_name}")
                print(f" Arguments: {arguments}")

                function = tool_functions[function_name]
                result = function(**arguments)

                print(f" Tool result: {result}\n")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })

    memClient.add(messages=[
        {
            "role": "user",
            "content": userInput
        },
        {
            "role": "assistant",
            "content": final_text
        }
    ], user_id="sudipto")
        