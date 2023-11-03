import openai
import os
import string
from bson import ObjectId
from utils.mongoDBManager import MongoDBManager


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

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages= query_message,
        temperature=0.2
        )
    result = response['choices'][0]['message']['content']
    ### 
    if result == "True":
        return True
    elif result == "False":
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
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages= query_message,
        temperature=0.2
        )
    # await asyncio.sleep(5)
    # print("TopicTrackerResponse")
    result = (response['choices'][0]['message']['content'])
    ###
    if result == "True":
        return True
    elif result == "False":
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
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages= query_message,
            temperature=0.2
            )
        # await asyncio.sleep(5)
        # print("TopicTrackerResponse")
        result = (response['choices'][0]['message']['content'])
        ###
        result = result.strip(string.punctuation + " ")
        return result
    
async def WebQuery(question:str, minutes_id:str, chat_history_id:str):
    """
    Return a short statemenet on the question asked. The context is based on the chat history that the user has.

    Args:
        question (string): the current question asked by the user
        minutes_id (string): document id in minutes collection
        chat_history_id (string): document id in chatHistory collection
    Return:
        String response generated by openai
        updates the database as well
    """
    mongoDB = MongoDBManager(minutes_id, chat_history_id)
    existing_minutes = mongoDB.read_MongoDB('chatHistory', False, None, 'web')
    openai.api_key = os.environ['OPENAI_API_KEY']
    query_message = [
    {"role": "system", "content": "You are an Simple question and answer Model. You do not have individuality, opinion or a personality. You will receive a question. Answer the question in the most straight forwawrd way possible. Minimising words where possible. Try and keep responses below 50 words."},
    ]
    for QAPair in existing_minutes['web']:
        query_message.append({"role": "user", "content": QAPair['user']})
        query_message.append({"role": "assistant", "content": QAPair['assistant']})
    query_message.append({"role": "user", "content": question})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages= query_message,
        temperature=0.2
        )
    newARPair = {'user': question, 'assistant': response['choices'][0]['message']['content']}
    status = await mongoDB.update_chat_history(newARPair, 'web')
    # await asyncio.sleep(5)
    # print("TopicTrackerResponse")
    result = (response['choices'][0]['message']['content'])
    return result
