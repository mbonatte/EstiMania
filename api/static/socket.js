// Get the username from localStorage
let username = localStorage.getItem('username');

// Check if the username is available
if (!username) {
  // Prompt the user to enter a name
  username = prompt('Please enter your name:');
  
  // Save the entered name to localStorage
  localStorage.setItem('username', username);
}

var socket = io.connect('https://' + document.domain + ':' + location.port);

// Get the current URL
var url = window.location.href;
// Extract the room ID from the URL
var roomID = url.substring(url.lastIndexOf('/') + 1);
socket.emit('join_room', roomID);  // Emit a custom event to join the room

socket.emit('username_response', username);

socket.on('error', function(msg) {
	alert(msg);
});

socket.on('message', function(msg) {
	$('#messageArea').append('<p>' + msg + '</p>');
	$('#messageArea').scrollTop($('#messageArea')[0].scrollHeight);
});

socket.on('bet', function(username, callback) {
	console.log('initiaing betting')
	showBetInputForm(function(bet) {
		callback(bet);
	});
	console.log('bet finished')
});


socket.on('pick', function(username, callback) {
	socket.send({username: username, message: 'is choosing card'});
	alert('Please choose your card!');
	
	// List of card elements with class 'card'
    var cardElements = document.getElementsByClassName('card');
	
	// Add event listeners to each card element
    for (var i = 0; i < cardElements.length; i++) {
        cardElements[i].addEventListener('click', function(event) {
            var clickedCard = event.target.textContent;
            //selectedCard = clickedCard;

            // Disable further card clicks to prevent multiple selections
            disableCardSelection();

            // Send the selected card back to the server
			console.log('Clicked card:', clickedCard);
            callback(clickedCard);
        });
    }
});

socket.on('table', function(tableCards) {
	var tableArea = document.getElementById('tableArea');
	
	// Clear the existing content of tableArea
	tableArea.innerHTML = '';
	
	// Generate HTML code for each card and append it to tableArea
	for (var i = 0; i < tableCards.length; i++) {
		var card = tableCards[i];
		var cardElement = document.createElement('div');
		cardElement.className = 'card';
		cardElement.textContent = card;
		tableArea.appendChild(cardElement)
		
		// Display card
		playerCard1 = new Card(card);
		playerCard1.displayCard(cardElement,true);
	}
});

socket.on('hand', function(userCards) {
	console.log('cards dealing')
	var handArea = document.getElementById('handArea');
	// Clear the existing content of userHandArea
	handArea.innerHTML = '';	
	
	// Generate HTML code for each card and append it to handArea
	for (var i = 0; i < userCards.length; i++) {
		var card = userCards[i];
		var cardElement = document.createElement('div');
		cardElement.className = 'card';
		cardElement.textContent = card;
		handArea.appendChild(cardElement)
		
		// Display card
		playerCard1 = new Card(card);
		playerCard1.displayCard(cardElement,true);
	}
	console.log('cards showing')
});

socket.on('score', function(users) {
	var userListHTML = '';
	for (var i = 0; i < users.length; i++) {
		userListHTML += '<p>' + users[i] + '</p>';
	}
	$('#scoreArea').html(userListHTML);
});

$('form#chatForm').submit(function(event) {
	event.preventDefault();
	var messageInput = $('input#message');
	var message = messageInput.val();
	socket.send({username: username, message: message});
	messageInput.val('');
});

$('button#startGameButton').click(function(event) {
	socket.emit('start_game');
});

$('button#drawCardButton').click(function(event) {
	socket.emit('draw_card');
});


function disableCardSelection() {
    // List of card elements with class 'card'
    var cardElements = document.getElementsByClassName('card');

    // Disable click event listeners on all card elements
    for (var i = 0; i < cardElements.length; i++) {
        cardElements[i].removeEventListener('click', function(event){});
    }
}

// Function to show the bet input modal
function showBetInputForm(callback) {
  const betModal = document.getElementById('betModal');
  const betInput = document.getElementById('betInput');
  const submitBetButton = document.getElementById('submitBetButton');

  // Show the bet input modal
  betModal.style.display = 'block';

  // Function to handle bet submission
  function submitBet() {
    // Get the bet value from the input
    const bet = parseInt(betInput.value);

    // Hide the bet input modal
    betModal.style.display = 'none';

    // Invoke the callback function with the bet value
    callback(bet);
  }

  // Attach event listener to submit button
  submitBetButton.addEventListener('click', submitBet);
}