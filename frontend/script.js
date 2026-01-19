// ===================================
// CyberSentryAI Dashboard JavaScript
// API Integration & UI Logic
// ===================================

// API Endpoints
const TEXT_API_URL = 'http://127.0.0.1:5000/detect-text';
const URL_API_URL = 'http://127.0.0.1:5001/detect-url';

// Sample Data for Quick Tests
const TEXT_SAMPLES = [
    "URGENT! Your bank account has been compromised. Click here immediately to verify your identity and prevent account closure: http://secure-bank-verify.com/login",
    "Congratulations! You've won $5,000 in our monthly lottery! Reply with your bank details to claim your prize within 24 hours or it will expire.",
    "Your package delivery failed. Pay ₹50 redelivery fee here: bit.ly/pkg-delivery. Your order #12345 will be returned if not claimed today!",
    "Hi John, just wanted to confirm our meeting tomorrow at 3 PM at the coffee shop. Let me know if you're still available. Thanks!"
];

const URL_SAMPLES = [
    "http://secure-sbi-login-verify@accountlogin.com/signin",
    "https://accounts-verify-login.com/secure/bank/upi-paytm",
    "http://bit.ly/urgent-action-required",
    "https://www.google.com"
];

// Statistics Object
let stats = {
    totalScans: 0,
    threatsDetected: 0,
    safeResults: 0
};

// History Arrays
let textHistory = [];
let urlHistory = [];

// ===================================
// Initialization
// ===================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('CyberSentryAI Frontend Loaded');
    console.log('Text API URL:', TEXT_API_URL);
    console.log('URL API URL:', URL_API_URL);
    
    // Load saved statistics and history
    loadStatistics();
    loadHistory();
    
    // Initialize tab switching
    initTabSwitching();
    
    // Initialize event listeners
    initTextDetector();
    initURLDetector();
    
    console.log('All initializations complete');
});

// ===================================
// Tab Switching Logic
// ===================================

function initTabSwitching() {
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const tabId = item.getAttribute('data-tab');

            // Remove active class from all nav items and tabs
            navItems.forEach(nav => nav.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Add active class to clicked item
            item.classList.add('active');
            document.getElementById(`${tabId}-tab`).classList.add('active');

            // Update breadcrumb
            const pageName = tabId === 'text' ? 'Text Analysis' : 'URL Scanner';
            document.getElementById('current-page').textContent = pageName;

            // Clear previous results when switching tabs
            clearResults(tabId);
        });
    });
}

// ===================================
// Quick Sample Loaders
// ===================================

function loadTextSample(index) {
    const textInput = document.getElementById('text-input');
    textInput.value = TEXT_SAMPLES[index];
    textInput.focus();
    
    // Add a subtle animation
    textInput.style.borderColor = 'var(--accent-cyan)';
    setTimeout(() => {
        textInput.style.borderColor = '';
    }, 1000);
}

function loadURLSample(index) {
    const urlInput = document.getElementById('url-input');
    urlInput.value = URL_SAMPLES[index];
    urlInput.focus();
    
    // Add a subtle animation
    urlInput.style.borderColor = 'var(--accent-cyan)';
    setTimeout(() => {
        urlInput.style.borderColor = '';
    }, 1000);
}

// ===================================
// Statistics Management
// ===================================

function loadStatistics() {
    const savedStats = localStorage.getItem('cyberSentryStats');
    if (savedStats) {
        stats = JSON.parse(savedStats);
    }
    updateStatisticsDisplay();
}

function saveStatistics() {
    localStorage.setItem('cyberSentryStats', JSON.stringify(stats));
}

function updateStatistics(isThreat) {
    stats.totalScans++;
    if (isThreat) {
        stats.threatsDetected++;
    } else {
        stats.safeResults++;
    }
    saveStatistics();
    updateStatisticsDisplay();
}

function updateStatisticsDisplay() {
    // Update main counters (if they exist in the old layout)
    const totalScans = document.getElementById('total-scans');
    const threatsDetected = document.getElementById('threats-detected');
    const safeResults = document.getElementById('safe-results');
    const successRate = document.getElementById('success-rate');
    
    if (totalScans) totalScans.textContent = stats.totalScans;
    if (threatsDetected) threatsDetected.textContent = stats.threatsDetected;
    if (safeResults) safeResults.textContent = stats.safeResults;
    if (successRate) {
        const protectionRate = stats.totalScans > 0 
            ? Math.round((stats.safeResults / stats.totalScans) * 100) 
            : 100;
        successRate.textContent = protectionRate + '%';
    }
    
    // Update sidebar stats
    document.getElementById('sidebar-total').textContent = stats.totalScans;
    document.getElementById('sidebar-threats').textContent = stats.threatsDetected;
    document.getElementById('sidebar-safe').textContent = stats.safeResults;
}

// ===================================
// History Management
// ===================================

