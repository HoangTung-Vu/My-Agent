// Global state
let currentSessionId = null;
let sessions = [];

// DOM Elements
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatMessages = document.getElementById('chat-messages');
const sessionList = document.getElementById('conversation-list');
const newSessionBtn = document.getElementById('new-conversation-btn');
const deleteSessionBtn = document.getElementById('delete-conversation-btn');
const sessionActions = document.getElementById('conversation-actions');

// Templates
const sessionItemTemplate = document.getElementById('conversation-item-template');
const messageTemplate = document.getElementById('message-template');

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    // Focus on input field
    userInput.focus();
    
    // Load sessions
    loadSessions();
    
    // Add event listeners
    setupEventListeners();
});

// Set up event listeners
function setupEventListeners() {
    // New session button
    newSessionBtn.addEventListener('click', createNewSession);
    
    // Delete session button
    deleteSessionBtn.addEventListener('click', deleteCurrentSession);
    
    // Chat form submission
    chatForm.addEventListener('submit', handleChatFormSubmit);
}

// Create a new session
async function createNewSession() {
    try {
        // Clear current session UI
        clearChatMessages();
        showWelcomeMessage();
        
        // Reset current session ID
        currentSessionId = null;
        
        // Update UI to reflect new session
        updateActiveSession(null);
        sessionActions.style.display = 'none';
        
        // Focus on input
        userInput.focus();
        
    } catch (error) {
        console.error('Error creating new session:', error);
        showErrorMessage('Failed to create a new session. Please try again.');
    }
}

// Handle chat form submission
async function handleChatFormSubmit(e) {
    e.preventDefault();
    
    const message = userInput.value.trim();
    if (!message) return;
    
    // Clear input
    userInput.value = '';
    
    // Add user message to UI
    addMessage('user', message);
    
    // Show typing indicator
    addTypingIndicator();
    
    try {
        // Send message to API
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                session_id: currentSessionId
            })
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Update session ID if this is a new session
        if (!currentSessionId) {
            currentSessionId = data.session_id;
            sessionActions.style.display = 'block';
            
            // Reload sessions to include the new one
            await loadSessions();
            
            // Update the active session
            updateActiveSession(currentSessionId);
        }
        
        // Remove typing indicator
        removeTypingIndicator();
        
        // Add assistant response to UI
        addMessage('assistant', data.response);
        
        // Focus on input
        userInput.focus();
        
    } catch (error) {
        console.error('Error sending message:', error);
        removeTypingIndicator();
        showErrorMessage('Failed to send message. Please try again.');
    }
}

// Load all sessions
async function loadSessions() {
    try {
        const response = await fetch('/api/sessions');
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        
        sessions = await response.json();
        
        // Clear session list
        while (sessionList.firstChild) {
            sessionList.removeChild(sessionList.firstChild);
        }
        
        if (sessions.length === 0) {
            // Show empty state
            const emptyState = document.createElement('div');
            emptyState.classList.add('empty-state-message');
            emptyState.innerHTML = `
                <p>No sessions yet.</p>
                <p>Start a new session!</p>
            `;
            sessionList.appendChild(emptyState);
        } else {
            // Add sessions to list
            sessions.forEach(session => {
                addSessionToList(session);
            });
        }
        
    } catch (error) {
        console.error('Error loading sessions:', error);
        showErrorMessage('Failed to load sessions. Please refresh the page.');
    }
}

// Add a session to the list
function addSessionToList(session) {
    // Clone the template
    const sessionItem = document.importNode(sessionItemTemplate.content, true).querySelector('.conversation-item');
    
    // Set session ID
    sessionItem.dataset.conversationId = session.id;
    
    // Get first few characters of system_prompt or first message as title
    const title = session.system_prompt 
        ? session.system_prompt.substring(0, 30) + (session.system_prompt.length > 30 ? '...' : '')
        : 'Session';
    
    // Format date
    const date = new Date(session.updated_at);
    const formattedDate = date.toLocaleString();
    
    // Set content
    sessionItem.querySelector('.conversation-title').textContent = title;
    sessionItem.querySelector('.conversation-timestamp').textContent = formattedDate;
    
    // Add click event
    sessionItem.addEventListener('click', () => loadSession(session.id));
    
    // Add to list
    sessionList.appendChild(sessionItem);
    
    // Mark as active if it's the current session
    if (session.id === currentSessionId) {
        sessionItem.classList.add('active');
    }
}

