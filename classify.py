import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

model_dir = "./brain/models/classify_large"
# Load tokenizer & model from local directory
tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
model = AutoModelForSequenceClassification.from_pretrained(model_dir, local_files_only=True)

model.eval()

labels = {0: "tool-use", 1: "general", 2: "needs-internet", 3: "suggestion", 4: "hardware"}

def classify_input(test_text):
    encodings = tokenizer(test_text, truncation=True, padding=True, max_length=128, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**encodings)
        logits = outputs.logits
        predictions = torch.argmax(logits, dim=1)
        print(f"Predicted class index: {predictions}")
        label = labels[predictions.item()]
        print(label)
        return label

if __name__ == "__main__":
    while True:
        test_text = input("Enter your command: ")
        if test_text.lower() == "exit":
            break
        classify_input(test_text)


# to find the count of items in classify.json file
# import json

# with  open("memory/classify.json", "r") as f:
#     data = json.load(f)

# count = 0

# for item in data:
#     if "content" in item and "repeat" in item["content"]:
#         count += 1

# print(f"Total items with 'repeat': {count}")

# Total items with 'input_prompt': 105
# Total items with 'tool-use': 80
# Total items with 'general': 21
# Total items with 'repeat': 2