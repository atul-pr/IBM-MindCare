// ==========================================
// MINDCARE - ENHANCED SCRIPT
// ==========================================

// Handle Enter key press
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault(); // Prevent new line
        sendMessage();
        return false;
    }
}

// Auto-resize textarea
function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

// Send message function
function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();

    if (message === '') {
        return; // Don't send empty messages
    }

    // Add user message to chat
    addUserMessage(message);

    // Clear input
    input.value = '';
    input.style.height = 'auto';

    // Show typing indicator
    showTypingIndicator();

    // Send to backend API
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: message })
    })
        .then(response => response.json())
        .then(data => {
            hideTypingIndicator();

            // Check for crisis
            if (data.crisis) {
                showCrisis(data.response);
            }

            // Add bot response
            addBotMessage(data.response);
            scrollToBottom();
        })
        .catch(error => {
            console.error('Error sending message:', error);
            hideTypingIndicator();
            addBotMessage("I'm having trouble connecting right now. Please try again or reach out to Kiran helpline: 1800-599-0019");
            scrollToBottom();
        });
}

// Add user message to chat
function addUserMessage(text) {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message fade-in';

    messageDiv.innerHTML = `
        <div class="message-wrapper">
            <div class="message-content">
                <p>${escapeHtml(text)}</p>
            </div>
            <div class="timestamp">${getCurrentTime()}</div>
        </div>
        <div class="message-avatar">
            <i class="fas fa-user"></i>
        </div>
    `;

    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Add bot message to chat
function addBotMessage(text) {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message fade-in';

    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-user-nurse"></i>
        </div>
        <div class="message-wrapper">
            <div class="message-content">
                <p>${text}</p>
            </div>
            <div class="timestamp">${getCurrentTime()}</div>
        </div>
    `;

    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Show typing indicator
function showTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    indicator.style.display = 'flex';
    scrollToBottom();
}

// Hide typing indicator
function hideTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    indicator.style.display = 'none';
}

// Get current time
function getCurrentTime() {
    const now = new Date();
    let hours = now.getHours();
    let minutes = now.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';

    hours = hours % 12;
    hours = hours ? hours : 12;
    minutes = minutes < 10 ? '0' + minutes : minutes;

    return hours + ':' + minutes + ' ' + ampm;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Smooth scroll to bottom
function scrollToBottom() {
    const chatContainer = document.getElementById('chatContainer');
    setTimeout(() => {
        chatContainer.scrollTo({
            top: chatContainer.scrollHeight,
            behavior: 'smooth'
        });
    }, 100);
}

// Quick message sender
function sendQuickMessage(message) {
    document.getElementById('messageInput').value = message;
    sendMessage();
}

// ==========================================
// MOOD TRACKER
// ==========================================

let moodHistory = [];

function showMoodTracker() {
    const modal = document.getElementById('moodModal');
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
    displayMoodHistory();
}

function closeMoodTracker() {
    const modal = document.getElementById('moodModal');
    modal.classList.remove('show');
    document.body.style.overflow = 'auto';
}

function logMood(rating) {
    const moodLabels = {
        1: { emoji: '😢', label: 'Very Bad', color: '#f56565' },
        2: { emoji: '😔', label: 'Bad', color: '#ed8936' },
        3: { emoji: '😐', label: 'Okay', color: '#718096' },
        4: { emoji: '🙂', label: 'Good', color: '#48bb78' },
        5: { emoji: '😊', label: 'Very Good', color: '#667eea' }
    };

    const mood = {
        rating: rating,
        ...moodLabels[rating],
        timestamp: new Date().toLocaleString()
    };

    // Send to backend API
    fetch('/mood', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ mood: rating })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update local storage
                moodHistory.unshift(mood);
                if (moodHistory.length > 7) {
                    moodHistory = moodHistory.slice(0, 7);
                }
                localStorage.setItem('moodHistory', JSON.stringify(moodHistory));

                // Display updated history
                displayMoodHistory();

                // Show confirmation
                showMoodConfirmation(mood);

                // Close modal after 2 seconds
                setTimeout(() => {
                    closeMoodTracker();
                }, 2000);
            }
        })
        .catch(error => {
            console.error('Error logging mood:', error);
            alert('Failed to log mood. Please try again.');
        });
}

function displayMoodHistory() {
    const historyContent = document.getElementById('moodHistoryContent');

    // Load from localStorage
    const saved = localStorage.getItem('moodHistory');
    if (saved) {
        moodHistory = JSON.parse(saved);
    }

    if (moodHistory.length === 0) {
        historyContent.innerHTML = '<p style="text-align: center; color: #718096;">No mood entries yet. Start tracking!</p>';
        return;
    }

    let html = '<div style="display: flex; flex-direction: column; gap: 12px;">';

    moodHistory.forEach(mood => {
        html += `
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 15px; background: white; border-radius: 12px; border-left: 4px solid ${mood.color};">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 28px;">${mood.emoji}</span>
                    <div>
                        <div style="font-weight: 600; color: #2d3748;">${mood.label}</div>
                        <div style="font-size: 12px; color: #718096;">${mood.timestamp}</div>
                    </div>
                </div>
            </div>
        `;
    });

    html += '</div>';
    historyContent.innerHTML = html;
}

function showMoodConfirmation(mood) {
    const chatContainer = document.getElementById('chatContainer');
    const confirmDiv = document.createElement('div');
    confirmDiv.className = 'message bot-message fade-in';

    confirmDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-user-nurse"></i>
        </div>
        <div class="message-wrapper">
            <div class="message-content">
                <p>Thank you for tracking your mood! ${mood.emoji}</p>
                <p>You're feeling <strong>${mood.label}</strong> today. I'm here if you want to talk about it.</p>
            </div>
            <div class="timestamp">${getCurrentTime()}</div>
        </div>
    `;

    chatContainer.appendChild(confirmDiv);
    scrollToBottom();
}

// ==========================================
// RESOURCES MODAL
// ==========================================

function showResources() {
    const modal = document.getElementById('resourcesModal');
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
}

function closeResources() {
    const modal = document.getElementById('resourcesModal');
    modal.classList.remove('show');
    document.body.style.overflow = 'auto';
}

// ==========================================
// CRISIS MODAL
// ==========================================

function showCrisis(message) {
    const modal = document.getElementById('crisisModal');
    const messageDiv = document.getElementById('crisisMessage');

    messageDiv.innerHTML = message;
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeCrisis() {
    const modal = document.getElementById('crisisModal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

function callHotline() {
    // US Suicide & Crisis Lifeline
    window.location.href = 'tel:988';
}

// ==========================================
// OPTIONS MENU
// ==========================================

function showOptions() {
    const options = [
        'Share Resources',
        'Breathing Exercise',
        'Positive Affirmations',
        'Guided Meditation'
    ];

    // Create options menu (you can enhance this)
    alert('Options:\n\n' + options.join('\n'));
}

// ==========================================
// INITIALIZE
// ==========================================

document.addEventListener('DOMContentLoaded', function () {
    // Focus on input
    const input = document.getElementById('messageInput');
    input.focus();

    // Load mood history
    displayMoodHistory();

    // Add welcome message animation
    setTimeout(() => {
        const quickActions = document.getElementById('quickActions');
        if (quickActions) {
            quickActions.style.animation = 'fadeIn 0.5s ease-out';
        }
    }, 500);
});

// ==========================================
// EXAMPLE: Detect crisis keywords
// ==========================================

function checkForCrisisKeywords(message) {
    const crisisKeywords = ['suicide', 'kill myself', 'end my life', 'want to die', 'hurt myself'];
    const lowerMessage = message.toLowerCase();

    for (let keyword of crisisKeywords) {
        if (lowerMessage.includes(keyword)) {
            showCrisis(`
                <p style="font-size: 18px; margin-bottom: 20px;">
                    I'm really concerned about what you've shared. Your safety is the top priority.
                </p>
                <p style="font-size: 16px; margin-bottom: 15px;">
                    <strong>National Suicide Prevention Lifeline:</strong><br>
                    Call or text <strong>988</strong> (Available 24/7)
                </p>
                <p style="font-size: 16px; margin-bottom: 15px;">
                    <strong>Crisis Text Line:</strong><br>
                    Text <strong>HELLO</strong> to <strong>741741</strong>
                </p>
                <p style="font-size: 14px; color: #718096;">
                    You don't have to face this alone. Please reach out to one of these services right now.
                </p>
            `);
            return true;
        }
    }
    return false;
}