from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from langchain_core.messages import HumanMessage, SystemMessage
import re

def get_response(text: str) -> str:
    """
    this function generates a personalized AI response to a user input using a combination of 
    semantic search and a large language model (Ollama).
    """
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vectorstore = FAISS.load_local("personachat_faiss_2", embeddings, allow_dangerous_deserialization=True) # previously embedded vectorstore of normal text messages

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
        
    filled_system_prompt = prompt.format(USER_NAME="username", # your name
                                        STYLE_DESCRIPTION = "casual, soft, short, uses contractions and incomplete sentences", # your style
                                        PREFERENCES = "very sparse use of emojis, ums every now and then", # your preferences
                                        LENGTH_GUIDE = "short sentences", # your preferences
                                        CONTEXT = "a 26 year old man", # your identity
                                        EXAMPLES = examples) # feed the examples from the vectorstore
    messages = [
            SystemMessage(content=filled_system_prompt),
            HumanMessage(content=text),
        ]

    llm = OllamaLLM(model = "mistral")
    response = llm.invoke(messages)
    return response.lower() # text messages are usually in lowercase
