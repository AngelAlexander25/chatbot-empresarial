# Chatbot Empresarial con IA

Sistema de chatbot empresarial que utiliza LLMs (Groq/OpenAI) para responder preguntas basadas en documentos de la empresa y fuentes de datos automáticas.

## Tabla de Contenidos

1. [Arquitectura del Sistema](#arquitectura)
2. [Componentes Principales](#componentes)
3. [Flujo de Funcionamiento](#flujo)
4. [Instalación](#instalación)
5. [Uso de la API](#uso)
6. [Ejemplos Prácticos](#ejemplos)

---

## Arquitectura del Sistema {#arquitectura}

```
┌─────────────────────────────────────────────────────────────┐
│                      Usuario / Cliente                       │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP Request
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI (app/main.py)                     │
│                  - Maneja rutas HTTP                         │
│                  - Middleware y configuración                │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Router (app/routes/chat.py)                     │
│          - POST /api/ask          (hacer pregunta)           │
│          - POST /api/load-wikipedia                          │
│          - POST /api/load-rss                                │
│          - POST /api/load-api                                │
│          - POST /api/load-news                               │
│          - GET  /api/available-sources                       │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│           LLM Service (app/services/llm_service.py)          │
│  - Gestiona contexto de la empresa                           │
│  - Se comunica con Groq/OpenAI                               │
│  - Genera respuestas basadas en el contexto                  │
└───────────┬────────────────────────────┬────────────────────┘
            │                            │
            ▼                            ▼
┌─────────────────────┐    ┌──────────────────────────────────┐
│   AutoSources       │    │    Groq/OpenAI API               │
│  (auto_sources.py)  │    │    - llama-3.3-70b-versatile     │
│  - Wikipedia        │    │    - gpt-3.5-turbo               │
│  - RSS Feeds        │    └──────────────────────────────────┘
│  - APIs Públicas    │
└─────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│              Fuentes de Datos Externas                       │
│  - Wikipedia API                                             │
│  - RSS Feeds (BBC, TechCrunch, etc.)                         │
│  - APIs REST Públicas                                        │
│  - Documentos locales (data/documentos_empresa.txt)          │
└─────────────────────────────────────────────────────────────┘
```

---

## Componentes Principales {#componentes}

### 1. **app/main.py** - Punto de Entrada
```python
# Qué hace:
- Inicializa la aplicación FastAPI
- Carga variables de entorno (.env)
- Registra los routers (endpoints)
- Define eventos de inicio y cierre
```

**Funciones clave:**
- `startup_event()`: Se ejecuta al iniciar el servidor
- `shutdown_event()`: Se ejecuta al detener el servidor

---

### 2. **app/routes/chat.py** - Endpoints de la API

Este archivo define todas las rutas HTTP disponibles:

#### **POST /api/ask**
- **Función:** Procesar pregunta del usuario
- **Input:** `{"question": "¿Cuál es el horario?"}`
- **Output:** `{"answer": "...", "tokens_used": 150}`
- **Proceso:**
  1. Valida que la pregunta no esté vacía
  2. Llama a `llm_service.ask()`
  3. Retorna la respuesta generada

#### **POST /api/load-wikipedia**
- **Función:** Cargar información de Wikipedia
- **Input:** `{"topic": "inteligencia artificial"}`
- **Output:** `{"message": "Información cargada..."}`
- **Proceso:**
  1. Busca el tema en Wikipedia (español)
  2. Extrae resumen y contenido
  3. Agrega al contexto del chatbot

#### **POST /api/load-rss**
- **Función:** Cargar noticias desde RSS
- **Input:** `{"feed_url": "https://...", "max_items": 5}`
- **Output:** `{"message": "Noticias cargadas..."}`

#### **POST /api/load-api**
- **Función:** Cargar datos de API pública
- **Input:** `{"api_url": "https://api.github.com/..."}`
- **Output:** `{"message": "Datos cargados..."}`

#### **POST /api/load-news**
- **Función:** Cargar noticias predefinidas
- **Output:** `{"message": "Noticias cargadas..."}`
- **Fuentes:** BBC Mundo, TechCrunch, Entrepreneur

#### **GET /api/available-sources**
- **Función:** Ver fuentes de datos disponibles
- **Output:** Lista de fuentes RSS y APIs

---

### 3. **app/services/llm_service.py** - Servicio de IA

Este es el cerebro del chatbot. Gestiona la interacción con el LLM.

```python
class LLMService:
    def __init__(self):
        self.client = None      # Cliente de OpenAI/Groq
        self.model = None       # Modelo a usar
        self.context = None     # Contexto acumulado
```

#### **Métodos principales:**

**`_initialize()`**
- Se ejecuta la primera vez que se usa el servicio
- Configura el cliente de Groq o OpenAI
- Carga el contexto inicial desde documentos_empresa.txt

**`ask(question: str)`**
- Proceso paso a paso:
  1. Inicializa el cliente si no existe
  2. Construye el prompt del sistema con el contexto
  3. Envía la pregunta al LLM (Groq/OpenAI)
  4. Recibe y retorna la respuesta
  
**`load_wikipedia_topic(topic: str)`**
- Carga información de Wikipedia al contexto
- Permite al chatbot responder sobre ese tema

**`load_rss_feed(url: str)`**
- Extrae noticias de un feed RSS
- Agrega títulos, resúmenes y links al contexto

**`load_public_api(url: str)`**
- Obtiene datos JSON de APIs públicas
- Convierte a texto y agrega al contexto

---

### 4. **app/services/auto_sources.py** - Fuentes Automáticas

Gestiona la obtención de datos de fuentes externas.

#### **`get_wikipedia_summary(topic, lang='es')`**
```python
# Paso a paso:
1. Configura el idioma de Wikipedia
2. Busca la página del tema
3. Extrae título, resumen y contenido
4. Maneja errores (página no encontrada, ambigüedad)
5. Retorna texto formateado
```

#### **`get_news_from_rss(feed_url, max_items=5)`**
```python
# Paso a paso:
1. Hace request al feed RSS
2. Parsea el XML con feedparser
3. Extrae título, resumen, fecha y link de cada noticia
4. Formatea como texto
5. Retorna las últimas N noticias
```

#### **`get_public_api_data(api_url)`**
```python
# Paso a paso:
1. Hace HTTP GET a la API
2. Parsea respuesta JSON
3. Formatea con indentación
4. Retorna datos legibles
```

---

### 5. **app/utils/logger.py** - Sistema de Logs

Registra todos los eventos importantes:

```python
# Ejemplos de logs:
2026-02-06 16:05:16 - INFO - Iniciando aplicación
2026-02-06 16:05:20 - INFO - Pregunta recibida: ¿Horario?
2026-02-06 16:05:23 - INFO - Respuesta generada exitosamente
2026-02-06 16:05:25 - ERROR - Error al cargar RSS: timeout
```

---

## Flujo de Funcionamiento {#flujo}

### Flujo 1: Hacer una Pregunta

```
1. Usuario envía POST /api/ask
   {"question": "¿Cuál es el horario de trabajo?"}
        ↓
2. Router (chat.py) recibe la petición
   - Valida que question no esté vacía
        ↓
3. Llama a llm_service.ask(question)
        ↓
4. LLM Service:
   a) Inicializa cliente (si es primera vez)
   b) Carga contexto desde documentos_empresa.txt
   c) Construye prompt:
      "Eres un asistente de IA...
       Contexto: [documentos_empresa.txt]
       Pregunta: ¿Cuál es el horario?"
        ↓
5. Envía a Groq API (llama-3.3-70b-versatile)
        ↓
6. Groq procesa y genera respuesta:
   "El horario de trabajo es de lunes a viernes 
    de 9:00 AM a 6:00 PM"
        ↓
7. LLM Service retorna:
   {
     "success": true,
     "answer": "...",
     "tokens_used": 150
   }
        ↓
8. Router retorna al usuario:
   {
     "answer": "El horario...",
     "tokens_used": 150
   }
```

### Flujo 2: Cargar Datos de Wikipedia

```
1. Usuario envía POST /api/load-wikipedia
   {"topic": "Python"}
        ↓
2. Router llama a llm_service.load_wikipedia_topic("Python")
        ↓
3. LLM Service llama a auto_sources.get_wikipedia_summary("Python")
        ↓
4. AutoSources:
   a) Configura Wikipedia API a español
   b) Busca página "Python"
   c) Extrae resumen y contenido
        ↓
5. Retorna texto formateado:
   "Título: Python
    Resumen: Python es un lenguaje de programación..."
        ↓
6. LLM Service agrega al contexto:
   self.context += "\n--- WIKIPEDIA ---\n[texto]"
        ↓
7. Retorna success = True
        ↓
8. Router responde: {"message": "Información cargada"}
        ↓
9. Ahora el chatbot puede responder preguntas sobre Python
```

---

## Instalación {#instalación}

### Requisitos
- Python 3.13
- Cuenta en Groq (gratuita): https://console.groq.com

### Pasos

1. **Clonar/Descargar el proyecto**
```powershell
cd C:\Users\test\Desktop\chatbot-empresarial
```

2. **Crear entorno virtual**
```powershell
python -m venv .venv
```

3. **Activar entorno virtual**
```powershell
.venv\Scripts\Activate.ps1
```

4. **Instalar dependencias**
```powershell
pip install -r requirements.txt
```

5. **Configurar .env**
```env
GROQ_API_KEY=gsk_tu_key_aqui
MODEL_NAME=llama-3.3-70b-versatile
```

6. **Iniciar servidor**
```powershell
python -m uvicorn app.main:app --reload
```

7. **Acceder a la documentación**
- http://127.0.0.1:8000/docs

---

## Uso de la API {#uso}

### 1. Hacer una Pregunta Simple

**Endpoint:** `POST /api/ask`

**Request:**
```json
{
  "question": "¿Cuál es el horario de trabajo?"
}
```

**Response:**
```json
{
  "answer": "El horario de trabajo es de lunes a viernes de 9:00 AM a 6:00 PM según las políticas de la empresa.",
  "tokens_used": 45
}
```

### 2. Cargar Información de Wikipedia

**Endpoint:** `POST /api/load-wikipedia`

**Request:**
```json
{
  "topic": "inteligencia artificial"
}
```

**Response:**
```json
{
  "message": "Informacion de Wikipedia cargada: inteligencia artificial"
}
```

**Ahora puedes preguntar:**
```json
{
  "question": "¿Qué es la inteligencia artificial?"
}
```

### 3. Cargar Noticias Predefinidas

**Endpoint:** `POST /api/load-news`

**Response:**
```json
{
  "message": "Noticias predefinidas cargadas exitosamente"
}
```

**Fuentes incluidas:**
- BBC Mundo
- TechCrunch
- Entrepreneur

### 4. Cargar RSS Personalizado

**Endpoint:** `POST /api/load-rss`

**Request:**
```json
{
  "feed_url": "https://feeds.bbci.co.uk/mundo/rss.xml",
  "max_items": 5
}
```

### 5. Cargar Datos de API Pública

**Endpoint:** `POST /api/load-api`

**Request:**
```json
{
  "api_url": "https://api.github.com/repos/microsoft/vscode"
}
```

### 6. Ver Fuentes Disponibles

**Endpoint:** `GET /api/available-sources`

**Response:**
```json
{
  "predefined_feeds": {
    "noticias_tecnologia": "https://feeds.bbci.co.uk/mundo/rss.xml",
    "noticias_negocios": "https://www.entrepreneur.com/latest.rss",
    "noticias_startups": "https://techcrunch.com/feed/"
  },
  "wikipedia": "Disponible - cualquier tema",
  "public_apis": "Disponible - cualquier API REST publica"
}
```

---

## Ejemplos Prácticos {#ejemplos}

### Ejemplo 1: Chatbot de Políticas de Empresa

**Paso 1:** El sistema ya tiene cargado `data/documentos_empresa.txt`

**Paso 2:** Hacer preguntas
```bash
curl -X POST http://127.0.0.1:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"¿Cuántos días de vacaciones tengo?"}'
```

**Respuesta:**
> "Tienes 15 días de vacaciones al año si tienes menos de 5 años de antigüedad, o 20 días si tienes más de 5 años."

### Ejemplo 2: Chatbot con Conocimiento de Wikipedia

**Paso 1:** Cargar tema
```bash
curl -X POST http://127.0.0.1:8000/api/load-wikipedia \
  -H "Content-Type: application/json" \
  -d '{"topic":"machine learning"}'
```

**Paso 2:** Hacer preguntas
```bash
curl -X POST http://127.0.0.1:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"¿Qué es machine learning?"}'
```

### Ejemplo 3: Chatbot de Noticias Tecnológicas

**Paso 1:** Cargar noticias
```bash
curl -X POST http://127.0.0.1:8000/api/load-news
```

**Paso 2:** Preguntar sobre noticias
```bash
curl -X POST http://127.0.0.1:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"¿Qué noticias recientes hay sobre tecnología?"}'
```

### Ejemplo 4: Información de Repositorio GitHub

**Paso 1:** Cargar datos del repo
```bash
curl -X POST http://127.0.0.1:8000/api/load-api \
  -H "Content-Type: application/json" \
  -d '{"api_url":"https://api.github.com/repos/facebook/react"}'
```

**Paso 2:** Preguntar
```bash
curl -X POST http://127.0.0.1:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Cuéntame sobre el repositorio de React"}'
```

---

## Configuración Avanzada

### Variables de Entorno (.env)

```env
# API Key de Groq (gratis)
GROQ_API_KEY=gsk_tu_key_aqui

# Modelo a usar
# Opciones Groq: llama-3.3-70b-versatile, mixtral-8x7b-32768, llama-3.1-8b-instant
MODEL_NAME=llama-3.3-70b-versatile

# Opcionalmente usar OpenAI
# OPENAI_API_KEY=sk-...
# MODEL_NAME=gpt-3.5-turbo
```

### Modelos Disponibles en Groq

| Modelo | Velocidad | Contexto | Uso Recomendado |
|--------|-----------|----------|-----------------|
| llama-3.3-70b-versatile | Medio | 128K | Propósito general |
| mixtral-8x7b-32768 | Rápido | 32K | Respuestas rápidas |
| llama-3.1-8b-instant | Muy rápido | 128K | Consultas simples |

---

## Estructura del Proyecto

```
chatbot-empresarial/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # Punto de entrada FastAPI
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   └── chat.py             # Endpoints de la API
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py      # Servicio de IA
│   │   └── auto_sources.py     # Fuentes automáticas
│   │
│   └── utils/
│       ├── __init__.py
│       └── logger.py           # Sistema de logs
│
├── data/
│   └── documentos_empresa.txt  # Documentos de la empresa
│
├── .env                        # Variables de entorno
├── requirements.txt            # Dependencias Python
└── README.md                   # Esta documentación
```

---

## Solución de Problemas

### Error: "No module named 'wikipedia'"
**Solución:** Instalar dependencias en el entorno virtual
```powershell
.venv\Scripts\Activate.ps1
pip install wikipedia feedparser beautifulsoup4 requests
```

### Error: "GROQ_API_KEY no está configurada"
**Solución:** Verificar archivo .env
```env
GROQ_API_KEY=gsk_tu_key_real
```

### Error: "Error code: 429 - insufficient_quota"
**Solución:** Tu API key de OpenAI no tiene créditos. Usa Groq (gratis)

---

## Próximas Mejoras

- [ ] Base de datos vectorial para búsqueda semántica
- [ ] Historial de conversaciones
- [ ] Soporte para múltiples idiomas
- [ ] Interfaz web con React
- [ ] Autenticación de usuarios
- [ ] Rate limiting
- [ ] Cache de respuestas
- [ ] Métricas y analytics

---

## Licencia

Este proyecto es de código abierto para uso educativo y empresarial.

---

## Soporte

Para preguntas o problemas, contacta al equipo de desarrollo.
