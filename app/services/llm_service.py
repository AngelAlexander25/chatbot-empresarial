import os
from openai import OpenAI
from app.utils.logger import logger
from app.services.auto_sources import auto_sources

class LLMService:
    def __init__(self):
        self.client = None
        self.model = None
        self.context = None
    
    def _initialize(self):
        if self.client is None:
            api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY o OPENAI_API_KEY no está configurada")
            
            # Usar Groq si la API key está configurada
            if os.getenv("GROQ_API_KEY"):
                self.client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.groq.com/openai/v1"
                )
                self.model = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
            else:
                self.client = OpenAI(api_key=api_key)
                self.model = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
            
            self.context = self._load_context()
    
    def _load_context(self):
        try:
            with open("data/documentos_empresa.txt", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.error("No se encontro el archivo de documentos")
            return ""
    
    def _auto_search_info(self, question: str) -> str:
        """
        Busca automáticamente información adicional si es necesario
        """
        additional_info = ""
        
        # Detectar si la pregunta requiere búsqueda externa
        keywords_wikipedia = ["qué es", "que es", "quien es", "quién es", "define", "significado", "historia de"]
        keywords_noticias = ["noticias", "actualidad", "reciente", "últimas", "ultimas", "nuevo", "nueva"]
        
        question_lower = question.lower()
        
        # Buscar en Wikipedia si parece una pregunta de conocimiento general
        if any(keyword in question_lower for keyword in keywords_wikipedia):
            logger.info("Detectada pregunta de conocimiento general, buscando en Wikipedia")
            # Extraer el tema de la pregunta
            topic = self._extract_topic(question)
            if topic:
                wiki_info = auto_sources.get_wikipedia_summary(topic)
                if wiki_info:
                    additional_info += f"\n\n--- INFORMACIÓN DE WIKIPEDIA ---\n{wiki_info[:2000]}\n"
                    logger.info(f"Información de Wikipedia agregada: {topic}")
        
        # Buscar noticias si pregunta sobre actualidad
        if any(keyword in question_lower for keyword in keywords_noticias):
            logger.info("Detectada pregunta sobre actualidad, buscando noticias")
            news = auto_sources.get_news_from_rss("https://feeds.bbci.co.uk/mundo/rss.xml", max_items=3)
            if news:
                additional_info += f"\n\n--- NOTICIAS RECIENTES ---\n{news[:2000]}\n"
                logger.info("Noticias agregadas al contexto")
        
        return additional_info
    
    def _extract_topic(self, question: str) -> str:
        """
        Extrae el tema principal de una pregunta
        """
        # Remover palabras comunes de pregunta
        question_clean = question.lower()
        remove_words = ["qué es", "que es", "quien es", "quién es", "cuál es", "cual es", 
                       "define", "definición", "definicion", "significado de", "?", "¿"]
        
        for word in remove_words:
            question_clean = question_clean.replace(word, "")
        
        return question_clean.strip()
    
    def ask(self, question: str) -> dict:
        try:
            self._initialize()
            logger.info(f"Pregunta recibida: {question}")
            
            # Buscar automáticamente información adicional si es necesario
            additional_context = self._auto_search_info(question)
            
            # Construir el contexto completo
            full_context = self.context + additional_context
            
            system_prompt = f"""Eres un asistente de IA inteligente y útil. 
Tu trabajo es responder preguntas usando la siguiente información:

{full_context}

Instrucciones:
- Si tienes información sobre el tema, responde de manera clara y concisa
- Si no tienes información suficiente, dilo honestamente
- Sé conversacional y amigable
- Responde en español"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            logger.info("Respuesta generada exitosamente")
            
            return {
                "success": True,
                "answer": answer,
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"Error al generar respuesta: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def load_wikipedia_topic(self, topic: str) -> bool:
        try:
            self._initialize()
            text = auto_sources.get_wikipedia_summary(topic)
            if text:
                self.context += f"\n\n--- INFORMACION DE WIKIPEDIA ---\n{text}\n"
                logger.info(f"Informacion de Wikipedia agregada: {topic}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error cargando Wikipedia: {str(e)}")
            return False
    
    def load_rss_feed(self, feed_url: str, max_items: int = 5) -> bool:
        try:
            self._initialize()
            text = auto_sources.get_news_from_rss(feed_url, max_items)
            if text:
                self.context += f"\n\n--- NOTICIAS RSS ---\n{text}\n"
                logger.info(f"Noticias RSS agregadas desde: {feed_url}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error cargando RSS: {str(e)}")
            return False
    
    def load_public_api(self, api_url: str) -> bool:
        try:
            self._initialize()
            text = auto_sources.get_public_api_data(api_url)
            if text:
                self.context += f"\n\n--- DATOS DE API PUBLICA ---\n{text}\n"
                logger.info(f"Datos de API agregados desde: {api_url}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error cargando API: {str(e)}")
            return False
    
    def load_predefined_news(self) -> bool:
        try:
            self._initialize()
            sources = auto_sources.get_predefined_sources()
            success_count = 0
            
            for name, url in sources.items():
                if self.load_rss_feed(url, max_items=3):
                    success_count += 1
            
            logger.info(f"Noticias predefinidas cargadas: {success_count}/{len(sources)}")
            return success_count > 0
        except Exception as e:
            logger.error(f"Error cargando noticias predefinidas: {str(e)}")
            return False

llm_service = LLMService()