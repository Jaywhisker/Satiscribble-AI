from fastapi import FastAPI, Body
from fastapi import HTTPException
import asyncio
from pydantic import BaseModel
from queue import Queue
from uuid import uuid4


import queue

from microservice.track_minutes import *
from microservice.document_qna import *
from microservice.web_qna import *
from microservice.summarisation import *
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

class QnA(BaseModel):
    query: str
    type: str
    minutesID: str
    chatHistoryID: str 

class SummarisationRequest(BaseModel):
    text: str
    minutesID: str
    chatHistoryID: str
    topicTitle: str
    topicID: str 

app = FastAPI()

# So mostly done by chatgpt lmao
# But essentially, we create this function that just handles things in the queue

@app.on_event("startup")
async def start_worker():
    asyncio.create_task(worker())
    print("worker started")

# The queue of task and a dictionary with their id and results
task_queue = Queue()
pending_tasks = {}


stop_signal = False

# Honestly I have no idea why this is needed but oh well
@app.on_event("shutdown")
async def stop_worker():
    global stop_signal
    stop_signal = True



async def worker():
    while not stop_signal:
        if not task_queue.empty():
            task_type, task_data, task_id = task_queue.get()
            event, _ = pending_tasks[task_id]
            
            try:
                if task_type == 'update_agenda':
                    mongoDB = MongoDBManager(task_data.minutesID, task_data.chatHistoryID)
                    result = await mongoDB.update_agenda_meeting(task_data.agenda, True) 

                elif task_type == 'track_minutes':
                    result = await track_minutes(task_data.minutes, task_data.topicTitle, task_data.topicID, task_data.minutesID, task_data.chatHistoryID, task_data.abbreviation)
                
                elif task_type == 'update_meeting':
                    mongoDB = MongoDBManager(task_data.minutesID, task_data.chatHistoryID)
                    result = await mongoDB.update_agenda_meeting(task_data.data, False) 
                
                elif task_type == 'delete_topic':
                    mongoDB = MongoDBManager(task_data.minutesID, task_data.chatHistoryID)
                    result =  await mongoDB.delete_topic(task_data.topicID)
                
                elif task_type == 'clear':
                    mongoDB = MongoDBManager(task_data.minutesID, task_data.chatHistoryID)
                    result = await mongoDB.clear_chat_history(task_data.type)

                elif task_type == 'webquery':
                    result = await web_query(task_data.query, task_data.minutesID, task_data.chatHistoryID)

                elif task_type == 'summary':
                    result = await summarisation(task_data.text, task_data.topicTitle, task_data.minutesID, task_data.chatHistoryID)
                
                # Store the result
                _, _ = pending_tasks[task_id]
                pending_tasks[task_id] = (event, result)
            
            except Exception as e:
                # You can handle exceptions here, and potentially return a meaningful error to the caller
                pending_tasks[task_id] = (event, {"error": str(e)})
            
            finally:
                # Signal that the task is done
                event.set()

        else:
            await asyncio.sleep(1)


# Function used to put things in a queue and wait for response

async def AddTaskWaitResponse(task_type: str, task_data):
    task_id = uuid4().hex
    event = asyncio.Event()
    task = (task_type, task_data, task_id)
    task_queue.put(task)
    pending_tasks[task_id] = (event, None)  # The second element is for the result, which is None initially
    
    await event.wait()
    result = pending_tasks.pop(task_id)[1]
    
    return result


# Update_agenda and track_minutes have been updated, they will now just put things into the queue
# Wait for the worker to work on them and when there is completion, take the result and return
# They also clear their result from pending task
@app.post("/update_agenda")
async def update_agenda(request_body: AgendaUpdateRequest):
    return await AddTaskWaitResponse('update_agenda', request_body)

@app.post("/track_minutes")
async def handle_track_minutes(request_body: TrackMinutesRequest):
    return await AddTaskWaitResponse('track_minutes', request_body)

@app.post("/update_meeting")
async def update_meeting(request_body: MeetingUpdateRequest):
    return await AddTaskWaitResponse('update_meeting', request_body)

@app.post("/delete_topic")
async def handle_delete_topic(request_body: DeleteTopicRequest):
    return await AddTaskWaitResponse('delete_meeting', request_body)

@app.post("/clear")
async def handle_clear_chat(request_body:ClearChatHistory):
    return await AddTaskWaitResponse('clear', request_body)

@app.post("/web_query")
async def handleWebQuery(request_body:QnA):
    return await AddTaskWaitResponse('webquery', request_body)





# I have no clue if we should keep these functions as are or just move them into the worker

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


@app.post("/document_query")
async def handle_document_qna(request_body: QnA):
    return await document_qna(request_body.query, request_body.minutesID, request_body.chatHistoryID)


@app.post("/clear")
async def handle_clear_chat(request_body:ClearChatHistory):
        mongoDB = MongoDBManager(request_body.minutesID, request_body.chatHistoryID)
        return await mongoDB.clear_chat_history(request_body.type)

@app.post("/summary")
async def handle_summarisation(request_body: SummarisationRequest):
    result = await summarisation(
        request_body.minutesID,
        request_body.chatHistoryID,
        request_body.topicID,  
        request_body.topicTitle
    )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return {"summary": result["summary"]}

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

# These functions have been moved into the worker

# @app.post("/track_minutes")
# async def handle_track_minutes(request_body: TrackMinutesRequest):
#     return await track_minutes(request_body.minutes, request_body.topicTitle, request_body.topicID, request_body.minutesID, request_body.chatHistoryID, request_body.abbreviation)

# @app.post("/update_agenda")
# async def update_agenda(request_body: AgendaUpdateRequest):
#     mongoDB = MongoDBManager(request_body.minutesID, request_body.chatHistoryID)
#     return await mongoDB.update_agenda_meeting(request_body.agenda, True) 


# Untested cause I forgot the input json format lmao
# @app.post("/update_meeting")
# async def update_meeting(request_body: MeetingUpdateRequest):
#     mongoDB = MongoDBManager(request_body.minutesID, request_body.chatHistoryID)
#     return await mongoDB.update_agenda_meeting(request_body.data, False) 

# @app.post("/delete_topic")
# async def handle_delete_topic(request_body: DeleteTopicRequest):
#     mongoDB = MongoDBManager(request_body.minutesID, request_body.chatHistoryID)
#     return await mongoDB.delete_topic(request_body.topicID)


# @app.post("/clear")
# async def handle_clear_chat(request_body:ClearChatHistory):
#         mongoDB = MongoDBManager(request_body.minutesID, request_body.chatHistoryID)
#         return await mongoDB.clear_chat_history(request_body.type)

