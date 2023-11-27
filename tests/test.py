import json
import requests
import asyncio

class APITester():

    def __init__(self) -> None:
        """
        Initiate endpoint URL and document IDs

        Returns:
            Error if unable to hit /create endpoint, else None
        """
        self.url = "http://localhost:8000"
        document_ids = self._initialisation()
        self.minutesID = document_ids['minutesID']
        self.chatHistoryID = document_ids['chatHistoryID']


    def _initialisation(self):
        """
        /create endpoint
        Initialises minutes and chatHistory document in the database

        Returns:
            dictionary in the format {minutesID: str, chatHistoryID: str}
        """
        url = self.url + "/create"
        r = requests.get(url)
        print(f"/create endpoint status: {r.status_code}, res: {r.json()}")
        return r.json()

    #--------------------------------------------------------------------------------
    #         Reading Endpoints
    #--------------------------------------------------------------------------------
    
    async def read_history(self):
        """
        /read_history endpoint
        Reads the chatHistory

        Returns:
            dictionary in the format {"document": [{user: str}, {assistant: str, sourceTopicIDs: []}], "web": [{user: str}, {assistant: str}]}
        """
        data = {"minutesID": self.minutesID, 
                "chatHistoryID": self.chatHistoryID}
        url = self.url + "/read_history"
        r = requests.post(url, json=data)
        print(f"/read_history endpoint status: {r.status_code}, res: {r.json()}")
    

    async def read_glossary(self):
        """
        /read_glossary endpoint
        Reads the glossary from minutesDB

        Returns:
            dictionary in the format {"glossary": [{abbreviation:str, meaning: str}]}
        """
        data = {"minutesID": self.minutesID, 
                "chatHistoryID": self.chatHistoryID}
        url = self.url + "/read_glossary"
        r = requests.post(url, json=data)
        print(f"/read_glossary endpoint status: {r.status_code}, res: {r.json()}")
    
    #--------------------------------------------------------------------------------
    #         Updating Endpoints
    #--------------------------------------------------------------------------------
    
    async def update_agenda(self, agenda:list):
        """
        /update_agenda endpoint
        Updates agenda

        Args:
            agenda (list): List of agenda to be updated
        
        Returns:
            dictionary of status 200 or raise Exception
        """
        data = {"agenda": agenda, 
                "minutesID": self.minutesID, 
                "chatHistoryID": self.chatHistoryID}
        url = self.url + "/update_agenda"
        r = requests.post(url, json=data)
        print(f"/update_agenda endpoint status: {r.status_code}, res: {r.json()}")

        
    async def update_meeting(self, meetingData:dict):
        """
        /update_meeting endpoint
        Updates meeting details

        Args:
            meetingData (str/dict): Dictionary of meeting details to be updated {location: str, date: DateObject, attendees: [str]}
        
        Returns:
            dictionary of status 200 or raise Exception
        """
        data = {"data": meetingData, 
                "minutesID": self.minutesID, 
                "chatHistoryID": self.chatHistoryID}
        url = self.url + "/update_meeting"
        r = requests.post(url, json=data)
        print(f"/update_meeting endpoint status: {r.status_code}, res: {r.json()}")
    

    async def update_glossary(self, abbreviation:str, meaning:str, type:str):
        """
        /update_glossary endpoint
        Create / Update / Delete glossary based on the type

        Args:
            abbreviation (str): abbreviation of interest
            meaning(str): meaning of abbreviation
            type (str): new / update / delete, defines the action taken related to the abbreviation

        Returns:
            dictionary of status 200 or raise Exception
        """
        data = {"abbreviation": abbreviation, 
                "meaning": meaning, 
                "type": type,
                "minutesID": self.minutesID, 
                "chatHistoryID": self.chatHistoryID}
        url = self.url + "/update_glossary"
        r = requests.post(url, json=data)
        print(f"/update_glossary endpoint status: {r.status_code}, res: {r.json()}")
    
    #--------------------------------------------------------------------------------
    #         Topic Related Endpoints
    #--------------------------------------------------------------------------------
  
    async def track_minutes(self, topicTitle:str, topicID:str, abbreviation:str, minutes:str):
        """
        /track_minutes endpoint
        Updates minutes under the topic and check if topic and agenda are on track and if any abbreviations

        Args:
            topicTitle (str): Topic title name (none if no topic title)
            topicID (str): Topic ID
            minutes(str): Minutes in topic block split by \n
            abbreviation (str): Abbreviation if exist else None
        
        Returns:
            dictionary of status 200 or raise Exception
        """
        data = {"topicTitle": topicTitle, 
                "topicID": topicID, 
                "abbreviation": abbreviation,
                 "minutes": minutes,
                "minutesID": self.minutesID, 
                "chatHistoryID": self.chatHistoryID}
        url = self.url + "/track_minutes"
        r = requests.post(url, json=data)
        print(f"/track_minutes endpoint status: {r.status_code}, res: {r.json()}")
    

    async def summarise_minutes(self,  topicID:str):
        """
        /summarise endpoint
        Summarise minutes in the specific topic
        
        Args:
            topicID (str): Topic ID
            
        Returns:
            dictionary of status 200 or raise Exception
        """
        data = {"topicID": topicID, 
                "minutesID": self.minutesID, 
                "chatHistoryID": self.chatHistoryID}
        url = self.url + "/summarise"
        r = requests.post(url, json=data)
        print(f"/summarise endpoint status: {r.status_code}, res: {r.json()}")
    

    async def delete_topic(self, topicID:str):
        """
        /delete_topic endpoint
        Delete entire topic in minutes
        
        Args:
            topicID (str): Topic ID
            
        Returns:
            dictionary of status 200 or raise Exception
        """
        data = {"topicID": topicID, 
                "minutesID": self.minutesID, 
                "chatHistoryID": self.chatHistoryID}
        url = self.url + "/delete_topic"
        r = requests.post(url, json=data)
        print(f"/delete_topic endpoint status: {r.status_code}, res: {r.json()}")
        
    #--------------------------------------------------------------------------------
    #         QnA Endpoints
    #--------------------------------------------------------------------------------
    
    async def document_query(self, query:str, type:str):
        """
        /document_query endpoint
        Do document qna on the minutes
        
        Args:
            query (str): query to the LLM
            type (str): document / web, determine which query type
            
        Returns:
            dictionary of status 200 or raise Exception
        """
        data = {"query": query, 
                "type": type,
                "minutesID": self.minutesID, 
                "chatHistoryID": self.chatHistoryID}
        url = self.url + "/document_query"
        r = requests.post(url, json=data, stream=True)
        for line in r.iter_lines():
            # filter out keep-alive new lines
            if line:
                decoded_line = line.decode('utf-8')
                print(decoded_line)

        print(f"/document_query endpoint status: {r.status_code}")
           
     

    async def web_query(self, query:str, type:str):
        """
        /web_query endpoint
        Do web qna
        
        Args:
            query (str): query to the LLM
            type (str): document / web, determine which query type
            
        Returns:
            dictionary of status 200 or raise Exception
        """
        data = {"query": query, 
                "type": type,
                "minutesID": self.minutesID, 
                "chatHistoryID": self.chatHistoryID}
        url = self.url + "/web_query"
        r = requests.post(url, json=data, stream=True)
        for line in r.iter_lines():
            # filter out keep-alive new lines
            if line:
                decoded_line = line.decode('utf-8')
                print(decoded_line)

        print(f"/web_query endpoint status: {r.status_code}")


    async def clear(self, type:str):
        """
        /clear endpoint
        Remove chat history for type in chatHistoryDB
        
        Args:
            type (str): document / web, determine which chat history to clear
            
        Returns:
            dictionary of status 200 or raise Exception
        """
        data = {"type": type,
                "minutesID": self.minutesID, 
                "chatHistoryID": self.chatHistoryID}
        url = self.url + "/clear"
        r = requests.post(url, json=data)
        print(f"/clear endpoint status: {r.status_code}, res: {r.json()}")

    #--------------------------------------------------------------------------------
    #         Deleting Database Endpoints
    #--------------------------------------------------------------------------------

    async def delete_document(self, collectionName:str, documentID:str = None):
        """
        /delete_document endpoint
        Delete document from mongoDB

        Args:
            collectionName (str): Name of collection to delete from, minutes or chatHistory
            documentID (str): ID of document to be deleted, defaults to None (will delete minutesID or chatHistoryID based on collectionName)
        
        Returns:
            dictionary of status 200 or raise Exception
        """
        data = {"collectionName": collectionName, "documentID": documentID, "minutesID": self.minutesID, "chatHistoryID": self.chatHistoryID}
        url = self.url + "/delete_document"
        r = requests.post(url, json=data)
        print(f"/delete_document endpoint status: {r.status_code}, res: {r.json()}")
    
    
    async def delete_collection(self, collectionName:str):
        """
        /delete_collection endpoint
        Delete entire collection from mongoDB

        Args:
            collectionName (str): Name of collection to delete from, minutes or chatHistory
        
        Returns:
            dictionary of status 200 or raise Exception
        """
        data = {"collectionName": collectionName, 
                "minutesID": self.minutesID, 
                "chatHistoryID": self.chatHistoryID}
        url = self.url + "/delete_collection"
        r = requests.post(url, json=data)
        print(f"/delete_collection endpoint status: {r.status_code}, res: {r.json()}")
    

