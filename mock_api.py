"""本地 mock API：提供 3 个 JSON 接口，用于离线演示并发请求（任务一）。"""
from __future__ import annotations

import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path.startswith("/api/"):
            time.sleep(0.5)  # 故意慢一点，方便看出并发的优势
        body = json.dumps({"path": self.path, "ok": True}, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: object) -> None:
        pass


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
    print("mock api: http://127.0.0.1:8000/api/a  /api/b  /api/c")
    server.serve_forever()
