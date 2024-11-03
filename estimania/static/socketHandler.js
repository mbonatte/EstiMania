export default class SocketHandler {
    constructor(userManager, uiManager) {
        this.userManager = userManager;
        this.uiManager = uiManager;
        this.socket = null;
    }

    initialize() {
        this.socket = io.connect('//' + document.domain + ':' + location.port);
        this.setupEventListeners();
    }

    setupEventListeners() {
        const roomID = this.getRoomIDFromURL();
        this.socket.emit('join_room', roomID, this.userManager.getUsername());

        this.socket.on('error', (msg) => alert(msg));
        this.socket.on('message', (msg) => this.uiManager.appendMessage(msg));
        this.socket.on('remove_start_game_btn', () => this.uiManager.removeStartGameButton());
        this.socket.on('bet', (username, callback) => this.uiManager.showBetInputForm(callback));
        this.socket.on('pick', (username, callback) => this.uiManager.handleCardPick(callback));
        this.socket.on('table', (data) => this.uiManager.updateTable(data));
        this.socket.on('hand', (userCards) => this.uiManager.updateHand(userCards));
        this.socket.on('score', (users) => this.uiManager.updateScore(users));
        this.socket.on('round', (round) => this.uiManager.updateRound(round));
        this.socket.on('turn', (player) => this.uiManager.highlightPlayerTurn(player));
        this.socket.on('winner-card', (card) => this.uiManager.highlightWinnerCard(card));
        this.socket.on('final-score', (scores) => this.uiManager.showFinalScore(scores));
    }

    getRoomIDFromURL() {
        const url = window.location.href;
        return url.substring(url.lastIndexOf('/') + 1);
    }

    sendMessage(message) {
        this.socket.send({ username: this.userManager.getUsername(), message });
    }

    startGame(maxTurns, numBots) {
        this.socket.emit('start_game', { max_turns: maxTurns, num_bots: numBots });
    }
}