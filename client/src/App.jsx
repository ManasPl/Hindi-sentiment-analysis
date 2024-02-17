import { useEffect, useState } from "react";
import PredictionCard from "./components/PredictionCard";
import { Send } from "lucide-react";
import axios from "axios";

function App() {
  const [isOnboarding, setIsOnboarding] = useState(true);
  const [predictions, setPredictions] = useState([]);
  const [inputStatement, setInputStatement] = useState("");

  const demoStatements = [
    "आप कैसे हो?",
    "तेरे जैसा गधा मैंने आज तक नहीं देखा",
    "गर्मी का मौसम है कृपया अपने वाहन चलाने से पहले ये जरूर देख ले कि कही कोई जानवर आपकी गाड़ी के नीचे सो तो नही रहा।",
  ];

  useEffect(() => {
    if (predictions.length > 0) {
      setIsOnboarding(false);
    }
  }, [predictions]);

  const handleChange = (e) => {
    setInputStatement(e.target.value);
  };

  const handleSubmit = async (e) => {
    if (inputStatement === "") return;
    e.preventDefault();
    const statement = inputStatement;
    const prediction = 0;
    const isLoading = true;
    const newPrediction = {
      statement,
      prediction,
      isLoading,
    };
    // setPredictions([newPrediction, ...predictions])
    setPredictions([...predictions, newPrediction]);
    setInputStatement("");
    const res = await axios.post("http://localhost:8000/predict", {
      Sentence: inputStatement.toString(),
    });
    const data = res.data;
    console.log(data);
    newPrediction.prediction = data.value;
    newPrediction.isLoading = false;
    setPredictions([newPrediction, ...predictions]);
    console.log(predictions);
  };

  return (
    <>
      <div className="w-full h-screen px-4 sm:px-40 flex flex-col items-center bg-surface">
        <div className="flex flex-col py-5 sm:py-12 px-0 items-center sticky">
          <img
            src="/logo.svg"
            alt="Our Logo"
            className="w-72 sm:w-128 cursor-pointer"
            onClick={() => window.location.reload(false)}
          />
        </div>
        <div className="w-full flex flex-col flex-1 p-4 align-middle gap-4 bg-surface overflow-scroll no-scrollbar">
          {!isOnboarding &&
            predictions.map((prediction, index) => (
              <PredictionCard
                key={index}
                statement={prediction.statement}
                prediction={prediction.prediction}
                isLoading={prediction.isLoading}
              />
            ))}
          {isOnboarding && (
            <div className="w-full flex flex-col gap-9">
              <div className="flex flex-col gap-2">
                <p className="text-[1.5rem] sm:text-[2.25rem] font-bold text-text leading-none">
                  Enter your
                </p>
                <p className="text-[2.5rem] sm:text-[3.75rem] font-bold bg-gradient-to-r from-blue-500 to-indigo-700 bg-clip-text text-transparent leading-none">
                  Statement!
                </p>
              </div>
              <div className="w-full flex flex-col px-6 py-6 gap-6 rounded-3xl bg-white">
                <p className="text-[1.25rem] font-bold text-text leading-none">
                  Examples
                </p>
                <div className="flex flex-col gap-4">
                  {demoStatements.map((statement, index) => (
                    <button
                      key={index}
                      className="flex flex-row self-start px-4 py-3 sm:py-2 rounded-3xl sm:rounded-full bg-[#EFF2F8]"
                      onClick={() => {
                        setInputStatement(statement);
                      }}
                    >
                      <p className="text-text text-start">{statement}</p>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
        <form
          className="w-full flex flex-row px-4 pt-4 pb-4 sm:pb-12 gap-2 sm:gap-4 items-center bg-surface fixed bottom-0 sm:relative"
          onSubmit={handleSubmit}
        >
          <input
            type="text"
            className="w-full h-12 px-4 py-2 rounded-2xl bg-white text-text text-body.base"
            placeholder="Enter a statement"
            onChange={handleChange}
            value={inputStatement}
          />
          <button className="w-12 h-12 px-4 flex items-center justify-center rounded-2xl bg-primary-base">
            <Send type="submit" color="background" className="w-6 h-6" />
          </button>
        </form>
      </div>
    </>
  );
}

export default App;
