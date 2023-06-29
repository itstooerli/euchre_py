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
    RANDOM = 1

class Card:
    def __init__(self, rank: str, suit: Suit):
        """Card class constructor to initialize the object
        
        Input Arguments:
        rank -- the rank of the card
        suit -- the suit of the card
        """
        self.rank = rank
        self.suit = suit
    
    def get_card_string(self) -> str:
        """Returns the string representation of the card"""
        return f" {self.rank}{self.suit.value}"

class Deck:
    def __init__(self, ranks: list[str], suits: list[Suit]):
        """Deck class constructor to initialize the object
        
        Input Arguments:
        ranks -- a list of the possible ranks for the deck
        suits -- a list of the possible suits for the deck
        """
        self.base: list[Card] = []
        for suit in suits:
            for rank in ranks:
                self.base.append(Card(rank, suit))
        self.current: list[Card] = []
    
    def shuffle(self):
        """Resets the current deck as a shuffled copy of the base deck"""
        self.current = copy.deepcopy(self.base)
        random.shuffle(self.current)
    
    def deal_one_card(self) -> Card:
        """Removes a card from the current deck"""
        return self.current.pop()
    
    def add_back_to_deck(self, card: Card):
        """Adds a card back to the current deck
        
        Input Arguments:
        card -- the card to add back to the current deck
        """
        self.current.append(card)

class Player:
    def __init__(self,
                 seat_number: int, 
                 is_user: bool = False, 
                 trump_decision_logic: PlayerTrumpDecision = PlayerTrumpDecision.ALWAYS_ACCEPT, 
                 card_decision_logic: PlayerCardDecision = PlayerCardDecision.RANDOM):
        """Player class constructor to initialize the object
        
        Input Arguments:
        seat_number -- the number from 0 to 3 representing the position of the player
        is_player   -- boolean indicating whether the player is a human user
        trump_decision_logic -- the logic this player uses during the trump decision phase
        card_decision_logic  -- the logic this player uses during the trick taking phase
        """
        self.hand: list[Card] = []
        self.seat_number = seat_number
        self.partner_seat_number = (seat_number + 2) % 4
        self.is_user = is_user
        self.trump_decision_logic = trump_decision_logic if trump_decision_logic is not None else PlayerTrumpDecision.ALWAYS_ACCEPT
        self.card_decision_logic = card_decision_logic if card_decision_logic is not None else PlayerCardDecision.RANDOM
    
    def add_card(self, card: Card):
        """Add a card to the player's hand"""
        self.hand.append(card)

    def sort_hand(self, trump_suit: Suit, left_bower_suit: Suit):
        """Rearrange the player's hand in the order [SPADES, HEARTS, CLUBS, DIAMONDS] and appropriate trump order
        
        Input Arguments:
        trump_suit      -- the suit decided to be trump for this round
        left_bower_suit -- the suit of the other Jack that is trump (if trump is SPADES, left bower is CLUBS)
        """
        def compare_trump(card : Card):
            value = 0
            if trump_suit and card.rank == "J":
                if card.suit == trump_suit:
                    value = -7
                    return value
                elif card.suit == left_bower_suit:
                    value = -6
                    return value

            if card.rank == "A":
                value = 1
            elif card.rank == "K":
                value = 2
            elif card.rank == "Q":
                value = 3
            elif card.rank == "J":
                value = 4
            elif card.rank == "10":
                value = 5
            elif card.rank == "9":
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
            
        self.hand.sort(key = compare_trump)
    
    def decide_trump(self, up_card: Card, hidden_up_card: Card):
        """Decide whether the player wishes to serve trump based on the trump decision logic, returns the suit if decided, None if passed
        
        Input Arguments:
        up_card        -- the card being offered to determine trump suit
        hidden_up_card -- the now-hidden up_card which cannot be chosen as trump if previously passed on
        """
        if self.trump_decision_logic == PlayerTrumpDecision.ALWAYS_ACCEPT:
            return up_card.suit
        elif self.trump_decision_logic == PlayerTrumpDecision.RANDOM:
            if up_card:
                return random.choice([up_card.suit, None])
            else:
                return random.choice([e.value for e in Suit if e != hidden_up_card.suit] + [None])

        return up_card.suit

    def play_card(self, trump_suit: Suit, left_bower_suit: Suit, lead_seat: int, cards_played: list[Card]):
        """Decide which card the player will play based on the card decision logic, returns the Card
        
        Input Arguments:
        trump_suit      -- the trump suit
        left_bower_suit -- the suit of the left bower
        lead_seat       -- the seat that led suit
        cards_played    -- an array of length 4 of Cards, None if the seat has not played yet
        """
        lead_card = cards_played[lead_seat]
        if not lead_card:
            playable_cards = self.hand
        else:
            playable_cards = []

            for card in self.hand:
                if lead_card.suit == trump_suit and card.suit == left_bower_suit and card.rank == "J":
                    playable_cards.append(card)
                elif lead_card.suit == left_bower_suit and lead_card.rank == "J" and card.suit == trump_suit:
                    playable_cards.append(card)
                elif lead_card.suit == card.suit:
                    if card.rank == "J" and card.suit == left_bower_suit:
                        continue
                    else:
                        playable_cards.append(card)
            
            if not playable_cards:
                playable_cards = self.hand

        if self.card_decision_logic == PlayerCardDecision.RANDOM:
            choice = random.choice(playable_cards)
            self.hand.remove(choice)
            return choice
        
        return self.hand.pop()

