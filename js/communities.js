// Communities Module
// Handles community listing, join/leave, and real-time chat via WebSocket

class Communities {
    constructor() {
        this.communities = [];
        this.activeCommunity = null;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // Start with 1 second
    }

    // Load and render communities
    async loadCommunities() {
        const container = document.getElementById('communities-list');
        if (!container) return;

        UI.showLoading(container, 'Loading communities...');

        const result = await API.getCommunities();

        if (!result.success) {
            UI.showError(container, result.error || 'Failed to load communities');
            return;
        }

        this.communities = result.data.communities || [];

        if (this.communities.length === 0) {
            UI.showEmpty(container, 'No communities available', '🏘️');
            return;
        }

        this.renderCommunities(container);
    }

    // Render community list
    renderCommunities(container) {
        container.innerHTML = '';

        this.communities.forEach(community => {
            const card = document.createElement('div');
            card.className = 'card community-card';
            card.style.cssText = 'margin-bottom: 15px; cursor: pointer;';

            const header = document.createElement('div');
            header.style.cssText = 'display: flex; justify-content: space-between; align-items: start;';

            const info = document.createElement('div');
            info.style.flex = '1';

            const name = document.createElement('h3');
            name.textContent = community.name;
            name.style.margin = '0 0 8px 0';

            const desc = document.createElement('p');
            desc.textContent = community.description;
            desc.style.cssText = 'margin: 0 0 10px 0; color: #666; font-size: 14px;';

            const meta = document.createElement('div');
            meta.style.cssText = 'font-size: 12px; color: #999;';
            meta.innerHTML = `<span>👥 ${community.member_count} members</span>`;

            info.appendChild(name);
            info.appendChild(desc);
            info.appendChild(meta);

            const actions = document.createElement('div');
            actions.style.cssText = 'display: flex; flex-direction: column; gap: 8px;';

            if (community.is_member) {
                const chatBtn = document.createElement('button');
                chatBtn.className = 'btn btn-blue';
                chatBtn.textContent = '💬 Chat';
                chatBtn.style.cssText = 'padding: 8px 16px; font-size: 14px;';
                chatBtn.onclick = (e) => {
                    e.stopPropagation();
                    this.openChat(community);
                };

                const leaveBtn = document.createElement('button');
                leaveBtn.className = 'btn btn-red';
                leaveBtn.textContent = 'Leave';
                leaveBtn.style.cssText = 'padding: 8px 16px; font-size: 14px;';
                leaveBtn.onclick = (e) => {
                    e.stopPropagation();
                    this.leaveCommunity(community.id, card);
                };

                actions.appendChild(chatBtn);
                actions.appendChild(leaveBtn);
            } else {
                const joinBtn = document.createElement('button');
                joinBtn.className = 'btn btn-green';
                joinBtn.textContent = 'Join';
                joinBtn.style.cssText = 'padding: 8px 16px;';
                joinBtn.onclick = (e) => {
                    e.stopPropagation();
                    this.joinCommunity(community.id, card);
                };

                actions.appendChild(joinBtn);
            }

            header.appendChild(info);
            header.appendChild(actions);
            card.appendChild(header);
            container.appendChild(card);
        });
    }

    // Join community
    async joinCommunity(communityId, cardElement) {
        const btn = cardElement.querySelector('.btn-green');
        const originalText = UI.disableButton(btn, 'Joining...');

        const result = await API.joinCommunity(communityId);

        if (result.success) {
            UI.showToast('Joined community successfully!', 'success');
            await this.loadCommunities(); // Reload to update status
        } else {
            UI.showToast(result.error || 'Failed to join community', 'error');
            UI.enableButton(btn, originalText);
        }
    }

