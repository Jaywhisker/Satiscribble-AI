import time
from fastapi import HTTPException
import openai
import os
from starlette.responses import StreamingResponse
import asyncio
from utils.formatData import *

async def queryGPT(query:list, model:str='gpt-3.5-turbo', temperature:float=0.2, request_timeout:int=3, max_retries:int=3):
    """
        General function to query gpt while maintaining timeout. Only returns full response

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
                request_timeout=request_timeout,
            )
            

            # if stream:
            #     return StreamingResponse(streamGenerator(response),
            #                             media_type='text/event-stream',
            #                             headers=header)

            return response['choices'][0]['message']['content']
        
        except Exception as e:
            print(e)
            retry_count += 1
            if retry_count <= max_retries:
                print(f"Request failed (Retry {retry_count}). Pausing for 1 second before retrying.")
                await asyncio.sleep(1)
            else:
                print("Max retries reached. Returning an error.")
                raise HTTPException(status_code=500, detail="GPT timeout, please check GPT server.")



def streamGPTQuery(query:list, user_query:str, type:str, model:str='gpt-3.5-turbo', temperature:float=0.2, request_timeout:int=3, max_retries:int=3, source_ids = None, mongoDB = None):
    """
        Function to query gpt and return STREAMED response

        Args:
            query (list): formatted user query with context to be passed to gpt
            user_query (str): formatted user query alone (no context) to be passed to mongoDB
            type (str): either 'document' / 'web', determine query type
            model (str, optional): gpt model to be used. Defaults to 'gpt-3.5-turbo'.
            temperature (float, optional): temperature of model. Defaults to 0.2.
            request_timeout (int, optional): time in seconds before a response timeouts. Defaults to 3.
            max_retries (int, optional): maximum number of retries before throwing an error. Defaults to 3.
            source_ids (list, optional): header to be added to the response. Defaults to None.
            mongoDB (mongoDB, optional): mongoDB instance to allow for updating of chatHistory. Defaults to None.

        Returns:
            streamingResponse for fastAPI
    """
    openai.api_key = os.environ['OPENAI_API_KEY']
    retry_count = 0

    header = {
        "source_id": str(source_ids)
    }

    while retry_count <= max_retries:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=query,
                temperature=temperature,
                request_timeout=request_timeout,
                stream = True
            )

            return StreamingResponse(streamGenerator(response, mongoDB, user_query, type, source_ids),
                                    media_type='text/event-stream',
                                    headers=header)
        
        except Exception as e:
            print(e)
            retry_count += 1
            if retry_count <= max_retries:
                print(f"Request failed (Retry {retry_count}). Pausing for 1 second before retrying.")
                time.sleep(1)
            else:
                print("Max retries reached. Returning an error.")
                raise HTTPException(status_code=500, detail="GPT timeout, please check GPT server.")


async def streamGenerator(response, mongoDB, user_query, type, source_ids):
    """
        Function to prepare response for streaming
        If the response ended (by having chunk['choices'][0]['delta'] == {}), update mongoDB
    
        Args:
            response (streaming_chunk): chunk of streaming response
            mongoDB: instance of mongoDB for updating chatHistory
            user_query: original user query
            type: document / web for mongoDB to update
            source_ids: update topic ids
    """
    full_response = ''
    try:
        for chunk in response:
            if chunk['choices'][0]['delta'] != {}:
                yield chunk['choices'][0]['delta']['content']
                full_response += chunk['choices'][0]['delta']['content']
                await asyncio.sleep(0.1)
            else:
                if mongoDB:
                    if source_ids != None:
                        query_resp_pair = {'user': user_query, 'assistant': full_response, 'sourcetopicIDs': source_ids}
                    else:
                        query_resp_pair = {'user': user_query, 'assistant': full_response}

                    await mongoDB.update_chat_history(query_resp_pair, type)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Stream timed out")
    


async def TopicTracker(current_minutes: str, topic_title: str):
    """
        Return True or False on whether the current sentence is still coherent with the topic block.
        
        Args:
            current_minutes: existing minutes on the frontend
            topic_title: title of the topic block
        Return:
            True or False 
            if Chatgpt returns something other than T/F, then we will print a statement and take as True
    """
    # check how many sentences in meeting minutes
    sentence_list = formatTextMinutesList(current_minutes)
    if len(sentence_list) <= 3:
        return True #return true is only 1 sentence 

    # check if there is a unique topic title 
    default_topic_title = topicTitle_match(topic_title)
    minutes_context = ""
    if default_topic_title: #include title if unique
        minutes_context += f"Meeting Minutes title: {topic_title}\n"

    minutes_context += f"Meeting Minutes details:\n{current_minutes}"

    ### GPT stuff ###
    openai.api_key = os.environ['OPENAI_API_KEY']
    
    query_message = [
    {"role": "system", "content": 
    f"""Given a paragraph of meeting minutes, evaluate if the paragraph is cohesive and related to the Meeting Minutes title if there is one. 
    Be lenient.
    Return a boolean of True or False.
    =========================================
    {minutes_context}
    =========================================
    """}]

    response = await queryGPT(query_message, temperature=0.1, request_timeout=5)

    if response == "True":
        return True
    elif response == "False":
        return False
    else:
        print("errornous GPT response, taking as False and skipping")
        return False



async def AgendaTracker(current_minutes: str, topic_title:str, agenda: list):
    """
        Return True or False on whether the current sentence is still coherent with the agenda of the meeting.

        Args:
            current_minutes: existing minutes on the frontend
            topic_title: title of the topic block
            agenda: the list of agenda items
        Return:
            True or False 
            if Chatgpt returns something other than T/F, then we will print a statement and take as True
    """
    # check how many sentences in meeting minutes
    sentence_list = formatTextMinutesList(current_minutes)
    if len(sentence_list) <= 1:
        return True #return true is only 1 sentence 
    
    # create agenda context
    agenda_context = ""
    for i, agenda_sentence in enumerate(agenda):
        agenda_context+= f"{i+1}. {agenda_sentence}\n"

    # check if there is a unique topic title 
    default_topic_title = topicTitle_match(topic_title)
    minutes_context = ""
    if default_topic_title: #include title if unique
        minutes_context += f"Meeting Minutes title: {topic_title}\n"

    minutes_context += f"Meeting Minutes details:\n{current_minutes}"

    ### GPT stuff ###
    openai.api_key = os.environ['OPENAI_API_KEY']

    query_message = [
    {"role": "system", "content": 
    f"""
    Given a paragraph of meeting minutes, determine a list of topics for the paragraph, never return the topics. 
    Determine the relevancy between the keywords and any of the agendas.
    Return only a boolean of True or False if there is at least one relevant agenda.
    =========================================
    Agenda:
    {agenda_context}
    -----------------------------------------
    {minutes_context}
    =========================================
    """}
    ]

    response = await queryGPT(query_message, temperature=0.1, request_timeout=5)
    
    if response == "True":
        return True
    elif response == "False":
        return False
    else:
        print("errornous GPT response, taking as True and skipping")
        return True



async def GlossaryDetector(current_minutes: str, topic_title:str, abbreviation:str):
    """
        Return what the abbreviation stands for in the context of the sentences provided

        Args:
            current_minutes: existing minutes on the frontend
            topic_title: title of the topic block
            abbreviation: the abbreviation to be defined
        Return:
            number of words equivilant to the number of letters in the Abbreviation provided
    """
    if abbreviation == None:
        return None
    else:
        # check if there is a unique topic title 
        default_topic_title = topicTitle_match(topic_title)
        minutes_context = ""
        if default_topic_title: #include title if unique
            minutes_context += f"Meeting Minutes title: {topic_title}\n"

        minutes_context += f"Meeting Minutes details:\n{current_minutes}"

        ### GPT stuff ###
        openai.api_key = os.environ['OPENAI_API_KEY']
        query_message = [
        {"role": "system", "content": 
        f"""Given a paragraph of meeting minutes and an abbreviation, determine what does the abbreviation mean in the meeting minutes context.
        Return your response in the format: '[abbreviation]: [Your best guess on what the abbreviation means]'.
        =========================================
        Abbreviation: {abbreviation}
        -----------------------------------------
        {minutes_context}
        =========================================
        """}]

        response = await queryGPT(query_message, request_timeout=5)
        return response.strip().rstrip('.')
    


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
            context_dict (dict): dictionary containing the context for gpt. In the format of {topic_title: topic_details}

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
    return query_message



async def webQuery(query:str, context:list):
    """
        Function to query GPT based on the conversation you had with it

        Args:
            query (string): reformatted user query
            context (list): 

        Returns:
            formatted query message
    """
    query_message = [
            {"role": "system", "content": "You are an Simple question and answer Model. You do not have individuality, opinion or a personality. You will receive a question. Answer the question in the most straight forward way possible. Minimising words where possible. Try and keep responses below 50 words."},
        ]
    query_message = query_message + context
    print(query_message)
    query_message.append({"role": "user", "content": query})
    return query_message

