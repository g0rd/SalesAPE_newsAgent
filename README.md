# SalesAPE News Agent

A web-based chat interface that allows users to interact with an AI-powered news agent. The agent collects user preferences and utilizes external tools to fetch and summarize news articles.

## Features

- **Chat Interface**: Simple, responsive chat interface with real-time message history
- **User Preference Collection**: Interactive checklist collecting 5 key preferences through conversation
- **Advanced Tool Integration**: 
  - **Exa AI News Fetcher**: Fetches latest news articles with FULL article content (not just snippets)
  - **News Summarizer**: Creates comprehensive summaries using complete article content
  - **Combined Tool**: `get_news_with_summary` - fetches articles AND provides summaries in one operation
- **AI-Powered**: Uses OpenAI tool calling for intelligent responses and automatic tool selection
- **Full Content Extraction**: Retrieves complete article content from news sources
- **Comprehensive Summaries**: Detailed summaries with key points, quotes, and implications

## Project Structure

```
SalesAPE_newsAgent/
├── frontend/                 # Next.js frontend application
│   ├── components/          # React components
│   ├── pages/              # Next.js pages
│   ├── styles/             # CSS styles
│   └── package.json        # Frontend dependencies
├── backend/                 # Python backend application
│   ├── app.py              # FastAPI main application
│   ├── requirements.txt    # Python dependencies
│   └── tools/              # Tool implementations
└── README.md               # This file
```

## Prerequisites

- Node.js 18+ and npm
- Python 3.8+
- OpenAI API key
- Exa API key

## Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd SalesAPE_newsAgent
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
```

### 4. Environment Configuration
Create `.env.local` in the frontend directory:
```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

Create `.env` in the backend directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
EXA_API_KEY=your_exa_api_key_here
```

### 5. Run the Application

**Option 1: Separate Terminals**
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python app.py

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

**Option 2: Single Command (Recommended)**
```bash
cd frontend
npm run start:both
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

## Usage

1. **Open the chat interface** in your browser
2. **Preference Collection**: The AI agent will start by asking for your 5 preferences:
   - Preferred Tone of Voice (formal, casual, enthusiastic)
   - Preferred Response Format (bullet points, paragraphs, numbered lists)
   - Language Preference (English, Spanish, etc.)
   - Interaction Style (concise, detailed, comprehensive)
   - Preferred News Topics (technology, sports, politics, business, entertainment)
3. **Visual Progress Tracking**: Watch the preference checklist update in real-time
4. **News Requests**: Ask for news on specific topics (e.g., "Get me news about artificial intelligence")
5. **Automatic Tool Selection**: The AI automatically chooses the best tool for your request
6. **Full Content + Summaries**: Receive complete articles with comprehensive AI-generated summaries

## API Endpoints

- `POST /chat` - Send a message and receive AI response with tool calling
- `GET /health` - Health check endpoint

## Tool Capabilities

### Available AI Tools:
1. **`get_news_with_summary`** (Recommended): Fetches news articles AND provides comprehensive summaries in one operation
2. **`fetch_news`**: Fetches latest news articles with full content extraction
3. **`summarize_news`**: Creates detailed summaries of news articles using complete content

### News Sources:
- Reuters, BBC News, AP News, CNN, NBC News, Yahoo News
- Full article content extraction (not just snippets)
- Real-time news fetching with comprehensive content analysis

## Development Decisions

- **FastAPI**: Chosen for its modern async support and automatic API documentation
- **OpenAI Tool Calling**: Direct integration without high-level abstractions as required
- **Exa API Integration**: Full content extraction for comprehensive news analysis
- **Smart Tool Selection**: AI automatically chooses the best tool for user requests
- **Responsive Design**: Mobile-first approach with modern CSS modules
- **Preference Tracking**: Visual checklist showing real-time completion status
- **Error Handling**: Comprehensive error handling with graceful fallbacks

## Technologies Used

- **Frontend**: Next.js 14, React 18, TypeScript, CSS Modules
- **Backend**: Python 3.8+, FastAPI, OpenAI API, Exa AI API, HTTPX
- **AI**: OpenAI GPT-3.5-turbo with advanced tool calling capabilities
- **Content Extraction**: Exa AI for full article content retrieval
- **Styling**: Modern CSS with responsive design and animations

## Key Improvements & Current Capabilities

### ✅ **What's Working Now:**
- **Full Article Content**: Successfully extracts complete articles (10,000+ characters) from news sources
- **Comprehensive Summaries**: AI generates detailed summaries with key points, quotes, and implications
- **Smart Tool Selection**: AI automatically chooses `get_news_with_summary` for optimal user experience
- **Real-time Preference Tracking**: Visual checklist updates as user preferences are collected
- **Responsive Design**: Works seamlessly on desktop and mobile devices

### 🔧 **Technical Achievements:**
- **Exa API Integration**: Fixed content extraction to get full articles instead of snippets
- **Tool Calling System**: Implemented three specialized tools for different news needs
- **Error Handling**: Robust fallback system when content extraction fails
- **Performance**: Optimized for fast response times with async operations

### 📱 **User Experience:**
- **Seamless Workflow**: Users get articles + summaries in one request
- **Visual Feedback**: Real-time progress indicators and loading states
- **Intelligent Responses**: AI adapts tone and format based on user preferences
- **Mobile-First**: Touch-friendly interface optimized for all devices
