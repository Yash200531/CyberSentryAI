import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
import pickle

data = pd.read_csv("../datasets/spam.csv")
data = data.rename(columns={"v1":"label","v2":"text"})


X = data["text"]
y = data["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1,3), min_df=2)
svm = LinearSVC(class_weight="balanced")
model = CalibratedClassifierCV(svm)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

model.fit(X_train_vec, y_train)

acc = model.score(X_test_vec, y_test)
print("Model Accuracy:", acc)

with open("models/text_scam_model.pkl", "wb") as f:
    pickle.dump((model, vectorizer), f)

print("SVM Model saved successfully!")
