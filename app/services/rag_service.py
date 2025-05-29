from typing import List, Dict
from app.utils.embedding_utils import get_embedding
from app.utils.pinecone_utils import query_similar_chunks
from app.core.cache import cache_manager
from langchain_openai import ChatOpenAI
from app.core.config import settings
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4.1", temperature=0.2, api_key=settings.OPENAI_API_KEY)
    
    def process_rag_query(self, query: str) -> List[Dict]:
        """Process query using RAG system"""
        try:
            logger.info(f"Processing RAG query: {query}")
            
            # Create cache key
            normalized_query = re.sub(r'\s+', ' ', query.lower().strip())
            cache_key = f"rag_results_{hash(normalized_query)}"
            
            # Check cache
            cached_results = cache_manager.get(cache_key, ttl=3600)
            if cached_results:
                logger.info("Using cached RAG results")
                return cached_results
                
            # Generate embedding
            query_embedding = get_embedding(query)
            
            # Query Pinecone
            similar_chunks = query_similar_chunks(query_embedding)
            
            # Format results
            results = [
                {
                    "text": match.metadata["text"],
                    "score": match.score
                }
                for match in similar_chunks
            ]
            
            # Store in cache
            cache_manager.set(cache_key, results, ttl=3600)
            
            logger.info(f"RAG results fetched and cached")
            return results
            
        except Exception as e:
            logger.error(f"Error in RAG processing: {str(e)}")
            raise e

    def format_response_with_llm(self, query: str, chunks: List[Dict]) -> str:
        """Format the response using LLM"""
        # Clean and prepare chunks
        cleaned_chunks = []
        for i, chunk in enumerate(chunks):
            cleaned_text = ' '.join(chunk['text'].split())
            cleaned_chunks.append({
                'text': cleaned_text,
                'score': chunk['score']
            })
        
        # Prepare context
        context = "\n\n".join([
            f"Chunk {i+1} (relevance: {chunk['score']:.2f}):\n{chunk['text']}"
            for i, chunk in enumerate(cleaned_chunks)
        ])
        
        prompt = f"""You are a professional assistant for Big Toe Provider. Analyze the reference information and provide a comprehensive, well-formatted response to the user's question.

                **User Question**: {query}

                **Reference Information**: {context}

                **Instructions**:
                - Lead with the most relevant answer that directly addresses the question
                - Use formatting to enhance readability:
                * Return the **only those resonse** which is **relevant to the user query**, not the whole context
                * **Bold text** for key terms, amounts, and important headings
                * Bullet points (•) for lists of options, features, or steps
                * Insert \\n (newline characters) after each major section and bullet point for proper line breaks
                * Add \\n\\n (double newlines) between different major sections
                * Organized structure when multiple items need explanation
                - Integrate supporting details from the reference material seamlessly
                - Write in plain language: use "dollars" not "$", "percent" not "%"
                - Maintain professional tone while being conversational and easy to understand
                - When explaining multiple options or methods, structure them clearly with formatting
                - Limit response to 120 words maximum to allow for formatting elements
                
                
                ** IMPORTANT:** (Always remember the following)
                - Do not include any information that is not relevant to the user query
                - Do not include any information that is not in the context
                
                Provide a complete, well-formatted response with appropriate bold text, bullet points, and \\n newline characters for proper display:
                
                Response:
            """
            
        try:
            response = self.llm.predict(prompt)
            cleaned_response = ' '.join(response.split())
            cleaned_response = cleaned_response.replace('$', ' dollars')
            cleaned_response = cleaned_response.replace('%', ' percent')
            cleaned_response = re.sub(r'([.!?])\s*', r'\1 ', cleaned_response)
            cleaned_response = re.sub(r'\s+', ' ', cleaned_response)
            
            formatted_response = f"{cleaned_response.strip()}\n\n"
            
            print("Formatted response byy uq:", formatted_response)
                    
            message = f"""Here is the information I found:
                {formatted_response} 
                Please try to format this response in a more professional way. Because I dont want long paragraphs. Only provide me response.
                
                **Instructions for Formatting:**
                - Use some grammatically correct and professional language from the response
                
                Don't include several type of message or sentences in response like,
                - Certainly! Here's a more professionally formatted response:
                - Absolutely! Here's a more polished version of the response:
                
                
                ** Only format the response**
                """
                
            print("Message to LLM:", message)
            # Prepare the message for LLM
            final_response = self.llm.predict(message)
            
            formatted_response = f"{final_response.strip()}\n\n"
            logger.info(f"Formatted response: {formatted_response}")
            
            return formatted_response
        
        except Exception as e:
            return f"I encountered an error while formatting the response: {str(e)}"