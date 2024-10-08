import os
import pymongo
import datetime
from fastapi import HTTPException

def initialiseMongoData():
    """
    Function to create a new document for the minutes and chatHistory collection

    Args: None

    Res: dictionary of minutes collection ID and chatHistory collection ID
    """
    try:
        mongoDB_url = f"mongodb://{os.environ['MONGODB_USERNAME']}:{os.environ['MONGODB_PASSWORD']}@{os.environ['MONGODB_URL']}"
        client = pymongo.MongoClient(mongoDB_url)
        database = client['document_db']

        base_minutes_template = { "agenda": [],
                                    "meetingDetails": {
                                        "date":  datetime.datetime.now(),
                                        "location": "",
                                        "attendees": []
                                    },
                                    "topics": [],
                                    "glossary": []
                                }

        base_chatHistory_template = { "document": [], "web": []}

        minutes_result = database.minutes.insert_one(base_minutes_template)
        chat_result = database.chatHistory.insert_one(base_chatHistory_template)

        if minutes_result.inserted_id and chat_result.inserted_id:
            print(f"minute_id: {minutes_result.inserted_id}")
            print(f"chat_id: {chat_result.inserted_id}")

            return {"minutesID": str(minutes_result.inserted_id), "chatHistoryID": str(chat_result.inserted_id)}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=422,detail="Unable to create document, is database up?")


if __name__ == "__main__":
    initialiseMongoData()