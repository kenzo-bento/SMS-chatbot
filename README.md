# SMS Chatbot with RAG + Ollama

This project implements an automated SMS chatbot using **Retrieval-Augmented Generation (RAG)**, the **PersonaChat dataset**, and a **local Ollama-hosted LLM**, integrated with **native AppleScript** to send and receive messages on macOS.

The system enhances conversational naturalness by injecting persona-aware contextual knowledge from a vector database directly into the model’s system prompt.

---

## Features

- RAG-based persona grounding using the PersonaChat dataset  
- Local LLM inference via Ollama (no cloud dependency)  
- Automated SMS messaging through AppleScript on macOS  
- Vector search to retrieve relevant persona/context snippets  
- More natural, consistent conversational style via prompt conditioning  

---

## Architecture Overview

1. **PersonaChat Dataset**
   - Preprocessed and embedded into a vector store
   - Used to model consistent conversational personas

2. **Vector Store (RAG)**
   - Retrieves the most relevant persona/context entries
   - Retrieved context is injected into the LLM’s system prompt

3. **LLM (Ollama)**
   - Runs locally for low-latency, private inference
   - Generates responses conditioned on retrieved persona context

4. **AppleScript Automation**
   - Interfaces with the macOS Messages app
   - Sends and receives SMS/iMessage messages automatically

---

## Requirements

- macOS (required for AppleScript + Messages)
- Python 3.9+
- Ollama installed and running locally
- Supported Ollama model (e.g. `llama3`, `mistral`, etc.)
- PersonaChat dataset
- Vector database (e.g. FAISS, Chroma, etc.)

---
