document.addEventListener("DOMContentLoaded", () => {
    const toggleBtn = document.getElementById("chatbot-toggle-btn");
    const widget = document.getElementById("chatbot-widget");
    const closeBtn = document.getElementById("chatbot-close-btn");
    const messagesContainer = document.getElementById("chatbot-messages");
    const inputField = document.getElementById("chatbot-input-field");
    const sendBtn = document.getElementById("chatbot-send-btn");
    
    let conversationHistory = [];

    // Toggle widget
    toggleBtn.addEventListener("click", () => {
        widget.classList.toggle("active");
        if (widget.classList.contains("active")) {
            inputField.focus();
            scrollToBottom();
        }
    });

    closeBtn.addEventListener("click", () => {
        widget.classList.remove("active");
    });

    // Send message
    sendBtn.addEventListener("click", sendMessage);
    inputField.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });

    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function addMessage(text, sender) {
        const msgDiv = document.createElement("div");
        msgDiv.className = `message ${sender}-message`;
        msgDiv.innerText = text;
        messagesContainer.appendChild(msgDiv);
        scrollToBottom();
    }

    function addTypingIndicator() {
        const msgDiv = document.createElement("div");
        msgDiv.className = "message typing-indicator";
        msgDiv.id = "chatbot-typing";
        msgDiv.innerText = "Typing...";
        messagesContainer.appendChild(msgDiv);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        const typing = document.getElementById("chatbot-typing");
        if (typing) typing.remove();
    }

    async function sendMessage() {
        const text = inputField.value.trim();
        if (!text) return;

        // Add user message to UI
        addMessage(text, "user");
        inputField.value = "";
        
        // Disable input while waiting
        inputField.disabled = true;
        sendBtn.disabled = true;
        
        addTypingIndicator();

        try {
            const response = await fetch('/chatbot/message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: text,
                    history: conversationHistory
                })
            });

            removeTypingIndicator();

            if (!response.ok) {
                throw new Error("API Error");
            }

            const data = await response.json();
            
            // Add bot reply to UI
            addMessage(data.reply, "bot");

            // Update history
            conversationHistory.push({"role": "user", "content": text});
            conversationHistory.push({"role": "assistant", "content": data.reply});

            // Keep history length manageable
            if (conversationHistory.length > 20) {
                conversationHistory = conversationHistory.slice(-20);
            }

        } catch (error) {
            removeTypingIndicator();
            addMessage("Sorry, I am having trouble connecting. Please try again.", "bot");
            console.error(error);
        } finally {
            inputField.disabled = false;
            sendBtn.disabled = false;
            inputField.focus();
        }
    }
});
