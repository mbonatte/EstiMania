export default class Card {
  constructor(card) {
      this.card = card;
      const cardValues = {
        "1 of Hearts":1, "2 of Hearts":2, "3 of Hearts":3, "4 of Hearts":4, "5 of Hearts":5, "6 of Hearts":6, "7 of Hearts":7, "8 of Hearts":8, "9 of Hearts":9, "10 of Hearts":10, "11 of Hearts":11, "12 of Hearts":12, "13 of Hearts":13,
				"1 of Diamonds":1, "2 of Diamonds":2, "3 of Diamonds":3, "4 of Diamonds":4, "5 of Diamonds":5, "6 of Diamonds":6, "7 of Diamonds":7, "8 of Diamonds":8, "9 of Diamonds":9, "10 of Diamonds":10, "11 of Diamonds":11, "12 of Diamonds":12, "13 of Diamonds":13,
				"1 of Clubs":1, "2 of Clubs":2, "3 of Clubs":3, "4 of Clubs":4, "5 of Clubs":5, "6 of Clubs":6, "7 of Clubs":7, "8 of Clubs":8, "9 of Clubs":9, "10 of Clubs":10, "11 of Clubs":11, "12 of Clubs":12, "13 of Clubs":13,
				"1 of Spades":1, "2 of Spades":2, "3 of Spades":3, "4 of Spades":4, "5 of Spades":5, "6 of Spades":6, "7 of Spades":7, "8 of Spades":8, "9 of Spades":9, "10 of Spades":10, "11 of Spades":11, "12 of Spades":12, "13 of Spades":13
      };
    
    this.value = cardValues[card];
    this.suit = card.substring(card.indexOf(" of ")+4);
    this.pl1Holder = null;
    this.flipped = false;
  
    var suits = {'Hearts':0, 'Diamonds':13, 'Clubs':26, 'Spades':39 }
    this.position = suits[this.suit] + this.value; //Position in a sorted deck
  }
  
  displayCard(pl1Holder) {
	this.pl1Holder = pl1Holder;
    this.pl1Holder.classList.add("card");
    this.pl1Holder.style.backgroundPosition = -150*this.position + "px";
  }  
}