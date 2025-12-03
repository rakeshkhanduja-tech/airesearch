document.addEventListener('DOMContentLoaded', () => {
    const messagesContainer = document.getElementById('messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const modelCountSpan = document.getElementById('model-count');
    
    // Modal elements
    const modal = document.getElementById('knowledge-modal');
    const addKnowledgeBtn = document.getElementById('add-knowledge-btn');
    const closeBtn = document.getElementsByClassName('close')[0];
    const saveKnowledgeBtn = document.getElementById('save-knowledge-btn');
    const knowledgeInput = document.getElementById('knowledge-input');

    // Load initial config
    fetch('/api/config')
        .then(res => res.json())
        .then(data => {
            modelCountSpan.textContent = data.llms.length;
        });

    function addMessage(text, sender, metadata = null) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'content';
        contentDiv.textContent = text;
        msgDiv.appendChild(contentDiv);

        if (metadata) {
            const metaDiv = document.createElement('div');
            metaDiv.className = 'metadata';
            
            if (metadata.source) {
                const sourceTag = document.createElement('span');
                sourceTag.className = 'tag';
                sourceTag.textContent = `Source: ${metadata.source}`;
                metaDiv.appendChild(sourceTag);
            }
            
            if (metadata.cost_saved !== undefined && metadata.cost_saved > 0) {
                const costTag = document.createElement('span');
                costTag.className = 'tag';
                costTag.style.color = 'green';
                costTag.textContent = `Saved: $${metadata.cost_saved.toFixed(6)}`;
                metaDiv.appendChild(costTag);
            } else if (metadata.cost !== undefined) {
                 const costTag = document.createElement('span');
                costTag.className = 'tag';
                costTag.textContent = `Cost: $${metadata.cost.toFixed(6)}`;
                metaDiv.appendChild(costTag);
            }

            if (metadata.categories) {
                const catTag = document.createElement('span');
                catTag.className = 'tag';
                catTag.textContent = `Cats: ${metadata.categories.join(', ')}`;
                metaDiv.appendChild(catTag);
            }

            msgDiv.appendChild(metaDiv);
        }

        messagesContainer.appendChild(msgDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        addMessage(text, 'user');
        userInput.value = '';

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            
            const data = await response.json();
            addMessage(data.text, 'bot', data);
        } catch (error) {
            addMessage('Error communicating with server.', 'system');
            console.error(error);
        }
    }

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Modal Logic
    addKnowledgeBtn.onclick = () => modal.style.display = "block";
    closeBtn.onclick = () => modal.style.display = "none";
    window.onclick = (event) => {
        if (event.target == modal) modal.style.display = "none";
    }

    saveKnowledgeBtn.onclick = async () => {
        const text = knowledgeInput.value.trim();
        if (!text) return;

        try {
            await fetch('/api/knowledge', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            alert('Knowledge added successfully!');
            knowledgeInput.value = '';
            modal.style.display = "none";
        } catch (error) {
            alert('Failed to add knowledge');
            console.error(error);
        }
    }
});
