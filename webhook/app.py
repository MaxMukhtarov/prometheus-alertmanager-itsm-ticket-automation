import http.server
import socketserver
import json
import requests
import os
import re

PORT = 5000

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("API_KEY")

SERVICE_DESK_URL = "http://project1-service-desk-1:8080/sdpapi/request"

SEVERITY_TO_PRIORITY = {
    "critical": "High",
    "warning": "Medium",
    "info": "Low"
}


def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

        response = requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": message
        })

        print("📩 Telegram response:", response.text)

    except Exception as e:
        print("❌ Telegram error:", e)


class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/alert":
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)

        print("\n=== RAW BODY ===")
        print(body.decode())

        try:
            data = json.loads(body)
            alerts = data.get("alerts", [])

            print("ALERTS:", alerts)

            for a in alerts:
                annotations = a.get("annotations", {})
                labels = a.get("labels", {})

                summary = annotations.get("summary", "No summary")
                description = annotations.get("description", "")

                severity = labels.get("severity", "info")
                priority = SEVERITY_TO_PRIORITY.get(severity, "Medium")

                technician = labels.get("technician", "administrator")

                print("➡️ SUMMARY:", summary)
                print("➡️ DESCRIPTION:", description)

                # ✅ правильный XML
                xml_data = f"<Operation><Details><Requester>administrator</Requester><Subject>{summary}</Subject><Description>{description}</Description><Priority>{priority}</Priority></Details></Operation>"

                print("➡️ XML:", xml_data)

                payload = {
                    "OPERATION_NAME": "ADD_REQUEST",
                    "TECHNICIAN_KEY": API_KEY,
                    "INPUT_DATA": xml_data
                }

                try:
                    response = requests.post(
                        SERVICE_DESK_URL,
                        data=payload
                    )

                    print("✅ ServiceDesk status:", response.status_code)
                    print("✅ ServiceDesk response:", response.text)

                    match = re.search(r"<workorderid>(\d+)</workorderid>", response.text)
                    ticket_id = match.group(1) if match else "unknown"

                    message = f"""🚨 Incident detected!

📌 Source: Prometheus
📄 Summary: {summary}
📝 Description: {description}
🎯 Priority: {priority}
🎫 Ticket ID: {ticket_id}
👤 Technician: {technician}
"""

                    send_telegram(message)

                except Exception as e:
                    print("❌ ServiceDesk error:", e)

        except Exception as e:
            print("❌ PROCESSING ERROR:", e)

        self.send_response(200)
        self.end_headers()


with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"🚀 Webhook listening on port {PORT}")
    httpd.serve_forever()