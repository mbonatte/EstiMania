export default class SocketHandler {
    constructor(userManager, uiManager) {
        this.userManager = userManager;
        this.uiManager = uiManager;
        this.socket = null;
        console.log("Socket Handler initialized.");
    }

    initialize() {
        this.socket = io.connect('//' + document.domain + ':' + location.port);
        console.log("Socket connection initialized.");
        this.setupEventListeners();
    }

    setupEventListeners() {
        const roomID = this.getRoomIDFromURL();
        console.log(`Joining room: ${roomID}`);
        this.socket.emit('join_room', roomID, this.userManager.getUsername());

        this.socket.on('error', (msg) => this.uiManager.showError(msg));
        this.socket.on('message', (msg) => this.uiManager.appendMessage(msg));
        this.socket.on('remove_start_game_btn', () => this.uiManager.removeStartGameButton());
        this.socket.on('coach_bet_advice', (data) => this.uiManager.onCoachBetAdvice(data));
        this.socket.on('coach_card_advice', (data) => this.uiManager.onCoachCardAdvice(data));
        this.socket.on('bet', (username, callback) => this.uiManager.showBetInputForm(callback));
        this.socket.on('pick', (username, callback) => this.uiManager.handleCardPick(callback));
        this.socket.on('table', (data) => this.uiManager.updateTable(data));
        this.socket.on('hand', (userCards) => this.uiManager.updateHand(userCards));
        this.socket.on('score', (users) => this.uiManager.updateScore(users));
        this.socket.on('round', (round) => this.uiManager.updateRound(round));
        this.socket.on('turn', (player) => this.uiManager.highlightPlayerTurn(player));
        this.socket.on('winner-card', (card) => this.uiManager.highlightWinnerCard(card));
        this.socket.on('final-score', (scores) => this.uiManager.showFinalScore(scores));

        // Clean room leave on page unload / navigation
        window.addEventListener('beforeunload', () => this.leaveRoom());
        window.addEventListener('pagehide', () => this.leaveRoom());

        const leaveBtn = document.getElementById('leaveRoomBtn');
        if (leaveBtn) {
            leaveBtn.addEventListener('click', (e) => {
                this.leaveRoom();
            });
        }
    }

    leaveRoom() {
        const roomID = this.getRoomIDFromURL();
        const sid = this.socket ? this.socket.id : null;
        if (this.socket && this.socket.connected) {
            try {
                this.socket.emit('leave_room', roomID, this.userManager.getUsername());
                this.socket.disconnect();
            } catch (err) {}
        }
        try {
            if (navigator.sendBeacon) {
                const payload = JSON.stringify({ sid: sid, room_id: roomID });
                navigator.sendBeacon('/api/leave_room', new Blob([payload], { type: 'application/json' }));
            }
        } catch (err) {}
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