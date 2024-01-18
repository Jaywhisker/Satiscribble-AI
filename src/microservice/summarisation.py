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

    topicTitleExist = topicTitle_match(content['topicTitle'])
    #format minutes into a single string
    formatted_minutes = formatPreSummaryMinutes(content["sentences"], content['topicTitle'] if not topicTitleExist else None)

    #check if string is empty
    if not formatted_minutes.strip():
        return {"summary": "Nothing to summarise."}

    #prepare prompt for OpenAI
    query_message=[{"role": "system", "content": 
                    f"""Given a paragraph of topic minutes, your task is to write a sypnosis of the content of the meeting minutes.
                    Your sypnosis will only be one line with less than 15 words in a third person point of view.
                    Priority should be given to deadlines and action items.
                    ===============================
                    {formatted_minutes}
                    ==============================="""
                    }]
    
    # query_message.append({"role": "user", "content": formatted_minutes})
    
    #query for response and return json format
    response = await queryGPT(query=query_message, request_timeout=5)
    return {"summary": response}