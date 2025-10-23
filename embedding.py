from datasets import load_dataset
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

dataset = load_dataset("AlekseyKorshuk/persona-chat", split = "train")

candidate_pairs = []
for dialog in dataset:
    for utt in dialog["utterances"]:
        context = " ".join(utt["history"])
        for cand in utt["candidates"]:
            candidate_pairs.append({
                "context": context,
                "response": cand
            })

print(f"Extracted {len(candidate_pairs)} conversational pairs.")

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

docs = [
    Document(page_content=p["context"], metadata={"context": p["response"]})
    for p in candidate_pairs
]

vectorstore = FAISS.from_documents(docs, embeddings)

vectorstore.save_local("personachat_faiss_2")