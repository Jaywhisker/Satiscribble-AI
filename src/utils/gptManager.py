from fastapi import HTTPException
import openai
import os
import string

async def queryGPT(query:list, model:str='gpt-3.5-turbo', temperature:float=0.2, request_timeout:int=3, max_retries:int=3):
    """
    General function to query gpt while maintaining timeout

    Args:
        query (list): your query to gpt
        model (str): name of model you are using, defults gpt-3.5-turbo
        temperature (int): what temperature are you setting, defaults 0.2
        request_timeout (int): maximum time (in seconds) before timeout error
        max_retries (int): maximum number of retries in the case of timeout

    Returns:
        gpt response
    """
    openai.api_key = os.environ['OPENAI_API_KEY']
    retry_count = 0
    while retry_count <= max_retries:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=query,
                temperature=temperature,
                request_timeout=request_timeout
            )
            return response['choices'][0]['message']['content']
        
        except Exception as e:
            retry_count += 1
            if retry_count <= max_retries:
                print(f"Request failed (Retry {retry_count}). Pausing for 1 second before retrying.")
                await asyncio.sleep(1)
            else:
                print("Max retries reached. Returning an error.")
                raise HTTPException(status_code=500, detail="GPT timeout, please check GPT server.")



async def TopicTracker(context: list):
    """
    Return True or False on whether the current sentence is still cohernt with the rest of the paragraph.

    Args:
        context: the "min_context" number of sentences to be used as context for chatgpt

    Return:
        True or False 
        if Chatgpt returns something other than T/F, then we will print a statement and take as False
    """
    if len(context) <= 1:
        return True
    sentences = ' '.join(context)
    ### GPT stuff ###
    openai.api_key = os.environ['OPENAI_API_KEY']
    query_message = [
    {"role": "system", "content": "You are a topictracker model. You do not have individuality, opinion or a personality. You can only reply in True or False. You will expect a list of sentences. Return False if the last sentence is incoherent with the rest of the paragraph. Return True if the last sentence is coherent with the rest of the paragraph. If the subject of a sentence does  not fit in with the current context, it is most likely incoherent and should return False."},
    ]
    user_input = {"role": "user", "content": sentences}
    query_message.append(user_input)

    response = await queryGPT(query_message, request_timeout=5)

    ### 
    if response == "True":
        return True
    elif response == "False":
        return False
    else:
        print("errornous GPT response, taking as False and skipping")
        return False



async def AgendaTracker(context: list, agenda: list):
    """
    Return True or False on whether the current sentence is still cohernt with the agenda of the meeting.

    Args:
        context: the "min_context" number of sentences to be used as context for chatgpt
        agenda: the list of agenda items
    Return:
        True or False 
        if Chatgpt returns something other than T/F, then we will print a statement and take as False
    """
    if len(context) <= 1:
        return True
    sentences = ' '.join(context)
    ### GPT stuff ###
    openai.api_key = os.environ['OPENAI_API_KEY']
    query_message = [
    {"role": "system", "content": "You are a AgendaTracker model. You do not have individuality, opinion or a personality. You can only reply in True or False. You will expect a list of sentences that was recently mentioned and a list of potential Agenda items. Return False if the list of sentences is not related to any of the agenda items. Return True if the list of sentences is coherent with the agenda items. If even one sentence is not related, return False"},
    ]
    user_input = {"role": "user", "content": "AgendaItems:" + str(agenda) + ", Sentences:" + sentences}
    query_message.append(user_input)
    response = await queryGPT(query_message, request_timeout=5)
    # await asyncio.sleep(5)
    # print("TopicTrackerResponse")
    ###
    if response == "True":
        return True
    elif response == "False":
        return False
    else:
        print("errornous GPT response, taking as False and skipping")
        return False



