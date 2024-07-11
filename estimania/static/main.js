document.addEventListener('DOMContentLoaded', () => {
    const userManager = new UserManager();
    const uiManager = new UIManager();
    const socketHandler = new SocketHandler(userManager, uiManager);

    socketHandler.initialize();
    uiManager.initialize(socketHandler);
});