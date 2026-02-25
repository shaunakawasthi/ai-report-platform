from openai import AsyncAzureOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize the Azure OpenAI client
# This is the object you use to make all LLM calls
client = AsyncAzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

async def generate_report(topic: str) -> str:
    """
    Takes a topic and generates a research report using Azure OpenAI.
    This is the core AI function our agents will build upon.
    """
    
    response = await client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[
            {
                "role": "system",
                "content": """You are an expert research analyst. 
                When given a topic, you generate a comprehensive, 
                well-structured research report with the following sections:
                1. Executive Summary
                2. Key Findings
                3. Detailed Analysis
                4. Implications
                5. Conclusion
                Be factual, precise and professional."""
            },
            {
                "role": "user", 
                "content": f"Generate a detailed research report on: {topic}"
            }
        ],
        temperature=0.3,
        max_tokens=2000
    )
    
    # Extract the text content from the response
    return response.choices[0].message.content

async def get_token_usage(topic: str) -> dict:
    """
    Same as generate_report but also returns token usage.
    Useful for cost monitoring.
    """
    response = await client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[
            {
                "role": "system",
                "content": "You are an expert research analyst."
            },
            {
                "role": "user",
                "content": f"Generate a brief summary on: {topic}"
            }
        ],
        temperature=0.3,
        max_tokens=500
    )
    
    return {
        "content": response.choices[0].message.content,
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
        "finish_reason": response.choices[0].finish_reason
    }