"""
Feedback Database Manager for Adaptive Learning
Stores user feedback and manages pending validations
"""
import json
import os
from datetime import datetime
import pandas as pd

class FeedbackDB:
    def __init__(self, feedback_dir="feedback_data"):
        self.feedback_dir = feedback_dir
        self.text_feedback_file = os.path.join(feedback_dir, "text_feedback.json")
        self.url_feedback_file = os.path.join(feedback_dir, "url_feedback.json")
        
        # Create directories if they don't exist
        os.makedirs(feedback_dir, exist_ok=True)
        
        # Initialize files if they don't exist
        if not os.path.exists(self.text_feedback_file):
            self._save_json(self.text_feedback_file, [])
        if not os.path.exists(self.url_feedback_file):
            self._save_json(self.url_feedback_file, [])
    
    def _load_json(self, filepath):
        """Load JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_json(self, filepath, data):
        """Save JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def add_text_prediction(self, text, is_scam, confidence, user_ip=None):
        """Store automatic prediction for text"""
        feedback_data = self._load_json(self.text_feedback_file)
        
        # Check if text already exists
        for item in feedback_data:
            if item['text'] == text:
                item['prediction_count'] += 1
                item['last_predicted'] = datetime.now().isoformat()
                self._save_json(self.text_feedback_file, feedback_data)
                return
        
        # Add new entry
        entry = {
            'text': text,
            'model_prediction': 'scam' if is_scam else 'safe',
            'confidence': confidence,
            'user_reports': [],
            'status': 'pending',  # pending, validated, rejected
            'prediction_count': 1,
            'created_at': datetime.now().isoformat(),
            'last_predicted': datetime.now().isoformat(),
            'user_ip': user_ip
        }
        feedback_data.append(entry)
        self._save_json(self.text_feedback_file, feedback_data)
    
    def add_url_prediction(self, url, is_phishing, confidence, user_ip=None):
        """Store automatic prediction for URL"""
        feedback_data = self._load_json(self.url_feedback_file)
        
        # Check if URL already exists
        for item in feedback_data:
            if item['url'] == url:
                item['prediction_count'] += 1
                item['last_predicted'] = datetime.now().isoformat()
                self._save_json(self.url_feedback_file, feedback_data)
                return
        
        # Add new entry
        entry = {
            'url': url,
            'model_prediction': 'phishing' if is_phishing else 'safe',
            'confidence': confidence,
            'user_reports': [],
            'status': 'pending',
            'prediction_count': 1,
            'created_at': datetime.now().isoformat(),
            'last_predicted': datetime.now().isoformat(),
            'user_ip': user_ip
        }
        feedback_data.append(entry)
        self._save_json(self.url_feedback_file, feedback_data)
    
    def add_text_report(self, text, user_label, user_ip=None, comment=""):
        """Add user report for text (safe/scam)"""
        feedback_data = self._load_json(self.text_feedback_file)
        
        # Find existing entry or create new one
        entry = None
        for item in feedback_data:
            if item['text'] == text:
                entry = item
                break
        
        if not entry:
            entry = {
                'text': text,
                'model_prediction': None,
                'confidence': None,
                'user_reports': [],
                'status': 'pending',
                'prediction_count': 0,
                'created_at': datetime.now().isoformat(),
                'last_predicted': None,
                'user_ip': user_ip
            }
            feedback_data.append(entry)
        
        # Add user report
        report = {
            'label': user_label,  # 'safe' or 'scam'
            'user_ip': user_ip,
            'comment': comment,
            'timestamp': datetime.now().isoformat()
        }
        entry['user_reports'].append(report)
        
        # Auto-validate if threshold met (3+ reports with same label)
        self._check_validation_threshold(entry)
        
        self._save_json(self.text_feedback_file, feedback_data)
        return True
    
    def add_url_report(self, url, user_label, user_ip=None, comment=""):
        """Add user report for URL (safe/phishing)"""
        feedback_data = self._load_json(self.url_feedback_file)
        
        # Find existing entry or create new one
        entry = None
        for item in feedback_data:
            if item['url'] == url:
                entry = item
                break
        
        if not entry:
            entry = {
                'url': url,
                'model_prediction': None,
                'confidence': None,
                'user_reports': [],
                'status': 'pending',
                'prediction_count': 0,
                'created_at': datetime.now().isoformat(),
                'last_predicted': None,
                'user_ip': user_ip
            }
            feedback_data.append(entry)
        
        # Add user report
        report = {
            'label': user_label,  # 'safe' or 'phishing'
            'user_ip': user_ip,
            'comment': comment,
            'timestamp': datetime.now().isoformat()
        }
        entry['user_reports'].append(report)
        
        # Auto-validate if threshold met
        self._check_validation_threshold(entry)
        
        self._save_json(self.url_feedback_file, feedback_data)
        return True
    
    def _check_validation_threshold(self, entry, threshold=3):
        """Check if entry meets validation threshold"""
        if len(entry['user_reports']) < threshold:
            return
        
        # Count votes
        votes = {}
        for report in entry['user_reports']:
            label = report['label']
            votes[label] = votes.get(label, 0) + 1
        
        # If consensus reached (>= threshold with same label)
        max_votes = max(votes.values()) if votes else 0
        if max_votes >= threshold:
            entry['status'] = 'validated'
            entry['validated_at'] = datetime.now().isoformat()
    
    def get_validated_text_data(self):
        """Get validated text entries for retraining"""
        feedback_data = self._load_json(self.text_feedback_file)
        validated = [
            item for item in feedback_data 
            if item['status'] == 'validated' and item['user_reports']
        ]
        
        # Convert to training format
        training_data = []
        for item in validated:
            # Determine final label by majority vote
            votes = {}
            for report in item['user_reports']:
                label = report['label']
                votes[label] = votes.get(label, 0) + 1
            
            final_label = max(votes, key=votes.get)
            training_data.append({
                'text': item['text'],
                'label': final_label
            })
        
        return pd.DataFrame(training_data)
    
    def get_validated_url_data(self):
        """Get validated URL entries for retraining"""
        feedback_data = self._load_json(self.url_feedback_file)
        validated = [
            item for item in feedback_data 
            if item['status'] == 'validated' and item['user_reports']
        ]
        
        # Convert to training format
        training_data = []
        for item in validated:
            # Determine final label by majority vote
            votes = {}
            for report in item['user_reports']:
                label = report['label']
                votes[label] = votes.get(label, 0) + 1
            
            final_label = max(votes, key=votes.get)
            training_data.append({
                'url': item['url'],
                'label': final_label
            })
        
        return pd.DataFrame(training_data)
    
    def get_pending_reviews(self, data_type='text'):
        """Get items pending review"""
        filepath = self.text_feedback_file if data_type == 'text' else self.url_feedback_file
        feedback_data = self._load_json(filepath)
        return [item for item in feedback_data if item['status'] == 'pending']
    
    def admin_validate(self, data_type, identifier, status):
        """Admin manual validation"""
        filepath = self.text_feedback_file if data_type == 'text' else self.url_feedback_file
        feedback_data = self._load_json(filepath)
        
        key = 'text' if data_type == 'text' else 'url'
        for item in feedback_data:
            if item[key] == identifier:
                item['status'] = status  # 'validated' or 'rejected'
                item['admin_reviewed_at'] = datetime.now().isoformat()
                break
        
        self._save_json(filepath, feedback_data)
    
    def get_stats(self):
        """Get statistics about feedback data"""
        text_data = self._load_json(self.text_feedback_file)
        url_data = self._load_json(self.url_feedback_file)
        
        return {
            'text': {
                'total': len(text_data),
                'pending': len([x for x in text_data if x['status'] == 'pending']),
                'validated': len([x for x in text_data if x['status'] == 'validated']),
                'rejected': len([x for x in text_data if x['status'] == 'rejected'])
            },
            'url': {
                'total': len(url_data),
                'pending': len([x for x in url_data if x['status'] == 'pending']),
                'validated': len([x for x in url_data if x['status'] == 'validated']),
                'rejected': len([x for x in url_data if x['status'] == 'rejected'])
            }
        }