async def test():
    testManager = APITester()
    #initial read
    await testManager.read_history()
    await testManager.read_glossary()

    #updating
    await testManager.update_agenda(['plan iter 3 timeline', 'frontend updates', 'web experiment planning'])
    await testManager.update_meeting({'date': '2023-11-27T13:29:20.152Z', 'location': 'studio', 'attendees':['wx', 'yl', 'jx', 'hn']})
    #topics
    await testManager.track_minutes(topicTitle="iter 3 timeline", topicID="0", abbreviation=None, minutes="Need to do finish frontend and web experiment by 14 Aug\nWe have exactly 1.5 weeks left\nFrontend try to finish by Wednesday\nConsulting kenny for the web experiment on wednesday also\ndesign webexperiment task on wed aft consult\nconduct study on friday and next mon\nmeet again on tues to eval result and finish documents")
    await testManager.track_minutes(topicTitle="frontend updates", topicID="1", abbreviation=None, minutes="morgan finished his topic blocks\nhardcoded in pixels instead of using vw and vh\nneed to edit again as screen aspect ratio is not the same\nlooks jank on hubob side\njefferson is working on tables\ncurrently struggling because there is incompatibility between react versions\nmaterial ui needs react 17 but next needs react 18\nwill try a different lib, if cannot just do from scratch\nhubob and morgan has finished the rough web experiment pages\nthere is a bug where the delete isnt functioning because the space is a special character that messed up the length\nwill continue to try debugging\nif can't fix by friday will js tell users NO DELETE")
    await testManager.track_minutes(topicTitle="frontend updates", topicID="1", abbreviation=None, minutes="morgan finished his topic blocks\nhardcoded in pixels instead of using vw and vh\nneed to edit again as screen aspect ratio is not the same\nlooks jank on hubob side\njefferson is working on tables\ncurrently struggling because there is incompatibility between react versions\nmaterial ui needs react 17 but next.js needs react 18\nwill try a different lib, if cannot just do from scratch\nhubob and morgan has finished the rough web experiment pages\nthere is a bug where the delete function isnt working well because the space is a special character that messed up the length\nif can't fix by friday will js tell users NO DELETE")

    #glossary
    await testManager.update_glossary('vw', 'view width', 'new')
    await testManager.update_glossary('vh', 'view height', 'new')
    await testManager.read_glossary()
    await testManager.update_glossary('vw', 'Volkswagen', 'update')
    await testManager.read_glossary()
    await testManager.update_glossary('vw', 'Volkswagen', 'delete')
    await testManager.read_glossary()

    #summarise
    await testManager.summarise_minutes('0')
    await testManager.summarise_minutes('1')

    #query
    await testManager.document_query(query="Why are we meeting kenny", type="document")
    await testManager.document_query(query="When are we meeting him", type="document")
    await testManager.delete_topic('1')
    await testManager.document_query(query="Who is doing the tables for the frontend", type="document")
    await testManager.read_history()

    await testManager.web_query(query="What is a good database for documents", type="web")
    await testManager.web_query(query="What about for structured data", type="web")
    await testManager.read_history()

    await testManager.clear('document')
    await testManager.read_history()

    #termination
    await testManager.delete_document("minutes")
    await testManager.delete_collection("chatHistory")


if __name__ == '__main__':
    asyncio.run(test())
