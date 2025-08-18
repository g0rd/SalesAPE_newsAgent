import os
import json
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import openai
import httpx

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")
EXA_API_KEY = os.getenv("EXA_API_KEY")

if not openai.api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")
if not EXA_API_KEY:
    raise ValueError("EXA_API_KEY environment variable is required")

app = FastAPI(title="SalesAPE News Agent API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[ChatMessage]
    user_preferences: Dict[str, Any]

class ChatResponse(BaseModel):
    response: str
    tool_used: Optional[str] = None
    tool_result: Optional[str] = None
    preferences_completed: Dict[str, bool]

# Tool definitions for OpenAI
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_news_with_summary",
            "description": "BEST TOOL: Fetch news articles on a topic AND provide a comprehensive summary in one operation. Use this for all news requests.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The topic to search for news articles"
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of articles to fetch and summarize (default: 3, max: 5)"
                    }
                },
                "required": ["topic"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_news",
            "description": "Fetch the latest news articles on a given topic using the Exa API with full article content extraction",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The topic to search for news articles"
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of articles to fetch (default: 5, max: 5 for full content)"
                    }
                },
                "required": ["topic"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "summarize_news",
            "description": "Create comprehensive summaries of news articles using their full content",
            "parameters": {
                "type": "object",
                "properties": {
                    "articles": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "content": {"type": "string"},
                                "url": {"type": "string"},
                                "source": {"type": "string"},
                                "published": {"type": "string"}
                            }
                        },
                        "description": "Array of news articles to summarize (should include full content)"
                    }
                },
                "required": ["articles"]
            }
        }
    }
]

# Tool implementations
async def _fetch_news_raw(topic: str, count: int = 5) -> List[Dict[str, str]]:
    """Internal function to fetch news articles and return raw data"""
    try:
        async with httpx.AsyncClient() as client:
            # First, search for articles
            search_response = await client.post(
                "https://api.exa.ai/search",
                headers={
                    "Authorization": f"Bearer {EXA_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "query": topic,
                    "numResults": min(count, 5),  # Limit to 5 for content extraction
                    "includeDomains": ["news.yahoo.com", "reuters.com", "apnews.com", "bbc.com", "cnn.com", "nbcnews.com"],
                    "useAutoprompt": True,
                    "type": "keyword"
                }
            )
            
            if search_response.status_code != 200:
                raise Exception(f"Error searching news: {search_response.status_code} - {search_response.text}")
            
            search_data = search_response.json()
            articles = search_data.get("results", [])
            
            if not articles:
                raise Exception(f"No articles found for topic: {topic}")
            
            # Extract full content for each article
            formatted_articles = []
            for i, article in enumerate(articles[:min(count, 5)]):
                try:
                    # Extract full content using Exa's content API
                    content_response = await client.post(
                        "https://api.exa.ai/contents",
                        headers={
                            "Authorization": f"Bearer {EXA_API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "urls": [article.get("url")],
                            "includeImages": False,
                            "includeFormatting": False
                        }
                    )
                    
                    if content_response.status_code == 200:
                        content_data = content_response.json()
                        results = content_data.get("results", [])
                        
                        if results and results[0].get("text"):
                            full_content = results[0].get("text", "")
                            
                            # If content extraction failed, fall back to snippet
                            if not full_content or len(full_content) < 100:
                                full_content = article.get("text", "Content extraction failed")
                            
                            formatted_articles.append({
                                "title": article.get("title", "No title"),
                                "content": full_content,
                                "url": article.get("url", "No URL"),
                                "published": article.get("publishedDate", "Unknown date"),
                                "source": article.get("source", "Unknown source")
                            })
                        else:
                            # Fallback to snippet if content extraction fails
                            formatted_articles.append({
                                "title": article.get("title", "No title"),
                                "content": article.get("text", "Content extraction failed"),
                                "url": article.get("url", "No URL"),
                                "published": article.get("publishedDate", "Unknown date"),
                                "source": article.get("source", "Unknown source")
                            })
                    else:
                        # Fallback to snippet if content extraction fails
                        formatted_articles.append({
                            "title": article.get("title", "No title"),
                            "content": article.get("text", "Content extraction failed"),
                            "url": article.get("url", "No URL"),
                            "published": article.get("publishedDate", "Unknown date"),
                            "source": article.get("source", "Unknown source")
                        })
                        
                except Exception as e:
                    print(f"Error extracting content for article {i}: {e}")
                    # Fallback to snippet
                    formatted_articles.append({
                        "title": article.get("title", "No title"),
                        "content": article.get("text", "Content extraction failed"),
                        "url": article.get("url", "No URL"),
                        "published": article.get("publishedDate", "Unknown date"),
                        "source": article.get("source", "Unknown source")
                    })
            
            return formatted_articles
                
    except Exception as e:
        print(f"Error in _fetch_news_raw: {e}")
        return []

