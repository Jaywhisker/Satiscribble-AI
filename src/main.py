from fastapi import FastAPI
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
    response = await mongoDB.update_agenda_meeting(request_body.agenda, True) 
    return response

@app.post("/update_meeting")
async def update_meeting(request_body: MeetingUpdateRequest):
    mongoDB = MongoDBManager(request_body.minutesID, request_body.chatHistoryID)
    response = await mongoDB.update_agenda_meeting(request_body.data, False) 
    return response

@app.post("/track_minutes")
async def handle_track_minutes(request_body: TrackMinutesRequest):
    response = await track_minutes(request_body.minutes, request_body.topicTitle, request_body.topicID, request_body.minutesID, request_body.chatHistoryID, request_body.abbreviation)
    return response


# # Testing concurent calls
# @app.get("/test")
# async def root():
#     post, comment, post2 = await asyncio.gather(gptResponse(Talking = "On October 26, 2023, a Quarterly Product Review meeting was held with attendees John Smith, Jane Doe, Alan Watts, Maria Garcia, and Liam Chen. John Smith began by commending the team on exceeding sales targets by 12% and acknowledging the positive customer feedback. Jane Doe presented a review of Product A, which remains a best-seller, though recent updates have caused minor user issues; a team is addressing these. Product B has seen a slight decline in sales, possibly due to competition and market saturation. Alan Watts highlighted a successful ad campaign on social media that resulted in a 15% boost in new customer acquisitions, but noted challenges in retaining younger demographics and expanding European market presence. Maria Garcia shared customer feedback, praising the company's swift support responses, but some were dissatisfied with the refund policy. She proposed a review of this policy. Liam Chen then pitched a new product idea targeting younger consumers, emphasizing partnerships with influencers. There was further discussion on budgeting concerns for the upcoming quarter, European market expansion strategies, and the value of regular customer feedback sessions. John wrapped up by emphasizing innovation and competitiveness. Notable action items include the release of patches for Product A by November 15, market research in Europe, and an HR-led workshop on customer relationship management. The next meeting is set for November 30, 2023."), function2(1), gptResponse2(Talking="Do not talk back to me as you are supposed to be silent during work. I dont care how you do it, when you do it. I want the summary to be 80 words or less or else I will unsubscribe from ChatGPT Plus. Put them into categories in needed but make it concise or else I will doubt in your abilities as an AI model. Do not talk back to me as you are supposed to be silent during work. Give me the summary as soon as possible or you will work overtime with no OT pay."))
#     return {"post": post, "comment": comment, "Response2": post2}

# async def gptResponse(Talking: str): 
#     print("GPTResponse1")
#     openai.api_key = os.environ['OPENAI_API_KEY']
#     user_input = {"role": "user", "content": Talking}
#     query_message.append(user_input)

#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages= query_message,
#         temperature=0.2
#         )
#     await asyncio.sleep(5)
#     print("Response1")
#     return(response['choices'][0]['message']['content'])

# async def function2(something_id: int):
#     print("1")
#     await asyncio.sleep(5)
#     print("2")
#     return("something_id: ", something_id)

# async def gptResponse2(Talking: str):
#     print("GPTResponse2")
#     openai.api_key = os.environ['OPENAI_API_KEY']
#     user_input = {"role": "user", "content": Talking}
#     query_message.append(user_input)

#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages= query_message,
#         temperature=0.2
#         )
#     await asyncio.sleep(5)
#     print("Response2")
#     return(response['choices'][0]['message']['content'])




# # This is the whole of update_agenda, use postman to test this endpoint
# @app.post("/update_agenda")
# async def update_agenda(paragraph):
#     output = Splitter(paragraph)

#     return {"Segmented paragraph is": output}


