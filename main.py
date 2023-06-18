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
    
    def get_card_string(self):
        return f" {self.value}{self.suit.value}"


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

    def sort_hand(self, trump_suit, left_bower_suit):
        def compare_pre_trump(card : Card):
            value = 0
            if card.value == "A":
                value = 1
            elif card.value == "K":
                value = 2
            elif card.value == "Q":
                value = 3
            elif card.value == "J":
                value = 4
            elif card.value == "10":
                value = 5
            elif card.value == "9":
                value = 6

            if card.suit == Suit.SPADES:
                value = value + 0
            elif card.suit == Suit.HEARTS:
                value = value + 6
            elif card.suit == Suit.CLUBS:
                value = value + 12
            elif card.suit == Suit.DIAMONDS:
                value = value + 18
            
            return value
        
        def compare_trump(card : Card):
            value = 0
            if card.value == "J":
                if card.suit == trump_suit:
                    value = -7
                    return value
                elif card.suit == left_bower_suit:
                    value = -6
                    return value

            if card.value == "A":
                value = 1
            elif card.value == "K":
                value = 2
            elif card.value == "Q":
                value = 3
            elif card.value == "J":
                value = 4
            elif card.value == "10":
                value = 5
            elif card.value == "9":
                value = 6

            if card.suit == trump_suit:
                value = value - 6
            elif card.suit == Suit.SPADES:
                value = value + 0
            elif card.suit == Suit.HEARTS:
                value = value + 6
            elif card.suit == Suit.CLUBS:
                value = value + 12
            elif card.suit == Suit.DIAMONDS:
                value = value + 18
            
            return value
            
        self.hand.sort(key = compare_pre_trump if not trump_suit else compare_trump)
    
    def decide_trump(self, up_card):
        return up_card.suit

class EuchreTable:
    def __init__(self, test_mode = False):
        self.test_mode = test_mode
        
        self.players = {
            0 : Player(0),
            1 : Player(1),
            2 : Player(2),
            3 : Player(3),
        }
        values = ["9","10","J","Q","K","A"]
        suits = [Suit.SPADES, Suit.HEARTS, Suit.CLUBS, Suit.DIAMONDS]
        self.deck = Deck(values, suits)
        self.dealer = 0
        self.curr_seat = 0
        self.up_card = None
        self.trump_suit = None
        self.left_bower_suit = None
    
    def determine_dealer(self):
        if self.test_mode: print("Determing Dealer...")
        curr_seat = 0
        self.deck.shuffle()
        curr_card = self.deck.deal_one_card()
        if self.test_mode: print(f"({curr_seat % 4}){curr_card.get_card_string()}", end='')

        while curr_card.value != "J" or curr_card.suit not in (Suit.SPADES, Suit.CLUBS):
            curr_seat = curr_seat + 1
            curr_card = self.deck.deal_one_card()
            if self.test_mode: print(f" ({curr_seat % 4}){curr_card.get_card_string()}", end='')
        
        self.dealer = curr_seat % 4
        self.curr_seat = (self.dealer + 1) % 4
        if self.test_mode: print()

    def deal_cards(self):
        self.deck.shuffle()
        num_cards = 0
        while num_cards < 5:
            for player in self.players.values():
                player.add_card(self.deck.deal_one_card())
            num_cards = num_cards + 1
        
        self.up_card = self.deck.deal_one_card()
    
    def euchre_deal_cards(self):
        self.deck.shuffle()
        max_hand_size = 5

        num_cards_to_deal = 0
        while len(self.players[self.dealer].hand) < max_hand_size:
            player = self.players[self.curr_seat]
            if len(player.hand) == 0:
                num_cards_to_deal = 2 if num_cards_to_deal == 3 else 3
            else:
                num_cards_to_deal = max_hand_size - len(player.hand)
            
            for _ in range(num_cards_to_deal):
                player.add_card(self.deck.deal_one_card())
            if self.test_mode: self.print_state()
            
            self.curr_seat = (self.curr_seat + 1) % 4
        
        self.up_card = self.deck.deal_one_card()
        self.sort_player_hands()
        if self.test_mode: self.print_state()

    def sort_player_hands(self):
        for player in self.players.values():
            player.sort_hand(self.trump_suit, self.left_bower_suit)
    
    def determine_trump(self):
        self.curr_seat = (self.dealer + 1) % 4
        self.trump_suit = self.players[self.curr_seat].decide_trump(self.up_card)
        
        while not self.trump_suit:
            self.curr_seat = (self.curr_seat + 1) % 4
            
            ## All players passed on up card
            if self.curr_seat == (self.dealer + 1) % 4:
                self.up_card = None
            
            self.trump_suit = self.players[self.curr_seat].decide_trump(self.up_card)
        
        if self.trump_suit == Suit.SPADES:
            self.left_bower_suit = Suit.CLUBS
        elif self.trump_suit == Suit.HEARTS:
            self.left_bower_suit = Suit.DIAMONDS
        elif self.trump_suit == Suit.CLUBS:
            self.left_bower_suit = Suit.SPADES
        elif self.trump_suit == Suit.DIAMONDS:
            self.left_bower_suit = Suit.HEARTS

        self.curr_seat = (self.dealer + 1) % 4
        self.sort_player_hands()

    def print_state(self):
        ## Print Game Info
        print(f"Dealer: Player {self.dealer}")
        
        ## Print Deck
        deck_info = "Deck :"
        for card in self.deck.current:
            deck_info = deck_info + card.get_card_string()
        print(deck_info)
        
        ## Print Hands
        for player_no, player in self.players.items():
            player_info = f"{player_no} :"
            for card in player.hand:
                player_info = player_info + card.get_card_string()
            print(player_info)
        
        ## Print Up-Card or Trump
        if self.trump_suit: 
            print(f"Trump: {self.trump_suit}")
        elif self.up_card: 
            print(f"Up Card: {self.up_card.get_card_string()}")
    
    def play(self):
        self.determine_dealer()
        self.euchre_deal_cards()
        self.determine_trump()
        self.print_state()

def main():
    game = EuchreTable(True)
    game.play()

if __name__ == "__main__":
    main()