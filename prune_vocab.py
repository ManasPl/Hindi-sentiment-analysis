import torch
from transformers import DistilBertTokenizer

device = torch.device("cpu")
model = torch.load("hindi_model_bert_8Sept.pt", map_location=device, weights_only=False)
model.eval()

tokenizer = DistilBertTokenizer.from_pretrained("tokenizer")
vocab = tokenizer.get_vocab()  # token -> old_id
id_to_token = {v: k for k, v in vocab.items()}
old_vocab_size = len(vocab)


def keep(token):
    if token in tokenizer.all_special_tokens:
        return True
    body = token[2:] if token.startswith("##") else token
    for ch in body:
        code = ord(ch)
        devanagari = 0x0900 <= code <= 0x097F
        ascii_range = code <= 0x7F
        if not (devanagari or ascii_range):
            return False
    return True


# Preserve original relative order so special tokens keep their usual low ids
kept_old_ids = [i for i in range(old_vocab_size) if keep(id_to_token[i])]
print(f"Pruning vocab: {old_vocab_size} -> {len(kept_old_ids)}")

old_to_new = {old_id: new_id for new_id, old_id in enumerate(kept_old_ids)}

# Rebuild vocab.txt in new id order
new_vocab_lines = [id_to_token[old_id] for old_id in kept_old_ids]
with open("tokenizer_pruned_vocab.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(new_vocab_lines) + "\n")

# Slice the embedding matrix to keep only the kept rows, in new order
old_embeddings = model.distilbert.embeddings.word_embeddings.weight.data  # (old_vocab, hidden)
hidden_size = old_embeddings.shape[1]
new_embeddings = torch.zeros((len(kept_old_ids), hidden_size), dtype=old_embeddings.dtype)
for new_id, old_id in enumerate(kept_old_ids):
    new_embeddings[new_id] = old_embeddings[old_id]

new_embedding_layer = torch.nn.Embedding(len(kept_old_ids), hidden_size, padding_idx=model.distilbert.embeddings.word_embeddings.padding_idx)
new_embedding_layer.weight.data = new_embeddings
model.distilbert.embeddings.word_embeddings = new_embedding_layer
model.config.vocab_size = len(kept_old_ids)

torch.save(model, "hindi_model_pruned.pt")
print("Saved pruned model: hindi_model_pruned.pt")

# Build new tokenizer pointing at the pruned vocab
import shutil
import os

os.makedirs("tokenizer_pruned", exist_ok=True)
shutil.copy("tokenizer_pruned_vocab.txt", "tokenizer_pruned/vocab.txt")
shutil.copy("tokenizer/tokenizer_config.json", "tokenizer_pruned/tokenizer_config.json")
shutil.copy("tokenizer/special_tokens_map.json", "tokenizer_pruned/special_tokens_map.json")

new_tokenizer = DistilBertTokenizer.from_pretrained("tokenizer_pruned")
print("New vocab size:", new_tokenizer.vocab_size)

# Sanity check: verify special token ids match what the model expects
for tok in tokenizer.all_special_tokens:
    old_id = vocab[tok]
    if old_id in old_to_new:
        print(tok, "old id", old_id, "-> new id", old_to_new[old_id], "| new tokenizer id:", new_tokenizer.convert_tokens_to_ids(tok))
