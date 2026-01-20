import json
import joblib
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "data/intent_data.json")
MODEL_DIR = os.path.join(BASE_DIR, "model")

os.makedirs(MODEL_DIR, exist_ok=True)

# 1. Load data
with open(DATA_PATH, "r") as f:
    intents = json.load(f)

texts = []
labels = []

for intent, examples in intents.items():
    for sentence in examples:
        texts.append(sentence.lower())
        labels.append(intent)

# 2. Vectorization
vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),
    stop_words="english"
)

X = vectorizer.fit_transform(texts)

# 3. Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, labels, test_size=0.2, random_state=42
)

# 4. Model
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# 5. Evaluation
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))

# 6. Save model
joblib.dump(model, os.path.join(MODEL_DIR, "intent_model.pkl"))
joblib.dump(vectorizer, os.path.join(MODEL_DIR, "vectorizer.pkl"))

print("✅ Model trained and saved successfully")
