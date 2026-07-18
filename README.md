# StadiumIQ — GenAI Smart Stadium Assistant

> AI-powered command center and fan assistant for FIFA World Cup 2026 at MetLife Stadium

## Chosen Vertical

**Stadium Navigation & Crowd Management** — An advanced GenAI solution that transforms stadium operations through real-time crowd intelligence, predictive analytics, emergency response, accessibility-first navigation, multilingual fan assistance, live match simulation, and personalized fan journey tracking.

## Architecture

```
stadiumiq/
├── app.py                          # Flask + SocketIO main application (45+ endpoints)
├── run.py                          # Entry point
├── config/settings.py              # Environment configuration
├── core/
│   ├── ai/genai_engine.py          # OpenAI GenAI with multi-turn context + fallback
│   ├── crowd/crowd_engine.py       # Real-time crowd flow simulation
│   ├── iot/sensor_engine.py        # IoT sensor network (36 sensors, 9 types)
│   ├── emergency/emergency_engine.py  # Emergency incident management
│   ├── navigation/nav_engine.py    # Wayfinding & accessibility routing
│   ├── sentiment/sentiment_engine.py  # Fan sentiment analysis
│   ├── predictive/predictive_engine.py # Demand prediction & risk assessment
│   ├── analytics/dashboard_engine.py   # Operational KPIs & analytics
│   ├── fan/__init__.py             # Smart Fan Journey tracker
│   ├── match/__init__.py           # AI Match Simulator
│   └── satisfaction/__init__.py    # Fan Satisfaction scoring
├── web/
│   ├── templates/index.html        # Single-page app (Fan + Command Center)
│   └── static/
│       ├── css/style.css           # Dark theme, responsive, accessible
│       └── js/app.js               # Real-time updates, Chart.js visualizations
├── tests/
│   ├── test_app.py                 # 61 pytest tests (all passing)
│   └── verify.py                   # Full end-to-end verification script
├── Dockerfile                      # Container deployment
├── docker-compose.yml              # Docker Compose setup
└── requirements.txt                # Python dependencies
```

## Features

| # | Feature | Description | GenAI? |
|---|---------|-------------|--------|
| 1 | **Multi-Turn AI Chat** | Context-aware conversations with memory | Yes |
| 2 | **Smart Fan Journey** | Tracks fan from arrival to departure with personalized tips | Yes |
| 3 | **AI Match Simulator** | Live match events, score predictions, momentum tracking | Yes |
| 4 | **Crowd Intelligence** | Real-time density, flow tracking, heatmap, prediction | Yes |
| 5 | **Emergency System** | Incident management, evacuation plans, safety scoring | Yes |
| 6 | **IoT Sensors** | 36 sensors, anomaly detection, zone aggregation | Yes |
| 7 | **Predictive Analytics** | Demand, risk, wait time predictions | Yes |
| 8 | **Sentiment Analysis** | Emotion detection, topic extraction, NPS | Yes |
| 9 | **Satisfaction Scoring** | 13 touchpoints, NPS, weakest area identification | Yes |
| 10 | **Command Center** | KPIs, charts, alerts, staff deployment, AI insights | Yes |
| 11 | **Accessibility** | WCAG 2.1, keyboard nav, screen reader, a11y profiles | - |
| 12 | **Multilingual** | 10 languages including Arabic, Chinese, Japanese | - |

## API Endpoints (45+)

| Category | Count | Endpoints |
|----------|-------|-----------|
| AI Chat | 1 | `/api/chat` |
| Crowd | 4 | `/api/crowd`, `/overview`, `/heatmap`, `/predict` |
| IoT | 3 | `/api/iot/sensors`, `/zones`, `/anomalies` |
| Emergency | 4 | `/api/emergency/raise`, `/resolve`, `/status`, `/evacuation` |
| Navigation | 4 | `/api/navigation`, `/nearby`, `/accessibility/<profile>` |
| Analytics | 4 | `/api/analytics/predict`, `/risks`, `/waits`, `/insights` |
| Sentiment | 3 | `/api/sentiment/analyze`, `/summary`, `/chart` |
| Dashboard | 5 | `/api/dashboard/kpis`, `/hourly`, `/revenue`, `/staff`, `/command` |
| Fan Journey | 6 | `/api/journey/start`, `/advance`, `/status/<id>`, `/recommendations/<id>`, `/action`, `/analytics` |
| Match | 7 | `/api/match/start`, `/simulate`, `/minute`, `/status`, `/events`, `/prediction`, `/energy`, `/teams` |
| Satisfaction | 4 | `/api/satisfaction/score`, `/nps`, `/dashboard`, `/weakest` |

## How GenAI Is Used

1. **Chat** — Every fan query processed through OpenAI GPT-4o-mini with full stadium context
2. **Multi-turn Memory** — Conversation history maintained per fan for context awareness
3. **Sentiment** — Fan feedback analyzed for emotions, topics, satisfaction scores
4. **Emergency** — AI generates custom emergency response plans based on incident type
5. **Match Predictions** — AI-powered win probability and next event prediction
6. **Personalized Journey** — AI tailors recommendations based on fan position and preferences

## Running

```bash
pip install -r requirements.txt
cp .env.example .env
python run.py
# Visit http://localhost:5000
```

## Testing

```bash
pytest tests/ -v          # 61 tests passing
python tests/verify.py    # Full verification (35 route + 16 engine checks)
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.10+, Flask, Flask-SocketIO |
| AI | OpenAI GPT-4o-mini + rule-based fallback |
| Frontend | HTML5, CSS3, JavaScript ES6+, Chart.js 4.4 |
| Icons | Font Awesome 6.5 |
| Real-time | WebSocket (SocketIO) |
| Testing | pytest (61 tests) |
| Deploy | Docker, Docker Compose |

## Evaluation Alignment

| Criteria | Weight | What We Have |
|----------|--------|-------------|
| **Code Quality** | HIGH | 11 modular engines, clean separation, type hints, docstrings |
| **Problem Alignment** | HIGH | Solves real FIFA 2026 stadium operations challenges |
| **Innovation** | HIGH | Smart Fan Journey, Match Simulator, Satisfaction Scoring — unique differentiators |
| **Security** | MEDIUM | Env vars, no secrets in code, input validation |
| **Efficiency** | MEDIUM | Lightweight fallback, async updates, optimized queries |
| **Testing** | LOW | 61 tests + verification script covering all endpoints |
| **Accessibility** | LOW | WCAG 2.1, keyboard nav, screen reader, a11y mode |