class EuchreTable:
    def __init__(self, 
                 trump_logic: dict[int, PlayerTrumpDecision] = {}, 
                 play_logic: dict[int, PlayerCardDecision] = {},
                 test_mode: bool = False):
        """EuchreTable class constructor to initialize the object

        Input Arguments:
        trump_logic -- a dictionary holding each player's trump decision logic
        play_logic  -- a dictionary holding each player decision logic for which card to play
        test_mode   -- boolean for whether to run the table in test mode, True if yes
        """
        self.test_mode = test_mode
        self.players = {
            0 : Player(0, False, trump_logic.get(0, None), play_logic.get(0, None)),
            1 : Player(1, False, trump_logic.get(1, None), play_logic.get(1, None)),
            2 : Player(2, False, trump_logic.get(2, None), play_logic.get(2, None)),
            3 : Player(3, False, trump_logic.get(3, None), play_logic.get(3, None)),
        }
        ranks = ["9","10","J","Q","K","A"]
        suits = [Suit.SPADES, Suit.HEARTS, Suit.CLUBS, Suit.DIAMONDS]
        self.deck = Deck(ranks, suits)
        self.dealer = 0
        self.curr_seat = 0
        self.up_card = None
        self.hidden_up_card = None
        self.trump_suit = None
        self.left_bower_suit = None
        self.lead_seat = None
        self.trump_caller = None
        self.score_02 = 0
        self.score_13 = 0
        self.cards_played = {0 : None, 1 : None, 2 : None, 3 : None}
        self.tricks_won_02 = 0
        self.tricks_won_13 = 0
    
    def is_value_bigger(self, card1: Card, card2: Card):
        """Returns True if the value of card1 is greater than card2"""
        value1 = self.assign_card_value(card1)
        value2 = self.assign_card_value(card2)
        return value1 > value2
    
    def assign_card_value(self, card: Card):
        """Returns the relative ranking of the card in euchre w/o trump"""
        if card.rank == "9":
            return 0
        elif card.rank == "10":
            return 1
        elif card.rank == "J":
            return 2
        elif card.rank == "Q":
            return 3
        elif card.rank == "K":
            return 4
        elif card.rank == "A":
            return 5
        return 0

    def determine_dealer(self):
        """Runs the phase to determine the dealer - currently, the seat w/ the first black jack"""
        if self.test_mode: print("Determing Dealer...")
        curr_seat = 0
        self.deck.shuffle()
        curr_card = self.deck.deal_one_card()
        if self.test_mode: print(f"({curr_seat % 4}){curr_card.get_card_string()}", end='')

        while curr_card.rank != "J" or curr_card.suit not in (Suit.SPADES, Suit.CLUBS):
            curr_seat = curr_seat + 1
            curr_card = self.deck.deal_one_card()
            if self.test_mode: print(f" ({curr_seat % 4}){curr_card.get_card_string()}", end='')
        
        self.dealer = curr_seat % 4
        self.curr_seat = (self.dealer + 1) % 4
        if self.test_mode: print()
    
    def euchre_deal_cards(self):
        """Resets the deck and deals 5 cards to each player, in euchre-fashion"""
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
        """Sorts each of the player's hands in suit order then euchre-rank order"""
        for player in self.players.values():
            player.sort_hand(self.trump_suit, self.left_bower_suit)
    
    def determine_trump(self):
        """Runs the phase to determine the trump"""
        self.curr_seat = (self.dealer + 1) % 4
        self.trump_suit = self.players[self.curr_seat].decide_trump(self.up_card, self.hidden_up_card)
        
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
            
            self.trump_suit = self.players[self.curr_seat].decide_trump(self.up_card, self.hidden_up_card)
        
        if self.trump_suit == Suit.SPADES:
            self.left_bower_suit = Suit.CLUBS
        elif self.trump_suit == Suit.HEARTS:
            self.left_bower_suit = Suit.DIAMONDS
        elif self.trump_suit == Suit.CLUBS:
            self.left_bower_suit = Suit.SPADES
        elif self.trump_suit == Suit.DIAMONDS:
            self.left_bower_suit = Suit.HEARTS
        
        self.trump_caller = self.curr_seat
        print(f"Seat {self.trump_caller} determined trump.")

        self.curr_seat = (self.dealer + 1) % 4
        self.sort_player_hands()
        return True

    def play_trick(self):
        """Runs the phase to play a trick (1 card played by each player)"""
        num_cards_played = 0
        while num_cards_played < 4:
            self.cards_played[self.curr_seat] = self.players[self.curr_seat].play_card(self.trump_suit, self.left_bower_suit, self.lead_seat, self.cards_played)
            print("Table")
            for player in self.cards_played:
                print(f"{player} : {self.cards_played[player].get_card_string() if self.cards_played[player] else 'None'}")
            self.curr_seat = (self.curr_seat + 1) % 4
            num_cards_played = num_cards_played + 1
        self.process_trick()
        input("Press Enter to continue...")
    
    def process_trick(self):
        """Determines which team won the trick and updates the number of tricks won appropriately"""
        cards_processed = 0
        seat_processing = self.lead_seat
        winning_player = -1
        while cards_processed < 4:
            if seat_processing == self.lead_seat:
                lead_suit = self.cards_played[self.lead_seat].suit
            
            if winning_player == -1:
                winning_player = seat_processing
            else:
                if self.cards_played[winning_player].suit == self.trump_suit:
                    if self.cards_played[winning_player].rank == "J":
                        pass
                    elif self.cards_played[seat_processing].suit == self.left_bower_suit and self.cards_played[seat_processing].rank == "J":
                        ## Left Bower
                        winning_player = seat_processing
                    elif self.cards_played[seat_processing].suit == self.trump_suit:
                        if self.is_value_bigger(self.cards_played[seat_processing], self.cards_played[winning_player]):
                            winning_player = seat_processing
                elif self.cards_played[winning_player].suit == self.left_bower_suit and self.cards_played[winning_player].rank == "J":
                    if self.cards_played[seat_processing].suit == self.trump_suit and self.cards_played[seat_processing].rank == "J":
                        winning_player = seat_processing
                elif self.cards_played[seat_processing].suit == self.trump_suit:
                    winning_player = seat_processing
                elif self.cards_played[seat_processing].suit == self.left_bower_suit and self.cards_played[seat_processing].rank == "J":
                    winning_player = seat_processing
                else:
                    if self.cards_played[seat_processing].suit == lead_suit:
                        if self.is_value_bigger(self.cards_played[seat_processing], self.cards_played[winning_player]):
                            winning_player = seat_processing
            cards_processed = cards_processed + 1
            seat_processing = (seat_processing + 1) % 4
        
        print(f"Player {winning_player} wins the trick")
        if winning_player in (0,2):
            self.tricks_won_02 = self.tricks_won_02 + 1
        else:
            self.tricks_won_13 = self.tricks_won_13 + 1
        self.curr_seat = winning_player
        print(f"[TRICKS] Team 02: {self.tricks_won_02} - Team 13: {self.tricks_won_13}")
    
    def play_round(self):
        """Runs the phase to play the euchre round, where each player plays each of the 5 cards"""
        self.euchre_deal_cards()
        self.print_state()
        if not self.determine_trump():
            self.print_state()
            input("No trump. Press Enter to continue...")
            self.dealer = (self.dealer + 1) % 4
            self.curr_seat = (self.dealer + 1) % 4
            return
        self.print_state()
        
        self.tricks_won_02 = self.tricks_won_13 =  0
        while self.tricks_won_02 + self.tricks_won_13 < 5:
            self.print_state()
            self.lead_seat = self.curr_seat
            self.cards_played = {0 : None, 1 : None, 2 : None, 3 : None}
            self.play_trick()
        self.process_round()

        input("Press Enter to continue...")
        self.dealer = (self.dealer + 1) % 4
        self.curr_seat = (self.dealer + 1) % 4
    
    def process_round(self):
        """Determines who won the most tricks and updates the score appropriately"""
        if self.trump_caller in (0, 2):
            if self.tricks_won_02 == 5:
                self.score_02 = self.score_02 + 2
            elif self.tricks_won_02 >= 3:
                self.score_02 = self.score_02 + 1
            else:
                self.score_13 = self.score_13 + 2
        else:
            if self.tricks_won_13 == 5:
                self.score_13 = self.score_13 + 2
            elif self.tricks_won_13 >= 3:
                self.score_13 = self.score_13 + 1
            else:
                self.score_02 = self.score_02 + 2
        
        print(f"[SCORE] Team 02: {self.score_02} - Team 13: {self.score_13}")

    def print_state(self):
        """Prints the current state of the game"""
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
        """Plays a game of euchre until a team has 10 points"""
        self.determine_dealer()
        while self.score_02 < 10 and self.score_13 < 10:
            self.play_round()

def main():
    """The main body that initializes the game and plays"""
    player_trump_decision = {0 : PlayerTrumpDecision.RANDOM,
                             1 : PlayerTrumpDecision.RANDOM,
                             2 : PlayerTrumpDecision.RANDOM,
                             3 : PlayerTrumpDecision.RANDOM,}
    player_play_decision = {0 : PlayerCardDecision.RANDOM,
                            1 : PlayerCardDecision.RANDOM,
                            2 : PlayerCardDecision.RANDOM,
                            3 : PlayerCardDecision.RANDOM,}
    game = EuchreTable(player_trump_decision, player_play_decision, True)
    game.play()

if __name__ == "__main__":
    main()