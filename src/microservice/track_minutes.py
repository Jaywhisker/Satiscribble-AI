import asyncio
from utils.mongoDBManager import MongoDBManager
from utils.chromaDBManager import ChromaDBManager
from utils.formatData import *
from utils.gptManager import *

async def track_minutes(new_minutes:str, topic_title:str, topic_id:str, minutes_id:str, chat_history_id:str, abbreviation:str):
    """
    Function for endpoint /track_minutes. The rough pipeline is as follows:
        1. Format the new minutes to a dictionary
        2. Read from mongoDB
        3. If mongoDB does not contain this topic, create topic and run TopicTracker, AgendaTracker and GlossaryDetector
        4. If mongoDB does contain this topic, do a comparison to see which minutes are different, update mongoDB and run TopicTracker, AgendaTracker and GlossaryDetector

    Args:
        new_minutes (string): minutes on the frontend, where each bulletpoint is split by \n
        topic_title (string): topic title of the topic block minutes reside in
        topic_id (string): topic id of topic block
        minutes_id (string): document id in minutes collection
        chat_history_id (string): document id in chatHistory collection
        abbreviation (string): None if no abbreviation, else the abbreviation text

    Returns:
        dictionary in the format {topic: True/False, agenda: True/False, glossary: None or suggested name of abbreviation}
    """
    chromaDB = ChromaDBManager(minutes_id)
    mongoDB = MongoDBManager(minutes_id, chat_history_id)
    existing_minutes = mongoDB.read_MongoDB('minutes', False, topic_id, None)
    formatted_new_minutes =  formatTextMinutes(new_minutes, topic_id)

    newMinutesList = createContext(new_minutes)

    existingAgenda = mongoDB.read_MongoDB('minutes', True, None, None)
    existingAgenda = existingAgenda['agenda']
    
    if existing_minutes == None:
        # New topic block
        Topic, Agenda, Glossary, MongoStatus, ChromaStatus = await asyncio.gather(
                                                            TopicTracker(newMinutesList),
                                                            AgendaTracker(new_minutes, topic_title, existingAgenda),
                                                            GlossaryDetector(newMinutesList,abbreviation),
                                                            mongoDB.update_topic_minutes(formatted_new_minutes, True, topic_id, topic_title),
                                                            chromaDB.update_embeddings(formatted_new_minutes, topic_id, topic_title)
                                                        )
  

    else:
        formatted_existing_minutes = formatMongoMinutes(existing_minutes['sentences'])
        update_dict = {}

        for sentenceID in formatted_new_minutes.keys():
            new_sentence = formatted_new_minutes[sentenceID]
            old_sentence = formatted_existing_minutes.get(sentenceID, '')
            if new_sentence != old_sentence:
                update_dict[sentenceID] = new_sentence
        
        
        if len(formatted_existing_minutes) > len(formatted_new_minutes):
            i = len(formatted_new_minutes)
            while i < len(formatted_existing_minutes):
                update_dict[topic_id + str(i)] = None
                i += 1
        
        Topic, Agenda, Glossary, MongoStatus, ChromaStatus = await asyncio.gather(
                                                        TopicTracker(newMinutesList),
                                                        AgendaTracker(new_minutes, topic_title, existingAgenda),
                                                        GlossaryDetector(newMinutesList,abbreviation),
                                                        mongoDB.update_topic_minutes(update_dict, False, topic_id, topic_title),
                                                        chromaDB.update_embeddings(update_dict, topic_id, topic_title)
                                                    )
    

    return {"topic": Topic, "agenda": Agenda, "abbreviation": Glossary}


