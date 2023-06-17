from enum import Enum
import copy
import random

class Suit(Enum):
    SPADES = "\u2664"
    HEARTS = "\u2661"
    CLUBS = "\u2667"
    DIAMONDS = "\u2662"

class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

class Deck:
    def __init__(self, values, suits):
        self.base = []
        for suit in suits:
            for value in values:
                self.base.append(Card(value, suit))
        self.current = []
    
    def shuffle(self):
        self.current = copy.deepcopy(self.base)
        random.shuffle(self.current)
    
    def deal_one_card(self):
        return self.current.pop()

class Player:
    def __init__(self, seat_number):
        self.hand = []
        self.seat_number = seat_number
        self.partner_seat_number = (seat_number + 2) % 4
    
    def add_card(self, card):
        self.hand.append(card)

class EuchreTable:
    def __init__(self):
        self.players = {
            0 : Player(0),
            1 : Player(1),
            2 : Player(2),
            3 : Player(3),
        }
        values = ["9","10","J","Q","K","A"]
        suits = [Suit.SPADES, Suit.HEARTS, Suit.CLUBS, Suit.DIAMONDS]
        self.deck = Deck(values, suits)
    
    def deal_cards(self):
        self.deck.shuffle()
        num_cards = 0
        while num_cards < 5:
            for player in self.players.values():
                player.add_card(self.deck.deal_one_card())
            num_cards = num_cards + 1
    
    def print_state(self):
        for player_no, player in self.players.items():
            player_info = f"{player_no} :"
            for card in player.hand:
                player_info = player_info + f" {card.value}{card.suit.value}"
            print(player_info)

def main():
    game = EuchreTable()
    game.deal_cards()
    game.print_state()

if __name__ == "__main__":
    main()