from flask import Flask, request, jsonify
from threading import Thread

class PMServer:
    def __init__(self, config, event_queue, host="0.0.0.0", port=8080):
        self.app = Flask(__name__)
        self.queue = event_queue
        self.host = host
        self.port = port
        self.config = config
        self._setup_routes()

    def _setup_routes(self):
        @self.app.route("/command", methods=["POST"])
        def command():
            data = request.get_json()
            if not data:
                return jsonify({"error": "Missing 'action'"}), 400
            self.queue.put(data)
            return jsonify({"status": "queued", "action": data.get("action")})

    def start(self):
        def run():
            self.app.run(host=self.host, port=self.port, threaded=True)
        Thread(target=run, daemon=True).start()

