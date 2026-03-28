# 🚀 Prometheus → Alertmanager → ServiceDesk Integration

## 📌 Overview

This project implements a full monitoring pipeline that automatically creates ServiceDesk tickets from Prometheus alerts.

**Flow:**

```
Prometheus → Alertmanager → Webhook → ServiceDesk
```

---

## 🧩 Architecture

* **Prometheus** – generates alerts
* **Alertmanager** – routes alerts to webhook
* **Webhook (Python)** – transforms alert → ServiceDesk request
* **ServiceDesk (Docker)** – ticketing system

---

## ⚙️ Project Structure

```
project1/
├── alertmanager.yml
├── alerts.yml
├── docker-compose.yml
├── prometheus.yml
└── webhook/
    ├── app.py
    └── Dockerfile
```

---

## 🚀 Setup

### 1. Create Docker network

```bash
docker network create monitoring-net
```

---

### 2. Run ServiceDesk отдельно

```bash
docker run -d \
--name project1-service-desk-1 \
--network monitoring-net \
-p 8080:8080 \
vcibelli/service-desk
```

---

### 3. ⚠️ Generate API Key (IMPORTANT)

After starting ServiceDesk:

1. Open:

   ```
   http://localhost:8080
   ```
2. Login:

   * Username: `administrator`
   * Password: `administrator`
3. Go to:

   ```
   Admin → Technicians
   ```
4. Select user and generate **Technician Key**

---

### 4. Store API Key in `.env` (recommended)

Create `.env` file in project root:

```bash
nano .env
```

```env
API_KEY=YOUR_API_KEY
SERVICE_DESK_URL=http://project1-service-desk-1:8080/sdpapi/request
```

⚠️ Do NOT store API key directly in code.

---

### 5. Run monitoring stack

```bash
docker compose up --build
```

---

## 🔔 Prometheus Alert Example

```yaml
groups:
  - name: test_alerts
    rules:
      - alert: TestAlert
        expr: vector(1)
        for: 0s
        labels:
          severity: critical
        annotations:
          summary: "Test alert firing"
          description: "This is a test alert from Prometheus"
```

---

## 🔗 Alertmanager Config

```yaml
route:
  receiver: "webhook"

receivers:
  - name: "webhook"
    webhook_configs:
      - url: "http://webhook:5000/alert"
```

---

## 🧠 Webhook Logic

Webhook receives alert JSON and converts it into ServiceDesk XML request.

### Mapping

| Prometheus  | ServiceDesk |
| ----------- | ----------- |
| summary     | Subject     |
| description | Description |
| severity    | Priority    |

---

## 🔥 IMPORTANT (API GOTCHA)

ServiceDesk API is **case-sensitive**.

Correct XML:

```xml
<Operation>
  <Details>
    <Subject>...</Subject>
```

❌ Wrong:

```xml
<operation>
<subject>
```

---

## 🧪 Manual API Test

```bash
curl -X POST "http://localhost:8080/sdpapi/request" \
-H "Content-Type: application/x-www-form-urlencoded" \
--data-urlencode "OPERATION_NAME=ADD_REQUEST" \
--data-urlencode "TECHNICIAN_KEY=YOUR_KEY" \
--data-urlencode "INPUT_DATA=<Operation><Details><Requester>administrator</Requester><Subject>Test</Subject><Description>Test</Description><Priority>High</Priority></Details></Operation>"
```

---

## 🐍 Webhook Example (Core Part)

```python
xml_data = f"<Operation><Details><Requester>administrator</Requester><Subject>{summary}</Subject><Description>{description}</Description><Priority>{priority}</Priority></Details></Operation>"
```

---

## 🧰 Technologies Used

* Prometheus
* Alertmanager
* Python (http.server)
* Docker / Docker Compose
* ManageEngine ServiceDesk (Docker)

---

## 📈 Features

* ✅ Automatic ticket creation from alerts
* ✅ Severity → Priority mapping
* ✅ Customizable via Prometheus labels
* ✅ Fully containerized
* ✅ Production-ready architecture (stateful + stateless separation)

---

## 🚀 Future Improvements

* 🔁 Alert deduplication (1 alert = 1 ticket)
* 🔄 Auto-close ticket on resolved alert
* 🧠 Alert fingerprint tracking
* 📊 Logging & retry logic

---

## 👨‍💻 Author

Mamurjon Mukhtorov (Monitoring & Automation)

---

## 📜 License

MIT
