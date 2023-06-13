// Get the username from localStorage
let username = localStorage.getItem('username');

// Check if the username is available
if (!username) {
  // Prompt the user to enter a name
  username = prompt('Please enter your name:');
  
  // Save the entered name to localStorage
  localStorage.setItem('username', username);
}

var socket = io.connect('//' + document.domain + ':' + location.port);

// Get the current URL
var url = window.location.href;
// Extract the room ID from the URL
var roomID = url.substring(url.lastIndexOf('/') + 1);

socket.emit('join_room', roomID, username);

socket.on('error', function(msg) {
	alert(msg);
});

socket.on('message', function(msg) {
	$('#messageArea').append('<p>' + msg + '</p>');
	$('#messageArea').scrollTop($('#messageArea')[0].scrollHeight);
});

socket.on('remove_start_game_btn', function(msg) {
	const startGameButton = document.getElementById('startGameButton');
	startGameButton.remove();
});

socket.on('bet', function(username, callback) {
	showBetInputForm(function(bet) {
		callback(bet);
	});
});


socket.on('pick', function(username, callback) {
	//alert('Please choose your card!');
	bringAttention()
	
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
            callback(clickedCard);
        });
    }
});

socket.on('table', function(data) {
	var tableArea = document.getElementById('tableArea');
	
	// Clear the existing content of tableArea
	tableArea.innerHTML = '';
	
	tableCards = data.table;
	playersName = data.names;
	
	// Generate HTML code for each card and append it to tableArea
	for (var i = 0; i < tableCards.length; i++) {
		var card = tableCards[i];
		var playerName = playersName[i];
		
		var cardWrapper = document.createElement('div');
		cardWrapper.className = 'card-wrapper';
		
		var cardElement = document.createElement('div');
		cardElement.id = card;
		cardElement.className = 'card';
		cardElement.textContent = card;
		
		var playerNameElement = document.createElement('div');
        playerNameElement.className = 'player-name';
        playerNameElement.textContent = playerName;
		
		cardWrapper.appendChild(cardElement);
		cardWrapper.appendChild(playerNameElement);
		tableArea.appendChild(cardWrapper);
		
		// Display card
		playerCard1 = new Card(card);
		playerCard1.displayCard(cardElement,true);
	}
});

socket.on('hand', function(userCards) {
	var handArea = document.getElementById('handArea');
	// Clear the existing content of userHandArea
	handArea.innerHTML = '';	
	
	// Generate HTML code for each card and append it to handArea
	for (var i = 0; i < userCards.length; i++) {
		var card = userCards[i];
		var cardWrapper = document.createElement('div');
		cardWrapper.className = 'card-wrapper';
		var cardElement = document.createElement('div');
		cardElement.className = 'card';
		cardElement.textContent = card;
		cardWrapper.appendChild(cardElement);
		handArea.appendChild(cardWrapper);
		
		// Display card
		playerCard1 = new Card(card);
		playerCard1.displayCard(cardElement,true);
	}
});

socket.on('score', function(users) {
	// Display player information in the scoreArea tbody
	var tbody = document.querySelector("#scoreArea tbody");
	tbody.innerHTML = ""; // Clear the existing content

	users.forEach(function(player) {
		var playerRow = document.createElement("tr");

		var nameCell = document.createElement("td");
		nameCell.textContent = player.name;
		playerRow.appendChild(nameCell);

		var betCell = document.createElement("td");
		betCell.textContent = player.bet;
		playerRow.appendChild(betCell);

		var winsCell = document.createElement("td");
		winsCell.textContent = player.wins;
		playerRow.appendChild(winsCell);
		
		// Set the data-player attribute with the player's name
        playerRow.setAttribute("data-player", player.name);

		tbody.appendChild(playerRow);
	});
});

socket.on('turn', function(player) {
	// Get all the score table rows
    var rows = document.querySelectorAll("#scoreArea tbody tr");

    // Clear the background color from all rows
    rows.forEach(function(row) {
        row.style.backgroundColor = "";
    });
	
    // Get the score table row for the player
    var playerRow = document.querySelector("#scoreArea tbody tr[data-player='" + player + "']");

    // Add the styles to highlight the player's turn
	playerRow.style.backgroundColor = "red";
	//playerRow.style.border = '5px red solid';
    //playerRow.style.animation = 'highlight 1s infinite';
});

socket.on('winner-card', function(card) {
	const winner_card = document.getElementById(card);
	winner_card.style.border = '5px red solid';
	winner_card.style.border = '5px red solid';
	winner_card.style.animation =  'highlight 1s infinite';
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

// Bring attention for picking
function bringAttention() {
	// Get the floating text element
	const floatingText = document.getElementById('floatingText');

	// Function to start the float animation
	function startFloatAnimation() {
	  floatingText.style.animation = 'none'; // Reset the animation
	  void floatingText.offsetWidth; // Trigger a reflow
	  floatingText.style.animation = 'floatAnimation 6s forwards';
	}

	// Call the startFloatAnimation function to begin the animation
	startFloatAnimation();

}