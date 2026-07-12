from fastapi import APIRouter, Depends

from trader_intelligence_ai_copilot.api.dependencies import get_chat_service
from trader_intelligence_ai_copilot.application.chat_service import ChatService
from trader_intelligence_ai_copilot.schemas.chat import ChatRequest, ChatResponse, SourceResponse

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:

    result = await service.chat(request.question)

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