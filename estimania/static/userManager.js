export default class UserManager {
    constructor() {
        this.username = this.getStoredUsername() || this.promptForUsername();
        console.log(`User Manager initialized with username: ${this.getUsername()}`);
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