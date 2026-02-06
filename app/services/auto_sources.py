import wikipedia
import feedparser
import requests
from typing import Dict
from app.utils.logger import logger

class AutoSources:
    
    @staticmethod
    def get_wikipedia_summary(topic: str, lang: str = 'es') -> str:
        try:
            logger.info(f"Buscando en Wikipedia: {topic}")
            wikipedia.set_lang(lang)
            
            page = wikipedia.page(topic, auto_suggest=True)
            
            summary = f"Titulo: {page.title}\n\n"
            summary += f"Resumen: {page.summary}\n\n"
            
            if page.content:
                summary += f"Contenido adicional: {page.content[:2000]}\n"
            
            logger.info(f"Wikipedia: Extraidos {len(summary)} caracteres")
            return summary
            
        except wikipedia.exceptions.DisambiguationError as e:
            logger.warning(f"Multiples opciones para '{topic}': {e.options[:5]}")
            return f"Multiples opciones encontradas: {', '.join(e.options[:5])}"
        except wikipedia.exceptions.PageError:
            logger.error(f"No se encontro pagina para: {topic}")
            return ""
        except Exception as e:
            logger.error(f"Error en Wikipedia: {str(e)}")
            return ""
    
    @staticmethod
    def get_news_from_rss(feed_url: str, max_items: int = 5) -> str:
        try:
            logger.info(f"Obteniendo noticias de RSS: {feed_url}")
            feed = feedparser.parse(feed_url)
            
            news_text = f"Fuente: {feed.feed.get('title', 'RSS Feed')}\n\n"
            
            for entry in feed.entries[:max_items]:
                news_text += f"Titulo: {entry.get('title', 'Sin titulo')}\n"
                news_text += f"Resumen: {entry.get('summary', entry.get('description', ''))}\n"
                news_text += f"Fecha: {entry.get('published', 'N/A')}\n"
                news_text += f"Link: {entry.get('link', '')}\n\n"
            
            logger.info(f"RSS: Extraidos {len(news_text)} caracteres de {len(feed.entries[:max_items])} noticias")
            return news_text
            
        except Exception as e:
            logger.error(f"Error obteniendo RSS: {str(e)}")
            return ""
    
    @staticmethod
    def get_public_api_data(api_url: str) -> str:
        try:
            logger.info(f"Obteniendo datos de API publica: {api_url}")
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            import json
            formatted_data = json.dumps(data, indent=2, ensure_ascii=False)
            
            logger.info(f"Datos de API extraidos: {len(formatted_data)} caracteres")
            return formatted_data
            
        except Exception as e:
            logger.error(f"Error obteniendo datos de API: {str(e)}")
            return ""
    
    @staticmethod
    def get_predefined_sources() -> Dict[str, str]:
        sources = {
            "noticias_tecnologia": "https://feeds.bbci.co.uk/mundo/rss.xml",
            "noticias_negocios": "https://www.entrepreneur.com/latest.rss",
            "noticias_startups": "https://techcrunch.com/feed/",
        }
        return sources

auto_sources = AutoSources()
