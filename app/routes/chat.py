from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.llm_service import llm_service
from app.utils.logger import logger

router = APIRouter()

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str
    tokens_used: int

@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    Endpoint principal del chatbot.
    
    El chatbot automáticamente:
    - Responde sobre políticas de la empresa
    - Busca en Wikipedia si necesita información general
    - Busca noticias si preguntas sobre actualidad
    
    Ejemplos de preguntas:
    - "¿Cuál es el horario de trabajo?"
    - "¿Qué es la inteligencia artificial?"
    - "¿Cuáles son las últimas noticias de tecnología?"
    """
    if not request.question or len(request.question.strip()) == 0:
        logger.warning("Pregunta vacia recibida")
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacia")
    
    result = llm_service.ask(request.question)
    
    if not result["success"]:
        logger.error(f"Error en el servicio LLM: {result.get('error')}")
        raise HTTPException(status_code=500, detail="Error al procesar la pregunta")
    
    return AnswerResponse(
        answer=result["answer"],
        tokens_used=result["tokens_used"]
    )

@router.get("/health")
async def health_check():
    """Verificar que el servicio está funcionando"""
    return {"status": "ok", "service": "chatbot-empresarial"}
