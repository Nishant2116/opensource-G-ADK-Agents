document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatHistory = document.getElementById('chat-history');
    const sendBtn = document.getElementById('send-btn');

    userInput.focus();

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = userInput.value.trim();
        if (!message) return;

        addMessage(message, 'user');
        userInput.value = '';
        userInput.disabled = true;
        sendBtn.disabled = true;

        const loadingId = addLoadingIndicator();

        try {
            const response = await fetch(`/agent/query?prompt=${encodeURIComponent(message)}`, {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();

            removeMessage(loadingId);

            if (data.error) {
                addMessage(`Error: ${data.error}`, 'system');
            } else {
                addMessage(formatResponse(data.response), 'system', true);
            }

        } catch (error) {
            removeMessage(loadingId);
            addMessage(`Sorry, something went wrong: ${error.message}`, 'system');
        } finally {
            userInput.disabled = false;
            sendBtn.disabled = false;
            userInput.focus();
        }
    });

    document.querySelectorAll('.suggestion-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const text = chip.dataset.prompt || chip.textContent;
            userInput.value = text;
            chatForm.dispatchEvent(new Event('submit'));
        });
    });

    async function renderCharts(container) {
        const charts = container.querySelectorAll('.plotly-chart');
        for (const chartDiv of charts) {
            if (chartDiv.dataset.rendered) continue;

            const url = chartDiv.dataset.url;
            const id = chartDiv.id;

            try {
                const response = await fetch(url);
                if (!response.ok) throw new Error("Failed to fetch chart data");
                const graphData = await response.json();

                const layout = {
                    ...graphData.layout,
                    autosize: true
                };

                Plotly.newPlot(id, graphData.data, layout, { responsive: true, displayModeBar: 'hover' });

                const chartWidth = chartDiv.offsetWidth;
                if (chartWidth > 0) {
                    Plotly.relayout(id, { width: chartWidth });
                }

                chartDiv.dataset.rendered = "true";
            } catch (e) {
                console.error("Chart error:", e);
                chartDiv.innerHTML = `<div style="color:#ef4444; padding:10px; border:1px solid #ef4444; border-radius:8px;">Failed to load chart: ${e.message}</div>`;
            }
        }
    }

    function addMessage(text, type, isHtml = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;

        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.innerHTML = type === 'user' ? '<i class="fa-solid fa-user"></i>' : '<img src="/static/logo.png" class="avatar-icon">';

        const content = document.createElement('div');
        content.className = 'content';

        if (isHtml) {
            content.innerHTML = text;
        } else {
            content.textContent = text;
        }

        if (type === 'user') {
            messageDiv.appendChild(content);
            messageDiv.appendChild(avatar);
        } else {
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(content);
        }

        chatHistory.appendChild(messageDiv);

        if (isHtml) {
            renderCharts(content);
        }

        scrollToBottom();
        return messageDiv;
    }

    function addLoadingIndicator() {
        const id = 'loading-' + Date.now();
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message system-message';
        messageDiv.id = id;

        messageDiv.innerHTML = `
            <div class="avatar"><img src="/static/logo.png" class="avatar-icon"></div>
            <div class="content">
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;

        chatHistory.appendChild(messageDiv);
        scrollToBottom();
        return id;
    }

    function removeMessage(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function scrollToBottom() {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function formatResponse(text) {
        if (!text) return "";

        text = text.replace(/<thinking>[\s\S]*?<\/thinking>/gi, '');
        text = text.replace(/<\/?answer>/gi, '');

        const parseTable = (block) => {
            const lines = block.trim().split('\n');
            if (lines.length < 2) return block;

            let html = '<div class="table-container"><table>';

            const headerRow = lines[0].split('|').filter(c => c.trim() !== '');
            html += '<thead><tr>';
            headerRow.forEach(h => html += `<th>${h.trim()}</th>`);
            html += '</tr></thead>';

            html += '<tbody>';
            for (let i = 2; i < lines.length; i++) {
                const cols = lines[i].split('|').filter(c => c.trim() !== '');
                if (cols.length === 0) continue;
                html += '<tr>';
                cols.forEach(c => html += `<td>${c.trim()}</td>`);
                html += '</tr>';
            }
            html += '</tbody></table></div>';
            return html;
        };

        const tableRegex = /((?:^\s*\|.*\|\s*(?:\n|$))+(?:^\s*\|[-:| ]+\|\s*(?:\n|$))+(?:^\s*\|.*\|\s*(?:\n|$))*)/gm;

        let formatted = text;
        const tables = [];

        formatted = formatted.replace(tableRegex, (match) => {
            tables.push(parseTable(match));
            return `__TABLE_${tables.length - 1}__`;
        });

        let formattedText = formatted;

        const imageRegex = /!\[([^\]]*)\]\(([^)]+)\)/g;
        formattedText = formattedText.replace(imageRegex, (match, alt, src) => {
            const cleanSrc = src.trim();

            if (cleanSrc.toLowerCase().endsWith('.json')) {
                const chartId = 'chart-' + Math.random().toString(36).substr(2, 9);
                return `<div id="${chartId}" class="plotly-chart" data-url="${cleanSrc}" style="width:100%;"></div>`;
            }

            return `<div class="message-image-container">
                        <img src="${cleanSrc}" alt="${alt}" class="message-image" loading="lazy" onclick="window.open(this.src, '_blank')">
                    </div>`;
        });

        formatted = formattedText
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');

        tables.forEach((tableHtml, index) => {
            formatted = formatted.replace(`__TABLE_${index}__`, tableHtml);
        });

        return formatted;
    }
});