// Load a specific session
async function loadSession(sessionId) {
    try {
        // Show loading state
        clearChatMessages();
        addTypingIndicator();
        
        const response = await fetch(`/api/sessions/${sessionId}`);
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        
        const messages = await response.json();
        
        // Update current session ID
        currentSessionId = sessionId;
        
        // Show delete button
        sessionActions.style.display = 'block';
        
        // Update active session in list
        updateActiveSession(sessionId);
        
        // Remove typing indicator
        removeTypingIndicator();
        
        // Display messages
        if (messages.length === 0) {
            showWelcomeMessage();
        } else {
            messages.forEach(msg => {
                addMessage(msg.role, msg.content);
            });
        }
        
    } catch (error) {
        console.error('Error loading session:', error);
        removeTypingIndicator();
        showErrorMessage('Failed to load session. Please try again.');
    }
}

// Delete the current session
async function deleteCurrentSession() {
    if (!currentSessionId) return;
    
    if (!confirm('Are you sure you want to delete this session? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/sessions/${currentSessionId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        
        // Create a new session
        createNewSession();
        
        // Reload sessions
        await loadSessions();
        
    } catch (error) {
        console.error('Error deleting session:', error);
        showErrorMessage('Failed to delete session. Please try again.');
    }
}

// Update the active session in the UI
function updateActiveSession(sessionId) {
    // Remove active class from all session items
    document.querySelectorAll('.conversation-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Add active class to current session item
    if (sessionId) {
        const sessionItem = document.querySelector(`.conversation-item[data-conversation-id="${sessionId}"]`);
        if (sessionItem) {
            sessionItem.classList.add('active');
        }
    }
}

// Add a message to the UI
function addMessage(role, content) {
    // Clone the template
    const messageElement = document.importNode(messageTemplate.content, true).querySelector('.message');
    
    // Add role class
    messageElement.classList.add(role);
    
    // Set content
    messageElement.querySelector('p').textContent = content;
    
    // Add to chat
    chatMessages.appendChild(messageElement);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Show typing indicator
function addTypingIndicator() {
    const indicatorDiv = document.createElement('div');
    indicatorDiv.classList.add('message', 'assistant', 'typing-indicator');
    indicatorDiv.id = 'typing-indicator';
    
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('span');
        dot.classList.add('typing-dot');
        indicatorDiv.appendChild(dot);
    }
    
    chatMessages.appendChild(indicatorDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Remove typing indicator
function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// Clear all chat messages
function clearChatMessages() {
    while (chatMessages.firstChild) {
        chatMessages.removeChild(chatMessages.firstChild);
    }
}

// Show welcome message
function showWelcomeMessage() {
    const welcomeDiv = document.createElement('div');
    welcomeDiv.classList.add('welcome-message');
    welcomeDiv.innerHTML = `
        <h2>Welcome to AI Agent Chatbot!</h2>
        <p>Ask me anything or select a previous conversation from the sidebar.</p>
    `;
    chatMessages.appendChild(welcomeDiv);
}

// Show error message
function showErrorMessage(message) {
    const errorDiv = document.createElement('div');
    errorDiv.classList.add('message', 'system');
    
    const errorContent = document.createElement('div');
    errorContent.classList.add('message-content');
    
    const errorText = document.createElement('p');
    errorText.textContent = message;
    
    errorContent.appendChild(errorText);
    errorDiv.appendChild(errorContent);
    chatMessages.appendChild(errorDiv);
    
    chatMessages.scrollTop = chatMessages.scrollHeight;
}