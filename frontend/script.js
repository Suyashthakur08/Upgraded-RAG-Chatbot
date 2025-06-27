// frontend/script.js

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const pdfUploader = document.getElementById('pdf-uploader');
    const uploadButton = document.getElementById('upload-button');
    const uploadStatus = document.getElementById('upload-status');
    const chatMessages = document.getElementById('chat-messages');
    const messageInput = document.getElementById('message-input');
    
    // State
    let sessionId = null;

    // Event Listeners
    uploadButton.addEventListener('click', handleFileUpload);
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    async function handleFileUpload() {
        const files = pdfUploader.files;
        if (files.length === 0) {
            updateStatus('Please select at least one PDF file.', 'red');
            return;
        }

        // A new upload always means a new session. Reset the state.
        sessionId = null; 
        sessionStorage.removeItem('sessionId');
        disableChat();

        const formData = new FormData();
        for (const file of files) {
            formData.append('files', file);
        }

        updateStatus('Uploading and processing...', 'orange');
        uploadButton.disabled = true;
        chatMessages.innerHTML = ''; // Clear chat on new upload
        addMessage('bot', 'Processing your documents. This might take a moment...');

        try {
            // Corrected fetch call - no session_id sent
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData,
            });
            
            const data = await response.json();

            if (!response.ok) throw new Error(data.detail);

            // The backend provides the new session ID. We save it.
            sessionId = data.session_id;
            sessionStorage.setItem('sessionId', sessionId);
            
            updateStatus(`Success! Ready to chat.`, 'green');
            updateMessage(chatMessages.lastChild, data.answer); // Update "Processing..." to "Success!" message
            enableChat();

        } catch (error) {
            updateStatus(`Error: ${error.message}`, 'red');
            updateMessage(chatMessages.lastChild, `Error processing documents: ${error.message}`);
        } finally {
            uploadButton.disabled = false;
        }
    }

    async function sendMessage() {
        const query = messageInput.value.trim();
        if (!query || !sessionId) return;

        addMessage('user', query);
        messageInput.value = '';
        messageInput.disabled = true;
        const typingIndicator = addMessage('bot', '...');

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, session_id: sessionId }),
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail);
            
            updateMessage(typingIndicator, data.answer);

        } catch (error) {
            updateMessage(typingIndicator, `Error: ${error.message}`);
        } finally {
            messageInput.disabled = false;
            messageInput.focus();
        }
    }

    function addMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = marked.parse(text); // Use marked.js for markdown rendering
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return messageDiv; // Return the element to allow updating it (for the typing indicator)
    }

    function updateMessage(element, newText) {
        const contentDiv = element.querySelector('.message-content');
        contentDiv.innerHTML = marked.parse(newText);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function updateStatus(message, color) {
        uploadStatus.textContent = message;
        uploadStatus.style.color = color;
    }

    function enableChat() {
        messageInput.disabled = false;
        messageInput.placeholder = 'Ask a question about your documents...';
        messageInput.focus();
    }

    function disableChat() {
        messageInput.disabled = true;
        messageInput.placeholder = 'First, upload documents...';
    }
});