    // Leave community
    async leaveCommunity(communityId, cardElement) {
        if (!UI.confirm('Are you sure you want to leave this community?')) {
            return;
        }

        const btn = cardElement.querySelector('.btn-red');
        const originalText = UI.disableButton(btn, 'Leaving...');

        const result = await API.leaveCommunity(communityId);

        if (result.success) {
            UI.showToast('Left community successfully', 'success');
            await this.loadCommunities(); // Reload to update status
        } else {
            UI.showToast(result.error || 'Failed to leave community', 'error');
            UI.enableButton(btn, originalText);
        }
    }

    // Open chat for a community
    async openChat(community) {
        this.activeCommunity = community;

        // Show chat panel
        const chatPanel = document.getElementById('chat-panel');
        const chatOverlay = document.getElementById('chat-overlay');

        if (!chatPanel || !chatOverlay) {
            console.error('Chat panel elements not found');
            return;
        }

        // Set community name
        document.getElementById('chat-community-name').textContent = community.name;

        // Show panel
        chatOverlay.style.display = 'block';
        chatPanel.style.display = 'block';

        // Load messages
        await this.loadMessages(community.id);

        // Connect WebSocket
        this.connectWebSocket(community.id);

        // Focus on input
        setTimeout(() => {
            document.getElementById('chat-input').focus();
        }, 100);
    }

    // Close chat
    closeChat() {
        const chatPanel = document.getElementById('chat-panel');
        const chatOverlay = document.getElementById('chat-overlay');

        if (chatPanel) chatPanel.style.display = 'none';
        if (chatOverlay) chatOverlay.style.display = 'none';

        // Disconnect WebSocket
        this.disconnectWebSocket();

        this.activeCommunity = null;
    }

    // Load chat messages
    async loadMessages(communityId) {
        const messagesContainer = document.getElementById('chat-messages');
        UI.showLoading(messagesContainer, 'Loading messages...');

        const result = await API.getCommunityMessages(communityId);

        if (!result.success) {
            UI.showError(messagesContainer, result.error || 'Failed to load messages');
            return;
        }

        const messages = result.data.messages || [];

        if (messages.length === 0) {
            UI.showEmpty(messagesContainer, 'No messages yet. Start the conversation!', '💬');
            return;
        }

        this.renderMessages(messages);
    }

    // Render messages
    renderMessages(messages) {
        const container = document.getElementById('chat-messages');
        container.innerHTML = '';

        const currentUser = Auth.getUserData();

        messages.forEach(msg => {
            const msgDiv = document.createElement('div');
            msgDiv.className = 'chat-message';

            const isOwnMessage = msg.user_id === currentUser?.user_id;
            msgDiv.classList.add(isOwnMessage ? 'chat-message-own' : 'chat-message-other');

            const header = document.createElement('div');
            header.className = 'chat-message-header';

            const username = document.createElement('strong');
            username.textContent = msg.username;

            const time = document.createElement('span');
            time.className = 'chat-message-time';
            time.textContent = UI.formatTime(msg.created_at);

            header.appendChild(username);
            header.appendChild(time);

            const content = document.createElement('div');
            content.className = 'chat-message-content';
            content.textContent = msg.message; // Safe rendering via textContent

            msgDiv.appendChild(header);
            msgDiv.appendChild(content);
            container.appendChild(msgDiv);
        });

        // Scroll to bottom
        container.scrollTop = container.scrollHeight;
    }

    // Connect WebSocket
    connectWebSocket(communityId) {
        const token = Auth.getToken();
        if (!token) {
            UI.showToast('Authentication required', 'error');
            return;
        }

        // Close existing connection
        this.disconnectWebSocket();

        // Update connection status
        this.updateConnectionStatus('connecting');

        // Connect to WebSocket
        const wsUrl = `ws://localhost:8888/api/communities/${communityId}/ws`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.updateConnectionStatus('connected');
            this.reconnectAttempts = 0;
            this.reconnectDelay = 1000;
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateConnectionStatus('error');
        };

