# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **paviewer** (Price Action Viewer) - a personal trading decision support tool for Chinese stock and futures markets using AL Brooks Price Action methodology. The project is in its initial stages with only requirements documentation currently available.

## Project Architecture (Planned)

Based on the requirements, this will be a full-stack trading analysis application with:

### Backend Stack
- **FastAPI** for REST API endpoints
- **openctp Python API** for real-time market data
- **WebSocket** for real-time data streaming
- **SQLite** for historical market data caching
- Optional Redis for memory caching
- **uv** for Python package management

### Frontend Stack  
- **TradingView Lightweight Charts** or Advanced Charts for candlestick visualization
- Interactive measurement tools (Measured Move and Measure tools)
- Support for multiple timeframes (5min, 15min, 60min, daily)

### Core Features to Implement
1. **Chart Display**: Clean K-line charts with EMA20/MA16 indicators only
2. **Measured Move Tool**: Risk/reward ratio calculation with stop-loss and entry points
3. **Measure Tool**: Price movement measurement between any two points
4. **Real-time Data**: Live market data streaming via WebSocket

## Development Setup (To Be Implemented)

The project structure is now established:

```
paviewer/
├── backend/
│   └── app/
│       ├── api/          # API endpoints
│       ├── models/       # Data models
│       ├── services/     # Business logic
│       └── main.py       # FastAPI application
├── frontend/
│   ├── src/
│   │   ├── components/   # UI components
│   │   ├── services/     # API services
│   │   └── main.js       # TradingView charts setup
│   ├── package.json
│   └── index.html
├── docker/
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
├── docker-compose.yml
└── pyproject.toml        # Python dependencies (uv)
```

## Key Technical Requirements

- Real-time data latency < 500ms
- Docker deployment for easy local/server setup
- Personal use only (no multi-user considerations)
- Log/percentage chart view switching
- Interactive drag-and-drop measurement tools

## Development Commands

### Python Dependencies
- `uv sync` - Install/sync Python dependencies
- `uv run <command>` - Run commands in the virtual environment

### Development Servers
- `uv run uvicorn backend.app.main:app --reload` - Start FastAPI backend server
- `cd frontend && npm install && npm run dev` - Start frontend development server

### Docker Commands
- `docker-compose up` - Start all services with Docker
- `docker-compose up --build` - Rebuild and start all services
- `docker-compose down` - Stop all services

This file should be updated as the project develops beyond the requirements phase.

## Memories
- to memorize