import asyncio
from .vectorstore import VectorStore
from .llm_runner import LLMRunner
from .utils import fetch_and_clean_api_docs
from autogen_agentchat.ui import Console
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
import logging
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
import os
from .prompts import DEVELOPER_PROMPT, REVIEW_PROMPT, LLM_PROMPT, API_PROMPT
from dotenv import load_dotenv

# Load .env automatically
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main(api_doc_url: str, use_case: str, language: str, source_type: str) -> str:
    try:
        urls = LLMRunner.llm_call(API_PROMPT, {"API_DOC_URL" : api_doc_url, "USER_USE_CASE" : use_case})
        visited_urls = set()
        content = ""
        for url in urls:
            visited_urls.add(url)
            content += '\n\n' + fetch_and_clean_api_docs(api_doc_url, source_type, visited_urls=visited_urls).strip()
        file_path = "GTI_test.txt"
        with open(file_path, 'w') as file:
            file.write(content)
        if content:
            logger.info("Content fetched successfully")
            VectorStore.create_faiss_vectorstore(content)
            relevant_context = VectorStore.load_and_query_vectorstore(use_case)
            
            logger.info("Relevant context saved to file")

            response = LLMRunner.llm_call(LLM_PROMPT, {"use_case" : use_case, "content" : relevant_context, "language": language})
            code = LLMRunner.extract_updated_code(response)
            logger.info("LLM code script generated")

            # Get OpenAI API key from environment variable
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key is None:
                raise ValueError("OPENAI_API_KEY environment variable not set")

            # Create OpenAI chat completion client
            chat_client = OpenAIChatCompletionClient(
                model="gpt-4-turbo",
                api_key=api_key
            )

            # Create reviewer agent
            reviewer = AssistantAgent(
                "Reviewer",
                model_client=chat_client,
                system_message=REVIEW_PROMPT
            )

            # Create developer agent
            developer = AssistantAgent(
                "Developer",
                model_client=chat_client,
                system_message=DEVELOPER_PROMPT
            )

            # Set termination condition (reviewer must mention approval)
            termination = TextMentionTermination("APPROVE")

            # Run the team chat session
            groupchat = RoundRobinGroupChat(
                [developer, reviewer], termination_condition=termination
            )
            response = await Console(groupchat.run_stream(task=f"Here is the code to review:\n{code}"))
            updated_code = LLMRunner.extract_updated_code(str(response))

            if updated_code:
                logger.info("Agent updated code generated")
                return updated_code
            else:
                logger.info("No updated code found")
                return "No updated code found."
        else:
            logger.error("Failed to retrieve content")
            return "Failed to retrieve content from source."
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise Exception(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
