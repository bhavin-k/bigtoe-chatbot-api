from typing import List, Dict, Any, Optional, Literal, Callable
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph, START
from app.services.rag_service import RAGService
from app.services.session_service import SessionService
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class WorkflowState(TypedDict):
    query: str
    provider_id: str
    results: Optional[List[Dict]]
    session_data: Optional[List[Dict]]
    route: Optional[Literal["rag", "session_api"]]
    response: Optional[str]
    error: Optional[str]

class WorkflowService:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4.1", temperature=0.2, api_key=settings.OPENAI_API_KEY)
        self.rag_service = RAGService()
        self.session_service = SessionService()
        self.workflow = self._create_workflow()
    
    def route_query(self, state: WorkflowState) -> WorkflowState:
        """Route the query to the appropriate system"""
        query = state["query"]
        
        prompt = f"""
            You are an AI system that routes user queries to one of two systems:

            1. **session_api** - Choose this if the query is asking about the user's own session history, records, appointments, or usage. This includes:
            - Number of sessions (e.g., "How many sessions did I do in 2025?")
            - Details of specific past sessions (e.g., date, duration, location, review)
            - Analytics about user sessions (e.g., average length, most recent session)
            - Session queries involving personal context or time ranges (e.g., "last week", "last year", "yesterday", "my sessions")

            2. **rag** - Choose this if the query is asking about general information or platform details that are **not specific to the user's session history**. This includes:
            - Session policies or structures (e.g., "What are the standard session durations?")
            - Platform functionality (e.g., "Can I cancel a session?", "How do reschedules work?")
            - General FAQs, Booking & Scheduling, pricing, payment policies, Tips & Cancellations, Professional Appearance & Hygiene, Ethics  or technical help
            
            User query: "{query}"
            
            Respond with only one of these values: **session_api** or **rag**.
            Do not include any explanation or extra words.
           """
        
        try:
            classification = self.llm.predict(prompt).strip().lower()
            
            if classification == "session_api":
                logger.info("LLM classified query as session-related")
                state["route"] = "session_api"
            else:
                logger.info("LLM classified query as general knowledge (RAG)")
                state["route"] = "rag"
        except Exception as e:
            logger.error(f"Error in LLM classification: {str(e)}")
            state["route"] = "rag"
        
        return state

    def process_rag_query(self, state: WorkflowState) -> WorkflowState:
        """Process query using RAG system"""
        try:
            results = self.rag_service.process_rag_query(state["query"])
            print("RAG results in process_rag_query:", results)
            state["results"] = results
            return state
        except Exception as e:
            logger.error(f"Error in RAG processing: {str(e)}")
            state["error"] = str(e)
            return state

    def process_session_api_query(self, state: WorkflowState) -> WorkflowState:
        """Process query using session API"""
        try:
            session_response = self.session_service.process_session_query(
                state["query"], 
                state["provider_id"]
            )
            state["session_data"] = session_response
            return state
        except Exception as e:
            logger.error(f"Error in session processing: {str(e)}")
            state["error"] = str(e)
            return state

    def synthesize_rag_response(self, state: WorkflowState) -> WorkflowState:
        """Synthesize response from RAG results"""
        if state.get("error"):
            state["response"] = f"I encountered an error: {state['error']}"
            return state
            
        results = state.get("results", [])
        print("\n\nRAG results in synthesize_rag_response:", results)
        if not results:
            state["response"] = "I couldn't find any relevant information to answer your question."
            return state
            
        response = self.rag_service.format_response_with_llm(state["query"], results[:2])
        state["response"] = response
        return state

    def synthesize_session_response(self, state: WorkflowState) -> WorkflowState:
        """Synthesize response from session data"""
        if state.get("error"):
            state["response"] = f"I encountered an error: {state['error']}"
            return state
            
        session_data = state.get("session_data")
        print("\n\nSession data in synthesize_session_response:", session_data)
        response = self.session_service.format_session_response(
            state["query"], 
            session_data
        )
        state["response"] = response
        return state

    def _create_workflow(self) -> Callable:
        """Create the LangGraph workflow"""
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("router", self.route_query)
        workflow.add_node("rag", self.process_rag_query)
        workflow.add_node("session_api", self.process_session_api_query)
        workflow.add_node("synthesize_rag", self.synthesize_rag_response)
        workflow.add_node("synthesize_session", self.synthesize_session_response)
        
        # Add edges
        workflow.add_edge(START, "router")
        
        workflow.add_conditional_edges(
            "router",
            lambda state: state["route"],
            {
                "rag": "rag",
                "session_api": "session_api",
            }
        )
        
        workflow.add_edge("rag", "synthesize_rag")
        workflow.add_edge("session_api", "synthesize_session")
        workflow.add_edge("synthesize_rag", END)
        workflow.add_edge("synthesize_session", END)
        
        return workflow.compile()

    def process_query(self, user_query: str, provider_id: str) -> str:
        """Process user query through the workflow"""
        try:
            initial_state = WorkflowState(
                query=user_query,
                provider_id=provider_id,
                results=None,
                session_data=None,
                route=None,
                response=None,
                error=None
            )
            
            result = self.workflow.invoke(initial_state)
            response = result.get("response", "I'm not sure how to answer that question.")
            print(f"Final response: {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error in workflow processing: {str(e)}")
            return f"An error occurred while processing your request: {str(e)}"