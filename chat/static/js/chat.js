// Initialize Markdown renderer with syntax highlighting and LaTeX support
const renderer = new marked.Renderer();
marked.setOptions({
    renderer: renderer,
    highlight: function(code, lang) {
        const language = hljs.getLanguage(lang) ? lang : 'plaintext';
        return hljs.highlight(code, { language }).value;
    },
    langPrefix: 'hljs language-',
    breaks: true,
});

// DOM elements
const chatMessages = document.getElementById('chatMessages');
const userMessageInput = document.getElementById('userMessage');
const messageForm = document.getElementById('messageForm');
const configForm = document.getElementById('configForm');
const resetBtn = document.getElementById('resetBtn');
const statusIndicator = document.getElementById('status');
const sendButton = document.getElementById('sendButton');

// API configuration elements
const apiEndpointInput = document.getElementById('apiEndpoint');
const apiKeyInput = document.getElementById('apiKey');
const modelNameInput = document.getElementById('modelName');

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Configure form submission
    configForm.addEventListener('submit', handleConfigSubmit);
    
    // Message form submission
    messageForm.addEventListener('submit', handleMessageSubmit);
    
    // Reset conversation
    resetBtn.addEventListener('click', handleReset);
    
    // Enable textarea keyboard shortcut (Ctrl+Enter to submit)
    userMessageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            e.preventDefault();
            messageForm.dispatchEvent(new Event('submit'));
        }
    });
    
    // Render any LaTeX in the messages
    renderMathInElement(chatMessages, {
        delimiters: [
            {left: '$$', right: '$$', display: true},
            {left: '$', right: '$', display: false}
        ]
    });
});

/**
 * Handle the configuration form submission
 */
async function handleConfigSubmit(e) {
    e.preventDefault();
    
    const apiEndpoint = apiEndpointInput.value.trim();
    const apiKey = apiKeyInput.value.trim();
    const modelName = modelNameInput.value.trim();
    
    if (!apiEndpoint || !apiKey || !modelName) {
        showNotification('Please fill in all fields', 'error');
        return;
    }
    
    setStatus('Saving configuration...');
    
    try {
        // Create FormData object and explicitly add all the inputs
        const formData = new FormData();
        formData.append('apiEndpoint', apiEndpoint);
        formData.append('apiKey', apiKey);
        formData.append('modelName', modelName);
        
        const response = await fetch('/setup', {
            method: 'POST',
            body: formData,
            headers: {
                'Accept': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Configuration saved successfully', 'success');
            // Clear the chat messages
            chatMessages.innerHTML = '';
        } else {
            showNotification('Failed to save configuration', 'error');
        }
    } catch (error) {
        console.error('Error saving configuration:', error);
        showNotification('Error saving configuration', 'error');
    } finally {
        setStatus('Idle');
    }
}

/**
 * Handle sending a message to the chatbot
 */
async function handleMessageSubmit(e) {
    e.preventDefault();
    
    const message = userMessageInput.value.trim();
    
    if (!message) return;
    
    // Disable input and button
    userMessageInput.disabled = true;
    sendButton.disabled = true;
    
    // Display user message
    addMessage(message, 'user');
    
    // Clear input
    userMessageInput.value = '';
    
    setStatus('Thinking...');
    
    try {
        const formData = new FormData();
        formData.append('message', message);
        
        const response = await fetch('/chat', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Display bot response
            addMessage(data.response, 'bot');
        } else {
            showNotification(`Error: ${data.error}`, 'error');
            addMessage('Sorry, I encountered an error. Please check your API configuration.', 'bot');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        addMessage('Network error. Please check your connection and try again.', 'bot');
    } finally {
        userMessageInput.disabled = false;
        sendButton.disabled = false;
        userMessageInput.focus();
        setStatus('Idle');
    }
}

/**
 * Handle resetting the conversation
 */
async function handleReset() {
    try {
        const response = await fetch('/reset', {
            method: 'POST',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Clear chat messages
            chatMessages.innerHTML = '';
            showNotification('Conversation reset', 'success');
        } else {
            showNotification('Failed to reset conversation', 'error');
        }
    } catch (error) {
        console.error('Error resetting conversation:', error);
        showNotification('Error resetting conversation', 'error');
    }
}

/**
 * Add a message to the chat UI
 */
function addMessage(content, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender === 'user' ? 'user-message' : 'bot-message'}`;
    
    if (sender === 'user') {
        // For user messages, simple escaping is enough
        messageDiv.textContent = content;
    } else {
        // For bot messages, use Markdown rendering
        messageDiv.innerHTML = marked.parse(content);
        
        // Render any LaTeX in the message
        renderMathInElement(messageDiv, {
            delimiters: [
                {left: '$$', right: '$$', display: true},
                {left: '$', right: '$', display: false}
            ]
        });
        
        // Apply syntax highlighting to code blocks
        messageDiv.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
    }
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll to the bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Set the status indicator text and style
 */
function setStatus(text) {
    statusIndicator.textContent = text;
    
    if (text === 'Idle') {
        statusIndicator.classList.remove('active');
    } else {
        statusIndicator.classList.add('active');
    }
}

/**
 * Show a notification message (to be improved in a future version)
 */
function showNotification(message, type = 'info') {
    // For now, just use alert, but this could be replaced with a nicer notification system
    alert(message);
}