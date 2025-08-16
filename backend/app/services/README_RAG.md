# Enhanced RAG Implementation for Edu-Guardian

## Overview

This directory contains an enhanced Retrieval Augmented Generation (RAG) implementation for the Edu-Guardian system. The implementation leverages LangChain and Google's Gemini models to provide intelligent insights and recommendations based on student emotion profiles.

## Files

- `enhanced_rag.py`: Core RAG service implementation
- `chunking_strategies.py`: Various chunking strategies for optimizing RAG performance
- `retrieval_strategies.py`: Specialized retrievers for finding similar emotion patterns
- `rag_examples.py`: Example usage of the RAG system
- `test_rag.py`: Simple test script to verify the RAG implementation
- `rag_documentation.md`: Comprehensive documentation of the RAG implementation
- `rag_diagnostic_report.md`: Diagnostic report with benchmarking and recommendations

## Setup

1. Ensure you have the required dependencies installed:

```bash
cd backend
source .venv/Scripts/activate
pip install -r requirements.txt
```

2. Set up your environment variables:

Create a `.env` file in the `backend` directory with the following content:

```
GOOGLE_API_KEY=your_google_api_key
```

3. Run the test script to verify the implementation:

```bash
cd backend
source .venv/Scripts/activate
python -m app.services.test_rag
```

## Usage

See `rag_examples.py` for comprehensive examples of using the RAG system. Here's a basic example:

```python
from app.services.enhanced_rag import EnhancedRAGService
from app.models.emotion import EmotionProfile

# Initialize RAG service
rag_service = EnhancedRAGService(api_key="your_api_key")
await rag_service.initialize_vector_stores()

# Create a sample emotion profile
emotion_profile = EmotionProfile(
    frustration_level=0.7,
    engagement_level=0.4,
    # ... other fields
)

# Add the emotion profile to the vector store
metadata = {
    "student_id": "student123",
    "course_id": "course456",
    "week_number": 3
}

document_id = await rag_service.add_emotion_profile(emotion_profile, metadata)

# Find similar emotion patterns
similar_patterns = await rag_service.find_similar_emotion_patterns(
    emotion_profile=emotion_profile,
    exclude_student_id="student123"
)

# Generate insights
query = "What are the main emotional challenges faced by this student?"
insights = await rag_service.generate_insights_from_patterns(query, similar_patterns)
```

## Documentation

For more detailed information, see the following files:

- `rag_documentation.md`: Comprehensive documentation of the RAG implementation
- `rag_diagnostic_report.md`: Diagnostic report with benchmarking and recommendations

## Integration

To integrate the enhanced RAG implementation with the existing system, update the relevant services to use the new RAG service. For example:

```python
from app.services.enhanced_rag import EnhancedRAGService

class YourExistingService:
    def __init__(self):
        # Initialize the enhanced RAG service
        self.rag_service = EnhancedRAGService(api_key="your_api_key")
        
    async def initialize(self):
        # Initialize vector stores
        await self.rag_service.initialize_vector_stores()
        
    async def your_existing_method(self):
        # Use the enhanced RAG service
        results = await self.rag_service.find_similar_emotion_patterns(...)
        # Process results
```

## Performance Considerations

1. **Caching**: The system uses caching for embeddings to improve performance
2. **Chunking Strategy**: The chunking strategy significantly impacts retrieval quality
3. **Vector Store Optimization**: Regular maintenance of the vector store improves performance

## Troubleshooting

1. **API Key Issues**: Ensure your Google API key is correctly set in the `.env` file
2. **Dependency Issues**: Make sure all required packages are installed
3. **Vector Store Issues**: If you encounter issues with the vector store, try clearing the ChromaDB cache

## Contributing

When contributing to the RAG implementation, please follow these guidelines:

1. Use the provided chunking and retrieval strategies
2. Follow the existing code style and patterns
3. Add comprehensive tests for new functionality
4. Update documentation as needed