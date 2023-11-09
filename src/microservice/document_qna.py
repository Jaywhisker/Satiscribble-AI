from utils.mongoDBManager import MongoDBManager
from utils.chromaDBManager import ChromaDBManager
from utils.formatData import *
from utils.gptManager import *


async def document_qna(query:str, mongoDB, minutes_id:str, k:int = 3):
    """
        Reformats user query to a standalone question before extracting the context from chromaDB and reformatting the context

        Args:
            query (str): User query
            mongoDB (_type_): mongoDB instance to read chatHistory
            minutes_id (str): The minutes_id for chroma
            k (int, optional): Chroma similarity search returns k nearest neighbour. Defaults to 3.

        Returns:
            header: response header in the format of "source_id": str(list of topic_ids context is pulled from)
            query_message: formatted query message with context
    """
    chromaDB = ChromaDBManager(minutes_id)

    #get chat history
    chat_history = mongoDB.read_MongoDB('chatHistory', False, None, 'document')
    
    if len(chat_history.get('document', [])) != 0:
        formatted_chat_history = formatChatHistory(chat_history.get('document', []))
        #prepare prompt for openAI
        query = await createStandAloneQuery(formatted_chat_history, query)

    #querying chroma to get the related articles
    unique_parent_topics, context_dict = await chromaDB.query_collection(query, k)

    query_message = await documentQuery(query, context_dict)

    return unique_parent_topics, query_message

        
