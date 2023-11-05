import os
import chromadb
from chromadb.utils import embedding_functions
from fastapi import HTTPException



class ChromaDBManager():

    def __init__(self, collection_name:str):
        self.chromaDB = chromadb.HttpClient(host=os.environ['CHROMADB_URL'], port=8001)
        self.collection_name = collection_name
        self.embeddingFunction = embedding_functions.OpenAIEmbeddingFunction(
                                                                    api_key=os.environ['OPENAI_API_KEY'],
                                                                    model_name="text-embedding-ada-002"
                                                                )
        self.minutesCollection = self.chromaDB.get_or_create_collection(self.collection_name, embedding_function=self.embeddingFunction)


    async def update_embeddings(self, update_list:dict, topic_id: str, topic_title:str):
        """
        Function to update vector embeddings inside chrome

        Args:
            update_list (dict): dictionary in the format of {sentenceID: sentenceText} that needs to be updated, will be {sentenceID: None} if to be deleted
            topic_id (str): string containing the topic id, will be the metadata (defines the parent document)

        Returns:
            dictionary of status 200
        """
        meta_data = {'topicID': topic_id, 'topicTitle': topic_title if topic_title!= None else 'No Title'}
        update_sentenceID = []
        update_sentenceText = []
        delete_sentenceID = []

        for sentenceID, sentenceText in update_list.items():
            if sentenceText != None:
                update_sentenceID.append(sentenceID)
                update_sentenceText.append(sentenceText)
            
            else:
                delete_sentenceID.append(sentenceID)
        try:
            if len(update_sentenceID) > 0:
                await self.upsert_embedding(update_sentenceID, update_sentenceText, meta_data)
            
            if len(delete_sentenceID) > 0:
                await self.delete_embedding(delete_sentenceID)
            
            return {'status': 200}
    
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail="Unable to update chromaDB")



    async def upsert_embedding(self, sentenceID, sentenceText, metadata):
        """
        Function to upsert embeddings

        Args:
            sentenceID (list): list of ids(str) to be updated
            sentenceText (list): list of sentence text (str) to be updated
            metadata (dict): dict in the format of {'topicID': topic_id}
        """
        self.minutesCollection.upsert(ids= sentenceID, 
                        metadatas= [metadata for i in range(len(sentenceID))],
                        documents= sentenceText)


    
    async def delete_embedding(self, deletedIDs):
        """
        Function to delete embeddings based on the specific ids

        Args:
            deletedIDs (list): list of ids(str) to be deleted
        """
        self.minutesCollection.delete(ids = deletedIDs)
            


    async def query_collection(self, query:str, k:int):
        try:
            results = self.minutesCollection.query(query_texts=query,
                                                n_results=k,
                                                include=['metadatas'])
            
            print(results)
            all_parent_topics = [data['topicID'] for sublist in results['metadatas'] for data in sublist]
            unique_parent_topics = list(set(all_parent_topics))
            
            #getting all parent ids
            context_dict = {}
            for parentID in unique_parent_topics:
                all_child_documents = self.minutesCollection.get(where={"topicID": parentID})

                #get topic title
                topic_title = all_child_documents['metadatas'][0]['topicTitle']
                #sort sentences into order by using sentenceID
                zipped_id_document = list(zip(all_child_documents['ids'], all_child_documents['documents']))
                sorted_id_document = sorted(zipped_id_document, key=lambda x: int(x[0]))
                #retrieve document
                topic_minutes = ''
                for item in sorted_id_document:
                    topic_minutes += f"{item[1]}\n"

                context_dict[topic_title] = topic_minutes

            return unique_parent_topics, context_dict


        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail="Unable to retrieve minutes from chromaDB")

            
    
    def delete_collection(self, collection_name:str):
        """
        Function to delete collection from chromaDB

        Args:
            collection_name (str): Name of collection to be deleted

        Returns:
            dict of status 200
        """
        self.chromaDB.delete_collection(collection_name)
        return {'status': 200}
    


    def list_collection(self):
        """
        Function to retrieve all collections in database

        Returns:
            list of all available collections
        """
        print(self.chromaDB.list_collections())
        return self.chromaDB.list_collections()


    def get_documents(self):
        """
        Function to retrieve all documents inside collection

        Returns:
            dictionary of all documents
        """
        print(self.minutesCollection.get(include=['documents', 'metadatas']))
        return self.minutesCollection.get(include=['documents', 'metadatas'])

