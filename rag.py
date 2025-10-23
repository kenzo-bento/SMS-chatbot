from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from langchain_core.messages import HumanMessage, SystemMessage
import re

def get_response(text: str) -> str:
    """
    Generate a personalized AI response to a user input using a combination of 
    semantic search and a large language model (Ollama).

    This function performs the following steps:
    1. Loads precomputed embeddings from the "sentence-transformers/all-MiniLM-L6-v2" model.
    2. Loads a local FAISS vector store ("personachat_faiss_2") containing dialogue examples.
    3. Performs a similarity search to find the top 3 relevant examples for the input `text`.
    4. Extracts and formats the relevant context from the retrieved examples.
    5. Reads a system prompt template from "system_prompt.txt" and fills it with:
       - User information
       - Style description
       - Preferences
       - Length guide
       - Context and retrieved examples
    6. Prepares a message sequence for the LLM (system + human messages).
    7. Invokes the Ollama LLM ("mistral") to generate a response.
    8. Returns the response in lowercase.

    Args:
        text (str): The input text from the user that the AI should respond to.

    Returns:
        str: The AI-generated response to the input, in lowercase.

    Raises:
        FileNotFoundError: If "system_prompt.txt" is missing.
        ValueError: If the FAISS vectorstore cannot be loaded.
        Any exceptions raised by the Ollama LLM during inference.

    Notes:
        - The FAISS vectorstore should already exist locally.
        - The system prompt template should include the placeholders:
          USER_NAME, STYLE_DESCRIPTION, PREFERENCES, LENGTH_GUIDE, CONTEXT, EXAMPLES.
        - The function uses regex-based splitting to format retrieved context for the LLM.
        - The response is returned in lowercase for standardization.

    Example:
        >>> prompt = "Hey, how are you?"
        >>> get_response(prompt)
        "i'm good, thanks! how about you?"
    """
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vectorstore = FAISS.load_local("personachat_faiss_2", embeddings, allow_dangerous_deserialization=True)

    results = vectorstore.similarity_search(text, k=3)

    examples = ""
    for r in results:
        context = r.metadata.get("context", "Unknown")
        response = r.page_content
        split_responses = re.split(r"(?=\b(hi|i|yeah|that|you)\b)", context)
        split_responses = [r.strip() for r in split_responses if len(r.strip()) > 3]
        formatted_response = "\n".join([f"- {r}" for r in split_responses])
        examples += formatted_response + "\n"

    with open("system_prompt.txt", "r") as f:
        template_text = f.read()

    prompt = PromptTemplate(input_variables=["USER_NAME", "STYLE_DESCRIPTION", "PREFERENCES", "LENGTH_GUIDE", "CONTEXT", "EXAMPLES"],
                                template=template_text)
        
    filled_system_prompt = prompt.format(USER_NAME="username", #your name
                                        STYLE_DESCRIPTION = "casual, soft, short, uses contractions and incomplete sentences", #your style
                                        PREFERENCES = "very sparse use of emojis, ums every now and then", #your preferences
                                        LENGTH_GUIDE = "short sentences", #your preferences
                                        CONTEXT = "a 26 year old man", #your identity
                                        EXAMPLES = examples)
    messages = [
            SystemMessage(content=filled_system_prompt),
            HumanMessage(content=text),
        ]

    llm = OllamaLLM(model = "mistral")
    response = llm.invoke(messages)
    return response.lower()