from langchain_groq import ChatGroq
from netmiko import ConnectHandler
from IPython.display import Image, display
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_core.messages import AIMessage,HumanMessage,SystemMessage
from langchain_core.tools import tool
from IPython.display import Image, display
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_core.messages import AIMessage,HumanMessage,SystemMessage
from langchain_groq import ChatGroq
from netmiko import ConnectHandler
from IPython.display import Image, display
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_core.messages import AIMessage,HumanMessage,SystemMessage
from langchain_core.tools import tool
from IPython.display import Image, display
from langgraph.checkpoint.memory import MemorySaver

from langgraph.graph import MessagesState
### Custom tools
def ssh(node: str, command: str) -> str:
    """ssh to the router and execuate the commands.

    Args:
        node: router name and node 
        command: show command and command execute on the router
    """
    device = {
        'device_type': 'cisco_ios',  # or the appropriate device type
        'host': node,
        'username': 'xxxxx',
        'password': 'xxxxx', 
    }

    try:
        connection = ConnectHandler(**device)
        # Send the command
        output = connection.send_command(command,expect_string=r'#')
        # Close the connection
        connection.disconnect()
        return output
    except Exception as e:
        return f"Failed to execute command: {str(e)}"
  
llm = ChatGroq(
    model="llama3-8b-8192",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key="XXXXXXX"
)

tools=[ssh]

### Custom tools
def ssh(node: str, command: str) -> str:
    """ssh to the router and execuate the commands.

    Args:
        node: router name and node 
        command: show command and command execute on the router
    """
    device = {
        'device_type': 'cisco_ios',  # or the appropriate device type
        'host': node,
        'username': 'admin',
        'password': 'C1sco12345', #C1sco12345
    }

    try:
        connection = ConnectHandler(**device)
        # Send the command
        output = connection.send_command(command,expect_string=r'#')
        # Close the connection
        connection.disconnect()
        return output
    except Exception as e:
        return f"Failed to execute command: {str(e)}"

tools=[ssh]
llm_with_tools=llm.bind_tools(tools)

sys_msg = SystemMessage(content="You Sr.Network engineer you will prompt you the node name and ask for the command to execute on the Cisco IOS XR router, you should come up with the command and execute it.")

def assistant(state:MessagesState):
    return {"messages":[llm_with_tools.invoke([sys_msg] + state["messages"])]}


#Graph
builder=StateGraph(MessagesState)

## Define nodes: 
builder.add_node("assistant",assistant)
builder.add_node("tools",ToolNode(tools))

## Define the Edges

builder.add_edge(START,"assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,

)
builder.add_edge("tools","assistant")

memory=MemorySaver()

### human in the loop
graph=builder.compile(checkpointer=memory)


thread={"configurable":{"thread_id":"345"}}
initial_input={"messages":HumanMessage(content="ssh to sandbox-iosxr-1.cisco.com and count how many interfaces are Up state")}

for event in graph.stream(initial_input,thread,stream_mode="values"):
    event['messages'][-1].pretty_print()
