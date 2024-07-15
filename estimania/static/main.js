import UIManager from './uiManager.js';
import UserManager from './userManager.js';
import SocketHandler from './socketHandler.js';

document.addEventListener('DOMContentLoaded', () => {
    const userManager = new UserManager();
    const uiManager = new UIManager();
    const socketHandler = new SocketHandler(userManager, uiManager);

    socketHandler.initialize();
    uiManager.initialize(socketHandler);
});