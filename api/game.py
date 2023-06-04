import random
from uuid import uuid4

class Game:

    def __init__(self, room_id, players=None):
        self.room_id = room_id
        self.players = players
        self.matches = []
        self.cards_in_table = []
        self.run()
    
    def set_matches(self):
        print(f'Setting matches')
        #from math import trunc
        #n_matches = trunc(52/self.numberOfPlayers)
        n_matches = 4
        self.matches = [i+1 for i in range(n_matches)]
        self.matches += ([i for i in range(n_matches,0,-1)])
    
    def deal(self,n_cards):
        print(f'Dealing bets')
        deck = Deck()
        for player in self.players:
            player.hand = deck.deal(n_cards)
    
    def setBets(self): 
        print(f'Setting bets')
        print("Bets:")
        for player in self.players:
            player.set_bet()
    
    def winner_of_turn(self):
        highest_card = self.cards_in_table[0]
        winner = 0
        for i,card in enumerate(self.cards_in_table):
            if card > highest_card:
                highest_card = card
                winner=i
        self.players[winner].score_in_turn += 1
        print(f'{self.players[winner].name} won this turn')
        print()
    
    def turn(self,n_cards): #This should be in the GameOnline class
        for turn in range(n_cards):
            print(f'Selecting cards ({turn+1}/{n_cards})')
            self.cards_in_table = []
            for player in self.players:
                card_played = player.select_card()
                self.cards_in_table.append(card_played)
                print(' ',player.name, ' - ',card_played)
            self.winner_of_turn()
    
    def initiateRound(self,n_cards):
        self.deal(n_cards)
        self.setBets()
        self.turn(n_cards)
        for player in self.players:
            player.check_points()
            player.print_score()

    def run(self):
        print(f'Starting game - {self.room_id}')
        self.set_matches()
        while(len(self.matches)!=0):
            print(f'Match {len(self.matches)}')
            self.initiateRound(self.matches.pop(0))
            print('----------------------------------------')
        for player in self.players:
            player.print_score()

class Player:
    def __init__(self, connection_id, room_id=None, username=None):
        self.connection_id = connection_id
        self.room_id = room_id
        if username==None:
            self.username = uuid4().hex
        else:
            self.username = username
        self.hand = []
        self.bet = -1
        self.score = 0
        self.score_in_turn = 0
        

    def set_bet(self,bet = None):
        if (bet==None):
            self.bet = int(input(f"{self.username}, what is your bet? "))
        else:
            self.bet = bet
        print(f'{self.username} = {self.bet}')
            
    def select_card(self,card = None):
        if (card==None):
            card = int(input(f"{self.username}, which card do you select ? "))
        else:
            card = card        
        if card in self.hand:
            self.hand.remove(card)
    
    def check_points(self):
        if self.bet == self.score_in_turn:
            if self.bet==0:
                self.score += 1
            else:
                self.score += 2*self.bet
        else:
            self.score -= abs(self.bet-self.score_in_turn)
        self.bet = -1
        self.score_in_turn = 0
            
    def print_score(self):
        print(f'{self.username} = {self.score}')
        
        
class Deck:
    def __init__(self):
        self.deck = []
        self.suits = ['hearts', 'diamonds', 'clubs', 'spades']
        self.ranks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        self.creat_deck()
        
    def creat_deck(self):
        for suit in self.suits:
            for rank in self.ranks:
                self.deck.append(Card(rank, suit))
        random.shuffle(self.deck)
    
    def deal(self,n_cards):
        cards = []
        for i in range(n_cards):
            cards.append(self.deck.pop(0))
        return cards
        
class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit
        
    def __str__ (self):
        return f'{self.value}_of_{self.suit}'
    
    def __eq__(self, other):
        return (self.value == other.value and
                self.suit == other.suit)


    def __gt__(self,other):
        if self.suit == other.suit:
            if int(self.value) > int(other.value):
                return True
            else:
                return False
        else:
            if self.suit == 'clubs':
                return False
            if self.suit == 'diamonds':
                return True
            if self.suit == 'spades' and other.suit != 'diamonds':
                return True
            else:
                return False
    
    def isHigherThan(self,card):
        if self.suit == card.suit:
            if int(self.value) > int(card.value):
                return True
            else:
                return False
        else:
            if self.suit == 'clubs':
                return False
            if self.suit == 'diamonds':
                return True
            if self.suit == 'spades' and card.suit != 'diamonds':
                return True
            else:
                return False