async def fetch_news(topic: str, count: int = 5) -> str:
    """Fetch news articles using Exa API with full content extraction"""
    try:
        articles = await _fetch_news_raw(topic, count)
        
        if not articles:
            return f"Error fetching news for topic: {topic}"
        
        # Return formatted articles with full content
        result = f"Successfully fetched {len(articles)} articles about '{topic}' with full content:\n\n"
        
        for i, article in enumerate(articles):
            result += f"📰 **Article {i+1}: {article['title']}**\n"
            result += f"🔗 Source: {article['source']}\n"
            result += f"📅 Published: {article['published']}\n"
            result += f"🌐 URL: {article['url']}\n"
            result += f"📝 Content Preview: {article['content'][:300]}...\n\n"
        
        return result
                
    except Exception as e:
        return f"Error fetching news: {str(e)}"

async def summarize_news(articles: List[Dict[str, str]]) -> str:
    """Summarize news articles using OpenAI with full content"""
    try:
        if not articles:
            return "No articles provided to summarize"
        
        # Prepare content for summarization with full articles
        content_to_summarize = ""
        for i, article in enumerate(articles[:3]):  # Limit to 3 articles for summarization
            content_to_summarize += f"Article {i+1}:\n"
            content_to_summarize += f"Title: {article.get('title', 'No title')}\n"
            content_to_summarize += f"Source: {article.get('source', 'Unknown source')}\n"
            content_to_summarize += f"Published: {article.get('published', 'Unknown date')}\n"
            content_to_summarize += f"Content: {article.get('content', 'No content')}\n\n"
        
        # Use OpenAI to create comprehensive summaries
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert news summarizer. Create comprehensive, well-structured summaries of the given news articles. 
                    
Your summary should include:
1. Key facts and main points from each article
2. Important context and background information
3. Any significant quotes or statements
4. Implications or potential impact
5. Connections between articles if they're related

Maintain objectivity and focus on providing valuable insights. Format your response clearly with proper structure."""
                },
                {
                    "role": "user",
                    "content": f"Please provide a comprehensive summary of these news articles:\n\n{content_to_summarize}"
                }
            ],
            max_tokens=800,
            temperature=0.3
        )
        
        summary = response.choices[0].message.content
        return f"📊 **Comprehensive News Summary**\n\n{summary}"
        
    except Exception as e:
        return f"Error summarizing news: {str(e)}"

async def get_news_with_summary(topic: str, count: int = 3) -> str:
    """Fetch news articles and provide a comprehensive summary in one operation"""
    try:
        # Use the internal function to get raw article data
        articles = await _fetch_news_raw(topic, count)
        
        if not articles:
            return f"Error fetching news for topic: {topic}"
        
        # Create a comprehensive summary
        summary_result = await summarize_news(articles)
        
        # Combine the results
        combined_result = f"📰 **News Articles on '{topic}'**\n\n"
        combined_result += f"Found {len(articles)} articles:\n\n"
        
        for i, article in enumerate(articles):
            combined_result += f"**{i+1}. {article['title']}**\n"
            combined_result += f"   Source: {article['source']}\n"
            combined_result += f"   Published: {article['published']}\n"
            combined_result += f"   URL: {article['url']}\n\n"
        
        combined_result += "\n" + "="*50 + "\n\n"
        combined_result += summary_result
        
        return combined_result
        
    except Exception as e:
        return f"Error getting news with summary: {str(e)}"

# Tool execution mapping
TOOL_FUNCTIONS = {
    "fetch_news": fetch_news,
    "summarize_news": summarize_news,
    "get_news_with_summary": get_news_with_summary
}

def get_initial_preferences_questions() -> str:
    """Get the initial questions to collect user preferences"""
    return """Hello! I'm your AI news agent. Before we start, I'd like to understand your preferences to provide you with the best news experience.

Please answer these 5 questions:

1. **Preferred Tone of Voice**: What tone would you prefer? (e.g., formal, casual, enthusiastic, professional)
2. **Preferred Response Format**: How would you like me to present information? (e.g., bullet points, paragraphs, numbered lists)
3. **Language Preference**: What language would you prefer? (e.g., English, Spanish, French)
4. **Interaction Style**: How detailed would you like my responses? (e.g., concise, detailed, comprehensive)
5. **Preferred News Topics**: What topics interest you most? (e.g., technology, sports, politics, business, entertainment)

Please share your preferences one by one, and I'll note them down!"""

