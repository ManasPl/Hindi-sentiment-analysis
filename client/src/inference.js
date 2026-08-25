import { AutoTokenizer, AutoModelForSequenceClassification, env } from "@huggingface/transformers";

// Model is served locally (client/public/models/hindi-sentiment), not from the HF Hub —
// this is what lets the whole app deploy as a static site with no backend.
env.allowRemoteModels = false;
env.allowLocalModels = true;
env.localModelPath = `${import.meta.env.BASE_URL}models/`;

const MODEL_ID = "hindi-sentiment";

let modelPromise = null;

function loadModel() {
  if (!modelPromise) {
    modelPromise = Promise.all([
      AutoTokenizer.from_pretrained(MODEL_ID),
      AutoModelForSequenceClassification.from_pretrained(MODEL_ID, { dtype: "q8" }),
    ]);
  }
  return modelPromise;
}

// Kick off loading as soon as this module is imported so the model is warm by the
// time the user submits their first statement.
loadModel();

// Returns 1 for "Not offensive", 0 for "Offensive" — matches the original FastAPI
// backend's /predict response shape ({ value: 0 | 1 }) so PredictionCard needs no changes.
export async function predict(sentence) {
  const [tokenizer, model] = await loadModel();
  const inputs = await tokenizer(sentence, { padding: "max_length", truncation: true, max_length: 128 });
  const { logits } = await model(inputs);
  const scores = logits.tolist()[0];
  const predictedClass = scores[0] > scores[1] ? 0 : 1;
  return predictedClass;
}
