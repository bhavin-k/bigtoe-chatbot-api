from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse, InitialMessageRequest, InitialMessageResponse
from app.services.workflow_service import WorkflowService
from app.services.session_service import SessionService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
workflow_service = WorkflowService()
session_service = SessionService()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint"""
    try:
        logger.info(f"Processing chat request: {request.user_query}")
        
        if request.user_query.strip() == "":
            response = session_service.get_initial_message(request.provider_id)
            return ChatResponse(
                response=response,
                success=False
            )
        
        response = workflow_service.process_query(
            user_query=request.user_query,
            provider_id=request.provider_id
        )
        
        return ChatResponse(
            response=response,
            success=True
        )
        # return ChatResponse(
        #     response="hello",
        #     success=True
        # )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return ChatResponse(
            response="An error occurred while processing your request.",
            success=False,
            error=str(e)
        )

@router.post("/initial-message", response_model=InitialMessageResponse)
async def initial_message_endpoint(request: InitialMessageRequest):
    """Get initial greeting message"""
    try:
        logger.info(f"Getting initial message for provider: {request.provider_id}")
        
        message = session_service.get_initial_message(request.provider_id)
        
        return InitialMessageResponse(
            message=message,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Error in initial message endpoint: {str(e)}")
        return InitialMessageResponse(
            message="Hey! I'm BigToe AI assistant. How can I help you today?",
            success=False,
            error=str(e)
        )