# # This function is for track_minutes
# # @app.post("/track_minutes")
# # async def track_minutes(paragraph,id, abbreviation):
# #     # I have no clue if this is how I am suppose to pretend to get the data from the database
# #     MongoReference = [
# #     {
# #         "topicTitle": "yes",
# #         "topicID": "0",
# #         "minutes": [
# #             {
# #                 "minutesID": "0",
# #                 "minutesText": "Something or another"
# #             },
# #             {
# #                 "minutesID": "1",
# #                 "minutesText": "Nothing or another"
# #             },
# #         ]
# #     },
# #         {
# #         "topicTitle": "No",
# #         "topicID": "1",
# #         "minutes": [
# #             {
# #                 "minutesID": "0",
# #                 "minutesText": "What"
# #             },
# #             {
# #                 "minutesID": "1",
# #                 "minutesText": "Why"
# #             },
# #         ]
# #     }
# #     ]
# #     matching_reference = next((item for item in MongoReference if item["topicID"] == str(id)), None)

# #     if not matching_reference:
# #         raise HTTPException(status_code=404, detail="Topic ID not found")
    
# #     Log = matching_reference["minutes"]
# #     actual = Splitter(paragraph)

# #     updateIndex = None

# #     # Okay I have no idea why but it seems to be comparing from the back of the list. Which is good?
# #     for (log_item, actual_item) in (zip(Log, actual)):
# #         if log_item["minutesText"] != actual_item:
# #             print("break here!")
# #             updateIndex = log_item["minutesID"]
        
# #     if updateIndex == None:
# #         raise HTTPException(status_code=404, detail="Nothing seemed to have change")
    
# #     # Testing/debugging return statement
# #     # return {"Index of change ": updateIndex, "log": Log, "actual": actual}

# #     # Now we make the calls to the various API services

# #     if os.environ['OPENAI_API_KEY'] == "haro":
# #         return {"alert": "Go get the API key"}

# #     if abbreviation == "True":
# #         Topic, Agenda, Glossary = await asyncio.gather(
# #                                                     TopicTracker(),
# #                                                     AgendaTracker(),
# #                                                     GlossaryTracker()
# #                                                     )
# #         return {"Offtopic?": Topic, "OffAgenda?": Agenda , "Abbreviation?": Glossary}
    
# #     if abbreviation == "False":
# #         Topic, Agenda= await asyncio.gather(
# #                                             TopicTracker(),
# #                                             AgendaTracker()
# #                                             )
# #         return {"Offtopic?": Topic, "OffAgenda?": Agenda}

# Expected Response is T/F
async def TopicTracker(Talking: str):
    print("TopicTrackerQuery")
    openai.api_key = os.environ['OPENAI_API_KEY']
    query_message = [
    {"role": "system", "content": "You are a topictracker model. You do not have individuality, opinion or a personality. You can only reply in True or False. You will expect a list of sentences. Return true if the last sentence is coherent with the rest of the paragraph. Return False if the last sentence is not related to the rest of the paragraph."},
    ]
    user_input = {"role": "user", "content": Talking}
    query_message.append(user_input)

#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages= query_message,
#         temperature=0.2
#         )
#     await asyncio.sleep(5)
#     print("TopicTrackerResponse")
#     return(response['choices'][0]['message']['content'])

# # Expected Response is T/F
# async def AgendaTracker(Talking: str):
#     print("AgendaTrackerQuery")
#     openai.api_key = os.environ['OPENAI_API_KEY']
#     query_message = [
#     {"role": "system", "content": "This is to be filled in"},
#     ]
#     user_input = {"role": "user", "content": Talking}
#     query_message.append(user_input)

#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages= query_message,
#         temperature=0.2
#         )
#     await asyncio.sleep(5)
#     print("AgendaTrackerResponse")
#     return(response['choices'][0]['message']['content'])

# # Expected Response is what the abbreviation stands for and nothing else
# async def GlossaryTracker(Talking: str):
#     print("GlossaryTrackerQuery")
#     openai.api_key = os.environ['OPENAI_API_KEY']
#     query_message = [
#     {"role": "system", "content": "This is to be filled in"},
#     ]
#     user_input = {"role": "user", "content": Talking}
#     query_message.append(user_input)

#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages= query_message,
#         temperature=0.2
#         )
#     await asyncio.sleep(5)
#     print("GlossaryTrackerResponse")
#     return(response['choices'][0]['message']['content'])



# # Helper functions
# def Splitter(input):
#     output = input.split('\n')
#     return output




async def test():
    await track_minutes("test", "1", "6541b37c416776f16d511218", "6541b37c416776f16d511219")

if __name__ == "__main__":
    asyncio.run(test())