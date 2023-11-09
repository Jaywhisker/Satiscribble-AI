import pymongo
import os
from fastapi import HTTPException
from bson import ObjectId


class MongoDBManager():
    def __init__(self, minutesID, chatHistoryID):
        self.mongoDB_url = f"mongodb://{os.environ['MONGODB_USERNAME']}:{os.environ['MONGODB_PASSWORD']}@{os.environ['MONGODB_URL']}"
        self.client = pymongo.MongoClient(self.mongoDB_url)
        self.database = self.client['document_db']
        self.minutesID = ObjectId(minutesID)
        self.chatHistoryID = ObjectId(chatHistoryID)



    def read_MongoDB(self, collection_name:str, agenda:bool= False, topic_id:str= None, chat_history_type:str= None):
        """
            Function to read from MongoDB

            Args: 
                collection_name (str): Only minutes / chatHistory
                agenda (boolean): True to query agenda, else use False
                topic_id (str): Used to query the topic through topicID
                chat_history_type (str): Used to determine which chatHistory to query, Only document / web
            
            Res: 
                mongoDB response, always in the format of a JSON
        """

        if collection_name != "minutes" and collection_name != "chatHistory":
            raise HTTPException(status_code=422,detail="Invalid Database Collection Name")

        elif collection_name == "minutes":
            if agenda:
                agendaData = self.database.minutes.find_one({'_id': self.minutesID}, {"agenda": 1, "_id": 0})
                return agendaData

            else:
                query = {"topics.topicID": topic_id, '_id': self.minutesID}
                topicData = self.database.minutes.find_one(query,  {"topics.$": 1}) #topics.$ means include the result that FIRST matches the condition
                # if topicId does not exist
                if topicData:
                    return topicData['topics'][0]
                else:
                    return None

        else:
            chatHistory = self.database.chatHistory.find_one({'_id': self.chatHistoryID}, {f"{chat_history_type}": 1, "_id": 0})
            if chatHistory:
                return chatHistory
            else:
                raise HTTPException(status_code=422,detail="ChatHistory Document unfound in Database")

    
    def read_glossary(self):
        glossaryData = self.database.minutes.find_one({'_id': self.minutesID}, {"glossary": 1, "_id": 0})
        return glossaryData


    async def update_agenda_meeting(self, new_data, agenda:bool):
        """
            Function to replace data in MongoDB

            Args: 
                new_data (list / dictionary): if agenda, expect list, if not agenda (meetingDetails), expect JSON
                agenda (boolean): True to replace agenda, else use False
            
            Res: 
                dictionary of status
        """
        if agenda and isinstance(new_data, list):
            # new_data in the format of [agenda, agenda etc]
            update_query = {"$set": {"agenda": new_data}}

        elif not agenda and isinstance(new_data, dict):
            # new_data in the format of {date:xxx, location:xxx, attendees: []}
            update_query = {"$set": {"meetingDetails": new_data}}

        else:
            raise HTTPException(status_code=422,detail="Invalid minutes input for updating")

        filter_query = {"_id": self.minutesID}      
        update = self.database.minutes.update_one(filter_query, update_query)
        if update.modified_count > 0 and update.acknowledged:
            return {'status': 200}
        elif update.acknowledged:
            return {'status': 'Same values, no update'}
        else:
            raise HTTPException(status_code=422,detail="Updating Database Failed")



    async def update_topic_minutes(self, update_list: dict, create_topic: bool, topic_id: str, topic_title: str):
        """
        Function to update minutes in MongoDB

        Args:
            update_list (dictionary): dictionary in the form of {sentenceID: sentenceText, ...}
            create_topic (boolean): True/False to determine if you need to create a topic in the database
            topic_id (string): string containing the topic id
            topic_title (string): string containing the topic title

        Returns:
            dictionary of status
        """
        filter_query = {"_id": self.minutesID}

        # topic does not exist in the DB, needs to create, can just directly push
        if create_topic:
            new_topic = {
                "topicID": topic_id,
                "topicTitle": topic_title,
                "sentences": []
            }

            for sentence_id in update_list.keys():
                sentence_dict = {"sentenceID": sentence_id, "sentenceText": update_list[sentence_id]}
                new_topic['sentences'].append(sentence_dict)

            update_operation = {"$push": {"topics": new_topic}}
            update = self.database.minutes.update_one(filter_query, update_operation)
            if not update.acknowledged:
                raise HTTPException(status_code=422,detail="Create topic in Database Failed")

        else:
            for sentence_id in update_list.keys():

                if update_list[sentence_id] == None:
                    #Delete sentence from database
                    update_operation = {
                        "$pull": {
                            "topics.$[topic].sentences": {"sentenceID": sentence_id}
                        },
                    }
                    
                    array_filters = [
                        {"topic.topicID": topic_id},
                    ]

                elif self.database.minutes.count_documents({
                    **filter_query,
                    "topics": {
                        "$elemMatch": {
                            "topicID": topic_id,
                            "sentences": {
                                "$elemMatch": {
                                    "sentenceID": sentence_id
                                }
                            }
                        }
                    }
                }) > 0:
                    #Sentence exist, replace with new sentence
                    update_operation = {
                        "$set": {
                            "topics.$[topic].sentences.$[sentence].sentenceText": update_list[sentence_id]
                        },
                    }

                    array_filters = [
                        {"topic.topicID": topic_id},
                        {"sentence.sentenceID": sentence_id}
                    ]

                else:
                    #push to the sentences db
                    update_operation = {
                        "$push": {
                            "topics.$[topic].sentences": {"sentenceID": sentence_id, "sentenceText": update_list[sentence_id]}
                        }
                    }
                    array_filters = [
                        {"topic.topicID": topic_id},
                    ]

                update = self.database.minutes.update_one(filter_query, update_operation, array_filters=array_filters)

                if not update.acknowledged:
                    raise HTTPException(status_code=422,detail="Updating Database Failed")

        return {"status": 200}


    async def update_glossary(self, abbreviation:str, meaning:str, action:str):
        """
        Function to update the glossary

        Args:
            abbreviation (str): abbreviation of the term
            meaning (str): full meaning
            action (str): action to be done
        """
        filter_query = {"_id": self.minutesID}
        array_filters = None
        if action == 'new':
            update_operation = {
                "$push": {
                    "glossary": {'abbreviation': abbreviation, "meaning": meaning}
                }
            }
        
        elif action == 'delete':
            update_operation = {
                "$pull": {
                    "glossary": {'abbreviation': abbreviation, "meaning": meaning}
                }
            }

        elif action == 'update': 
            update_operation = {
                "$set": {
                    "glossary.$[abbrev].meaning" : meaning 
                }
            }

            array_filters = [
                {"abbrev.abbreviation": abbreviation},
            ]
        
        update = self.database.minutes.update_one(filter_query, update_operation, array_filters=array_filters)
        if not update.acknowledged:
            raise HTTPException(status_code=422,detail="Unable to delete topic")

        return {"status": 200}


    async def delete_topic(self, topic_id:str):
        """
            Function to delete a topic and all minutes inside

            Args:
                topic_id (string): id of topic to be deleted
            
            Returns:
                dictionary of status
        """
        filter_query = {"_id": self.minutesID}
        update_operation = {
            "$pull": {
                "topics": {
                    "topicID": topic_id
                }
            }
        }

        update = self.database.minutes.update_one(filter_query, update_operation)
        if not update.acknowledged:
            raise HTTPException(status_code=422,detail="Unable to delete topic")

        return {"status": 200}

    

    async def update_chat_history(self, chat_history:dict, query_type:str):
        """
            Function to update the chatHistory collection with the next set of prompt and response

            Args:
                chat_history (dictionary): in the format of {'user': query, 'assistant': gpt response} 
                query_type (string): only web/document, determines which db to update
                topic_ids (list): list of unique topic ids
            
            Returns:
                dictionary of status
        """
        #chat_history should never have more than 2 keys!
        if query_type != 'document' and query_type != 'web':
            raise HTTPException(status_code=422,detail="Invalid Database Collection Name")

        filter_query = {"_id": self.chatHistoryID}
        update_operation = {
            "$push": {
                query_type: chat_history
            }
        }
        update = self.database.chatHistory.update_one(filter_query, update_operation)
        if not update.acknowledged:
            raise HTTPException(status_code=422,detail="Unable to update chat history")

        return {'status': 200}


    async def clear_chat_history(self, query_type:str):
        """
            Function to delete and clear chat history and replace with []

            Args:
                query_type (string): only web/document, determines which db to clear
            
            Returns:
                dictionary of status
        """
        if query_type != 'document' and query_type != 'web':
            raise HTTPException(status_code=422,detail="Invalid Database Collection Name")
        
        filter_query = {"_id": self.chatHistoryID}
        update_operation = {
            "$set": {
                query_type: []
            }
        }
        update = self.database.chatHistory.update_one(filter_query, update_operation)
        if not update.acknowledged:
            raise HTTPException(status_code=422,detail="Unable to clear chat history")

        return {'status': 200}



    async def delete_document(self, document_id:str, collection_name:str):
        """
            Function to delete any document from any collection

            Args:
                document_id (string): _id string value for the document to be deleted
                collection_name (string): only minutes / chatHistory
            
            Returns:
                dictionary of status
        """
        if collection_name != 'minutes' and collection_name != 'chatHistory':
            raise HTTPException(status_code=422,detail="Invalid Database Collection Name")
        result = self.database[collection_name].delete_one({'_id': ObjectId(document_id)})
        if result.deleted_count != 1:
            raise HTTPException(status_code=422,detail="Unable to delete document")
        
        return {"status": 200}



    async def delete_all_documents(self, collection_name:str):
        """
            Function to delete ALL document from collection

            Args:
                collection_name (string): only minutes / chatHistory
            
            Returns:
                dictionary of status
        """
        if collection_name != 'minutes' and collection_name != 'chatHistory':
            raise HTTPException(status_code=422,detail="Invalid Database Collection Name")

        result = self.database[collection_name].delete_many({})
        return {"status": 200}