        this.ws.onclose = () => {
            console.log('WebSocket closed');
            this.updateConnectionStatus('disconnected');
            this.ws = null;

            // Attempt reconnect if chat is still open
            if (this.activeCommunity && this.reconnectAttempts < this.maxReconnectAttempts) {
                this.reconnectAttempts++;
                console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);

                setTimeout(() => {
                    if (this.activeCommunity) {
                        this.connectWebSocket(communityId);
                    }
                }, this.reconnectDelay);

                // Exponential backoff
                this.reconnectDelay *= 2;
            }
        };
    }

    // Disconnect WebSocket
    disconnectWebSocket() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    // Handle WebSocket messages
    handleWebSocketMessage(data) {
        if (data.type === 'message') {
            // Add new message to chat
            this.addMessageToChat(data);
        } else if (data.type === 'error') {
            UI.showToast(data.message || 'Chat error', 'error');
        } else if (data.type === 'auth_success') {
            console.log('WebSocket authentication successful');
        }
    }

    // Add message to chat
    addMessageToChat(message) {
        const container = document.getElementById('chat-messages');

        // Clear empty state if present
        if (container.querySelector('.empty-state')) {
            container.innerHTML = '';
        }

        const currentUser = Auth.getUserData();
        const isOwnMessage = message.user_id === currentUser?.user_id;

        const msgDiv = document.createElement('div');
        msgDiv.className = `chat-message ${isOwnMessage ? 'chat-message-own' : 'chat-message-other'}`;

        const header = document.createElement('div');
        header.className = 'chat-message-header';

        const username = document.createElement('strong');
        username.textContent = message.username;

        const time = document.createElement('span');
        time.className = 'chat-message-time';
        time.textContent = UI.formatTime(message.created_at || new Date().toISOString());

        header.appendChild(username);
        header.appendChild(time);

        const content = document.createElement('div');
        content.className = 'chat-message-content';
        content.textContent = message.message; // Safe rendering

        msgDiv.appendChild(header);
        msgDiv.appendChild(content);
        container.appendChild(msgDiv);

        // Scroll to bottom
        container.scrollTop = container.scrollHeight;
    }

    // Send message
    sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();

        if (!message) return;

        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            UI.showToast('Not connected to chat', 'error');
            return;
        }

        const userData = Auth.getUserData();
        if (!userData || !userData.user_id) {
            UI.showToast('Authentication error', 'error');
            return;
        }

        // Send message via WebSocket (backend expects user_id and message)
        this.ws.send(JSON.stringify({
            user_id: userData.user_id,
            message: message
        }));

        // Clear input
        input.value = '';
    }

    // Update connection status
    updateConnectionStatus(status) {
        const statusEl = document.getElementById('chat-status');
        if (!statusEl) return;

        const statusText = {
            'connecting': '🔄 Connecting...',
            'connected': '✅ Connected',
            'disconnected': '⚠️ Disconnected',
            'error': '❌ Connection error'
        };

        statusEl.textContent = statusText[status] || '';
        statusEl.className = `chat-status status-${status}`;
    }
}

// Initialize on page load
let communitiesManager;

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('communities-list')) {
        communitiesManager = new Communities();
        communitiesManager.loadCommunities();

        // Set up chat panel close button
        const closeBtn = document.getElementById('chat-close');
        if (closeBtn) {
            closeBtn.onclick = () => communitiesManager.closeChat();
        }

        // Set up chat overlay click
        const overlay = document.getElementById('chat-overlay');
        if (overlay) {
            overlay.onclick = () => communitiesManager.closeChat();
        }

        // Set up send button
        const sendBtn = document.getElementById('chat-send');
        if (sendBtn) {
            sendBtn.onclick = () => communitiesManager.sendMessage();
        }

        // Set up Enter key to send
        const input = document.getElementById('chat-input');
        if (input) {
            input.onkeypress = (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    communitiesManager.sendMessage();
                }
            };
        }
    }
});

// Export to global scope
window.Communities = Communities;
window.communitiesManager = communitiesManager;
