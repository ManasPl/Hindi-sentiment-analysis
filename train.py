import random
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from torch.optim import AdamW
from transformers import (
    DistilBertTokenizer,
    DistilBertForSequenceClassification,
    get_linear_schedule_with_warmup,
)

device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print("Using device:", device)

seed_val = 42
random.seed(seed_val)
np.random.seed(seed_val)
torch.manual_seed(seed_val)

df = pd.read_csv("hindi_dataset.csv")
df = df.rename(columns={"text": "Text", "task_1": "Type"})
df["Type"] = df["Type"].astype("category")
print("Label mapping:", dict(enumerate(df["Type"].cat.categories)))
df["Type"] = df["Type"].cat.codes.astype(np.int64)

X = list(df["Text"].values)
y = list(df["Type"].values)

X_tmp, X_test, y_tmp, y_test = train_test_split(X, y, test_size=0.10, random_state=42, stratify=y)
X_train, X_valid, y_train, y_valid = train_test_split(X_tmp, y_tmp, test_size=0.111, random_state=42, stratify=y_tmp)
print(f"train={len(X_train)} valid={len(X_valid)} test={len(X_test)}")

model_name = "distilbert-base-multilingual-cased"
tokenizer = DistilBertTokenizer.from_pretrained(model_name)


def generate_dataset(X, y, tokenizer):
    encodings = tokenizer.batch_encode_plus(
        X, truncation=True, padding=True, max_length=128, return_tensors="pt", add_special_tokens=True
    )
    input_ids = encodings["input_ids"]
    attention_mask = encodings["attention_mask"]
    labels = torch.tensor(y)
    return TensorDataset(input_ids, attention_mask, labels)


train_dataset = generate_dataset(X_train, y_train, tokenizer)
valid_dataset = generate_dataset(X_valid, y_valid, tokenizer)
test_dataset = generate_dataset(X_test, y_test, tokenizer)


def get_data_loader(dataset, sampler):
    return DataLoader(dataset=dataset, sampler=sampler(dataset), batch_size=32)


train_loader = get_data_loader(train_dataset, RandomSampler)
validation_loader = get_data_loader(valid_dataset, SequentialSampler)
test_loader = get_data_loader(test_dataset, SequentialSampler)

model = DistilBertForSequenceClassification.from_pretrained(model_name, num_labels=2)
model.to(device)
print("Imported model!")

optimizer = AdamW(model.parameters(), lr=2e-5, eps=1e-8)
num_epochs = 8
total_steps = len(train_loader) * num_epochs
scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=total_steps)


def compute_accuracy(preds, labels):
    preds = preds.detach().cpu().numpy()
    labels = labels.detach().cpu().numpy()
    preds = np.argmax(preds, axis=1).flatten()
    labels = labels.flatten()
    return np.sum(preds == labels) / len(labels)


def train():
    total_loss = 0.0
    total_acc = 0.0
    model.train()
    for step, batch in enumerate(train_loader):
        if step % 50 == 0 and step != 0:
            print(f"  Batch {step:>5,} of {len(train_loader):>5,}.")
        input_ids = batch[0].to(device)
        attention_mask = batch[1].to(device)
        labels = batch[2].to(device)
        model.zero_grad()
        outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        logits = outputs.logits
        total_loss += loss.item()
        total_acc += compute_accuracy(logits, labels)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
    return total_loss / len(train_loader), total_acc / len(train_loader)


def evaluate(loader):
    total_loss = 0.0
    total_acc = 0.0
    model.eval()
    true_labels = []
    predictions = []
    with torch.no_grad():
        for step, batch in enumerate(loader):
            input_ids = batch[0].to(device)
            attention_mask = batch[1].to(device)
            labels = batch[2].to(device)
            outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            logits = outputs.logits
            total_loss += loss.item()
            total_acc += compute_accuracy(logits, labels)
            preds = np.argmax(logits.detach().cpu().numpy(), axis=1).flatten()
            predictions.extend(preds.tolist())
            true_labels.extend(labels.detach().cpu().numpy().flatten().tolist())
    f1 = f1_score(true_labels, predictions, average="weighted")
    return total_loss / len(loader), total_acc / len(loader), f1


best_f1 = 0.0
save_path = "hindi_model_bert_8Sept.pt"

for epoch in range(num_epochs):
    print(f"\nEpoch {epoch + 1} / {num_epochs}")
    train_loss, train_acc = train()
    valid_loss, valid_acc, f1 = evaluate(validation_loader)
    if f1 > best_f1:
        best_f1 = f1
        torch.save(model, save_path)
        print(f"  -> saved new best checkpoint (f1={f1:.3f})")
    print(
        f"Training Accuracy: {train_acc:.3f} | Training Loss: {train_loss:.3f} | "
        f"Validation Accuracy: {valid_acc:.3f} | Validation Loss: {valid_loss:.3f} | F1 Score: {f1:.3f}"
    )

print("\nLoading best checkpoint for final test evaluation...")
best_model = torch.load(save_path, map_location=device, weights_only=False)
best_model.to(device)
globals()["model"] = best_model
test_loss, test_acc, test_f1 = evaluate(test_loader)
print(f"\nTest Accuracy: {test_acc:.3f} | Test Loss: {test_loss:.3f} | F1 Score: {test_f1:.3f}")
print(f"\nSaved best model to {save_path} (best validation F1={best_f1:.3f})")
