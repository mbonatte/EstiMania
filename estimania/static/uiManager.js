import Card from './Card.js';

export default class UIManager {
    constructor() {
        this.messageArea = document.getElementById('messageArea');
        this.tableArea = document.getElementById('tableArea');
        this.handArea = document.getElementById('handArea');
        this.roundArea = document.getElementById("roundArea");
        this.scoreArea = document.querySelector("#scoreArea tbody");
        this.activeCardPickCallback = null;
        this.cardClickHandler = null;
        this.currentScores = [];
        this._lastErrorMsg = null;
        this._lastErrorTime = 0;
        
        this.createBetModal();
        this.createSetupModal();
        this.createFloatingText();
        console.log("UI Manager initialized.");
    }

    initialize(socketHandler) {
        this.socketHandler = socketHandler;
        this.setupEventListeners(socketHandler);
    }

    setupEventListeners(socketHandler) {
        const chatForm = document.getElementById('chatForm');
        if (chatForm) {
            chatForm.addEventListener('submit', (event) => {
                event.preventDefault();
                const messageInput = document.getElementById('message');
                if (messageInput.value.trim()) {
                    socketHandler.sendMessage(messageInput.value.trim());
                    messageInput.value = '';
                }
            });
        }

        const startBtn = document.getElementById('startGameButton');
        if (startBtn) {
            startBtn.addEventListener('click', () => {
                this.showSetupModal((maxTurns, numBots) => {
                    socketHandler.startGame(maxTurns, numBots);
                });
            });
        }

        const pointsBtn = document.getElementById('viewOverallPointsBtn');
        if (pointsBtn) {
            pointsBtn.addEventListener('click', () => this.showOverallPointsModal());
        }

        const pointsBtnTop = document.getElementById('viewOverallPointsBtnTop');
        if (pointsBtnTop) {
            pointsBtnTop.addEventListener('click', () => this.showOverallPointsModal());
        }
    }

    appendMessage(msg) {
        const p = document.createElement('p');
        p.textContent = msg;
        this.messageArea.appendChild(p);
        this.messageArea.scrollTop = this.messageArea.scrollHeight;
        console.log(`Appended message to chat: ${msg}`);
    }

    removeStartGameButton() {
        const startBtn = document.getElementById('startGameButton');
        if (startBtn) {
            startBtn.style.display = 'none';
        }
    }

    /* ========================================================================
       Game Setup Modal
       ======================================================================== */
    createSetupModal() {
        const setupModal = document.createElement('div');
        setupModal.id = 'setupModal';
        setupModal.className = 'modal';
        setupModal.innerHTML = `
            <div class="modal-content">
                <h2>Game Settings</h2>
                <p class="modal-desc">Configure opponents and round length before dealing.</p>
                
                <div class="modal-form-row">
                    <label>AI Bot Opponents</label>
                    <div class="bet-chips-container" id="botsChipsContainer">
                        <div class="bet-chip" data-value="0">0</div>
                        <div class="bet-chip" data-value="1">1</div>
                        <div class="bet-chip" data-value="2">2</div>
                        <div class="bet-chip active" data-value="3">3</div>
                    </div>
                </div>

                <div class="modal-form-row">
                    <label>Max Turns / Rounds</label>
                    <div class="bet-chips-container" id="turnsChipsContainer">
                        <div class="bet-chip" data-value="1">1</div>
                        <div class="bet-chip" data-value="2">2</div>
                        <div class="bet-chip" data-value="3">3</div>
                        <div class="bet-chip" data-value="4">4</div>
                        <div class="bet-chip active" data-value="5">5</div>
                    </div>
                </div>

                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" id="cancelSetupBtn">Cancel</button>
                    <button type="button" class="btn btn-emerald" id="confirmSetupBtn">Start Match</button>
                </div>
            </div>
        `;
        document.body.appendChild(setupModal);

        // Chip selection logic for setup modal
        this.setupChipGroup('botsChipsContainer');
        this.setupChipGroup('turnsChipsContainer');
    }