function loadHistory() {
    const savedTextHistory = localStorage.getItem('textHistory');
    const savedURLHistory = localStorage.getItem('urlHistory');
    
    if (savedTextHistory) {
        textHistory = JSON.parse(savedTextHistory);
    }
    if (savedURLHistory) {
        urlHistory = JSON.parse(savedURLHistory);
    }
    
    renderHistory('text');
    renderHistory('url');
}

function saveHistory(type) {
    if (type === 'text') {
        localStorage.setItem('textHistory', JSON.stringify(textHistory));
    } else {
        localStorage.setItem('urlHistory', JSON.stringify(urlHistory));
    }
}

function addToHistory(type, content, result) {
    const historyItem = {
        timestamp: new Date().toISOString(),
        content: content,
        isThreat: type === 'text' ? (result.is_spam || result.is_scam) : result.is_phishing,
        confidence: result.confidence,
        riskLevel: result.risk_level
    };
    
    if (type === 'text') {
        textHistory.unshift(historyItem);
        if (textHistory.length > 10) textHistory.pop(); // Keep only last 10
        saveHistory('text');
        renderHistory('text');
    } else {
        urlHistory.unshift(historyItem);
        if (urlHistory.length > 10) urlHistory.pop(); // Keep only last 10
        saveHistory('url');
        renderHistory('url');
    }
}

function renderHistory(type) {
    const historyList = document.getElementById(`${type}-history-list`);
    const historySection = document.getElementById(`${type}-history-section`);
    const history = type === 'text' ? textHistory : urlHistory;
    
    if (history.length === 0) {
        historySection.style.display = 'none';
        return;
    }
    
    historySection.style.display = 'block';
    
    historyList.innerHTML = history.map(item => {
        const date = new Date(item.timestamp);
        const timeStr = date.toLocaleString();
        const badgeClass = item.isThreat ? 'threat' : 'safe';
        const badgeText = item.isThreat ? '⚠️ Threat' : '✅ Safe';
        const contentClass = type === 'url' ? 'history-url' : '';
        const displayContent = item.content.length > 100 
            ? item.content.substring(0, 100) + '...' 
            : item.content;
        
        return `
            <div class="history-item">
                <div class="history-meta">
                    <span class="history-time">🕒 ${timeStr}</span>
                    <span class="history-badge ${badgeClass}">${badgeText}</span>
                </div>
                <div class="history-content ${contentClass}">${displayContent}</div>
            </div>
        `;
    }).join('');
}

function clearHistory(type) {
    if (confirm(`Are you sure you want to clear all ${type} scan history?`)) {
        if (type === 'text') {
            textHistory = [];
            localStorage.removeItem('textHistory');
            renderHistory('text');
        } else {
            urlHistory = [];
            localStorage.removeItem('urlHistory');
            renderHistory('url');
        }
    }
}

// ===================================
// Text Detection
// ===================================

function initTextDetector() {
    const checkBtn = document.getElementById('check-text-btn');
    const inputField = document.getElementById('text-input');

    checkBtn.addEventListener('click', () => analyzeText());
    
    // Allow Enter key to trigger analysis (with Ctrl for textarea)
    inputField.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            analyzeText();
        }
    });
}

async function analyzeText() {
    console.log('Analyze text function called');
    const textInput = document.getElementById('text-input');
    const text = textInput.value.trim();

    console.log('Text to analyze:', text);

    // Validation
    if (!text) {
        showError('text', 'Please enter some text to analyze');
        return;
    }

    // Show loading state
    showLoading('text');
    hideError('text');
    hideResults('text');

    try {
        console.log('Sending request to:', TEXT_API_URL);
        const response = await fetch(TEXT_API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text })
        });

        console.log('Response status:', response.status);

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        console.log('Response data:', data);
        displayTextResults(data);
        
        // Update statistics and history
        const isThreat = data.is_spam || data.is_scam;
        updateStatistics(isThreat);
        addToHistory('text', text, data);

    } catch (error) {
        console.error('Text detection error:', error);
        showError('text', 'Failed to analyze text. Make sure the Text Agent API is running on port 5000.');
    } finally {
        hideLoading('text');
    }
}

