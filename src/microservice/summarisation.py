import openai
import os
import asyncio
from utils.gptManager import *
from utils.formatData import *
from utils.mongoDBManager import MongoDBManager
from utils.chromaDBManager import ChromaDBManager

async def summariseText(topic_title: str, topic_id: str, minutes_id: str,chat_history_id: str):
    
    openai.api_key = os.environ.get('OPENAI_API_KEY')

    mongoDB = MongoDBManager(minutes_id, chat_history_id)
    
    content = mongoDB.read_MongoDB('minutes', False, topic_title, None)

    formatted_minutes=formatPreSummaryMinutes(content, topic_title)
    #prepare prompt for OpenAI
    query_message=[{"role": "system", "content": "You are a helpful summarizing model called CuriousCat. You do not have individuality, opinion or a personality. Please summarize the following paragraph in a maximum of 2 sentences or less. Make it concise, with all important details retained. The summary must have a MAX WORD LIMIT OF 80 WORDS, focusing on readability."},]
    query_message.append({"role": "user", "content": formatted_minutes})
    

    response = await queryGPT(query_message)
    return {"summary": response}