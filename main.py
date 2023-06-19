from enum import Enum
import copy
import random

class Suit(Enum):
    SPADES = "\u2664"
    HEARTS = "\u2661"
    CLUBS = "\u2667"
    DIAMONDS = "\u2662"

class PlayerTrumpDecision(Enum):
    PLAYER = 0
    ALWAYS_ACCEPT = 1
    RANDOM = 2

class PlayerCardDecision(Enum):
    PLAYER = 0
    LAST_CARD = 1
    RANDOM = 2

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
    
    def add_back_to_deck(self, card):
        self.current.append(card)

class Player:
    def __init__(self, seat_number, is_player = False, trump_decision_logic = PlayerTrumpDecision.ALWAYS_ACCEPT, card_decision_logic = PlayerCardDecision.LAST_CARD):
        self.hand = []
        self.seat_number = seat_number
        self.partner_seat_number = (seat_number + 2) % 4
        self.is_player = is_player
        self.trump_decision_logic = trump_decision_logic
        self.card_decision_logic = card_decision_logic
    
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
    
    def decide_trump(self, up_card, hidden_up_card, dealer):
        ## TODO: Add AI to determine whether choosing trump is worth it
        if self.trump_decision_logic == PlayerTrumpDecision.ALWAYS_ACCEPT:
            return up_card.suit
        elif self.trump_decision_logic == PlayerTrumpDecision.RANDOM:
            if up_card:
                return random.choice([up_card.suit, None])
            else:
                return random.choice([e.value for e in Suit if e != hidden_up_card.suit] + [None])

        return up_card.suit

    def play_card(self, lead_seat, cards_played):
        ## TODO
        if self.card_decision_logic == PlayerCardDecision.LAST_CARD:
            return self.hand.pop()
        
        return self.hand.pop()

class EuchreTable:
    def __init__(self, trump_logic = [], test_mode = False):
        self.test_mode = test_mode
        
        self.players = {
            0 : Player(0, False, trump_logic[0] if len(trump_logic) > 0 else None),
            1 : Player(1, False, trump_logic[1] if len(trump_logic) > 1 else None),
            2 : Player(2, False, trump_logic[2] if len(trump_logic) > 2 else None),
            3 : Player(3, False, trump_logic[3] if len(trump_logic) > 3 else None),
        }
        values = ["9","10","J","Q","K","A"]
        suits = [Suit.SPADES, Suit.HEARTS, Suit.CLUBS, Suit.DIAMONDS]
        self.deck = Deck(values, suits)
        self.dealer = 0
        self.curr_seat = 0
        self.up_card = None
        self.hidden_up_card = None
        self.trump_suit = None
        self.left_bower_suit = None
        self.lead_seat = None
        self.score_02 = 0
        self.score_13 = 0
        self.cards_played = {0 : None, 1 : None, 2 : None, 3 : None}
        self.tricks_won_02 = 0
        self.tricks_won_13 = 0
    
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
        self.trump_suit = self.players[self.curr_seat].decide_trump(self.up_card, self.hidden_up_card, self.dealer)
        
        while not self.trump_suit:
            print(f"Seat {self.curr_seat} passes.")
            self.curr_seat = (self.curr_seat + 1) % 4
            
            ## All players passed on up card
            if self.curr_seat == (self.dealer + 1) % 4:
                if self.up_card:
                    self.hidden_up_card = self.up_card
                    self.deck.add_back_to_deck(self.up_card)
                    self.up_card = None
                else:
                    return False
            
            self.trump_suit = self.players[self.curr_seat].decide_trump(self.up_card, self.hidden_up_card, self.dealer)
        
        if self.trump_suit == Suit.SPADES:
            self.left_bower_suit = Suit.CLUBS
        elif self.trump_suit == Suit.HEARTS:
            self.left_bower_suit = Suit.DIAMONDS
        elif self.trump_suit == Suit.CLUBS:
            self.left_bower_suit = Suit.SPADES
        elif self.trump_suit == Suit.DIAMONDS:
            self.left_bower_suit = Suit.HEARTS
        
        print(f"Seat {self.curr_seat} determined trump.")

        self.curr_seat = (self.dealer + 1) % 4
        self.sort_player_hands()
        return True

    def play_trick(self):
        num_cards_played = 0
        while num_cards_played < 4:
            self.cards_played[self.curr_seat] = self.players[self.curr_seat].play_card(self.lead_seat, self.cards_played)
            print("Table")
            for player in self.cards_played:
                print(f"{player} : {self.cards_played[player].get_card_string() if self.cards_played[player] else 'None'}")
            self.curr_seat = (self.curr_seat + 1) % 4
            num_cards_played = num_cards_played + 1
        self.process_trick()
    
    def process_trick(self):
        ## TODO
        self.tricks_won_02 = self.tricks_won_02 + 1
        self.print_state()
        print(f"Team 02: {self.tricks_won_02} - Team 03: {self.tricks_won_13}")
    
    def play_round(self):
        while self.tricks_won_02 + self.tricks_won_13 < 5:
            self.lead_seat = self.curr_seat
            self.cards_played = {0 : None, 1 : None, 2 : None, 3 : None}
            self.play_trick()

    def print_state(self):
        ## Print Game Info
        print(f"Dealer: Player {self.dealer}")
        if self.trump_suit: print(f"Seat {self.curr_seat} turn")
        
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
        while True:
            self.euchre_deal_cards()
            self.print_state()
            if not self.determine_trump():
                ## TODO: If dealer, stuck or reshuffle TBD
                self.print_state()
                input("No trump. Press Enter to continue...")
                continue
            self.print_state()
            self.play_round()
            if self.test_mode: break
            input("Press Enter to continue...")

def main():
    game = EuchreTable([PlayerTrumpDecision.RANDOM, PlayerTrumpDecision.RANDOM, PlayerTrumpDecision.RANDOM, PlayerTrumpDecision.RANDOM], True)
    game.play()

if __name__ == "__main__":
    main()