    setupChipGroup(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        container.addEventListener('click', (e) => {
            const chip = e.target.closest('.bet-chip');
            if (!chip) return;
            container.querySelectorAll('.bet-chip').forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
        });
    }

    showSetupModal(onStartCallback) {
        const setupModal = document.getElementById('setupModal');
        const confirmBtn = document.getElementById('confirmSetupBtn');
        const cancelBtn = document.getElementById('cancelSetupBtn');

        setupModal.style.display = 'flex';

        const onConfirm = () => {
            const activeBotsChip = document.querySelector('#botsChipsContainer .bet-chip.active');
            const activeTurnsChip = document.querySelector('#turnsChipsContainer .bet-chip.active');
            const numBots = activeBotsChip ? parseInt(activeBotsChip.dataset.value) : 3;
            const maxTurns = activeTurnsChip ? parseInt(activeTurnsChip.dataset.value) : 5;

            setupModal.style.display = 'none';
            cleanup();
            if (onStartCallback) onStartCallback(maxTurns, numBots);
        };

        const onCancel = () => {
            setupModal.style.display = 'none';
            cleanup();
        };

        const cleanup = () => {
            confirmBtn.removeEventListener('click', onConfirm);
            cancelBtn.removeEventListener('click', onCancel);
        };

        confirmBtn.addEventListener('click', onConfirm);
        cancelBtn.addEventListener('click', onCancel);
    }

    /* ========================================================================
       Betting Modal
       ======================================================================== */
    createBetModal() {
        const betModal = document.createElement('div');
        betModal.id = 'betModal';
        betModal.className = 'modal';
        betModal.innerHTML = `
            <div class="modal-content">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <h2 style="margin: 0; font-size: 1.4rem;">Place Your Bet</h2>
                    <span id="betCardsInHandBadge" class="room-badge" style="font-size: 0.8rem; padding: 0.25rem 0.75rem;">Cards in Hand: 0</span>
                </div>
                <p class="modal-desc" style="margin-bottom: 1rem; font-size: 0.88rem;">
                    Examine your hand below and current bids in the scoreboard.
                </p>
                
                <div class="bet-chips-container" id="betQuickChips">
                    <div class="bet-chip active" data-bet="0">0</div>
                    <div class="bet-chip" data-bet="1">1</div>
                    <div class="bet-chip" data-bet="2">2</div>
                    <div class="bet-chip" data-bet="3">3</div>
                </div>

                <div class="modal-form-row" style="margin-bottom: 1rem;">
                    <label for="betInput">Custom Bet Amount</label>
                    <input type="number" min="0" max="13" id="betInput" value="0">
                </div>

                <div class="modal-actions" style="margin-top: 1rem;">
                    <button id="submitBetButton" class="btn btn-emerald" style="width: 100%;">Confirm Bid</button>
                </div>
            </div>
        `;
        document.body.appendChild(betModal);

        const chips = betModal.querySelectorAll('.bet-chip');
        const betInput = betModal.querySelector('#betInput');

        chips.forEach(chip => {
            chip.addEventListener('click', () => {
                chips.forEach(c => c.classList.remove('active'));
                chip.classList.add('active');
                betInput.value = chip.dataset.bet;
            });
        });

        betInput.addEventListener('input', () => {
            const val = betInput.value;
            chips.forEach(c => {
                if (c.dataset.bet === val) c.classList.add('active');
                else c.classList.remove('active');
            });
        });
    }
    