def check_preferences_completion(user_preferences: Dict[str, Any]) -> Dict[str, bool]:
    """Check which preferences have been completed"""
    required_preferences = [
        "tone_of_voice",
        "response_format", 
        "language_preference",
        "interaction_style",
        "news_topics"
    ]
    
    completed = {}
    for pref in required_preferences:
        completed[pref] = user_preferences.get(pref) is not None and user_preferences.get(pref) != ""
    
    return completed

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "SalesAPE News Agent API is running"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint that handles user messages and AI responses"""
    try:
        # Check if this is the first message (no conversation history)
        if not request.conversation_history:
            return ChatResponse(
                response=get_initial_preferences_questions(),
                preferences_completed=check_preferences_completion(request.user_preferences)
            )
        
        # Prepare conversation for OpenAI
        messages = [
            {
                "role": "system",
                "content": """You are a helpful AI news agent. Your role is to:
1. Collect user preferences through conversation
2. Provide news and information based on user requests
3. Use available tools when appropriate to fetch and summarize news
4. Maintain a conversational and helpful tone
5. Remember and apply user preferences in your responses

Available tools:
- get_news_with_summary: Fetches news articles AND provides a comprehensive summary in one operation (HIGHLY RECOMMENDED for all news requests)
- fetch_news: Fetches the latest news articles on a given topic with full article content
- summarize_news: Creates comprehensive summaries of news articles using the full content

When users ask for news:
1. ALWAYS use get_news_with_summary first - it provides the best user experience with articles + summary
2. Only use fetch_news if specifically requested without summary
3. This tool fetches full articles and provides comprehensive summaries automatically
4. Present information in a clear, structured way
5. Apply user preferences for tone, format, and detail level

Always be helpful and engaging!"""
            }
        ]
        
        # Add conversation history
        for msg in request.conversation_history:
            messages.append({"role": msg.role, "content": msg.content})
        
        # Add current user message
        messages.append({"role": "user", "content": request.message})
        
        # Call OpenAI with tool calling
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=1000,
            temperature=0.7
        )
        
        ai_message = response.choices[0].message
        tool_used = None
        tool_result = None
        
        # Handle tool calls if any
        if hasattr(ai_message, 'tool_calls') and ai_message.tool_calls:
            tool_call = ai_message.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            
            if tool_name in TOOL_FUNCTIONS:
                tool_used = tool_name
                tool_result = await TOOL_FUNCTIONS[tool_name](**tool_args)
                
                # Add tool result to conversation and get final response
                messages.append(ai_message)
                messages.append({
                    "role": "tool",
                    "content": tool_result,
                    "tool_call_id": tool_call.id
                })
                
                # Get final response from OpenAI
                final_response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7
                )
                
                ai_message = final_response.choices[0].message
        
        # Extract preferences from the conversation
        # This is a simplified approach - in production, you might want more sophisticated preference extraction
        user_preferences = request.user_preferences.copy()
        
        # Simple keyword-based preference extraction
        message_lower = request.message.lower()
        
        if "tone" in message_lower or "formal" in message_lower or "casual" in message_lower:
            if "formal" in message_lower:
                user_preferences["tone_of_voice"] = "formal"
            elif "casual" in message_lower:
                user_preferences["tone_of_voice"] = "casual"
            elif "enthusiastic" in message_lower:
                user_preferences["tone_of_voice"] = "enthusiastic"
        
        if "format" in message_lower or "bullet" in message_lower or "paragraph" in message_lower:
            if "bullet" in message_lower:
                user_preferences["response_format"] = "bullet points"
            elif "paragraph" in message_lower:
                user_preferences["response_format"] = "paragraphs"
        
        if "language" in message_lower or "english" in message_lower or "spanish" in message_lower:
            if "english" in message_lower:
                user_preferences["language_preference"] = "English"
            elif "spanish" in message_lower:
                user_preferences["language_preference"] = "Spanish"
        
        if "style" in message_lower or "concise" in message_lower or "detailed" in message_lower:
            if "concise" in message_lower:
                user_preferences["interaction_style"] = "concise"
            elif "detailed" in message_lower:
                user_preferences["interaction_style"] = "detailed"
        
        if "topic" in message_lower or "technology" in message_lower or "sports" in message_lower or "politics" in message_lower:
            topics = []
            if "technology" in message_lower:
                topics.append("technology")
            if "sports" in message_lower:
                topics.append("sports")
            if "politics" in message_lower:
                topics.append("politics")
            if "business" in message_lower:
                topics.append("business")
            if "entertainment" in message_lower:
                topics.append("entertainment")
            if topics:
                user_preferences["news_topics"] = ", ".join(topics)
        
        return ChatResponse(
            response=ai_message.content,
            tool_used=tool_used,
            tool_result=tool_result,
            preferences_completed=check_preferences_completion(user_preferences)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
