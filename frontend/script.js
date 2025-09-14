// GreenBot Enhanced JavaScript - User-Friendly Chatbot Interface
class GreenBot {
    constructor() {
        this.apiUrl = 'http://localhost:5000';
        this.isConnected = false;
        this.messageCount = 0;
        this.userQuestions = 0;
        this.botResponses = 0;
        this.positiveFeedback = 0;
        this.negativeFeedback = 0;
        this.autoScroll = true;
        this.theme = 'light';
        this.currentConversation = [];
        
        this.init();
    }

    init() {
        console.log('🚀 Initializing GreenBot...');
        this.bindEvents();
        this.checkServerConnection();
        this.loadSettings();
        this.setupAutoResize();
        this.displayWelcomeMessage();
        
        // Test sidebar elements after DOM is loaded
        setTimeout(() => {
            this.testSidebarElements();
        }, 100);
    }

    testSidebarElements() {
        console.log('🧪 Testing sidebar elements...');
        const sidebar = document.getElementById('sidebar');
        const menuToggle = document.getElementById('menuToggle');
        const sidebarClose = document.getElementById('sidebarClose');
        const overlay = document.getElementById('sidebarOverlay');
        
        console.log('📋 Sidebar found:', !!sidebar);
        console.log('📋 Menu toggle found:', !!menuToggle);
        console.log('📋 Sidebar close found:', !!sidebarClose);
        console.log('📋 Overlay found:', !!overlay);
        
        if (sidebar) {
            console.log('📋 Sidebar current classes:', sidebar.className);
            console.log('📋 Sidebar computed style display:', window.getComputedStyle(sidebar).display);
            console.log('📋 Sidebar computed style transform:', window.getComputedStyle(sidebar).transform);
        }
        
        if (menuToggle) {
            console.log('📋 Menu toggle visible:', window.getComputedStyle(menuToggle).display !== 'none');
        }
        
        if (sidebarClose) {
            console.log('📋 Close button visible:', window.getComputedStyle(sidebarClose).display !== 'none');
            console.log('📋 Close button clickable:', !sidebarClose.disabled);
        }
        
        // Test click simulation
        console.log('🧪 Testing click simulation on close button...');
        if (sidebarClose) {
            sidebarClose.click();
        }
    }

