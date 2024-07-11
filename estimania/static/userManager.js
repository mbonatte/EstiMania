class UserManager {
    constructor() {
        this.username = this.getStoredUsername() || this.promptForUsername();
    }

    getStoredUsername() {
        return localStorage.getItem('username');
    }

    promptForUsername() {
        const username = prompt('Please enter your name:');
        localStorage.setItem('username', username);
        return username;
    }

    getUsername() {
        return this.username;
    }
}