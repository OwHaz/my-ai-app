from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "put that 'text' on request"}), 400

    text = data["text"]
    return jsonify({
        "message": "work together!",
        "text": text,
        "bilang_ng_salitang": len(text.split()),
        "haba_ng_teksto": len(text)
    })

@app.route("/")
def home():
    return jsonify({
        "status": "live!",
        "use": "POST /predict",
        "sample": {"text": "how are u?"}
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
