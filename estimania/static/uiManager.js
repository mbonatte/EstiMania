import Card from './Card.js';

export default class UIManager {
    constructor() {
        this.messageArea = document.getElementById('messageArea');
        this.tableArea = document.getElementById('tableArea');
        this.handArea = document.getElementById('handArea');
        this.roundArea = document.getElementById("roundArea");
        this.scoreArea = document.querySelector("#scoreArea tbody");
        this.createBetModal();
        this.createFloatingText();
    }

    initialize(socketHandler) {
        this.setupEventListeners(socketHandler);
    }

    setupEventListeners(socketHandler) {
        document.getElementById('chatForm').addEventListener('submit', (event) => {
            event.preventDefault();
            const messageInput = document.getElementById('message');
            socketHandler.sendMessage(messageInput.value);
            messageInput.value = '';
        });

        document.getElementById('startGameButton').addEventListener('click', () => {
            const maxTurns = parseInt(prompt("Enter the maximum number of turns:", "0"));
            const numBots = parseInt(prompt("Enter the number of bots:", "0"));
            if (!isNaN(maxTurns) && !isNaN(numBots)) {
                socketHandler.startGame(maxTurns, numBots);
            } else {
                alert("Please enter valid integer values.");
            }
        });
    }

    appendMessage(msg) {
        const p = document.createElement('p');
        p.textContent = msg;
        this.messageArea.appendChild(p);
        this.messageArea.scrollTop = this.messageArea.scrollHeight;
    }

    removeStartGameButton() {
        document.getElementById('startGameButton').remove();
    }

    createBetModal() {
        const betModal = document.createElement('div');
        betModal.id = 'betModal';
        betModal.className = 'modal';
        betModal.innerHTML = `
            <div class="modal-content">
                <h2>Place Your Bet</h2>
                <input type="number" min="0" id="betInput" placeholder="Enter your bet">
                <button id="submitBetButton">Submit</button>
            </div>
        `;
        document.body.appendChild(betModal);
    }
    
    showBetInputForm(callback) {
        const betModal = document.getElementById('betModal');
        const betInput = document.getElementById('betInput');
        const submitBetButton = document.getElementById('submitBetButton');

        betModal.style.display = 'block';

        const submitBet = () => {
            const bet = parseInt(betInput.value);
            betModal.style.display = 'none';
            callback(bet);
        };

        submitBetButton.addEventListener('click', submitBet);
    }

    handleCardPick(callback) {
        this.bringAttention();
        const cardElements = document.getElementsByClassName('card');
        
        const cardClickHandler = (event) => {
            const clickedCard = event.target.textContent;
            this.disableCardSelection();
            this.removeFloatingText();
            callback(clickedCard);
        };

        for (let card of cardElements) {
            card.addEventListener('click', cardClickHandler);
        }
    }

    updateTable(data) {
        this.tableArea.innerHTML = '';
        data.table.forEach((card, index) => {
            const cardWrapper = this.createCardWrapper(card, data.names[index]);
            this.tableArea.appendChild(cardWrapper);
        });
    }

    updateHand(userCards) {
        this.handArea.innerHTML = '';
        userCards.forEach(card => {
            const cardWrapper = this.createCardWrapper(card);
            this.handArea.appendChild(cardWrapper);
        });
    }

    updateScore(users) {
        this.scoreArea.innerHTML = "";
        users.forEach(player => {
            const row = this.createScoreRow(player);
            this.scoreArea.appendChild(row);
        });
    }
    
    updateRound(round) {
        this.roundArea.innerHTML = round;
    }


    highlightPlayerTurn(player) {
        const rows = this.scoreArea.querySelectorAll("tr");
        rows.forEach(row => row.style.backgroundColor = "");
        const playerRow = this.scoreArea.querySelector(`tr[data-player='${player}']`);
        if (playerRow) playerRow.style.backgroundColor = "red";
    }

