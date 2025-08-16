
"""Init Chroma module for the application.

This module provides functionality related to init chroma.
"""
import chromadb
import os
from dotenv import load_dotenv

load_dotenv()

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chromadb")

def init_chroma():
    """Initialize ChromaDB for vector storage"""
    # Create the directory if it doesn't exist
    os.makedirs(CHROMA_DB_PATH, exist_ok=True)

    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    # Create collections for emotion patterns (custom embeddings)
    try:
        emotion_patterns = client.create_collection(
            name="emotion_patterns",
            metadata={"description": "Collection for storing emotion pattern vectors with custom embeddings"}
        )
        print("Created emotion_patterns collection")
    except ValueError:
        # Collection already exists
        emotion_patterns = client.get_collection(name="emotion_patterns")
        print("Emotion patterns collection already exists")

    # Create collection for historical interventions (custom embeddings)
    try:
        interventions = client.create_collection(
            name="historical_interventions",
            metadata={"description": "Collection for storing historical intervention vectors with custom embeddings"}
        )
        print("Created historical_interventions collection")
    except ValueError:
        # Collection already exists
        interventions = client.get_collection(name="historical_interventions")
        print("Historical interventions collection already exists")

    # Create collections for emotion patterns (Gemini embeddings)
    try:
        emotion_patterns_gemini = client.create_collection(
            name="emotion_patterns_gemini",
            metadata={"description": "Collection for storing emotion pattern vectors with Gemini embeddings"}
        )
        print("Created emotion_patterns_gemini collection")
    except ValueError:
        # Collection already exists
        emotion_patterns_gemini = client.get_collection(name="emotion_patterns_gemini")
        print("Emotion patterns Gemini collection already exists")

    # Create collection for historical interventions (Gemini embeddings)
    try:
        interventions_gemini = client.create_collection(
            name="historical_interventions_gemini",
            metadata={"description": "Collection for storing historical intervention vectors with Gemini embeddings"}
        )
        print("Created historical_interventions_gemini collection")
    except ValueError:
        # Collection already exists
        interventions_gemini = client.get_collection(name="historical_interventions_gemini")
        print("Historical interventions Gemini collection already exists")

    return client

if __name__ == "__main__":
    client = init_chroma()
    print(f"ChromaDB initialized at {CHROMA_DB_PATH}")
