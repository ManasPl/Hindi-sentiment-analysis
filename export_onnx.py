import torch
from transformers import DistilBertTokenizer

device = torch.device("cpu")
model = torch.load("hindi_model_bert_8Sept.pt", map_location=device, weights_only=False)
model.eval()

tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-multilingual-cased")

dummy = tokenizer("आप कैसे हो?", return_tensors="pt", padding="max_length", truncation=True, max_length=128)

torch.onnx.export(
    model,
    (dummy["input_ids"], dummy["attention_mask"]),
    "model.onnx",
    input_names=["input_ids", "attention_mask"],
    output_names=["logits"],
    dynamic_axes={
        "input_ids": {0: "batch", 1: "sequence"},
        "attention_mask": {0: "batch", 1: "sequence"},
        "logits": {0: "batch"},
    },
    opset_version=14,
)

tokenizer.save_pretrained("tokenizer")

print("Exported model.onnx and tokenizer/")