    highlightWinnerCard(card) {
        const winnerCard = document.getElementById(card);
        if (winnerCard) {
            winnerCard.style.border = '5px red solid';
            winnerCard.style.animation = 'highlight 1s infinite';
        }
    }

    showFinalScore(scores) {
        const scorePopup = document.createElement("div");
        scorePopup.id = "scorePopup";
        scorePopup.classList.add("final-score-popup", "show");

        // Create close button
        const closeButton = document.createElement("button");
        closeButton.textContent = "X";
        closeButton.classList.add("close-button", "red-button");
        closeButton.setAttribute("aria-label", "Close");
        closeButton.addEventListener("click", () => {
            scorePopup.remove();
        });

        // Create header div to hold the title and close button
        const headerDiv = document.createElement("div");
        headerDiv.classList.add("popup-header");

        const title = document.createElement("h2");
        title.textContent = "Final Scores";

        headerDiv.appendChild(title);
        headerDiv.appendChild(closeButton);
        
        // Create content div
        const contentDiv = document.createElement("div");
        contentDiv.classList.add("popup-content");
        
        // Create table
        const scoreTable = document.createElement("table");
        scoreTable.classList.add("final-score-table");
        
        const headerRow = this.createScoreRow({ name: "Name", score: "Score" }, true);
        scoreTable.appendChild(headerRow);
        
        scores.forEach(score => {
            const row = this.createScoreRow(score);
            scoreTable.appendChild(row);
        });
        
        contentDiv.appendChild(scoreTable);
        
        
        // Create header-content div
        const headerContentDiv = document.createElement("div");
        headerContentDiv.classList.add("popup-header-content");
        
        headerContentDiv.appendChild(headerDiv);
        headerContentDiv.appendChild(contentDiv);

        scorePopup.appendChild(headerContentDiv);
        document.body.appendChild(scorePopup);
    }

    createCardWrapper(card, playerName = null) {
        const cardWrapper = document.createElement('div');
        cardWrapper.className = 'card-wrapper';
        
        const cardElement = document.createElement('div');
        cardElement.id = card;
        cardElement.className = 'card';
        cardElement.textContent = card;
        
        cardWrapper.appendChild(cardElement);
        
        if (playerName) {
            const playerNameElement = document.createElement('div');
            playerNameElement.className = 'player-name';
            playerNameElement.textContent = playerName;
            cardWrapper.appendChild(playerNameElement);
        }
        
        new Card(card).displayCard(cardElement, true);
        
        return cardWrapper;
    }

    createScoreRow(player, isHeader = false) {
        const row = document.createElement("tr");
        row.setAttribute("data-player", player.name);
        
        const nameCell = document.createElement(isHeader ? "th" : "td");
        nameCell.textContent = player.name;
        row.appendChild(nameCell);
        
        const scoreCell = document.createElement(isHeader ? "th" : "td");
        scoreCell.textContent = player.score || player.bet;
        row.appendChild(scoreCell);
        
        if (player.wins !== undefined) {
            const winsCell = document.createElement("td");
            winsCell.textContent = player.wins;
            row.appendChild(winsCell);
        }
        
        return row;
    }

    disableCardSelection() {
        const cardElements = document.getElementsByClassName('card');
        for (let card of cardElements) {
            card.removeEventListener('click', () => {});
        }
    }

    createFloatingText() {
        const floatingText = document.createElement('div');
        floatingText.id = 'floatingText';
        floatingText.textContent = 'Pick a card!';
        floatingText.style.display = 'none';
        document.body.appendChild(floatingText);
    }
    
    bringAttention() {
        const floatingText = document.getElementById('floatingText');
        floatingText.style.display = 'block';
        floatingText.style.animation = 'none';
        void floatingText.offsetWidth;
        floatingText.style.animation = 'floatAnimation 6s forwards';
    }

    removeFloatingText() {
        const floatingText = document.getElementById('floatingText');
        if (floatingText) {
            floatingText.style.display = 'none';
            floatingText.style.animation = 'none';
        }
    }
}