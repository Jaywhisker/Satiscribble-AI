import os
import pymongo

def initialiseMongoData():
    """
    Function to create a new document for the minutes and chatHistory collection

    Args: None

    Res: dictionary of minutes collection ID and chatHistory collection ID
    """
    mongoDB_url = f"mongodb://{os.environ['MONGODB_USERNAME']}:{os.environ['MONGODB_PASSWORD']}@{os.environ['MONGODB_URL']}"
    client = pymongo.MongoClient(mongoDB_url)
    database = client['document_db']

    base_minutes_template = { "agenda": [],
                                "meetingDetails": {
                                    "date": None,
                                    "location": None,
                                    "attendees": []
                                },
                                "topics": []
                            }

    base_chatHistory_template = { "document": [], "web": []}

    minutes_result = database.minutes.insert_one(base_minutes_template)
    chat_result = database.chatHistory.insert_one(base_chatHistory_template)

    if minutes_result.inserted_id and chat_result.inserted_id:
        print(f"minute_id: {minutes_result.inserted_id}")
        print(f"chat_id: {chat_result.inserted_id}")

        return {"minutesID": minutes_result.inserted_id, "chatHistoryID": chat_result.inserted_id}


if __name__ == "__main__":
    initialiseMongoData()