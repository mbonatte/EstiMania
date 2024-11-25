import UIManager from './uiManager.js';
import UserManager from './userManager.js';
import SocketHandler from './socketHandler.js';

document.addEventListener('DOMContentLoaded', () => {
    const userManager = new UserManager();
    const uiManager = new UIManager();
    const socketHandler = new SocketHandler(userManager, uiManager);
    
    socketHandler.initialize();
    uiManager.initialize(socketHandler);

    // Test scenario controls
    document.getElementById('loadScenario').addEventListener('click', () => {
        const scenario = document.getElementById('scenarioSelect').value;
        socketHandler.socket.emit('load_test_scenario', scenario);
        console.log(`Running: ${scenario} scenario`);
    });

    // Load initial scenario if specified in URL, else default to 'initial'
    const initialScenario = document.body.getAttribute('data-scenario') || 'initial';
    socketHandler.socket.emit('load_test_scenario', initialScenario);
    console.log(`Running: ${initialScenario} scenario`);
});