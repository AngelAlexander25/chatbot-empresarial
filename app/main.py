from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.routes import chat
from app.utils.logger import logger

load_dotenv()

app = FastAPI(
    title="Chatbot Empresarial",
    description="API para chatbot con LLM usando documentos internos",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes (cambiar en producción)
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los headers
)

app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.on_event("startup")
async def startup_event():
    logger.info("Iniciando aplicacion de chatbot empresarial")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Cerrando aplicacion")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)