    showBetInputForm(callback) {
        const betModal = document.getElementById('betModal');
        const betInput = document.getElementById('betInput');
        const submitBetButton = document.getElementById('submitBetButton');
        const badge = document.getElementById('betCardsInHandBadge');

        // Dynamically adjust quick chips based on cards in hand
        const handCount = this.handArea ? this.handArea.querySelectorAll('.card-wrapper').length : 0;
        if (badge) {
            badge.textContent = `${handCount} Card${handCount === 1 ? '' : 's'}`;
        }

        const chipsContainer = document.getElementById('betQuickChips');
        if (chipsContainer) {
            chipsContainer.innerHTML = '';
            const maxChip = Math.max(handCount, 3);
            for (let i = 0; i <= maxChip; i++) {
                const chip = document.createElement('div');
                chip.className = `bet-chip ${i === 0 ? 'active' : ''}`;
                chip.dataset.bet = i;
                chip.textContent = i;
                chip.addEventListener('click', () => {
                    chipsContainer.querySelectorAll('.bet-chip').forEach(c => c.classList.remove('active'));
                    chip.classList.add('active');
                    betInput.value = i;
                });
                chipsContainer.appendChild(chip);
            }
        }
        betInput.value = 0;

        // Visual emphasis: highlight hand & score areas so player can inspect them
        if (this.handArea) {
            this.handArea.classList.add('betting-hand-highlight');
        }
        const scoreWrapper = document.getElementById('scoreAreaWrapper');
        if (scoreWrapper) {
            scoreWrapper.classList.add('betting-score-highlight');
        }

        betModal.style.display = 'flex';

        const submitBet = () => {
            const bet = parseInt(betInput.value) || 0;
            betModal.style.display = 'none';

            if (this.handArea) {
                this.handArea.classList.remove('betting-hand-highlight');
            }
            if (scoreWrapper) {
                scoreWrapper.classList.remove('betting-score-highlight');
            }

            submitBetButton.removeEventListener('click', submitBet);
            console.log(`Bet submitted: ${bet}`);
            callback(bet);
        };

        submitBetButton.addEventListener('click', submitBet);
    }


    /* ========================================================================
       Card Playing Phase
       ======================================================================== */
    handleCardPick(callback) {
        this.bringAttention("Your Turn! Pick a card to play");
        this.activeCardPickCallback = callback;

        const handCards = this.handArea.querySelectorAll('.card');
        
        this.cardClickHandler = (event) => {
            const cardElement = event.currentTarget;
            const clickedCard = cardElement.dataset.card || cardElement.id;
            this.disableCardSelection();
            this.removeFloatingText();
            console.log(`Card selected: ${clickedCard}`);
            if (this.activeCardPickCallback) {
                const cb = this.activeCardPickCallback;
                this.activeCardPickCallback = null;
                cb(clickedCard);
            }
        };

        handCards.forEach(card => {
            card.classList.add('playable');
            card.addEventListener('click', this.cardClickHandler);
        });
    }

    disableCardSelection() {
        if (this.handArea) {
            const handCards = this.handArea.querySelectorAll('.card');
            handCards.forEach(card => {
                card.classList.remove('playable');
                if (this.cardClickHandler) {
                    card.removeEventListener('click', this.cardClickHandler);
                }
            });
        }
        this.cardClickHandler = null;
    }

    /* ========================================================================
       Table & Hand Updates
       ======================================================================== */
    updateTable(data) {
        this.tableArea.innerHTML = '';
        if (!data.table || data.table.length === 0) {
            const emptyHint = document.createElement('div');
            emptyHint.className = 'table-empty-hint';
            emptyHint.innerHTML = '<span>Played cards will appear here</span>';
            this.tableArea.appendChild(emptyHint);
            return;
        }

        data.table.forEach((card, index) => {
            const playerName = data.names ? data.names[index] : null;
            const cardWrapper = this.createCardWrapper(card, playerName);
            this.tableArea.appendChild(cardWrapper);
        });
        console.log(`Cards on Table:`, data.table);
    }

    updateHand(userCards) {
        this.handArea.innerHTML = '';
        if (!userCards || userCards.length === 0) {
            console.log("Hand is currently empty.");
            return;
        }
        userCards.forEach(card => {
            const cardWrapper = this.createCardWrapper(card);
            this.handArea.appendChild(cardWrapper);
        });
        console.log("Updating hand area with user cards: ", userCards);
    }

