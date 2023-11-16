import asyncio
import datetime
from src.utils.mongoDBManager import MongoDBManager
from src.utils.createMongoDocument import initialiseMongoData

async def MongoDBTest():

    document_ids = initialiseMongoData()

    mongo = MongoDBManager(document_ids["minutesID"], document_ids["chatHistoryID"])
    new_data_agenda = ['create design system', 'create web experiment']
    new_data_meeting_details = {
        "date": datetime.datetime.now(),
        "location": "studio",
        "attendees": ['hn', 'jx', 'yl', 'wx']
    }

    new_topic_update = {'00': 'bulletpoint1', '01': 'bulletpoint2'}
    append_topic_update = {'02': 'bulletpoint3'}
    replace_topic_update = {'01': 'new bulletpoint2', '03': 'bulletpoint4', '03': 'new bulletpoint4'}

    try:
        
        await mongo.update_agenda_meeting(new_data_agenda, True)
        await mongo.update_agenda_meeting(new_data_meeting_details, False)

        await mongo.update_topic_minutes(new_topic_update, True, '0', None)
        await mongo.update_topic_minutes(append_topic_update, False, '0', None)
        await mongo.update_topic_minutes(replace_topic_update, False, '0', None)

        await mongo.update_chat_history({'user': "what is the topic of work?",'assistant': "The topic can be found in ..."}, 'document')
        await mongo.update_chat_history({'user': "what about this?",'assistant': "The topic is about ..."}, 'document')
        await mongo.update_chat_history({'user': "what is 1+1",'assistant': "3"}, 'web')

        mongo.read_MongoDB('minutes', True, None, None)
        mongo.read_MongoDB('minutes', False, '0', None)
        mongo.read_MongoDB('chatHistory', False, None, 'document')
        mongo.read_MongoDB('chatHistory', False, None, 'web')

        await mongo.clear_chat_history('web')
        mongo.read_MongoDB('chatHistory', False, None, 'web')

        await mongo.delete_topic('0')
        mongo.read_MongoDB('minutes', False, '0', None)

        await mongo.delete_document(document_ids["minutesID"], 'minutes')

        await mongo.delete_all_documents('chatHistory')

        await mongo.delete_all_documents('minutes')

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(MongoDBTest())
