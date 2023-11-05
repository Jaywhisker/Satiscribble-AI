import openai
import os
import asyncio
from utils.gptManager import *
from utils.mongoDBManager import MongoDBManager
from utils.chromaDBManager import ChromaDBManager

async def summarizeText(minutes_id: str, chat_history_id: str, text: str, model: str='gpt-3.5-turbo', temperature: float=0.3, max_tokens: int=150, request_timeout: int=5, max_retries: int=3):
    
    openai.api_key = os.environ.get('OPENAI_API_KEY')

    # Initialize MongoDBManager
    mongoDB = MongoDBManager(minutes_id, chat_history_id)

    
    retry_count = 0
    prompt = (
        "You are a helpful summarizing model called CuriousCat. "
        "Please summarize the following paragraph in a maximum of 2 sentences or less. "
        "Make it concise, with all important details retained. "
        "The summary must have a MAX WORD LIMIT OF 80 WORDS, focusing on readability.\n\n"
        f"{text}\n\n"
        "Summary:"
    )

    while retry_count <= max_retries:
        try:
            response = openai.Completion.create(
                engine=model,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=request_timeout
            )
            summary = response.choices[0].text.strip()

            # Here you might want to update MongoDB with the summary result.
            
            return summary
        
        except openai.error.OpenAIError as e:
            print(f"An error occurred with OpenAI: {e}")
            retry_count += 1
            if retry_count <= max_retries:
                print(f"Summarization request failed, retry {retry_count}/{max_retries}. Retrying after a pause.")
                await asyncio.sleep(1)
            else:
                print("Max retries reached for summarization. Cannot return a summary.")
                # Here you might want to log the final failure to MongoDB.
                return "Failed to summarize the text after multiple attempts."

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            # Log the error to MongoDB or handle it as needed.
            return "An unexpected error occurred during summarization."