    createCardWrapper(card, playerName = null) {
        const cardWrapper = document.createElement('div');
        cardWrapper.className = 'card-wrapper';
        
        const cardElement = document.createElement('div');
        cardElement.id = card;
        cardElement.dataset.card = card;
        cardElement.className = 'card';
        // Note: Do not set cardElement.textContent = card to preserve clean card sprite face
        
        cardWrapper.appendChild(cardElement);
        
        if (playerName) {
            const playerNameElement = document.createElement('div');
            playerNameElement.className = 'player-name';
            playerNameElement.textContent = playerName;
            cardWrapper.appendChild(playerNameElement);
        }
        
        new Card(card).displayCard(cardElement);
        
        return cardWrapper;
    }

    /* ========================================================================
       Scoreboard & Round Info
       ======================================================================== */
    updateScore(users) {
        this.currentScores = users || [];
        this.scoreArea.innerHTML = "";
        this.currentScores.forEach(player => {
            const row = this.createScoreRow(player);
            this.scoreArea.appendChild(row);
        });
        this.updateOverallPointsModalContent();
    }
    
    updateRound(round) {
        this.roundArea.innerHTML = `<span>🃏</span> ${round}`;
    }

    highlightPlayerTurn(player) {
        const rows = this.scoreArea.querySelectorAll("tr");
        rows.forEach(row => row.classList.remove('active-turn'));
        
        const playerRow = this.scoreArea.querySelector(`tr[data-player='${player}']`);
        if (playerRow) {
            playerRow.classList.add('active-turn');
        }
        console.log(`It's ${player}'s turn`);
    }

    highlightWinnerCard(card) {
        const winnerCard = document.getElementById(card);
        if (winnerCard) {
            winnerCard.classList.add('winner-card-highlight');
        }
    }

    /* ========================================================================
       Final Score Leaderboard
       ======================================================================== */
    showFinalScore(scores) {
        const existingPopup = document.getElementById('scorePopup');
        if (existingPopup) existingPopup.remove();

        // Sort descending by score
        const sortedScores = [...scores].sort((a, b) => {
            const sA = (a.score !== undefined) ? a.score : (a.wins || 0);
            const sB = (b.score !== undefined) ? b.score : (b.wins || 0);
            return sB - sA;
        });

        const scorePopup = document.createElement("div");
        scorePopup.id = "scorePopup";
        scorePopup.classList.add("final-score-popup", "show");

        const headerContentDiv = document.createElement("div");
        headerContentDiv.classList.add("popup-header-content");

        // Header
        const headerDiv = document.createElement("div");
        headerDiv.classList.add("popup-header");

        const title = document.createElement("h2");
        title.innerHTML = `🏆 Final Standings`;

        const closeButton = document.createElement("button");
        closeButton.innerHTML = "&times;";
        closeButton.classList.add("close-button");
        closeButton.setAttribute("aria-label", "Close");
        closeButton.addEventListener("click", () => {
            scorePopup.remove();
        });

        headerDiv.appendChild(title);
        headerDiv.appendChild(closeButton);

        // Content Table
        const contentDiv = document.createElement("div");
        contentDiv.classList.add("popup-content");
        
        const scoreTable = document.createElement("table");
        scoreTable.classList.add("final-score-table");
        
        const headerRow = document.createElement("tr");
        headerRow.innerHTML = `
            <th>Rank & Player</th>
            <th style="text-align: right;">Final Score</th>
        `;
        scoreTable.appendChild(headerRow);
        
        const rankEmojis = ["🥇", "🥈", "🥉"];
        sortedScores.forEach((player, idx) => {
            const row = document.createElement("tr");
            if (idx === 0) row.classList.add("winner-row");
            
            const badge = rankEmojis[idx] || `#${idx + 1}`;
            const nameCell = document.createElement("td");
            nameCell.innerHTML = `<span style="margin-right: 0.5rem;">${badge}</span> ${player.name}`;
            
            const val = (player.score !== undefined) ? player.score : (player.wins || 0);
            const scoreCell = document.createElement("td");
            scoreCell.textContent = `${val} pts`;
            
            row.appendChild(nameCell);
            row.appendChild(scoreCell);
            scoreTable.appendChild(row);
        });
        
        contentDiv.appendChild(scoreTable);

        // Action Buttons
        const actionDiv = document.createElement("div");
        actionDiv.style.marginTop = "1.5rem";
        actionDiv.style.display = "flex";
        actionDiv.style.justifyContent = "center";
        
        const restartBtn = document.createElement("button");
        restartBtn.className = "btn btn-emerald";
        restartBtn.textContent = "Play Again";
        restartBtn.addEventListener("click", () => {
            scorePopup.remove();
            window.location.reload();
        });
        actionDiv.appendChild(restartBtn);

        headerContentDiv.appendChild(headerDiv);
        headerContentDiv.appendChild(contentDiv);
        headerContentDiv.appendChild(actionDiv);
        scorePopup.appendChild(headerContentDiv);
        document.body.appendChild(scorePopup);
    }