async def GlossaryDetector(context: list, abbreviation:str):
    """
    Return what the abbreviation stands for in the context of the sentences provided

    Args:
        context: the "min_context" number of sentences to be used as context for chatgpt
        abbreviation: the abbreviation to be defined
    Return:
        number of words equivilant to the number of letters in the Abbreviation provided    """
    if abbreviation == None:
        return None
    else:
        sentences = ' '.join(context)
        ### GPT stuff ###
        openai.api_key = os.environ['OPENAI_API_KEY']
        query_message = [
        {"role": "system", "content": "You are an Abbreviation DetectionModel. You do not have individuality, opinion or a personality. Expect an abbreviation and several sentences for the context of the word. Your response will be what the abbreviation stands for in the context of the sentences provided. Your responses will only contain a number of words equivilant to the number of letters in the Abbreviation provided. The only exception are short function words where appropriate. Each word will start with their corresponding letter in the abbreviation."},
        ]
        user_input = {"role": "user", "content": "Abbreviation: " + abbreviation + ", Context:" + sentences}
        query_message.append(user_input)
        # response = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",
        #     messages= query_message,
        #     temperature=0.2
        #     )
        # await asyncio.sleep(5)
        # print("TopicTrackerResponse")
        response = await queryGPT(query_message, request_timeout=5)

        return response.strip()
    


async def createStandAloneQuery(formatted_chat_history:list, query:str):
    """
    Function to convert the latest user query to a standalone question such that it can be used to query to the chromaDB
    Will only take the last 3 user input and user results

    Args:
        formatted_chat_history (list): chat history that will be used as context 
        query (string): user query that will be reformatted
    
    Returns:
        formatted query to become a standalone question
    """
    #only taking latest 3 user query
    if len(formatted_chat_history) > 6:
        formatted_chat_history = formatted_chat_history[len(formatted_chat_history)-6:]
        print(formatted_chat_history)
    
    #creating chat context
    chat_context = ''
    while len(formatted_chat_history) > 0:
        chat_context += f'{formatted_chat_history[0]["role"]}: {formatted_chat_history[0]["content"]}\n'
        chat_context += f'{formatted_chat_history[1]["role"]}: {formatted_chat_history[1]["content"]}\n'
        formatted_chat_history = formatted_chat_history[2:]
        print(len(formatted_chat_history))
    
    
    system_prompt = f"""You are given a conversation. Given a new question, you task is to rephrase the last user query to be a standalone question in its own original language. If the last user query is unrelated to the conversation, return the query. Your response should just be the question and nothing else.
    
    Chathistory:
    {chat_context}
    
    Last user query: {query}
    """
    query_message = [{"role": "system", "content": system_prompt}]
    response =  await queryGPT(query_message)
    return response.strip()



async def documentQuery(query:str, context_dict:dict):
    """
    Function to query GPT based on the minutes

    Args:
        query (string): reformatted user query
        context_dict (list): dictionary containing the context for gpt. In the format of {topic_title: topic_details}

    Returns:
        answer to the question
    """
    format_context = ''
    for topic_title, topic_text in context_dict.items():
        format_context += f"Topic Title: {topic_title}\n"
        format_context += f"{topic_text}\n\n"
    
    system_prompt = f"""You are given the following context in the format of Topic Title: Topic Content. Given a user query, response with the details from the context. Do not fabricate any information. Be short and concise. If the context does not contain any information, respond that you do not have the knowledge and apologise.
                        Context:
                        {format_context}

                        User Query:
                        {query}
                    """
    query_message = [{"role": "system", "content": system_prompt}]
    response =  await queryGPT(query_message, request_timeout=5)
    return response.strip()


async def webQuery(query:str, context:list):
    """
    Function to query GPT based on the conversation you had with it

    Args:
        query (string): reformatted user query
        context_dict (list): dictionary containing the context for gpt. In the format of {topic_title: topic_details}

    Returns:
        answer to the question
    """
    query_message = [
    {"role": "system", "content": "You are an Simple question and answer Model. You do not have individuality, opinion or a personality. You will receive a question. Answer the question in the most straight forwawrd way possible. Minimising words where possible. Try and keep responses below 50 words."},
    ]
    query_message = query_message + context
    query_message.append({"role": "user", "content": query})
    response = await queryGPT(query_message, request_timeout=5)
    return response.strip()

