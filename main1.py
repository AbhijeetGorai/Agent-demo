import os
import openai
from dotenv import load_dotenv
import autogen 
load_dotenv()
import http.client
import json

api_key = os.getenv("OPENAI_API_KEY")
llm_config1 = {"model":"gpt-4o","api_key":api_key,"temperature":0}

#Agent1
user_proxy = autogen.AssistantAgent(
    name="user_proxy",
    system_message="Human Admin. Once the task is completed, answer TERMINATE",
    human_input_mode="ALWAYS",
    is_termination_msg=lambda msg: "TERMINATE" in msg["content"],
    code_execution_config=False
)

#Agent2
Query_Pass_Agent = autogen.AssistantAgent(
    name="Query_Pass_Agent",
    system_message="""
    Your task is to pass the user query to relevant agent for further processing
    If the query is related to search, you will reply with "SEARCH" andpass it to Google_Search agent
    If the query is general question, you will reply with "ANSWER" and pass it to Answer_Agent
    For example: The query is like "Who is the president of India?", so this is a search query
    so you will reply with "SEARCH" and pass it to Google_Search agent for further processing
    """,
    llm_config=llm_config1,
    human_input_mode="NEVER",
    code_execution_config=False
)

#Agent3
Google_Search = autogen.AssistantAgent(
    name="Google_Search",
    system_message="You will pass the user query to search agent for further processing",
    llm_config=llm_config1,
    human_input_mode="NEVER",
    code_execution_config=False
)

#Agent4
Search_Agent = autogen.AssistantAgent(
    name="Search_Agent",
    llm_config=None,
    human_input_mode="NEVER",
    code_execution_config=False
)

@Search_Agent.register_for_execution()
@Google_Search.register_for_llm(description="Get the answer of the user query from web")

def search_serper(question: str) -> str:
    """
    Search using Google Serper API and return processed answer
    Args:
        question: The search query
    Returns:
        str: Processed answer from the search results
    """
    conn = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({
        "q": question,
        "gl": "in"
    })
    headers = {
        'X-API-KEY': '425ead50d860761af310f47b839ef98e6041f54e',
        'Content-Type': 'application/json'
    }
    
    try:
        conn.request("POST", "/search", payload, headers)
        res = conn.getresponse()
        data = res.read()
        json_data = json.loads(data.decode("utf-8"))
        
        # Return answer from answerBox if available
        if "answerBox" in json_data and "answer" in json_data["answerBox"]:
            return json_data["answerBox"]["answer"]
        
        # If no answerBox, return first organic result's snippet
        elif "organic" in json_data and len(json_data["organic"]) > 0:
            return json_data["organic"][0]["snippet"]
        
        else:
            return "No relevant answer found"
            
    except Exception as e:
        return f"Error processing request: {str(e)}"

#Agent5
Answer_Agent = autogen.AssistantAgent(
    name="Answer_Agent",
    system_message="You will answer the user query according to your knowledge",
    llm_config=llm_config1,
    human_input_mode="NEVER",
    code_execution_config=False
)

#State transition function
def state_transition(last_speaker,groupchat):
    message = groupchat.messages
    last_message = message[-1]["content"]
    if last_speaker is user_proxy:
        return Query_Pass_Agent
    if last_speaker is Query_Pass_Agent:
        if last_message == "SEARCH":
            return Google_Search
        if last_message == "ANSWER":
            return Answer_Agent
    if last_speaker is Google_Search:
        return Search_Agent
    
#Define the groupchat
groupchat = autogen.GroupChat(
    agents=[user_proxy,Query_Pass_Agent,Google_Search,Search_Agent,Answer_Agent],
    messages=[],
    max_round=50,
    speaker_selection_method=state_transition,
)

#Group Chat Manager
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=None)

#Start the chat
user_proxy.initiate_chat(
    manager,
    message="Write a 3 line horror story"
)







