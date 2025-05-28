// Global state
let currentConversationId = null;
let conversations = [];

// DOM Elements
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatMessages = document.getElementById('chat-messages');
const conversationList = document.getElementById('conversation-list');
const newConversationBtn = document.getElementById('new-conversation-btn');
const deleteConversationBtn = document.getElementById('delete-conversation-btn');
const conversationActions = document.getElementById('conversation-actions');

// Templates
const conversationItemTemplate = document.getElementById('conversation-item-template');
const messageTemplate = document.getElementById('message-template');

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    // Focus on input field
    userInput.focus();
    
    // Load conversations
    loadConversations();
    
    // Add event listeners
    setupEventListeners();
});

// Set up event listeners
function setupEventListeners() {
    // New conversation button
    newConversationBtn.addEventListener('click', createNewConversation);
    
    // Delete conversation button
    deleteConversationBtn.addEventListener('click', deleteCurrentConversation);
    
    // Chat form submission
    chatForm.addEventListener('submit', handleChatFormSubmit);
}

// Create a new conversation
async function createNewConversation() {
    try {
        // Clear current conversation UI
        clearChatMessages();
        showWelcomeMessage();
        
        // Reset current conversation ID
        currentConversationId = null;
        
        // Update UI to reflect new conversation
        updateActiveConversation(null);
        conversationActions.style.display = 'none';
        
        // Focus on input
        userInput.focus();
        
    } catch (error) {
        console.error('Error creating new conversation:', error);
        showErrorMessage('Failed to create a new conversation. Please try again.');
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
                conversation_id: currentConversationId
            })
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Update conversation ID if this is a new conversation
        if (!currentConversationId) {
            currentConversationId = data.conversation_id;
            conversationActions.style.display = 'block';
            
            // Reload conversations to include the new one
            await loadConversations();
            
            // Update the active conversation
            updateActiveConversation(currentConversationId);
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

// Load all conversations
async function loadConversations() {
    try {
        const response = await fetch('/api/conversations');
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        
        conversations = await response.json();
        
        // Clear conversation list
        while (conversationList.firstChild) {
            conversationList.removeChild(conversationList.firstChild);
        }
        
        if (conversations.length === 0) {
            // Show empty state
            const emptyState = document.createElement('div');
            emptyState.classList.add('empty-state-message');
            emptyState.innerHTML = `
                <p>No conversations yet.</p>
                <p>Start a new conversation!</p>
            `;
            conversationList.appendChild(emptyState);
        } else {
            // Add conversations to list
            conversations.forEach(conversation => {
                addConversationToList(conversation);
            });
        }
        
    } catch (error) {
        console.error('Error loading conversations:', error);
        showErrorMessage('Failed to load conversations. Please refresh the page.');
    }
}

// Add a conversation to the list
function addConversationToList(conversation) {
    // Clone the template
    const conversationItem = document.importNode(conversationItemTemplate.content, true).querySelector('.conversation-item');
    
    // Set conversation ID
    conversationItem.dataset.conversationId = conversation.id;
    
    // Get first few characters of system_prompt or first message as title
    const title = conversation.system_prompt 
        ? conversation.system_prompt.substring(0, 30) + (conversation.system_prompt.length > 30 ? '...' : '')
        : 'Conversation';
    
    // Format date
    const date = new Date(conversation.updated_at);
    const formattedDate = date.toLocaleString();
    
    // Set content
    conversationItem.querySelector('.conversation-title').textContent = title;
    conversationItem.querySelector('.conversation-timestamp').textContent = formattedDate;
    
    // Add click event
    conversationItem.addEventListener('click', () => loadConversation(conversation.id));
    
    // Add to list
    conversationList.appendChild(conversationItem);
    
    // Mark as active if it's the current conversation
    if (conversation.id === currentConversationId) {
        conversationItem.classList.add('active');
    }
}

// Load a specific conversation
async function loadConversation(conversationId) {
    try {
        // Show loading state
        clearChatMessages();
        addTypingIndicator();
        
        const response = await fetch(`/api/conversations/${conversationId}`);
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        
        const messages = await response.json();
        
        // Update current conversation ID
        currentConversationId = conversationId;
        
        // Show delete button
        conversationActions.style.display = 'block';
        
        // Update active conversation in list
        updateActiveConversation(conversationId);
        
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
        console.error('Error loading conversation:', error);
        removeTypingIndicator();
        showErrorMessage('Failed to load conversation. Please try again.');
    }
}

// Delete the current conversation
async function deleteCurrentConversation() {
    if (!currentConversationId) return;
    
    if (!confirm('Are you sure you want to delete this conversation? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/conversations/${currentConversationId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        
        // Create a new conversation
        createNewConversation();
        
        // Reload conversations
        await loadConversations();
        
    } catch (error) {
        console.error('Error deleting conversation:', error);
        showErrorMessage('Failed to delete conversation. Please try again.');
    }
}

// Update the active conversation in the UI
function updateActiveConversation(conversationId) {
    // Remove active class from all conversation items
    document.querySelectorAll('.conversation-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Add active class to current conversation item
    if (conversationId) {
        const conversationItem = document.querySelector(`.conversation-item[data-conversation-id="${conversationId}"]`);
        if (conversationItem) {
            conversationItem.classList.add('active');
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