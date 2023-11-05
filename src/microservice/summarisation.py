import openai
import os
import asyncio
from fastapi import HTTPException

async def summarizeText(text: str, model: str='gpt-3.5-turbo', temperature: float=0.3, max_tokens: int=150, request_timeout: int=5, max_retries: int=3):
    """
    Function to summarize a given text using GPT.

    Args:
        text (str): The text to summarize.
        model (str): Name of the GPT model to use, defaults to 'gpt-3.5-turbo'.
        temperature (float): The sampling temperature for randomness in response, defaults to 0.3.
        max_tokens (int): The maximum number of tokens to generate, defaults to 150.
        request_timeout (int): The maximum time (in seconds) before timing out, defaults to 5.
        max_retries (int): Maximum number of retries in case of a timeout, defaults to 3.

    Returns:
        str: A summary of the provided text.
    """
    openai.api_key = os.environ['OPENAI_API_KEY']
    retry_count = 0
    prompt = (
        "You are a helpful topic summarising model called CuriousCat. "
        "Please summarise the following paragraph in a maximum of 2 sentences or less. "
        "Make it as short as possible, really short, but with all the important details still retained. "
        "The summary must have a MAX WORD LIMIT OF 80 WORDS, and focus on readability too.\n\n"
        f"{text}\n\n"
        "Summary:"
    )

    while retry_count <= max_retries:
        try:
            response = openai.Completion.create(
                model=model,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                request_timeout=request_timeout
            )
            summary = response.choices[0].text.strip()
            return summary
        
        except Exception as e:
            print(f"An error occurred: {e}")
            retry_count += 1
            if retry_count <= max_retries:
                print(f"Summarization request failed (Retry {retry_count}). Pausing for a second before retrying.")
                await asyncio.sleep(1)
            else:
                print("Max retries reached for summarization. Returning an error.")
                raise HTTPException(status_code=500, detail="GPT summarization error, please check GPT server.")

