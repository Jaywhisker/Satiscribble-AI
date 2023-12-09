import openai
import os
from utils.gptManager import *
from utils.formatData import *
from utils.mongoDBManager import MongoDBManager

async def summariseText(minutes_id: str, chat_history_id: str, topic_id: str):
    
    openai.api_key = os.environ.get('OPENAI_API_KEY')

    mongoDB = MongoDBManager(minutes_id, chat_history_id)
    
    content = mongoDB.read_MongoDB('minutes', False, topic_id, None)
    print(content)


    #format minutes into a single string
    formatted_minutes=formatPreSummaryMinutes(content["sentences"], topic_id)

    #check if string is empty
    if not formatted_minutes.strip():
        return {"summary": "Nothing to summarise."}

    #prepare prompt for OpenAI
    query_message=[{"role": "system", "content": "Please read through the following paragraph. Please SUMMARISE the content of THE MOST IMPORTANT sentences into ONE single COHESIVE and EXTREMELY SHORT sentence topic description. The RESPONSE should be as CONCISE and COMPREHENSIVE as possible so as to cover as much content in AS FEW WORDS as possible. Your generated response must NEVER be LONGER than the given paragraph, and it must NEVER EXCEED 60 words.It must only be ONE sentence please. Please take A THIRD PERSON POINT OF VIEW. ALWAYS return only the one sentence description. NEVER preface the RESPONSE and just PURELY GIVE me the response directly. Please give your response from a THIRD PERSON PERSPECTIVE."},]
    query_message.append({"role": "user", "content": formatted_minutes})

    #query for response and return json format
    response = await queryGPT(query=query_message, request_timeout=5)
    return {"summary": response}