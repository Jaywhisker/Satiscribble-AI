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
    query_message=[{"role": "system", "content": """
                    Please read through the following paragraph.
                    Please SUMMARISE the content of THE MOST IMPORTANT sentences into ONE single COHESIVE and EXTREMELY SHORT sentence topic description.
                    The RESPONSE should be as CONCISE and COMPREHENSIVE as possible so as to cover as much content in AS FEW WORDS as possible. 
                    Your generated response must NEVER be LONGER than the given paragraph, and in at most 60 words. 
                    It must only be ONE sentence please. 
                    Please take A THIRD PERSON POINT OF VIEW. 
                    ALWAYS return only the one sentence description. 
                    NEVER preface the RESPONSE and just PURELY GIVE me the response directly. 
                    Please give your response from a THIRD PERSON PERSPECTIVE.
                    """},]
    query_message.append({"role": "user", "content": formatted_minutes})

    #query for response and return json format
    response = await queryGPT(query=query_message, request_timeout=5)
    return {"summary": response}


# slap = """
#     Your task is to write a 30 word synopsis of the following text, focus only on deadlines and tasks.
#     The response should be a single sentence.
#     """

# query_message=[{"role": "system", "content": slap},]

# openai.api_key = os.environ['OPENAI_API_KEY']
# main_container = []
# relevance_container = []


# def get_GPTANS(Talking):
#     user_input = {"role": "user", "content": slap + f"""
#                   Text:{Talking}
#     """}
#     query_message.append(user_input)

#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages= query_message,
#         temperature=0.2
#         )
#     return(response['choices'][0]['message']['content'])

# def basicTesting(paragraph):
#     print(len(paragraph.split()))
#     ans = get_GPTANS(paragraph)
#     words = len(ans.split())
#     print(ans)
#     print(words)

# def fullTesting(lists):
#     for i in lists:
#         print("=========================")
#         print(i)
#         basicTesting(i)
#         print("=========================")
    
# fullTesting(listOfParagraphs)