    bindEvents() {
        // Input events
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        
        sendButton.addEventListener('click', () => this.sendMessage());
        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        messageInput.addEventListener('input', () => {
            this.updateCharCount();
            this.toggleSendButton();
        });

        // UI events
        const menuToggle = document.getElementById('menuToggle');
        const sidebarClose = document.getElementById('sidebarClose');
        const sidebarOverlay = document.getElementById('sidebarOverlay');
        
        console.log('🔧 Binding UI events...');
        console.log('📋 Menu toggle element:', menuToggle);
        console.log('📋 Sidebar close element:', sidebarClose);
        console.log('📋 Sidebar overlay element:', sidebarOverlay);
        
        if (menuToggle) {
            menuToggle.addEventListener('click', () => {
                console.log('🖱️ Menu toggle clicked!');
                this.toggleSidebar();
            });
        } else {
            console.error('❌ Menu toggle button not found!');
        }
        
        if (sidebarClose) {
            sidebarClose.addEventListener('click', (e) => {
                console.log('🖱️ Sidebar close button clicked!');
                e.preventDefault();
                e.stopPropagation();
                this.closeSidebar();
            });
        } else {
            console.error('❌ Sidebar close button not found!');
        }
        
        if (sidebarOverlay) {
            sidebarOverlay.addEventListener('click', () => {
                console.log('🖱️ Sidebar overlay clicked!');
                this.closeSidebar();
            });
        } else {
            console.error('❌ Sidebar overlay not found!');
        }
        document.getElementById('newChatBtn').addEventListener('click', () => this.newChat());
        document.getElementById('clearChatBtn').addEventListener('click', () => this.clearChat());
        document.getElementById('themeToggle').addEventListener('click', () => this.toggleTheme());

        // Modal events
        document.getElementById('analyticsModal').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) this.closeModal('analyticsModal');
        });
        document.getElementById('settingsModal').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) this.closeModal('settingsModal');
        });
        document.getElementById('analyticsModalClose').addEventListener('click', () => this.closeModal('analyticsModal'));
        document.getElementById('settingsModalClose').addEventListener('click', () => this.closeModal('settingsModal'));

        // Navigation events
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => this.handleNavigation(item));
        });

        // Settings events
        document.querySelectorAll('.theme-option').forEach(option => {
            option.addEventListener('click', () => this.setTheme(option.dataset.theme));
        });
        document.getElementById('autoScrollToggle')?.addEventListener('change', (e) => {
            this.autoScroll = e.target.checked;
            this.saveSettings();
        });

        // Feedback events
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('like-btn')) {
                this.handleFeedback(e.target, 'like');
            } else if (e.target.classList.contains('dislike-btn')) {
                this.handleFeedback(e.target, 'dislike');
            }
        });
    }

    async checkServerConnection() {
        try {
            console.log('🔍 Checking server connection...');
            const response = await fetch(`${this.apiUrl}/health`);
            console.log('📡 Server response status:', response.status);
            
            if (response.ok) {
                const data = await response.json();
                console.log('✅ Server health data:', data);
                this.isConnected = true;
                this.updateConnectionStatus('online', 'Online');
                this.showToast('Connected to GreenBot server', 'success');
            } else {
                throw new Error(`Server responded with status: ${response.status}`);
            }
        } catch (error) {
            console.error('❌ Connection error:', error);
            this.isConnected = false;
            this.updateConnectionStatus('offline', 'Offline');
            this.showToast(`Unable to connect to server: ${error.message}`, 'error');
        }
    }

    updateConnectionStatus(status, text) {
        const statusDot = document.querySelector('.status-dot');
        const statusText = document.querySelector('.status-text');
        
        if (statusDot) {
            statusDot.className = `status-dot w-2 h-2 rounded-full ${status === 'online' ? 'bg-green-500' : 'bg-red-500'}`;
        }
        if (statusText) {
            statusText.textContent = text;
            statusText.className = `status-text font-medium ${status === 'online' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`;
        }
    }

    showToast(message, type = 'info') {
        // Create toast container if it doesn't exist
        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'fixed top-4 right-4 z-50 space-y-2';
            document.body.appendChild(toastContainer);
        }

        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast-notification flex items-center space-x-3 p-4 rounded-lg shadow-lg max-w-sm animate-slide-in-right ${
            type === 'success' ? 'bg-green-50 border border-green-200 text-green-800 dark:bg-green-900/20 dark:border-green-700 dark:text-green-300' :
            type === 'error' ? 'bg-red-50 border border-red-200 text-red-800 dark:bg-red-900/20 dark:border-red-700 dark:text-red-300' :
            'bg-blue-50 border border-blue-200 text-blue-800 dark:bg-blue-900/20 dark:border-blue-700 dark:text-blue-300'
        }`;

        // Toast icon based on type
        const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';

        toast.innerHTML = `
            <div class="flex-shrink-0">
                <span class="text-lg">${icon}</span>
            </div>
            <div class="flex-1 min-w-0">
                <p class="text-sm font-medium">${message}</p>
            </div>
            <button class="toast-close flex-shrink-0 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors duration-200 ml-2" onclick="this.parentElement.remove()">
                <span class="text-lg">×</span>
            </button>
        `;

        toastContainer.appendChild(toast);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentElement) {
                toast.classList.add('animate-slide-out-right');
                setTimeout(() => {
                    if (toast.parentElement) {
                        toast.remove();
                    }
                }, 300);
            }
        }, 5000);
    }

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (!message || !this.isConnected) return;

        // Clear input and disable send button
        messageInput.value = '';
        this.updateCharCount();
        this.toggleSendButton();

        // Add user message
        this.addMessage(message, 'user');
        this.userQuestions++;

        // Show typing indicator
        this.showTypingIndicator();

        try {
            const response = await fetch(`${this.apiUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Hide typing indicator
            this.hideTypingIndicator();

            // Add bot response
            const botMessage = data.answer || data.response || 'Sorry, I couldn\'t generate a response.';
            this.addMessage(botMessage, 'bot', {
                confidence: data.confidence,
                method: data.method,
                source: data.source,
                processing_time: data.processing_time
            });
            
            this.botResponses++;
            this.updateAnalytics();

        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.addMessage('Sorry, I\'m having trouble connecting to the server. Please try again.', 'bot', { isError: true });
            this.showToast('Failed to send message', 'error');
        }
    }

    addMessage(content, type, metadata = {}) {
        const messagesArea = document.getElementById('messagesArea');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type} flex gap-4 mb-8 message-appear`;
        
        // Ensure proper alignment for user messages
        if (type === 'user') {
            messageDiv.classList.add('justify-end');
        }

        const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        let avatarContent = type === 'user' ? '<dotlottie-wc src="https://lottie.host/27a54662-d9a1-4584-8984-c51941f5adcd/qkDHure2A0.lottie" style="width: 80px; height: 80px;" speed="1" autoplay loop></dotlottie-wc>' : '<dotlottie-wc src="https://lottie.host/ff7d4b1f-0c7e-4d5e-9395-88fef6d7c49e/iHjJjm484E.lottie" style="width: 80px; height: 80px;" speed="1" autoplay loop></dotlottie-wc>';
        let avatarClasses = type === 'user' ? 
            'w-12 h-12 rounded-full  flex items-center justify-center flex-shrink-0 shadow-lg border-2 border-white dark:border-gray-700 avatar-lottie' : 
            'w-12 h-12 rounded-full  flex items-center justify-center flex-shrink-0 shadow-lg border-2 border-white dark:border-gray-700 avatar-lottie';
        
        // Enhanced message content with messenger-style theme
        const messageContentClasses = type === 'user' ? 
            'chat-bubble-user bg-primary text-white p-4 rounded-2xl max-w-lg shadow-sm border-0 ml-auto' : 
            'chat-bubble-bot bg-white dark:bg-slate-800 p-4 rounded-2xl max-w-3xl shadow-sm border border-gray-200 dark:border-gray-600';
        
        const messageContent = type === 'bot' ? 
            `<div class="prose prose-sm max-w-none dark:prose-invert">${this.formatMessage(content)}</div>` : 
            this.formatMessage(content);
        
        // Add feedback buttons directly to bot messages
        const feedbackButtons = type === 'bot' && !metadata.isError ? 
            `<div class="feedback-buttons flex space-x-2 mt-3 pt-3 border-t border-gray-100 dark:border-gray-600">
                <button class="feedback-btn like-btn bg-gray-100 hover:bg-green-100 dark:bg-gray-700 dark:hover:bg-green-900/30 border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 px-3 py-2 rounded-full text-sm transition-all duration-200 flex items-center space-x-1 hover:border-green-300 dark:hover:border-green-500" title="This was helpful">
                    <span>👍</span><span class="text-xs font-medium">Helpful</span>
                </button>
                <button class="feedback-btn dislike-btn bg-gray-100 hover:bg-red-100 dark:bg-gray-700 dark:hover:bg-red-900/30 border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 px-3 py-2 rounded-full text-sm transition-all duration-200 flex items-center space-x-1 hover:border-red-300 dark:hover:border-red-500" title="This wasn't helpful">
                    <span>👎</span><span class="text-xs font-medium">Not helpful</span>
                </button>
            </div>` : '';
        
        messageDiv.innerHTML = type === 'user' ?
            `<div class="message-content ${messageContentClasses}">
                ${messageContent}
                ${feedbackButtons}
            </div>
            <div class="message-avatar ${avatarClasses}">${avatarContent}</div>` :
            `<div class="message-avatar ${avatarClasses}">${avatarContent}</div>
            <div class="message-content ${messageContentClasses}">
                ${messageContent}
                ${feedbackButtons}
            </div>`;

        // Add timestamp for all messages
        const timestampDiv = document.createElement('div');
        timestampDiv.className = `message-timestamp text-xs text-gray-500 dark:text-gray-400 mt-1 px-4 ${type === 'user' ? 'text-right' : ''}`;
        timestampDiv.textContent = timestamp;
        messageDiv.appendChild(timestampDiv);

        // Show notification popup for bot messages with metadata
        if (type === 'bot' && metadata.confidence !== undefined && !metadata.isError) {
            this.showMetadataNotification(metadata);
        }

        messagesArea.appendChild(messageDiv);
        
        // Animate message appearance for all messages
        setTimeout(() => messageDiv.classList.add('appear'), 50);
        
        // Auto-scroll
        if (this.autoScroll) {
            this.scrollToBottom();
        }

        // Store in conversation history
        this.currentConversation.push({ type, content, timestamp, metadata });
        this.messageCount++;
    }

    formatMessage(content) {
        // Enhanced formatting for better user experience
        
        // Format code blocks with better styling
        content = content.replace(/```(\w+)?\n([\s\S]*?)```/g, 
            '<div class="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg my-3 overflow-x-auto border border-gray-200 dark:border-gray-600"><pre class="text-sm font-mono text-gray-800 dark:text-gray-200"><code>$2</code></pre></div>');
        
        // Format inline code with better styling
        content = content.replace(/`([^`]+)`/g, 
            '<code class="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded text-sm font-mono text-gray-800 dark:text-gray-200 border border-gray-200 dark:border-gray-600">$1</code>');
        
        // Format links with better styling
        content = content.replace(
            /(https?:\/\/[^\s]+)/g, 
            '<a href="$1" target="_blank" rel="noopener" class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 underline font-medium">$1</a>'
        );
        
        // Format bold text
        content = content.replace(/\*\*([^*]+)\*\*/g, '<strong class="font-semibold text-gray-900 dark:text-gray-100">$1</strong>');
        
        // Format italic text
        content = content.replace(/\*([^*]+)\*/g, '<em class="italic text-gray-700 dark:text-gray-300">$1</em>');
        
        // Format numbered lists
        content = content.replace(/^\d+\.\s(.+)$/gm, '<li class="flex items-start space-x-2 mb-2"><span class="flex-shrink-0 w-6 h-6 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center text-xs font-medium text-blue-600 dark:text-blue-400 mt-0.5">•</span><span>$1</span></li>');
        
        // Format bullet points with better styling
        content = content.replace(/^•\s(.+)$/gm, '<li class="flex items-start space-x-2 mb-2"><span class="flex-shrink-0 w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full mt-2"></span><span>$1</span></li>');
        content = content.replace(/^-\s(.+)$/gm, '<li class="flex items-start space-x-2 mb-2"><span class="flex-shrink-0 w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full mt-2"></span><span>$1</span></li>');
        
        // Convert list items to proper lists
        content = content.replace(/(<li.*<\/li>\s*)+/gs, '<ul class="space-y-1 my-3 pl-4">$&</ul>');
        
        // Format headers
        content = content.replace(/^###\s(.+)$/gm, '<h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mt-4 mb-2">$1</h3>');
        content = content.replace(/^##\s(.+)$/gm, '<h2 class="text-xl font-bold text-gray-900 dark:text-gray-100 mt-4 mb-2">$1</h2>');
        content = content.replace(/^#\s(.+)$/gm, '<h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mt-4 mb-2">$1</h1>');
        
        // Format line breaks and paragraphs
        content = content.replace(/\n\n/g, '</p><p class="mb-3 leading-relaxed">');
        content = content.replace(/\n/g, '<br>');
        
        // Wrap in paragraph if not already wrapped
        if (!content.includes('<p>') && !content.includes('<div>') && !content.includes('<ul>') && !content.includes('<h')) {
            content = `<p class="leading-relaxed mb-2">${content}</p>`;
        }
        
        return content;
    }

    createFeedbackButtons(metadata) {
        // This method is no longer used since feedback buttons are now inline
        return '';
    }

    handleFeedback(button, type) {
        // Prevent multiple feedback on same message
        const messageContent = button.closest('.message-content');
        const buttons = messageContent.querySelectorAll('.feedback-btn');
        
        buttons.forEach(btn => {
            btn.classList.remove('active');
            // Reset button styles
            if (btn.classList.contains('like-btn')) {
                btn.classList.remove('bg-green-100', 'border-green-300', 'dark:bg-green-900/30', 'dark:border-green-500', 'text-green-600', 'dark:text-green-400');
                btn.classList.add('bg-gray-100', 'hover:bg-green-100', 'dark:bg-gray-700', 'dark:hover:bg-green-900/30', 'border-gray-300', 'dark:border-gray-600', 'text-gray-600', 'dark:text-gray-300', 'hover:border-green-300', 'dark:hover:border-green-500');
            } else if (btn.classList.contains('dislike-btn')) {
                btn.classList.remove('bg-red-100', 'border-red-300', 'dark:bg-red-900/30', 'dark:border-red-500', 'text-red-600', 'dark:text-red-400');
                btn.classList.add('bg-gray-100', 'hover:bg-red-100', 'dark:bg-gray-700', 'dark:hover:bg-red-900/30', 'border-gray-300', 'dark:border-gray-600', 'text-gray-600', 'dark:text-gray-300', 'hover:border-red-300', 'dark:hover:border-red-500');
            }
        });
        
        button.classList.add('active');
        
        // Apply active styles
        if (type === 'like') {
            button.classList.remove('bg-gray-100', 'hover:bg-green-100', 'dark:bg-gray-700', 'dark:hover:bg-green-900/30', 'border-gray-300', 'dark:border-gray-600', 'text-gray-600', 'dark:text-gray-300', 'hover:border-green-300', 'dark:hover:border-green-500');
            button.classList.add('bg-green-100', 'border-green-300', 'dark:bg-green-900/30', 'dark:border-green-500', 'text-green-600', 'dark:text-green-400');
            this.positiveFeedback++;
        } else {
            button.classList.remove('bg-gray-100', 'hover:bg-red-100', 'dark:bg-gray-700', 'dark:hover:bg-red-900/30', 'border-gray-300', 'dark:border-gray-600', 'text-gray-600', 'dark:text-gray-300', 'hover:border-red-300', 'dark:hover:border-red-500');
            button.classList.add('bg-red-100', 'border-red-300', 'dark:bg-red-900/30', 'dark:border-red-500', 'text-red-600', 'dark:text-red-400');
            this.negativeFeedback++;
        }

        // Send feedback to server
        this.sendFeedback(type, button.closest('.message'));
        this.updateAnalytics();
        
        // Show confirmation
        this.showToast(`Thank you for your feedback!`, 'success');
    }

    async sendFeedback(type, messageElement) {
        try {
            const messageContent = messageElement.querySelector('.message-content').textContent;
            const userMessage = this.findPreviousUserMessage(messageElement);
            
            await fetch(`${this.apiUrl}/feedback`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    feedback: type,
                    answer: messageContent,
                    question: userMessage
                }),
            });
        } catch (error) {
            console.error('Error sending feedback:', error);
        }
    }

    findPreviousUserMessage(botMessageElement) {
        let prev = botMessageElement.previousElementSibling;
        while (prev) {
            if (prev.classList.contains('user')) {
                return prev.querySelector('.message-content').textContent;
            }
            prev = prev.previousElementSibling;
        }
        return '';
    }

    showTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        indicator.classList.remove('hidden');
        indicator.style.display = 'flex';
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        indicator.classList.add('hidden');
        indicator.style.display = 'none';
    }

    scrollToBottom() {
        const messagesArea = document.getElementById('messagesArea');
        setTimeout(() => {
            messagesArea.scrollTop = messagesArea.scrollHeight;
        }, 100);
    }

    updateCharCount() {
        const messageInput = document.getElementById('messageInput');
        const charCount = document.getElementById('charCount');
        const count = messageInput.value.length;
        
        charCount.textContent = `${count}/2000`;
        
        if (count > 1800) {
            charCount.style.color = 'var(--primary-color)';
        } else {
            charCount.style.color = 'var(--text-secondary)';
        }
    }

    toggleSendButton() {
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        
        sendButton.disabled = !messageInput.value.trim() || !this.isConnected;
    }

    setupAutoResize() {
        const messageInput = document.getElementById('messageInput');
        
        messageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
    }

    toggleSidebar() {
        console.log('🔧 Toggle sidebar called');
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebarOverlay');
        
        console.log('📋 Sidebar element:', sidebar);
        console.log('📋 Overlay element:', overlay);
        
        if (sidebar) {
            const isOpen = sidebar.classList.contains('open');
            console.log('📋 Sidebar currently open:', isOpen);
            
            if (isOpen) {
                sidebar.classList.remove('open');
                sidebar.style.transform = '';  // Reset inline style
            } else {
                sidebar.classList.add('open');
                sidebar.style.transform = 'translateX(0)';  // Ensure it's visible
            }
            
            console.log('✅ Sidebar classes after toggle:', sidebar.className);
        } else {
            console.error('❌ Sidebar element not found!');
        }
        
        if (overlay) {
            const isActive = overlay.classList.contains('active');
            
            if (isActive) {
                overlay.classList.remove('active');
                overlay.style.opacity = '';
                overlay.style.visibility = '';
            } else {
                overlay.classList.add('active');
                overlay.style.opacity = '1';
                overlay.style.visibility = 'visible';
            }
            
            console.log('✅ Overlay classes after toggle:', overlay.className);
        } else {
            console.error('❌ Overlay element not found!');
        }
    }

    closeSidebar() {
        console.log('🔧 Close sidebar called');
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebarOverlay');
        
        console.log('📋 Sidebar element:', sidebar);
        console.log('📋 Overlay element:', overlay);
        
        if (sidebar) {
            const wasOpen = sidebar.classList.contains('open');
            console.log('📋 Sidebar was open:', wasOpen);
            
            sidebar.classList.remove('open');
            sidebar.style.transform = '';  // Reset inline style to default
            
            console.log('✅ Sidebar closed, classes:', sidebar.className);
        } else {
            console.error('❌ Sidebar element not found!');
        }
        
        if (overlay) {
            const wasActive = overlay.classList.contains('active');
            console.log('📋 Overlay was active:', wasActive);
            
            overlay.classList.remove('active');
            overlay.style.opacity = '';  // Reset inline styles
            overlay.style.visibility = '';
            
            console.log('✅ Overlay deactivated, classes:', overlay.className);
        } else {
            console.error('❌ Overlay element not found!');
        }
    }

    // Force open sidebar for testing
    forceOpenSidebar() {
        console.log('🔧 Force opening sidebar...');
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebarOverlay');
        
        if (sidebar) {
            sidebar.classList.add('open');
            sidebar.style.transform = 'translateX(0)';
            console.log('✅ Sidebar forced open');
        }
        
        if (overlay) {
            overlay.classList.add('active');
            overlay.style.opacity = '1';
            overlay.style.visibility = 'visible';
            console.log('✅ Overlay activated');
        }
    }

    // Force close sidebar for testing
    forceCloseSidebar() {
        console.log('🔧 Force closing sidebar...');
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebarOverlay');
        
        if (sidebar) {
            sidebar.classList.remove('open');
            sidebar.style.transform = 'translateX(-100%)';
            console.log('✅ Sidebar forced closed');
        }
        
        if (overlay) {
            overlay.classList.remove('active');
            overlay.style.opacity = '0';
            overlay.style.visibility = 'hidden';
            console.log('✅ Overlay deactivated');
        }
    }

    toggleTheme() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        this.setTheme(this.theme);
    }

    setTheme(theme) {
        this.theme = theme;
        document.documentElement.classList.toggle('dark', theme === 'dark');
        document.documentElement.setAttribute('data-theme', theme);
        
        // Update theme toggle icon
        const themeIcon = document.querySelector('.theme-icon');
        if (themeIcon) {
            themeIcon.textContent = theme === 'light' ? '🌙' : '☀️';
        }
        
        // Update theme options
        document.querySelectorAll('.theme-option').forEach(option => {
            option.classList.toggle('active', option.dataset.theme === theme);
        });
        
        this.saveSettings();
    }

    newChat() {
        this.currentConversation = [];
        this.clearMessages();
        this.displayWelcomeMessage();
        this.showToast('Started new conversation', 'success');
    }

    clearChat() {
        if (confirm('Are you sure you want to clear this conversation?')) {
            this.clearMessages();
            this.displayWelcomeMessage();
            this.showToast('Conversation cleared', 'success');
        }
    }

    clearMessages() {
        const messagesArea = document.getElementById('messagesArea');
        messagesArea.innerHTML = '';
    }

    displayWelcomeMessage() {
        // The enhanced welcome message is already in the HTML, so we don't need to add it again
        // unless the messages area was completely cleared
        const messagesArea = document.getElementById('messagesArea');
        if (messagesArea.children.length === 0) {
            // Since we have an enhanced welcome message in HTML, we'll just make sure it exists
            // If needed, we can add a simple fallback message
            this.addMessage(`👋 Hello! I'm GreenBot, your AI assistant for Green University of Bangladesh. How can I help you today?`, 'bot');
        }
    }

    handleNavigation(navItem) {
        // Remove active class from all nav items
        document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
        navItem.classList.add('active');

        const section = navItem.dataset.section;
        
        switch (section) {
            case 'analytics':
                this.openModal('analyticsModal');
                this.updateAnalyticsModal();
                break;
            case 'settings':
                this.openModal('settingsModal');
                break;
            case 'chat':
                this.closeSidebar();
                break;
        }
    }

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.classList.add('open');
        modal.style.display = 'flex';
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.classList.remove('open');
        setTimeout(() => {
            modal.style.display = 'none';
        }, 300);
    }

    updateAnalytics() {
        // Update sidebar stats
        const sidebarTotal = document.getElementById('sidebarTotalMessages');
        const sidebarActive = document.getElementById('sidebarActiveToday');
        
        if (sidebarTotal) sidebarTotal.textContent = this.messageCount;
        if (sidebarActive) sidebarActive.textContent = this.userQuestions;
    }

    updateAnalyticsModal() {
        // Update modal stats with error checking
        const elements = {
            modalTotalMessages: this.messageCount,
            modalUserQuestions: this.userQuestions,
            modalBotResponses: this.botResponses,
            modalPositiveFeedback: this.positiveFeedback,
            modalNegativeFeedback: this.negativeFeedback
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) element.textContent = value;
        });
        
        // Calculate satisfaction rate
        const totalFeedback = this.positiveFeedback + this.negativeFeedback;
        const satisfactionRate = totalFeedback > 0 ? Math.round((this.positiveFeedback / totalFeedback) * 100) : 100;
        const satisfactionElement = document.getElementById('modalSatisfactionRate');
        if (satisfactionElement) satisfactionElement.textContent = `${satisfactionRate}%`;
    }

    showMetadataNotification(metadata) {
        // Create notification container if it doesn't exist
        let notificationContainer = document.getElementById('metadataNotification');
        if (!notificationContainer) {
            notificationContainer = document.createElement('div');
            notificationContainer.id = 'metadataNotification';
            notificationContainer.className = 'fixed top-4 right-4 z-50 space-y-2';
            document.body.appendChild(notificationContainer);
        }

        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'metadata-notification bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg p-4 max-w-sm animate-slide-in-right';
        
        // Determine confidence color
        const confidence = Math.round(metadata.confidence * 100);
        let confidenceColor = 'text-green-600 dark:text-green-400';
        if (confidence < 70) confidenceColor = 'text-yellow-600 dark:text-yellow-400';
        if (confidence < 50) confidenceColor = 'text-red-600 dark:text-red-400';
        
        // Format method name for display
        const methodDisplay = metadata.method.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        
        notification.innerHTML = `
            <div class="flex items-start space-x-3">
                <div class="flex-shrink-0">
                    <div class="w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center">
                        <span class="text-blue-600 dark:text-blue-400 text-sm">ℹ️</span>
                    </div>
                </div>
                <div class="flex-1 min-w-0">
                    <h4 class="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-2">Response Details</h4>
                    <div class="space-y-1">
                        <div class="flex justify-between items-center">
                            <span class="text-xs text-gray-600 dark:text-gray-400">Confidence:</span>
                            <span class="text-sm font-medium ${confidenceColor}">${confidence}%</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-xs text-gray-600 dark:text-gray-400">Method:</span>
                            <span class="text-xs font-medium text-gray-900 dark:text-gray-100">${methodDisplay}</span>
                        </div>
                        ${metadata.processing_time ? `
                        <div class="flex justify-between items-center">
                            <span class="text-xs text-gray-600 dark:text-gray-400">Processing:</span>
                            <span class="text-xs font-medium text-gray-900 dark:text-gray-100">${metadata.processing_time}s</span>
                        </div>
                        ` : ''}
                    </div>
                </div>
                <button class="notification-close flex-shrink-0 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors duration-200" onclick="this.parentElement.parentElement.remove()">
                    <span class="text-lg">×</span>
                </button>
            </div>
        `;

        notificationContainer.appendChild(notification);

        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.classList.add('animate-slide-out-right');
                setTimeout(() => {
                    if (notification.parentElement) {
                        notification.remove();
                    }
                }, 300);
            }
        }, 10000);
    }

    saveSettings() {
        const settings = {
            theme: this.theme,
            autoScroll: this.autoScroll
        };
        localStorage.setItem('greenbot-settings', JSON.stringify(settings));
    }

    loadSettings() {
        const saved = localStorage.getItem('greenbot-settings');
        if (saved) {
            const settings = JSON.parse(saved);
            this.theme = settings.theme || 'light';
            this.autoScroll = settings.autoScroll !== undefined ? settings.autoScroll : true;
            
            this.setTheme(this.theme);
            const autoScrollToggle = document.getElementById('autoScrollToggle');
            if (autoScrollToggle) {
                autoScrollToggle.checked = this.autoScroll;
            }
        }
    }

    // Utility method to get conversation history
    getConversationHistory() {
        return this.currentConversation;
    }

    // Method to export conversation
    exportConversation() {
        const data = {
            timestamp: new Date().toISOString(),
            messages: this.currentConversation,
            stats: {
                messageCount: this.messageCount,
                userQuestions: this.userQuestions,
                botResponses: this.botResponses,
                positiveFeedback: this.positiveFeedback,
                negativeFeedback: this.negativeFeedback
            }
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `greenbot-conversation-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showToast('Conversation exported successfully', 'success');
    }
}

// Initialize the GreenBot application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.greenBot = new GreenBot();
    
    // Add some helpful keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K to focus message input
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            document.getElementById('messageInput').focus();
        }
        
        // Ctrl/Cmd + B to toggle sidebar (for testing)
        if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
            e.preventDefault();
            console.log('🔧 Keyboard shortcut: Force opening sidebar');
            window.greenBot.forceOpenSidebar();
        }
        
        // Ctrl/Cmd + Shift + B to force close sidebar (for testing)
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'B') {
            e.preventDefault();
            console.log('🔧 Keyboard shortcut: Force closing sidebar');
            window.greenBot.forceCloseSidebar();
        }
        
        // Ctrl/Cmd + Shift + C to clear chat
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'C') {
            e.preventDefault();
            window.greenBot.clearChat();
        }
        
        // Escape to close modals/sidebar
        if (e.key === 'Escape') {
            window.greenBot.closeModal('analyticsModal');
            window.greenBot.closeModal('settingsModal');
            window.greenBot.closeSidebar();
        }
    });
    
    console.log('🤖 GreenBot initialized successfully!');
});

// Export for external access
window.GreenBot = GreenBot;
