from fastapi import FastAPI, Body
from fastapi import HTTPException
from pydantic import BaseModel

from microservice.track_minutes import *
from microservice.document_qna import *
from microservice.web_qna import *
from microservice.summarisation import *
from microservice.read_history import *
from utils.createMongoDocument import initialiseMongoData
from utils.mongoDBManager import MongoDBManager
from utils.gptManager import streamGPTQuery

class BaseRequest(BaseModel):
    minutesID: str
    chatHistoryID: str

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

class GlossaryUpdateRequest(BaseModel):
    abbreviation: str
    meaning: str
    type: str
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

class QnA(BaseModel):
    query: str
    type: str
    minutesID: str
    chatHistoryID: str 

class SummarisationRequest(BaseModel):
    minutesID: str
    chatHistoryID: str
    topicTitle: str
    topicID: str 


app = FastAPI()


@app.get("/")
async def root():
    return{"message": "hello world"}


@app.get("/create")
async def create_document():
    return initialiseMongoData()


@app.post("/read_history")
async def handle_read_history(request_body: BaseRequest):
    return await read_history(request_body.minutesID, request_body.chatHistoryID)


@app.post("/read_glossary")
def read_glossary(request_body: BaseRequest):
    mongoDB = MongoDBManager(request_body.minutesID, request_body.chatHistoryID)
    return mongoDB.read_glossary()


@app.post("/update_agenda")
async def update_agenda(request_body: AgendaUpdateRequest):
    mongoDB = MongoDBManager(request_body.minutesID, request_body.chatHistoryID)
    return await mongoDB.update_agenda_meeting(request_body.agenda, True) 


@app.post("/update_meeting")
async def update_meeting(request_body: MeetingUpdateRequest):
    mongoDB = MongoDBManager(request_body.minutesID, request_body.chatHistoryID)
    return await mongoDB.update_agenda_meeting(request_body.data, False) 


@app.post("/update_glossary")
async def update_glossary(request_body: GlossaryUpdateRequest):
    mongoDB = MongoDBManager(request_body.minutesID, request_body.chatHistoryID)
    return await mongoDB.update_glossary(request_body.abbreviation, request_body.meaning, request_body.type)


@app.post("/track_minutes")
async def handle_track_minutes(request_body: TrackMinutesRequest):
    return await track_minutes(request_body.minutes, request_body.topicTitle, request_body.topicID, request_body.minutesID, request_body.chatHistoryID, request_body.abbreviation)


@app.post("/delete_topic")
async def handle_delete_topic(request_body: DeleteTopicRequest):
    mongoDB = MongoDBManager(request_body.minutesID, request_body.chatHistoryID)
    return await mongoDB.delete_topic(request_body.topicID)


@app.post("/document_query")
async def handle_document_qna(request_body: QnA):
    mongoDB = MongoDBManager(request_body.minutesID, request_body.chatHistoryID)
    source_ids, formatted_query_message =  await document_qna(request_body.query, mongoDB, request_body.minutesID)
    return streamGPTQuery(formatted_query_message, user_query=request_body.query, type=request_body.type, request_timeout=5, source_ids=source_ids, mongoDB=mongoDB)



@app.post("/web_query")
async def handle_web_qna(request_body: QnA):
    mongoDB = MongoDBManager(request_body.minutesID, request_body.chatHistoryID)
    formatted_query_message = await web_query(request_body.query, mongoDB)
    return streamGPTQuery(formatted_query_message, user_query=request_body.query, type=request_body.type, request_timeout=5, mongoDB=mongoDB)




@app.post("/clear")
async def handle_clear_chat(request_body:ClearChatHistory):
        mongoDB = MongoDBManager(request_body.minutesID, request_body.chatHistoryID)
        return await mongoDB.clear_chat_history(request_body.type)

@app.post("/summarise")
async def handle_summarisation(request_body: SummarisationRequest):
    return await summariseText(
        request_body.minutesID,
        request_body.chatHistoryID,
        request_body.topicID,  
        request_body.topicTitle
    )


##for our personal use, should never be called by frontend
@app.post("/delete_document")
async def handle_delete_document(collectionName: str = Body(...), documentID: str = Body(None), minutesID: str = Body(...), chatHistoryID: str = Body(...)):
    mongoDB = MongoDBManager(minutesID, chatHistoryID)
    if documentID == None:
        documentID = minutesID
    return await mongoDB.delete_document(documentID, collectionName)


@app.post("/delete_collection")
async def handle_delete_collection(collectionName: str = Body(...), minutesID: str = Body(...), chatHistoryID: str = Body(...)):
    mongoDB = MongoDBManager(minutesID, chatHistoryID)
    return await mongoDB.delete_all_documents(collectionName)

