# Guía de Uso Rápido - Chatbot Empresarial

## Inicio Rápido

### 1. Activar entorno virtual e iniciar servidor
```powershell
.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

### 2. Acceder a la documentación interactiva
Abre en tu navegador: http://127.0.0.1:8000/docs

---

## Casos de Uso Comunes

### Caso 1: Preguntas sobre Políticas de la Empresa

**Pregunta:** "¿Cuál es el código de vestimenta?"

**Cómo funciona:**
1. El usuario hace la pregunta mediante POST /api/ask
2. El sistema lee el contexto de `data/documentos_empresa.txt`
3. Groq/LLM procesa la pregunta con el contexto
4. Responde: "Business casual de lunes a jueves, casual los viernes"

**Prueba en Swagger UI:**
1. Ve a http://127.0.0.1:8000/docs
2. Expande `POST /api/ask`
3. Click en "Try it out"
4. Escribe en el body:
   ```json
   {
     "question": "¿Cuál es el código de vestimenta?"
   }
   ```
5. Click "Execute"

---

### Caso 2: Agregar Conocimiento de Wikipedia

**Objetivo:** Hacer que el chatbot conozca sobre un tema específico

**Pasos:**
1. Cargar tema de Wikipedia
2. Hacer preguntas sobre ese tema

**Ejemplo: Tema "Python (programming language)"**

**Paso 1 - Cargar información:**
```json
POST /api/load-wikipedia
{
  "topic": "Python programming language"
}
```

**Paso 2 - Hacer pregunta:**
```json
POST /api/ask
{
  "question": "¿Qué es Python y para qué se usa?"
}
```

**Respuesta esperada:**
> "Python es un lenguaje de programación de alto nivel, interpretado y de propósito general. Se utiliza para desarrollo web, análisis de datos, inteligencia artificial, automatización, y más..."

---

### Caso 3: Noticias Tecnológicas Recientes

**Objetivo:** Que el chatbot responda sobre noticias actuales

**Paso 1 - Cargar noticias predefinidas:**
```json
POST /api/load-news
```
Esto carga automáticamente de:
- BBC Mundo
- TechCrunch
- Entrepreneur

**Paso 2 - Preguntar sobre las noticias:**
```json
POST /api/ask
{
  "question": "¿Cuáles son las últimas noticias de tecnología?"
}
```

**Paso 3 - Preguntas específicas:**
```json
POST /api/ask
{
  "question": "¿Hay noticias sobre inteligencia artificial?"
}
```

---

### Caso 4: RSS Feed Personalizado

**Objetivo:** Agregar noticias de una fuente específica

**Ejemplo: Noticias de ciencia de la BBC**

```json
POST /api/load-rss
{
  "feed_url": "http://feeds.bbci.co.uk/mundo/ciencia/rss.xml",
  "max_items": 5
}
```

**Luego preguntar:**
```json
POST /api/ask
{
  "question": "¿Qué noticias científicas hay?"
}
```

---

### Caso 5: Información de Repositorios GitHub

**Objetivo:** Obtener info sobre proyectos open source

**Ejemplo: React de Facebook**

**Paso 1 - Cargar datos del repo:**
```json
POST /api/load-api
{
  "api_url": "https://api.github.com/repos/facebook/react"
}
```

**Paso 2 - Hacer preguntas:**
```json
POST /api/ask
{
  "question": "¿Cuántas estrellas tiene el repositorio de React?"
}
```

```json
POST /api/ask
{
  "question": "¿Cuál es la descripción del proyecto React?"
}
```

---

### Caso 6: Datos de APIs Públicas

**APIs útiles para probar:**

1. **Información de criptomonedas:**
```json
POST /api/load-api
{
  "api_url": "https://api.coindesk.com/v1/bpi/currentprice.json"
}
```

2. **Datos del clima (ejemplo):**
```json
POST /api/load-api
{
  "api_url": "https://api.open-meteo.com/v1/forecast?latitude=19.43&longitude=-99.13&current_weather=true"
}
```

3. **Información de países:**
```json
POST /api/load-api
{
  "api_url": "https://restcountries.com/v3.1/name/mexico"
}
```

---

## Flujo de Trabajo Completo

### Escenario: Chatbot para Soporte de Empleados

**Objetivo:** Crear un chatbot que responda sobre:
- Políticas de la empresa ✅ (ya está en documentos_empresa.txt)
- Información sobre Python (el lenguaje usado en la empresa)
- Noticias tecnológicas recientes

**Implementación paso a paso:**

```bash
# 1. Iniciar servidor
.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload

# 2. Cargar conocimiento adicional (usar Swagger UI o curl)
```

**En Swagger UI (http://127.0.0.1:8000/docs):**

1. **Cargar info de Python:**
   - POST /api/load-wikipedia
   - Body: `{"topic": "Python programming language"}`

2. **Cargar noticias:**
   - POST /api/load-news

3. **Verificar fuentes cargadas:**
   - GET /api/available-sources

4. **Probar preguntas:**

   **Pregunta 1 - Sobre la empresa:**
   ```json
   POST /api/ask
   {"question": "¿Cuántos días de vacaciones tengo?"}
   ```

   **Pregunta 2 - Sobre Python:**
   ```json
   POST /api/ask
   {"question": "¿Qué es Python y por qué es útil para nuestro equipo?"}
   ```

   **Pregunta 3 - Sobre noticias:**
   ```json
   POST /api/ask
   {"question": "¿Qué novedades hay en el mundo tech?"}
   ```

---

## Tips y Mejores Prácticas

### 1. Carga Selectiva de Datos

**NO hagas esto:**
```json
// ❌ Cargar todo sin pensar
POST /api/load-news
POST /api/load-wikipedia {"topic": "random"}
POST /api/load-api {"api_url": "random_api"}
```

**HAZ esto:**
```json
// ✅ Carga solo lo relevante para tu caso de uso
POST /api/load-wikipedia {"topic": "inteligencia artificial"}
POST /api/ask {"question": "¿Qué es IA?"}
```

### 2. Orden de Carga Importa

**Mejor orden:**
1. Primero carga datos estáticos (Wikipedia)
2. Luego datos dinámicos (RSS/APIs)
3. Finalmente haz preguntas

### 3. Preguntas Específicas

**Pregunta vaga:**
```json
❌ {"question": "info"}
```

**Pregunta específica:**
```json
✅ {"question": "¿Cuál es el proceso para solicitar vacaciones?"}
```

### 4. Actualizar Contexto

Si cargas nuevos datos, el contexto se actualiza automáticamente.
No necesitas reiniciar el servidor.

---

## Ejemplos con curl (PowerShell)

### Hacer una pregunta:
```powershell
curl -X POST "http://127.0.0.1:8000/api/ask" `
  -H "Content-Type: application/json" `
  -d '{\"question\":\"Cual es el horario?\"}'
```

### Cargar Wikipedia:
```powershell
curl -X POST "http://127.0.0.1:8000/api/load-wikipedia" `
  -H "Content-Type: application/json" `
  -d '{\"topic\":\"machine learning\"}'
```

### Cargar noticias:
```powershell
curl -X POST "http://127.0.0.1:8000/api/load-news" `
  -H "Content-Type: application/json"
```

### Ver fuentes:
```powershell
curl -X GET "http://127.0.0.1:8000/api/available-sources"
```

---

## Entendiendo las Respuestas

### Respuesta Exitosa:
```json
{
  "answer": "El horario de trabajo es de lunes a viernes de 9:00 AM a 6:00 PM",
  "tokens_used": 45
}
```

- `answer`: La respuesta generada por el LLM
- `tokens_used`: Cantidad de tokens consumidos (importante para control de costos)

### Error de Validación:
```json
{
  "detail": "La pregunta no puede estar vacia"
}
```

### Error del Servicio:
```json
{
  "detail": "Error al procesar la pregunta"
}
```

---

## Debugging

### Ver los logs en tiempo real:
Los logs se muestran en la terminal donde corre el servidor:

```
2026-02-06 16:05:20 - chatbot - INFO - Pregunta recibida: ¿Horario?
2026-02-06 16:05:23 - chatbot - INFO - Respuesta generada exitosamente
```

### Verificar que el servidor está corriendo:
```powershell
curl http://127.0.0.1:8000/api/health
```

**Respuesta esperada:**
```json
{
  "status": "ok",
  "service": "chatbot-empresarial"
}
```

---

## Ejercicios Prácticos

### Ejercicio 1: Chatbot de Atención al Cliente
1. Agrega más políticas a `data/documentos_empresa.txt`
2. Prueba preguntas sobre esas políticas
3. Verifica que las respuestas sean correctas

### Ejercicio 2: Chatbot Educativo
1. Carga 3 temas de Wikipedia relacionados
2. Haz preguntas que combinen información de los 3 temas
3. Observa cómo el LLM conecta la información

### Ejercicio 3: Monitor de Noticias
1. Carga diferentes feeds RSS
2. Pregunta por tendencias
3. Compara respuestas antes y después de cargar las noticias

---

## Recursos Adicionales

- **Groq Console:** https://console.groq.com
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Wikipedia API:** https://pypi.org/project/wikipedia/
- **Feedparser:** https://pythonhosted.org/feedparser/

---

¿Tienes dudas? Revisa el README.md principal para más detalles técnicos.
