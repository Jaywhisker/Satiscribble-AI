from utils.mongoDBManager import MongoDBManager
from utils.chromaDBManager import ChromaDBManager
from utils.formatData import *
from utils.gptManager import *


async def document_qna(query:str, minutes_id:str,  chat_history_id: str, k:int = 3):
    mongoDB = MongoDBManager(minutes_id, chat_history_id)
    chromaDB = ChromaDBManager(minutes_id)

    #get chat history
    chat_history = mongoDB.read_MongoDB('chatHistory', False, None, 'document')
    
    if len(chat_history.get('document', [])) != 0:
        formatted_chat_history = formatChatHistory(chat_history.get('document', []))
        #prepare prompt for openAI
        query = await createStandAloneQuery(formatted_chat_history, query)

    #querying chroma to get the related articles
    unique_parent_topics, context_dict = await chromaDB.query_collection(query, k)
    response = await documentQuery(query, context_dict)

    #update mongoDB
    query_resp_pair = {'user': query, 'assistant': response}
    await mongoDB.update_chat_history(query_resp_pair, 'document')

    return {'source_ids': unique_parent_topics, 'response': response}

        
