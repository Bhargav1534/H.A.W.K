from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration


def generate_image_caption(image_path):
    # Load the pre-trained BLIP model and processor
    processor = BlipProcessor.from_pretrained("Salesforce/blip2-flan-t5-xl")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip2-flan-t5-xl")

    # Load and preprocess the image
    image = Image.open(image_path).convert("RGB")
    prompt = ""
    inputs = processor(images=image, return_tensors="pt", use_fast=True)

    # Generate the caption
    out = model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)

    return caption

if __name__ == "__main__":
    image_path = "Screenshot 2025-10-05 174350.png"  # Replace with your image path
    caption = generate_image_caption(image_path)
    print("Generated Caption:", caption)