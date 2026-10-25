from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModel
import torch

app = Flask(__name__)

# I-load ang BERT pre-trained model mula sa Hugging Face
MODEL_NAME = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Kailangan ng 'text' sa request"}), 400

    text = data["text"]
    
    # I-proseso ang input gamit ang tokenizer
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=512
    )

    # Ipatakbo ang BERT model
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Kunin ang output (hidden states)
    embeddings = outputs.last_hidden_state[:, 0, :].squeeze().numpy().tolist()
    
    return jsonify({
        "model": MODEL_NAME,
        "input_text": text,
        "embedding_dimensions": len(embeddings),
        "embedding": embeddings
    })

@app.route("/")
def home():
    return {
        "message": "✅ BERT AI API — Gumagana!",
        "endpoint": "/predict",
        "method": "POST",
        "usage": '{"text": "Ang iyong teksto dito"}'
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)