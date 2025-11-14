# evaluate.py
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import pandas as pd
import os
from sklearn.metrics import accuracy_score

# -------------------------------
# 1. Paths
# -------------------------------
model_dir = "./brain/models/classify_large"  # path to the trained model
data_file = os.path.abspath("./brain/models/commandsnew.csv")  # dataset path

# -------------------------------
# 2. Load dataset
# -------------------------------
df = pd.read_csv(data_file)
labels = {label: i for i, label in enumerate(df["intent"].unique())}
df["label"] = df["intent"].map(labels)

# train_size = int(0.8 * len(df))
val_texts = df["text"].tolist()
val_labels = df["label"].tolist()

# -------------------------------
# 3. Load model + tokenizer
# -------------------------------
tokenizer = AutoTokenizer.from_pretrained(model_dir)
model = AutoModelForSequenceClassification.from_pretrained(model_dir)
model.eval()

# -------------------------------
# 4. Predict on validation set
# -------------------------------
preds = []
for text in val_texts:
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
    pred = torch.argmax(outputs.logits, dim=1).item()
    preds.append(pred)

# -------------------------------
# 5. Accuracy
# -------------------------------
for i in range(len(val_texts)):
    if val_labels[i] != preds[i]:
        print(f"Text: {val_texts[i]} | True: {val_labels[i]} | Pred: {preds[i]}")
accuracy = accuracy_score(val_labels, preds)
print(f"✅ Validation Accuracy: {accuracy * 100:.2f}%")