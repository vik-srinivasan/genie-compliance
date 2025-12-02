// Contract Safety Chatbot Frontend

let currentContractCode = '';
let currentStatus = '';

// DOM Elements
const contractInput = document.getElementById('contractInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const resultSection = document.getElementById('resultSection');
const statusBadge = document.getElementById('statusBadge');
const reasoning = document.getElementById('reasoning');
const evidenceSummary = document.getElementById('evidenceSummary');
const chatSection = document.getElementById('chatSection');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');

// Analyze contract
analyzeBtn.addEventListener('click', async () => {
    const code = contractInput.value.trim();
    
    if (!code) {
        alert('Please enter contract code');
        return;
    }
    
    currentContractCode = code;
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = 'Analyzing...';
    
    try {
        const response = await fetch('/api/classify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code: code })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Classification failed');
        }
        
        // Display results
        currentStatus = data.status;
        statusBadge.textContent = data.status.toUpperCase();
        statusBadge.className = `status-badge ${data.status}`;
        
        reasoning.textContent = data.reasoning || 'No reasoning provided';
        evidenceSummary.textContent = data.evidence_summary || 'No evidence summary';
        
        resultSection.classList.remove('hidden');
        chatSection.classList.remove('hidden');
        
        // Clear previous chat
        chatMessages.innerHTML = '';
        
        // Add initial assistant message
        if (data.status === 'unsafe') {
            addMessage('assistant', 'I found some safety issues in your contract. Ask me how to fix them! For example:\n- "What are the main issues?"\n- "How do I fix the balance check?"\n- "Show me a corrected version"');
        } else {
            addMessage('assistant', 'Your contract appears to be safe! However, I can still help you improve it or answer questions. What would you like to know?');
        }
        
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = 'Analyze Contract';
    }
});

// Send chat message
sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

async function sendMessage() {
    const message = chatInput.value.trim();
    
    if (!message) {
        return;
    }
    
    if (!currentContractCode) {
        alert('Please analyze a contract first');
        return;
    }
    
    // Add user message to chat
    addMessage('user', message);
    chatInput.value = '';
    sendBtn.disabled = true;
    
    // Show loading
    const loadingId = addMessage('assistant', 'Thinking...');
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                contract_code: currentContractCode,
                status: currentStatus
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Chat failed');
        }
        
        // Remove loading message and add assistant response
        removeMessage(loadingId);
        addMessage('assistant', data.message);
        
    } catch (error) {
        removeMessage(loadingId);
        addMessage('assistant', 'Sorry, I encountered an error: ' + error.message);
    } finally {
        sendBtn.disabled = false;
    }
}

function addMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    // Format code blocks if present
    if (content.includes('```')) {
        const parts = content.split('```');
        let formatted = '';
        for (let i = 0; i < parts.length; i++) {
            if (i % 2 === 0) {
                formatted += escapeHtml(parts[i]);
            } else {
                formatted += `<pre>${escapeHtml(parts[i])}</pre>`;
            }
        }
        messageDiv.innerHTML = formatted.replace(/\n/g, '<br>');
    } else {
        messageDiv.textContent = content;
    }
    
    const id = 'msg-' + Date.now() + '-' + Math.random();
    messageDiv.id = id;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return id;
}

function removeMessage(id) {
    const element = document.getElementById(id);
    if (element) {
        element.remove();
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