function displayTextResults(data) {
    console.log('Displaying text results:', data);
    
    // Show results container
    const resultsDiv = document.getElementById('text-results');
    resultsDiv.style.display = 'block';

    // Risk Indicator
    const riskBadge = document.getElementById('text-risk-badge');
    const isScam = data.is_spam || data.is_scam;
    riskBadge.textContent = data.risk_level || (isScam ? 'High Risk' : 'Low Risk');
    riskBadge.className = 'risk-indicator ' + (isScam ? 'high-risk' : 'low-risk');

    // Confidence Score
    const confidence = document.getElementById('text-confidence');
    const confidenceValue = (data.confidence || data.probability || 0) * 100;
    confidence.textContent = `${confidenceValue.toFixed(1)}%`;

    // Explanation Findings
    const explanationList = document.getElementById('text-explanation');
    explanationList.innerHTML = '';
    
    if (data.explanation && data.explanation.length > 0) {
        explanationList.className = 'findings-list';
        data.explanation.forEach(reason => {
            const li = document.createElement('li');
            li.textContent = reason;
            explanationList.appendChild(li);
        });
    } else if (isScam) {
        const li = document.createElement('li');
        li.textContent = 'Multiple suspicious patterns detected in the text';
        explanationList.appendChild(li);
    } else {
        explanationList.className = 'findings-list safe';
        const li = document.createElement('li');
        li.textContent = 'No suspicious patterns detected';
        explanationList.appendChild(li);
    }

    // Model Info Badge
    const modelInfo = document.getElementById('text-model-info');
    modelInfo.textContent = data.note || '🤖 Analyzed using Machine Learning model trained on spam dataset';
}

// ===================================
// URL Detection
// ===================================

function initURLDetector() {
    const checkBtn = document.getElementById('check-url-btn');
    const inputField = document.getElementById('url-input');

    checkBtn.addEventListener('click', () => analyzeURL());
    
    // Allow Enter key to trigger analysis
    inputField.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            analyzeURL();
        }
    });
}

async function analyzeURL() {
    const urlInput = document.getElementById('url-input');
    const url = urlInput.value.trim();

    // Validation
    if (!url) {
        showError('url', 'Please enter a URL to scan');
        return;
    }

    // Basic URL format validation
    if (!url.includes('.')) {
        showError('url', 'Please enter a valid URL (e.g., https://example.com)');
        return;
    }

    // Show loading state
    showLoading('url');
    hideError('url');
    hideResults('url');

    try {
        const response = await fetch(URL_API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        displayURLResults(data);
        
        // Update statistics and history
        updateStatistics(data.is_phishing);
        addToHistory('url', url, data);

    } catch (error) {
        console.error('URL detection error:', error);
        showError('url', 'Failed to scan URL. Make sure the URL Agent API is running on port 5001.');
    } finally {
        hideLoading('url');
    }
}

function displayURLResults(data) {
    // Show results container
    const resultsDiv = document.getElementById('url-results');
    resultsDiv.style.display = 'block';

    // Risk Indicator
    const riskBadge = document.getElementById('url-risk-badge');
    riskBadge.textContent = data.risk_level || (data.is_phishing ? 'High Risk' : 'Low Risk');
    riskBadge.className = 'risk-indicator ' + (data.is_phishing ? 'high-risk' : 'low-risk');

    // Confidence Score
    const confidence = document.getElementById('url-confidence');
    const confidenceValue = (data.confidence || 0) * 100;
    confidence.textContent = `${confidenceValue.toFixed(1)}%`;

    // Scanned URL
    const scannedUrl = document.getElementById('scanned-url');
    scannedUrl.textContent = data.url || data.URL;

    // Explanation Findings
    const explanationList = document.getElementById('url-explanation');
    explanationList.innerHTML = '';
    
    if (data.explanation && data.explanation.length > 0) {
        explanationList.className = 'findings-list';
        data.explanation.forEach(reason => {
            const li = document.createElement('li');
            li.textContent = reason;
            explanationList.appendChild(li);
        });
    } else if (data.is_phishing) {
        const li = document.createElement('li');
        li.textContent = 'Multiple phishing indicators detected';
        explanationList.appendChild(li);
    } else {
        explanationList.className = 'findings-list safe';
        const li = document.createElement('li');
        li.textContent = 'No major phishing indicators found';
        explanationList.appendChild(li);
    }

    // Model Info Badge
    const modelInfo = document.getElementById('url-model-info');
    modelInfo.textContent = data.note || '🤖 Analyzed using Random Forest model trained on PhiUSIIL dataset';
}

// ===================================
// UI Helper Functions
// ===================================

function showLoading(type) {
    const loadingDiv = document.getElementById(`${type}-loading`);
    if (loadingDiv) {
        loadingDiv.style.display = 'block';
    }
}

function hideLoading(type) {
    const loadingDiv = document.getElementById(`${type}-loading`);
    if (loadingDiv) {
        loadingDiv.style.display = 'none';
    }
}

function showError(type, message) {
    const errorDiv = document.getElementById(`${type}-error`);
    if (errorDiv) {
        errorDiv.textContent = `❌ ${message}`;
        errorDiv.style.display = 'block';
    }
}

function hideError(type) {
    const errorDiv = document.getElementById(`${type}-error`);
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
}

function hideResults(type) {
    const resultsDiv = document.getElementById(`${type}-results`);
    if (resultsDiv) {
        resultsDiv.style.display = 'none';
    }
}

function clearResults(type) {
    hideResults(type);
    hideError(type);
    hideLoading(type);
}

// ===================================
// Utility: Copy to Clipboard (bonus feature)
// ===================================

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        console.log('Copied to clipboard');
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}
