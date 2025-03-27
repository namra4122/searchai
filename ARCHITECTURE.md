# SearchAI System Architecture

## Overview

SearchAI is a comprehensive search and document generation tool that leverages AI to transform web search results into well-structured documents. The system integrates search engines, large language models, and document generation capabilities to provide users with rich, contextual information in various formats.

## System Components

The SearchAI architecture consists of the following primary components:

1. **User Interface Layer** - CLI-based interface for user interaction
2. **Search Engine** - Web search capabilities via SerperDev API
3. **Reasoning Engine** - AI-powered analysis using Google's Gemini LLM
4. **Document Generator** - Creates documents in various formats (Markdown, PDF, PowerPoint)
5. **Database Layer** - PostgreSQL for data persistence
6. **Configuration System** - Environment-based configuration management

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                SearchAI                                 │
│                                                                         │
│  ┌──────────────┐     ┌──────────────┐      ┌──────────────────────┐    │
│  │              │     │              │      │                      │    │
│  │  CLI Layer   │────▶│  Core Logic  │◀────▶│  Configuration       │    │
│  │              │     │              │      │                      │    │
│  └──────────────┘     └───────┬──────┘      └──────────────────────┘    │
│                               │                                         │
│                               ▼                                         │
│  ┌──────────────┐     ┌──────────────┐      ┌──────────────────────┐    │
│  │              │     │              │      │                      │    │
│  │  Database    │◀───▶│  CrewAI      │◀────▶│  Document Generator  │    │
│  │  (PostgreSQL)│     │  Framework   │      │                      │    │
│  │              │     │              │      └──────────────────────┘    │
│  └──────────────┘     └───────┬──────┘                                  │
│                               │                                         │
│                               ▼                                         │
│                      ┌────────────────┐     ┌──────────────────────┐    │
│                      │                │     │                      │    │
│                      │  Search Agent  │────▶│  SerperDev API       │    │
│                      │                │     │  (External Service)  │    │
│                      └────────┬───────┘     └──────────────────────┘    │
│                               │                                         │
│                               ▼                                         │
│                      ┌────────────────┐     ┌──────────────────────┐    │
│                      │                │     │                      │    │
│                      │ Reasoning Agent│────▶│  Google Gemini API   │    │
│                      │                │     │  (External Service)  │    │
│                      └────────────────┘     └──────────────────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

1. **User Query Flow**:

   - User inputs search query via CLI
   - Query is processed by core logic
   - Search is executed using SerperDev API
   - Search results are stored in the database
   - Results are processed by Gemini LLM for reasoning
   - Generated content is transformed into the requested document format
   - Document is presented to the user

2. **History Query Flow**:
   - User requests search history via CLI
   - History request is processed by core logic
   - Past queries and metadata are retrieved from database
   - Results are formatted and presented to the user

```
┌──────┐    ┌──────────┐    ┌────────────┐    ┌──────────────┐    ┌───────────────┐
│ User │───▶│   CLI    │───▶│ Core Logic │───▶│ Search Agent │───▶│ SerperDev API │
└──────┘    └──────────┘    └─────┬──────┘    └──────────────┘    └───────────────┘
                                  │
                                  ▼
┌────────────────┐    ┌───────────────┐    ┌────────────┐    ┌────────────────┐
│ Final Document │◀───│ Document Gen  │◀───│ Reasoning  │◀───│ Gemini LLM API │
└────────────────┘    └───────────────┘    │ Agent      │    └────────────────┘
                                           └────────────┘
```

## Database Schema

The SearchAI application uses PostgreSQL for data persistence. The primary entities include:

1. **Search Queries**

   - Stores user search queries
   - Includes timestamps and metadata

2. **Search Results**
   - Stores raw search results
   - Links to corresponding search queries

```
┌────────────────┐       ┌────────────────────┐
│ SearchQuery    │       │ SearchResult       │
├────────────────┤       ├────────────────────┤
│ id (PK)        │       │ id (PK)            │
│ query_text     │       │ query_id (FK)      │
│ created_at     │       │ source_url         │
│ document_format│       │ title              │
└────────────────┘       │ snippet            │
                         │ created_at         │
                         └────────────────────┘
```

## API Integrations

1. **SerperDev API Integration**

   - Used for web search capabilities
   - Configured via environment variables
   - API key and base URL are managed in config

2. **Google Gemini API Integration**
   - Used for LLM reasoning and analysis
   - Configured via environment variables
   - API key and model settings are managed in config

## Configuration Management

SearchAI uses a configuration system based on environment variables:

1. **Environment Variables**

   - API credentials (Serper, Gemini)
   - Database connection parameters
   - Application settings

2. **Configuration Files**
   - .env file for local development
   - Environment variables for production deployment

## Security Considerations

1. **API Keys** - Stored as environment variables, never hard-coded
2. **Database Credentials** - Securely managed via environment variables
3. **Data Storage** - User queries and results are stored in the database

## Scalability

The application's architecture allows for scaling in several ways:

1. **Horizontal Scaling** - Multiple application containers can be deployed
2. **Database Scaling** - PostgreSQL can be scaled independently
3. **API Rate Limiting** - Configuration manages rate limits for external APIs

## Future Architecture Considerations

Potential enhancements to the architecture:

1. **Web Interface** - Add a web-based frontend for broader accessibility
2. **Caching Layer** - Redis or similar for improved performance
3. **Microservices** - Split functionality into dedicated microservices
4. **Authentication** - User authentication and personalized results
5. **Advanced Document Processing** - Enhanced document generation capabilities

## Technology Stack

- **Backend** - Python
- **CLI Framework** - Click
- **AI Framework** - CrewAI
- **Database** - PostgreSQL
- **LLM** - Google Gemini
- **Search API** - SerperDev
- **Document Generation** - Custom modules for Markdown, PDF, and PowerPoint

## Conclusion

The SearchAI system architecture provides a robust framework for search-driven document generation. The modular design allows for easy extension and maintenance, while the containerized deployment enables consistent operation across different environments.
