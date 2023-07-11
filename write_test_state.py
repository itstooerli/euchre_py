import json
from enum import Enum
from main import PlayerTrumpDecision
from main import PlayerCardDecision

class TestState:
    def __init__(self):
        self.state = {}

    def print_enum(self, enum_class: type[Enum]):
        for x in enum_class:
            print(f"{x.value}: {x.name}")

    def input_player_trump_decision(self):
        self.state['PlayerTrumpDecision'] = {}
        value2member_map = PlayerTrumpDecision._value2member_map_
        player_number = 0

        while player_number < 4:
            self.print_enum(PlayerTrumpDecision)
            user_input = input(f"Enter the value of the Trump Decision Logic for player {player_number}: ")
            if user_input.isnumeric() and int(user_input) in value2member_map:
                self.state['PlayerTrumpDecision'][player_number] = value2member_map[int(user_input)]
            else:
                print('Invalid entry. Try again.')
                continue
            player_number = player_number + 1

    def write(self):
        self.input_player_trump_decision()
        return self.state

def main():
    """The main body that gathers input from user"""
    new_test_state = TestState()
    test_state = new_test_state.write()
    print(test_state)

if __name__ == "__main__":
    main()