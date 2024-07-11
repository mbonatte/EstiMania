class UIManager {
    constructor() {
        this.messageArea = document.getElementById('messageArea');
        this.tableArea = document.getElementById('tableArea');
        this.handArea = document.getElementById('handArea');
        this.scoreArea = document.querySelector("#scoreArea tbody");
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
        
        const scoreTable = document.createElement("table");
        scoreTable.classList.add("final-score-table");
        
        const headerRow = this.createScoreRow({ name: "Name", score: "Score" });
        scoreTable.appendChild(headerRow);
        
        scores.forEach(score => {
            const row = this.createScoreRow(score);
            scoreTable.appendChild(row);
        });
        
        scorePopup.appendChild(scoreTable);
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

    createScoreRow(player) {
        const row = document.createElement("tr");
        row.setAttribute("data-player", player.name);
        
        const nameCell = document.createElement("td");
        nameCell.textContent = player.name;
        row.appendChild(nameCell);
        
        const scoreCell = document.createElement("td");
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

    bringAttention() {
        const floatingText = document.getElementById('floatingText');
        floatingText.style.animation = 'none';
        void floatingText.offsetWidth;
        floatingText.style.animation = 'floatAnimation 6s forwards';
    }
}