    createScoreRow(player, isHeader = false) {
        const row = document.createElement("tr");
        row.setAttribute("data-player", player.name);
        
        const nameCell = document.createElement(isHeader ? "th" : "td");
        nameCell.textContent = player.name;
        row.appendChild(nameCell);
        
        const betCell = document.createElement(isHeader ? "th" : "td");
        betCell.textContent = (player.bet !== undefined && player.bet !== null) ? player.bet : '-';
        row.appendChild(betCell);
        
        const winsCell = document.createElement(isHeader ? "th" : "td");
        winsCell.textContent = (player.wins !== undefined) ? player.wins : ((player.score !== undefined) ? player.score : '-');
        row.appendChild(winsCell);
        
        return row;
    }

    /* ========================================================================
       Toast Notifications
       ======================================================================== */
    createFloatingText() {
        let floatingText = document.getElementById('floatingText');
        if (!floatingText) {
            floatingText = document.createElement('div');
            floatingText.id = 'floatingText';
            floatingText.textContent = 'Pick a card!';
            floatingText.style.display = 'none';
            document.body.appendChild(floatingText);
        }
    }
    
    bringAttention(msg = 'Pick a card!') {
        const floatingText = document.getElementById('floatingText');
        if (floatingText) {
            floatingText.textContent = msg;
            floatingText.style.display = 'block';
            floatingText.style.animation = 'none';
            void floatingText.offsetWidth;
            floatingText.style.animation = 'toastSlide 4.5s forwards';
        }
    }

    removeFloatingText() {
        const floatingText = document.getElementById('floatingText');
        if (floatingText) {
            floatingText.style.display = 'none';
            floatingText.style.animation = 'none';
        }
    }

    showError(msg) {
        const now = Date.now();
        if (this._lastErrorMsg === msg && (now - this._lastErrorTime < 2000)) {
            // Debounce identical duplicate error
            return;
        }
        this._lastErrorMsg = msg;
        this._lastErrorTime = now;

        let floatingText = document.getElementById('floatingText');
        if (!floatingText) {
            this.createFloatingText();
            floatingText = document.getElementById('floatingText');
        }

        if (floatingText) {
            floatingText.classList.add('toast-error');
            floatingText.innerHTML = `<span>⚠️</span> ${msg}`;
            floatingText.style.display = 'block';
            floatingText.style.animation = 'none';
            void floatingText.offsetWidth; // Force CSS reflow
            floatingText.style.animation = 'toastSlide 3.5s forwards';

            if (this._toastErrorTimeout) {
                clearTimeout(this._toastErrorTimeout);
            }
            this._toastErrorTimeout = setTimeout(() => {
                floatingText.classList.remove('toast-error');
            }, 3500);
        } else {
            console.warn("Game Error:", msg);
        }
    }

