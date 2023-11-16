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
    query_message=[{"role": "system", "content": "You are a helpful summarizing model called CuriousCat. You do not have individuality, opinion or a personality. Please summarize the following paragraph in a maximum of 2 sentences or less. Make it concise, with all important details retained. The summary must have a MAX WORD LIMIT OF 80 WORDS, focusing on readability."},]
    query_message.append({"role": "user", "content": formatted_minutes})
    
    #query for response and return json format
    response = await queryGPT(query_message)
    return {"summary": response}