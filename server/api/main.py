from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
import numpy as np
import torch 
from transformers import DistilBertTokenizer
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

import warnings
warnings.filterwarnings("ignore")

class InputData(BaseModel):
    Sentence: str

model = torch.load('hindi_model_bert_8Sept.pt', map_location=torch.device('cpu'))
model_name = 'distilbert-base-multilingual-cased'
tokenizer = DistilBertTokenizer.from_pretrained(model_name)

app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:3000/",
    "http://0.0.0.0:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
async def ping():
    return "Hello I am alive"
@app.post("/predict")
async def predict(data: InputData):
    input_data =  str(data.Sentence)
    print(input_data)
    model.eval()
    
    inputs = tokenizer(input_data, return_tensors='pt', truncation=True, padding=True)
    input_ids = inputs['input_ids']
    attention_mask = inputs['attention_mask']

    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)
    logits = outputs.logits
    logits = logits.detach().cpu().numpy()
    logits=np.array(logits)
    predicted_class = np.argmax(logits, axis=None)
    predicted_class = float(predicted_class)
    return {"value": predicted_class}

#sentence_to_evaluate = "आप कैसे हो?"


if __name__ == "__main__":
    # uvicorn.run(app,host='192.168.214.142', port=8000)
    uvicorn.run(app,host='localhost', port=8000)