    /* ========================================================================
       Live Overall Points & Standings Modal
       ======================================================================== */
    showOverallPointsModal() {
        let modal = document.getElementById('overallPointsModal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'overallPointsModal';
            modal.className = 'final-score-popup show';
            modal.innerHTML = `
                <div class="popup-header-content" style="max-width: 520px;">
                    <div class="popup-header">
                        <h2><span>🏆</span> Overall Standings</h2>
                        <button id="closeOverallPointsBtn" class="close-button" aria-label="Close">&times;</button>
                    </div>
                    <p style="font-size: 0.88rem; color: var(--text-muted); margin-bottom: 1.25rem;">
                        Cumulative points across all completed rounds.
                    </p>
                    <div class="popup-content">
                        <table class="final-score-table">
                            <thead>
                                <tr>
                                    <th>Rank & Player</th>
                                    <th style="text-align: center;">Round Status</th>
                                    <th style="text-align: right;">Total Points</th>
                                </tr>
                            </thead>
                            <tbody id="overallPointsTableBody"></tbody>
                        </table>
                    </div>
                    <div style="margin-top: 1.5rem;">
                        <button id="dismissOverallPointsBtn" class="btn btn-secondary" style="width: 100%;">
                            Back to Table
                        </button>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);

            const closeModal = () => {
                modal.classList.remove('show');
                modal.style.display = 'none';
            };

            modal.querySelector('#closeOverallPointsBtn').addEventListener('click', closeModal);
            modal.querySelector('#dismissOverallPointsBtn').addEventListener('click', closeModal);
            modal.addEventListener('click', (e) => {
                if (e.target === modal) closeModal();
            });
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && modal.style.display !== 'none' && modal.classList.contains('show')) {
                    closeModal();
                }
            });
        }

        modal.style.display = 'flex';
        modal.classList.add('show');
        this.updateOverallPointsModalContent();
    }

    updateOverallPointsModalContent() {
        const tbody = document.getElementById('overallPointsTableBody');
        if (!tbody) return;

        tbody.innerHTML = '';
        const scores = this.currentScores || [];

        if (scores.length === 0) {
            const emptyRow = document.createElement('tr');
            emptyRow.innerHTML = `
                <td colspan="3" style="text-align: center; color: var(--text-muted); padding: 1.5rem;">
                    Match is starting. Points will calculate after Round 1.
                </td>
            `;
            tbody.appendChild(emptyRow);
            return;
        }

        // Sort descending by total cumulative points
        const sorted = [...scores].sort((a, b) => {
            const sA = (a.total_score !== undefined) ? a.total_score : ((a.score !== undefined) ? a.score : 0);
            const sB = (b.total_score !== undefined) ? b.total_score : ((b.score !== undefined) ? b.score : 0);
            return sB - sA;
        });

        const myUsername = this.socketHandler?.userManager?.getUsername();

        sorted.forEach((player, index) => {
            const total = (player.total_score !== undefined) ? player.total_score : ((player.score !== undefined) ? player.score : 0);
            const rankMedals = ['🥇', '🥈', '🥉'];
            const rankLabel = rankMedals[index] || `#${index + 1}`;

            const row = document.createElement('tr');
            if (index === 0) row.classList.add('winner-row');

            // Player cell
            const isMe = (myUsername && player.name === myUsername);
            const meBadge = isMe ? `<span class="room-badge" style="margin-left: 0.5rem; font-size: 0.72rem; padding: 0.15rem 0.5rem; background: rgba(99, 102, 241, 0.2); border-color: var(--primary);">You</span>` : '';

            // Round status cell
            let roundStatus = '-';
            if (player.bet !== undefined && player.bet !== null) {
                roundStatus = `Bid: ${player.bet} &bull; Won: ${player.wins || 0}`;
            }

            // Score formatting
            let scoreFormatted = `${total} pts`;
            let scoreColor = 'var(--text-muted)';
            if (total > 0) {
                scoreFormatted = `+${total} pts`;
                scoreColor = '#10B981';
            } else if (total < 0) {
                scoreFormatted = `${total} pts`;
                scoreColor = '#EF4444';
            }

            row.innerHTML = `
                <td>
                    <span style="display: inline-block; width: 28px;">${rankLabel}</span>
                    <span style="font-weight: 700;">${player.name}</span>${meBadge}
                </td>
                <td style="text-align: center; font-size: 0.88rem; color: var(--text-muted);">
                    ${roundStatus}
                </td>
                <td style="text-align: right; font-weight: 700; color: ${scoreColor}; font-size: 1.1rem; font-family: 'Outfit', sans-serif;">
                    ${scoreFormatted}
                </td>
            `;
            tbody.appendChild(row);
        });
    }
}