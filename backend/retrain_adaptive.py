"""
Adaptive Model Retraining Script
Automatically retrain models with validated user feedback
Run this script periodically (e.g., daily via cron job or Task Scheduler)
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
import pickle
import os
from feedback_db import FeedbackDB
from datetime import datetime

def retrain_text_model():
    """Retrain text scam detection model with validated feedback"""
    print("\n" + "="*60)
    print(f"TEXT MODEL RETRAINING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Initialize feedback database
    feedback_db = FeedbackDB()
    
    # Load original training data
    print("Loading original training data...")
    original_data = pd.read_csv("../datasets/spam.csv")
    original_data = original_data.rename(columns={"v1":"label","v2":"text"})
    print(f"Original dataset size: {len(original_data)} samples")
    
    # Get validated feedback data
    print("\nFetching validated user feedback...")
    feedback_data = feedback_db.get_validated_text_data()
    
    if feedback_data.empty:
        print("⚠️ No validated feedback data available. Skipping retraining.")
        return False
    
    print(f"Validated feedback samples: {len(feedback_data)} new samples")
    print(f"  - Safe: {len(feedback_data[feedback_data['label'] == 'safe'])}")
    print(f"  - Scam: {len(feedback_data[feedback_data['label'] == 'scam'])}")
    
    # Combine original and feedback data
    print("\nCombining datasets...")
    combined_data = pd.concat([original_data, feedback_data], ignore_index=True)
    print(f"Combined dataset size: {len(combined_data)} samples")
    
    # Prepare training data
    X = combined_data["text"]
    y = combined_data["label"]
    
    print("\nSplitting data (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train model
    print("\nTraining TF-IDF Vectorizer...")
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1,3), min_df=2)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    print("Training SVM Model with Calibration...")
    svm = LinearSVC(class_weight="balanced", max_iter=2000)
    model = CalibratedClassifierCV(svm, cv=5)
    model.fit(X_train_vec, y_train)
    
    # Evaluate
    train_acc = model.score(X_train_vec, y_train)
    test_acc = model.score(X_test_vec, y_test)
    
    print("\n" + "-"*60)
    print("MODEL PERFORMANCE:")
    print(f"  Training Accuracy: {train_acc:.4f} ({train_acc*100:.2f}%)")
    print(f"  Testing Accuracy:  {test_acc:.4f} ({test_acc*100:.2f}%)")
    print("-"*60)
    
    # Backup old model
    old_model_path = "models/text_scam_model.pkl"
    if os.path.exists(old_model_path):
        backup_path = f"models/backups/text_scam_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        os.makedirs("models/backups", exist_ok=True)
        os.rename(old_model_path, backup_path)
        print(f"\n✓ Old model backed up to: {backup_path}")
    
    # Save new model
    with open(old_model_path, "wb") as f:
        pickle.dump((model, vectorizer), f)
    
    print(f"✓ New model saved to: {old_model_path}")
    print("\n" + "="*60)
    print("TEXT MODEL RETRAINING COMPLETED SUCCESSFULLY!")
    print("="*60 + "\n")
    
    return True

def retrain_url_model():
    """Retrain URL phishing detection model with validated feedback"""
    print("\n" + "="*60)
    print(f"URL MODEL RETRAINING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Initialize feedback database
    feedback_db = FeedbackDB()
    
    # Load original training data
    print("Loading original training data...")
    original_data = pd.read_csv("../datasets/PhiUSIIL_Phishing_URL_Dataset.csv")
    print(f"Original dataset size: {len(original_data)} samples")
    
    # Get validated feedback data
    print("\nFetching validated user feedback...")
    feedback_data = feedback_db.get_validated_url_data()
    
    if feedback_data.empty:
        print("⚠️ No validated feedback data available. Skipping retraining.")
        return False
    
    print(f"Validated feedback samples: {len(feedback_data)} new samples")
    print(f"  - Safe: {len(feedback_data[feedback_data['label'] == 'safe'])}")
    print(f"  - Phishing: {len(feedback_data[feedback_data['label'] == 'phishing'])}")
    
    # Note: Full URL model retraining would require feature extraction
    # For now, we'll save the feedback data for future use
    print("\n⚠️ URL model retraining requires feature engineering.")
    print("Validated feedback data has been collected and is ready for integration.")
    print("Consider implementing url_features.py integration for full retraining.")
    
    print("\n" + "="*60)
    print("URL FEEDBACK COLLECTION COMPLETED")
    print("="*60 + "\n")
    
    return False

if __name__ == "__main__":
    print("\n" + "#"*60)
    print("#" + " "*20 + "ADAPTIVE RETRAINING" + " "*20 + "#")
    print("#"*60)
    
    # Initialize feedback DB to check stats
    feedback_db = FeedbackDB()
    stats = feedback_db.get_stats()
    
    print("\nCURRENT FEEDBACK STATISTICS:")
    print(f"  Text Data - Total: {stats['text']['total']}, " +
          f"Validated: {stats['text']['validated']}, " +
          f"Pending: {stats['text']['pending']}")
    print(f"  URL Data  - Total: {stats['url']['total']}, " +
          f"Validated: {stats['url']['validated']}, " +
          f"Pending: {stats['url']['pending']}")
    
    print("\n" + "#"*60 + "\n")
    
    # Retrain text model
    text_retrained = retrain_text_model()
    
    # Retrain URL model
    url_retrained = retrain_url_model()
    
    # Summary
    print("\n" + "#"*60)
    print("RETRAINING SUMMARY:")
    print(f"  Text Model: {'✓ RETRAINED' if text_retrained else '✗ SKIPPED'}")
    print(f"  URL Model:  {'✓ RETRAINED' if url_retrained else '✗ SKIPPED'}")
    print("#"*60 + "\n")
    
    if text_retrained or url_retrained:
        print("⚠️ IMPORTANT: Restart the Flask servers to load the new models!")
        print("   - Text Server: python backend/text_app.py")
        print("   - URL Server: python backend/url_app.py")
    else:
        print("No models were retrained. Keep collecting feedback!")