# async def test():

#     document_ids = initialiseMongoData()

#     mongo = MongoDBManager(document_ids["minutesID"], document_ids["chatHistoryID"])
#     new_data_agenda = ['create design system', 'create web experiment']
#     new_data_meeting_details = {
#         "date": datetime.datetime.now(),
#         "location": "studio",
#         "attendees": ['hn', 'jx', 'yl', 'wx']
#     }

#     new_topic_update = {'00': 'bulletpoint1', '01': 'bulletpoint2'}
#     append_topic_update = {'02': 'bulletpoint3'}
#     replace_topic_update = {'01': 'new bulletpoint2', '03': 'bulletpoint4', '03': 'new bulletpoint4'}

    # try:
        
        # result = await mongo.update_agenda_meeting(new_data_agenda, True)
        # print(result)
        # result = await mongo.update_agenda_meeting(new_data_meeting_details, False)
        # print(result)

        # result = await mongo.update_topic_minutes(new_topic_update, True, '0', None)
        # print(result)
        # result = await mongo.update_topic_minutes(append_topic_update, False, '0', None)
        # print(result)
        # result = await mongo.update_topic_minutes(replace_topic_update, False, '0', None)
        # print(result)

        # result = await mongo.update_chat_history({'user': "what is the topic of work?",'assistant': "The topic can be found in ..."}, 'document')
        # print(result)
        # result = await mongo.update_chat_history({'user': "what about this?",'assistant': "The topic is about ..."}, 'document')
        # print(result)
        # result = await mongo.update_chat_history({'user': "what is 1+1",'assistant': "3"}, 'web')
        # print(result)

        # read_agenda = mongo.read_MongoDB('minutes', True, None, None)
        # read_topic = mongo.read_MongoDB('minutes', False, '0', None)
        # read_document_history = mongo.read_MongoDB('chatHistory', False, None, 'document')
        # read_web_history = mongo.read_MongoDB('chatHistory', False, None, 'web')
        # print(read_agenda, read_topic, read_document_history, read_web_history)

        # result = await mongo.clear_chat_history('web')
        # print(result)
        # read_web_history = mongo.read_MongoDB('chatHistory', False, None, 'web')
        # print(read_web_history)

        # result = await mongo.delete_topic('0')
        # print(result)
        # read_topic = mongo.read_MongoDB('minutes', False, '0', None)
        # print(read_topic)

        # result = await mongo.delete_document(document_ids["minutesID"], 'minutes')
        # print(result)

        # result = await mongo.delete_all_documents('chatHistory')
        # print(result)

        # result = await mongo.delete_all_documents('minutes')
        # print(result)

    # except Exception as e:
    #     print(f"Error: {e}")

# if __name__ == "__main__":
#     asyncio.run(test())


