from utils.mongoDBManager import MongoDBManager


async def read_history(minutes_id:str, chat_history_id: str):
    """
    Format chat history from mongoDB and return to client

    Args:
        minutes_id (str): minutes document id
        chat_history_id (str): chatHistory document id

    Returns:
        dict of list {document: [], web: []}
    """
    mongoDB = MongoDBManager(minutes_id, chat_history_id)

    document_chat_history = mongoDB.read_MongoDB('chatHistory', chat_history_type="document")
    formatted_document_history = format_chat_history(document_chat_history['document'], 'document')
    web_chat_history = mongoDB.read_MongoDB('chatHistory', chat_history_type="web")
    formatted_web_history = format_chat_history(web_chat_history['web'], 'web')
    
    return {'document': formatted_document_history, 'web': formatted_web_history}


def format_chat_history(chat_history:list, type:str):
    """
    Format chat history from [{"user": xxx, "assistant": yyy, "sourcetopicIDs": [],...}] to a list of [{user: xxx}, {assistant:yyy, sourcetopicIDs:[]}, ...]

    Args:
        chat_history (list): chathistory in mongoDB
        type (str): either document/web, determines if sourcetopicIDs exists

    Returns:
        list: list of formatted query
    """
    
    index = 0 
    formatted_chat_history = []

    if type == 'web':
        while index < len(chat_history):
            for role, query in chat_history[index].items():
                formatted_chat_history.append({role: query})
            index += 1

    if type == 'document':
        while index < len(chat_history):
            formatted_chat_history.append({'user': chat_history[index]['user']})
            formatted_chat_history.append({'assistant': chat_history[index]['assistant'], 'sourceID': chat_history[index]['sourcetopicIDs']})
            index += 1



    return formatted_chat_history
