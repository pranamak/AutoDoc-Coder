from typing import Dict, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os, re
from .prompts import LLM_PROMPT, DEVELOPER_PROMPT, REVIEW_PROMPT
from dotenv import load_dotenv

# Load .env automatically
load_dotenv()

class LLMRunner:
  def llm_call(llm_prompt: str, arguments: Dict[str, str]) -> Optional[str]:
    """
    Calls the LLM model with the given content, use case, and language.

    Args:
    content (str): The content to pass to the LLM model.
    use_case (str): The use case to pass to the LLM model.
    language (str): The language to pass to the LLM model.

    Returns:
    Optional[str]: The response from the LLM model, or None if an error occurred.
    """

    try:
        # Create prompt template
        prompt = ChatPromptTemplate.from_template(llm_prompt)

        # Create LLM model
        model = ChatOpenAI(
            model="gpt-4-turbo",
            temperature=0
        )

        # Create chain
        chain = prompt | model

        # Invoke chain with input parameters
        response = chain.invoke(arguments)

        # Return response content
        return response.content
    except Exception as e:
        raise Exception(f"Error calling LLM model: {e}")

  def extract_updated_code(context: str) -> Optional[str]:
    """
    Extracts the last code block from the given context.

    Args:
    context (str): The context to extract the code block from.

    Returns:
    Optional[str]: The extracted code block, or None if no code block was found.
    """

    try:
        # Find all code blocks
        code_blocks = re.findall(r'```\w+((?:[^`])*)```', context, re.DOTALL)
        if code_blocks:
            # Return the last code block
            code = code_blocks[-1].strip()
            code = code.replace('\\n', '\n')
            return code.replace('\\', '')
        else:
            return None
    except re.error as e:
        raise Exception(f"Error extracting code block: {e}")
    except Exception as e:
        raise Exception(f"Error extracting code block: {e}")
