import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle
import matplotlib.pyplot as plt

data = pd.read_csv("../datasets/PhiUSIIL_Phishing_URL_Dataset.csv")

# Drop non-numeric / non-feature columns
data = data.drop(columns=["FILENAME", "URL", "Domain", "TLD", "Title"], errors="ignore")

X = data.drop("label", axis=1)
y = data["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(n_estimators=500, class_weight="balanced", n_jobs=-1)
model.fit(X_train, y_train)

acc = model.score(X_test, y_test)
print("URL Model Accuracy:", acc)

with open("models/url_phishing_model.pkl", "wb") as f:
    pickle.dump(model, f)

# ===== Explainability =====
importances = model.feature_importances_
features = X.columns

top = sorted(zip(importances, features), reverse=True)[:10]

print("\nTop 10 Important Features:")
for i, f in top:
    print(f"{f}: {round(i,4)}")

plt.figure(figsize=(8,4))
plt.barh([f for _,f in top], [i for i,_ in top])
plt.title("Top Phishing Detection Features")
plt.tight_layout()
plt.savefig("models/url_feature_importance.png")
print("\nFeature importance chart saved as models/url_feature_importance.png")

print("URL Model saved successfully!")
