from utils.mongoDBManager import MongoDBManager


async def read_history(minutes_id:str, chat_history_id: str):
    
    mongoDB = MongoDBManager(minutes_id, chat_history_id)

    document_chat_history = mongoDB.read_MongoDB('chatHistory', chat_history_type="document")
    formatted_document_history = format_chat_history(document_chat_history['document'])
    web_chat_history = mongoDB.read_MongoDB('chatHistory', chat_history_type="web")
    formatted_web_history = format_chat_history(web_chat_history['web'])
    
    return {'document': formatted_document_history, 'web': formatted_web_history}


def format_chat_history(chat_history:list):
    
    index = 0 
    formatted_chat_history = []
    
    while index < len(chat_history):
        for role, query in chat_history[index].items():
            formatted_chat_history.append([role, query])
        index += 1

    return formatted_chat_history
