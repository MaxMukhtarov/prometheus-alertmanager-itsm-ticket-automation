import http.server
import socketserver
import json
import urllib.request
import urllib.parse
import traceback

PORT = 5000

API_KEY = os.getenv("API_KEY")
SERVICE_DESK_URL = "http://project1-service-desk-1:8080/sdpapi/request"

SEVERITY_TO_PRIORITY = {
    "critical": "High",
    "warning": "Medium",
    "info": "Low"
}

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

            for a in alerts:
                annotations = a.get("annotations", {})
                labels = a.get("labels", {})

                summary = annotations.get("summary", "No summary")
                description = annotations.get("description", "")

                severity = labels.get("severity", "info")
                priority = SEVERITY_TO_PRIORITY.get(severity, "Medium")

                # 🔥 ВСЁ В ПРАВИЛЬНОМ РЕГИСТРЕ
                xml_data = f"<Operation><Details><Requester>administrator</Requester><Subject>{summary}</Subject><Description>{description}</Description><Priority>{priority}</Priority></Details></Operation>"

                print("\n➡️ XML:")
                print(xml_data)

                form_data = {
                    "OPERATION_NAME": "ADD_REQUEST",
                    "TECHNICIAN_KEY": API_KEY,
                    "INPUT_DATA": xml_data
                }

                encoded_data = urllib.parse.urlencode(form_data).encode("utf-8")

                req = urllib.request.Request(
                    SERVICE_DESK_URL,
                    data=encoded_data,
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    method="POST"
                )

                try:
                    with urllib.request.urlopen(req) as response:
                        resp_body = response.read().decode()
                        print("\n✅ SUCCESS:")
                        print(resp_body)
                except Exception:
                    print("\n❌ ERROR:")
                    traceback.print_exc()

        except Exception:
            print("\n❌ PROCESSING ERROR:")
            traceback.print_exc()

        self.send_response(200)
        self.end_headers()


with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"🚀 Webhook listening on port {PORT}")
    httpd.serve_forever()