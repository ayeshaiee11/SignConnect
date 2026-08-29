import json
import pickle
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import numpy as np


ROOT_DIR = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 5000

MODELS = {
    "alphabet": ROOT_DIR / "model.pkl",
    "letters": ROOT_DIR / "nmodel.pkl",
    "phrases": ROOT_DIR / "wmodel.pkl",
}

EXPECTED_LENGTH = {
    "alphabet": 63,
    "letters": 63,
    "phrases": 126,
}

loaded_models = {}


def load_models():
    missing = []
    for mode, path in MODELS.items():
        if not path.exists():
            missing.append(str(path))
            continue
        with path.open("rb") as f:
            loaded_models[mode] = pickle.load(f)
    if missing:
        raise FileNotFoundError("Missing model files:\n" + "\n".join(missing))


def add_cors_headers(handler):
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")


def predict(mode, features):
    model = loaded_models.get(mode)
    if model is None:
        raise ValueError(f"Model not loaded for mode '{mode}'")

    target_len = EXPECTED_LENGTH[mode]
    vec = list(features[:target_len])
    if len(vec) < target_len:
        vec.extend([0.0] * (target_len - len(vec)))

    arr = np.array([vec], dtype=np.float32)
    pred = model.predict(arr)[0]

    confidence = 100.0
    if hasattr(model, "predict_proba"):
        try:
            probs = model.predict_proba(arr)[0]
            confidence = float(np.max(probs) * 100.0)
        except Exception:
            confidence = 100.0

    return str(pred), confidence


class DetectHandler(BaseHTTPRequestHandler):
    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        add_cors_headers(self)
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        add_cors_headers(self)
        self.end_headers()

    def do_GET(self):
        if self.path != "/health":
            self._send_json(404, {"ok": False, "error": "Not found"})
            return
        self._send_json(200, {"ok": True, "models": list(loaded_models.keys())})

    def do_POST(self):
        if self.path != "/predict":
            self._send_json(404, {"ok": False, "error": "Not found"})
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)
        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except Exception:
            self._send_json(400, {"ok": False, "error": "Invalid JSON body"})
            return

        mode = payload.get("mode")
        features = payload.get("features")
        if mode not in MODELS:
            self._send_json(400, {"ok": False, "error": "Mode must be alphabet, letters, or phrases"})
            return
        if not isinstance(features, list):
            self._send_json(400, {"ok": False, "error": "features must be a list"})
            return

        try:
            label, confidence = predict(mode, features)
        except Exception as exc:
            self._send_json(500, {"ok": False, "error": str(exc)})
            return

        self._send_json(200, {"ok": True, "label": label, "confidence": confidence, "mode": mode})


def main():
    load_models()
    print(f"PKL backend ready at http://{HOST}:{PORT}")
    server = HTTPServer((HOST, PORT), DetectHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
