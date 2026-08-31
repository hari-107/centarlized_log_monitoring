# Centralized Log Monitoring & Security Analytics Platform

A scalable, containerized log analytics and security monitoring system powered by AI (Ollama LLM). Simulates multiple servers generating diverse logs, processes them through Elasticsearch, and provides real-time threat detection with email alerting.

## 🚀 Quick Start

1. **Prerequisites**: [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
2. **Clone & Launch**:
   ```bash
   git clone <repository-url>
   cd centralized_log_monitoring
   docker-compose up --build -d
   ```
3. **Dashboard**: Open [http://localhost:8000](http://localhost:8000)

> **Note:** On first run, the `llama3` model (~4.7GB) will auto-download. This may take several minutes.

## 🏗️ Architecture

| Component | Description |
|-----------|-------------|
| **Elasticsearch** | Centralized log storage and search engine |
| **Filebeat** | Log collector forwarding structured JSON logs |
| **Ollama** | Local AI engine (`llama3`) for threat classification |
| **Django Backend** | REST API, processing pipeline, and email alerting |
| **Log Generator** | Multi-server simulator (5 servers, 4 severity levels) |
| **Grafana** | Optional visualization dashboards |

## 🖥️ Simulated Servers

| Server ID | Name | Environment | Threat Specialization |
|-----------|------|-------------|----------------------|
| srv-001 | linux-gateway | Linux System | SSH brute force, rootkits, privilege escalation |
| srv-002 | web-server-nginx | Web Server | XSS, SQL injection, DDoS, web shells |
| srv-003 | ssh-bastion | SSH Service | SSH brute force, dictionary attacks, key compromise |
| srv-004 | database-postgres | Database Server | SQL injection, data exfiltration, unauthorized access |
| srv-005 | api-gateway | API Gateway | Credential stuffing, token forgery, rate abuse |

Each server uses **weighted severity distribution** (Low ~50%, Medium ~25%, High ~15%, Critical ~10%) for realistic log patterns.

### Adding New Servers

Add a new entry to `log-generator/server_config.py` in the `SERVERS` list. No other changes needed.

## 🛠️ Key Features

- **Multi-Server Monitoring**: 5 independent simulated servers with unique identities
- **Advanced Filtering**: Filter by server, severity, keyword, IP, date range
- **Weighted Severity**: Natural distribution across Low/Medium/High/Critical
- **AI Threat Detection**: Automated classification via Ollama LLM every minute
- **Email Alerting**: SMTP notifications for High/Critical events
- **Severity Charts**: Doughnut chart for severity distribution, bar chart per server
- **Top Attacking IPs**: Aggregated across all servers (24h window)
- **Server Management**: Per-server drill-down with threat statistics
- **Threat Patching**: Mark threats as resolved from the dashboard

## 📧 Email Alerting Setup

Uncomment and configure in `docker-compose.yml`:
```yaml
- SMTP_HOST=smtp.gmail.com
- SMTP_PORT=587
- ALERT_EMAIL_FROM=your-sender@gmail.com
- ALERT_EMAIL_TO=your-recipient@gmail.com
- SMTP_USERNAME=your-sender@gmail.com
- SMTP_PASSWORD=your-app-password
```

For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833).

## 📊 Service URLs

| Service | URL |
|---------|-----|
| **Dashboard** | [http://localhost:8000](http://localhost:8000) |
| **Elasticsearch** | [http://localhost:9200](http://localhost:9200) |
| **Ollama** | [http://localhost:11434](http://localhost:11434) |
| **Grafana** | [http://localhost:3000](http://localhost:3000) (admin/admin) |

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/servers/` | List servers with threat stats |
| GET | `/api/logs/?server_id=&severity=&keyword=` | Filtered ES logs |
| GET | `/api/threats/?server_id=&severity=&status=` | Filtered threat alerts |
| GET | `/api/stats/` | Aggregated dashboard statistics |
| POST | `/api/analyze/` | Trigger manual AI analysis |
| POST | `/api/resolve/<id>/` | Mark threat as resolved |

## 🔍 Troubleshooting

- **No logs?** Wait ~30s for Filebeat to connect to Elasticsearch
- **AI fails?** Ensure 8GB+ RAM is available for `llama3`
- **Servers not showing?** Trigger an analysis first to sync servers from ES

## 📜 Commands

```bash
docker-compose up --build -d    # Start
docker-compose down             # Stop
docker-compose logs -f django-app  # View Django logs
docker-compose logs -f log-generator  # View log generations
```
