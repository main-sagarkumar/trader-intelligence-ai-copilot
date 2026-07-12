"""Authenticated personalized chat endpoint."""

from fastapi import APIRouter, Depends, HTTPException, status

from trader_intelligence_ai_copilot.application.graph_chat_service import GraphChatService
from trader_intelligence_ai_copilot.api.dependencies import (
    get_current_user,
    get_hybrid_chat_service,
)
from trader_intelligence_ai_copilot.auth import AuthenticatedUser
from trader_intelligence_ai_copilot.schemas.chat import (
    ChatResponse,
    PersonalizedChatRequest,
    SourceResponse,
)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/personalized", response_model=ChatResponse)
async def personalized_chat(
    request: PersonalizedChatRequest,
    user: AuthenticatedUser = Depends(get_current_user),
    service: GraphChatService = Depends(get_hybrid_chat_service),
) -> ChatResponse:
    """Answer with hybrid context only for a trader the caller may access."""
    trader_id = request.trader_id
    if trader_id is None:
        if len(user.trader_ids) != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A trader_id is required when multiple profiles are assigned.",
            )
        trader_id = next(iter(user.trader_ids))

    if "admin" not in user.roles and trader_id not in user.trader_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this trader profile.",
        )

    result = await service.chat(request.question, trader_id)
    return ChatResponse(
        answer=result.answer,
        sources=[
            SourceResponse(
                document_name=source.document_name,
                category=source.category,
                page=source.page,
                relative_path=source.relative_path,
            )
            for source in result.sources
        ],
    )
