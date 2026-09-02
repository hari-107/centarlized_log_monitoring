# Centralized Log Monitoring & Security Analytics Platform

A containerized centralized log analytics and security monitoring platform using Elasticsearch, Filebeat, Django, and a **local Ollama LLM**. The platform combines deterministic security rules with AI enrichment to classify suspicious logs, prioritize threats, explain findings, and generate defensive recommendations.

## 🚀 Quick Start

### Prerequisites

- Docker Desktop / Docker Engine with Compose
- At least 8 GB RAM recommended for a local LLM

### Launch

```bash
git clone https://github.com/hari-107/centarlized_log_monitoring.git
cd centarlized_log_monitoring
cp .env.example .env
docker compose up --build -d
```

Pull the configured Ollama model once after the Ollama container starts:

```bash
docker compose exec ollama ollama pull llama3.1
```

Then open the dashboard at **http://localhost:8000**.

> Ollama runs locally inside the Compose network. Log content is sent to the local model rather than a hosted AI API.

## 🏗️ Architecture

```text
Log Generator / Servers
        │
        ▼
     Filebeat
        │
        ▼
 Elasticsearch
        │
        ▼
 Django processing pipeline
        │
        ├── Rule-based detection
        │      ├── auth failures
        │      ├── brute force
        │      ├── injection patterns
        │      └── suspicious indicators
        │
        └── Ollama AI enrichment
               ├── classification
               ├── severity
               ├── attack type
               ├── confidence
               ├── indicators
               └── recommendation
                        │
                        ▼
                 Threat database
                        │
                ┌───────┴────────┐
                ▼                ▼
            Dashboard        Email alerts
```

| Component | Description |
|-----------|-------------|
| **Elasticsearch** | Centralized log storage and search |
| **Filebeat** | Collects structured logs and forwards them to Elasticsearch |
| **Ollama** | Local LLM used for security-log classification and enrichment |
| **Django Backend** | Processing pipeline, APIs, threat storage, and alerting |
| **Log Generator** | Simulates multiple monitored servers |
| **Grafana** | Optional visualization |

## 🧠 AI Threat Analysis

Each newly processed threat can be enriched by Ollama with a structured result:

```json
{
  "classification": "ATTACK",
  "severity": "HIGH",
  "attack_type": "BRUTE_FORCE",
  "confidence": 0.94,
  "summary": "Repeated authentication failures indicate possible credential attack activity.",
  "recommendation": "Correlate source IP activity and review authentication logs.",
  "indicators": ["repeated login failures", "root account targeted"]
}
```

The implementation intentionally uses **rules + AI** instead of relying on the LLM alone. Existing high-risk deterministic findings are not downgraded by an AI result.

### Supported detection categories

`AUTH_FAILURE`, `BRUTE_FORCE`, `SQL_INJECTION`, `XSS`, `PATH_TRAVERSAL`, `COMMAND_INJECTION`, `SSRF`, `RCE`, `DOS_PATTERN`, `PRIVILEGE_ESCALATION`, `MALWARE_INDICATOR`, `DATA_EXFILTRATION`, `UNAUTHORIZED_ACCESS`, `PORT_SCAN`, and `UNKNOWN`.

## 🛡️ Security Model

The AI layer is **analysis-only**. It does not execute commands or directly modify the monitored host. Existing active-response functionality remains separate from AI analysis.

High/Critical events can still trigger the configured email alerting workflow.

## 📊 Threat Data

AI metadata is stored on `ThreatLog`, including:

- `ai_analyzed`
- `ai_model`
- `ai_confidence`
- `ai_summary`
- `ai_recommendation`
- `ai_indicators`

Run Django migrations after an update:

```bash
docker compose exec django-app python project/manage.py migrate
```

## 📧 Email Alerting

Email credentials are **not stored in `docker-compose.yml`**. Copy `.env.example` to `.env` and configure:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-sender@gmail.com
SMTP_PASSWORD=your-gmail-app-password
ALERT_EMAIL_FROM=your-sender@gmail.com
ALERT_EMAIL_TO=your-recipient@gmail.com
```

For Gmail, use an App Password rather than a normal account password.

## 🌐 Service URLs

| Service | URL |
|---------|-----|
| **Dashboard** | http://localhost:8000 |
| **Elasticsearch** | http://localhost:9200 |
| **Ollama** | http://localhost:11434 |
| **Grafana** | http://localhost:3000 |

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/servers/` | List monitored servers and threat statistics |
| GET | `/api/logs/?server_id=&severity=&keyword=` | Search/filter Elasticsearch logs |
| GET | `/api/threats/?server_id=&severity=&status=` | Filter stored threats |
| GET | `/api/stats/` | Dashboard statistics |
| POST | `/api/analyze/` | Trigger processing / analysis |
| POST | `/api/resolve/<id>/` | Mark a threat as resolved |

## 🔧 Useful Commands

```bash
docker compose up --build -d

docker compose exec ollama ollama pull llama3.1

docker compose exec django-app python project/manage.py migrate

docker compose logs -f django-app
docker compose logs -f ollama
docker compose down
```

## ⚠️ Secret Rotation

If an SMTP password has ever been committed to this repository, revoke/rotate it immediately and create a new credential. The current Compose configuration uses environment variables so credentials stay outside source control.
