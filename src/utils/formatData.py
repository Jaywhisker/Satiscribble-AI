import re
from fastapi import HTTPException

def formatTextMinutes(text_minutes:str, topic_id:str):
    """
        Format text minutes where each bullet point is seperated by a \n

        Args:
            text_minutes (string): each bullet point is seperated by \n
            topic_id  (string): topic id of the text_minutes

        Return:
            dictionary in the format of {sentenceID: sentenceText}
    """
    minutes_dictionary = {}
    list_of_sentences = text_minutes.split("\n")
    
    for index, sentence in enumerate(list_of_sentences):
        minutes_dictionary[topic_id + str(index)] = sentence.strip()

    return minutes_dictionary


def formatMongoMinutes(mongo_minutes:list):
    """
        Format mongoDB minutes in the format of [{sentenceID:xx, sentenceText:yy}, ...]

        Args:
            mongo_minutes (list): each bullet point in a dictionary
        
        Return:
            dictionary in the format of {sentenceID: sentenceText}
    """
    minutes_dictionary = {}
    for bullet_point in mongo_minutes:
        minutes_dictionary[bullet_point['sentenceID']] = bullet_point['sentenceText']

    return minutes_dictionary
    

# ########### New Stuff ############
def formatTextMinutesList(text_minutes: str):
    """
        Format text minutes where each bullet point is seperated by a \n
        into a list for the chatgpt functions

        Args:
            text_minutes (string): each bullet point is seperated by \n
            (The function will also ignore double \n)

        Return:
            dictionary in the format of [sentence1, sentence2, ...]
    """
    sentences = re.split(r'(?<=[.!?])\s+|\n+', text_minutes)
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    return sentences



def  createContext(text_minutes:str, min_context:int = 3):
    """
        Takes in a list of sentences and returns the last min_context sentences as a list
        If the number of sentences is less than the min_context, then return all the sentences

        Args:
            text_minutes (string): each bullet point is seperated by \n
            min_context (int): number of sentences to return

        Return:
            dictionary in the format of [sentence1, sentence2, ...]
    """
    # We could combine the functions together, something to decide ltr
    sentences = formatTextMinutesList(text_minutes)
    if len(sentences) < 1:
        return sentences
    relevant_context = sentences[-min_context:] if len(sentences) >= min_context else sentences
    return relevant_context


def formatChatHistory(chat_history:list[dict]):
    """
        Function to format chatHistory nicely into a list of dictionary for chatCompletetion

        Args:
            chat_history (list[dict]): list of dictionary in the format of [{user: query, assistant: response}, {user:query, assistance: response}]

        Returns:
            formatted_chat_history: list of dictionary in the format [{role: user, content: query}, {role: assistant, content:response}, {}...]
    """
    formatted_chat_history = []
    while len(chat_history) > 0:
        formatted_chat_history.append({'role': 'user', 'content': chat_history[0]['user']})
        formatted_chat_history.append({'role': 'assistant', 'content': chat_history[0]['assistant']})
        chat_history = chat_history[2:]

    return formatted_chat_history

