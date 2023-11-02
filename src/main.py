from fastapi import FastAPI, Body
from fastapi import HTTPException
import asyncio
from pydantic import BaseModel

import queue

import openai
import os

from microservice.track_minutes import *
from utils.createMongoDocument import initialiseMongoData
from utils.mongoDBManager import MongoDBManager


class AgendaUpdateRequest(BaseModel):
    agenda: list
    minutesID: str
    chatHistoryID: str

class MeetingUpdateRequest(BaseModel):
    data: dict
    minutesID: str
    chatHistoryID: str

class TrackMinutesRequest(BaseModel):
    topicID: str
    topicTitle: str = None
    minutes: str
    abbreviation: str = None
    minutesID: str
    chatHistoryID: str 

class DeleteTopicRequest(BaseModel):
    topicID: str
    minutesID: str
    chatHistoryID: str 

class ClearChatHistory(BaseModel):
    type: str
    minutesID: str
    chatHistoryID: str 



app = FastAPI()

@app.get("/")
async def root():
    return{"message": "hello world"}


@app.get("/create")
async def create_document():
    return initialiseMongoData()


@app.post("/update_agenda")
async def update_agenda(request_body: AgendaUpdateRequest):
    mongoDB = MongoDBManager(request_body.minutesID, request_body.chatHistoryID)
    return await mongoDB.update_agenda_meeting(request_body.agenda, True) 


@app.post("/update_meeting")
async def update_meeting(request_body: MeetingUpdateRequest):
    mongoDB = MongoDBManager(request_body.minutesID, request_body.chatHistoryID)
    return await mongoDB.update_agenda_meeting(request_body.data, False) 


@app.post("/track_minutes")
async def handle_track_minutes(request_body: TrackMinutesRequest):
    return await track_minutes(request_body.minutes, request_body.topicTitle, request_body.topicID, request_body.minutesID, request_body.chatHistoryID, request_body.abbreviation)


@app.post("/delete_topic")
async def handle_delete_topic(request_body: DeleteTopicRequest):
    mongoDB = MongoDBManager(request_body.minutesID, request_body.chatHistoryID)
    return await mongoDB.delete_topic(request_body.topicID)


@app.post("/clear")
async def handle_clear_chat(request_body:ClearChatHistory):
        mongoDB = MongoDBManager(request_body.minutesID, request_body.chatHistoryID)
        return await mongoDB.clear_chat_history(request_body.type)



##for our personal use, should never be called by frontend
@app.post("/delete_document")
async def handle_delete_collection(collectionName: str = Body(...), documentID: str = Body(None), minutesID: str = Body(...), chatHistoryID: str = Body(...)):
    mongoDB = MongoDBManager(minutesID, chatHistoryID)
    if documentID == None:
        documentID = minutesID
    return await mongoDB.delete_document(documentID, collectionName)


@app.post("/delete_collection")
async def handle_delete_collection(collectionName: str = Body(...), minutesID: str = Body(...), chatHistoryID: str = Body(...)):
    mongoDB = MongoDBManager(minutesID, chatHistoryID)
    return await mongoDB.delete_all_documents(collectionName)

