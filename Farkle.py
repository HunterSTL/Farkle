import random
from collections import Counter

DICE_ID_COUTNER = 1
PLAYER_ID_COUNTER = 1

class Dice():
    def __init__(self):
        global DICE_ID_COUTNER
        self.value = 1
        self.ID = DICE_ID_COUTNER
        DICE_ID_COUTNER += 1

    def roll(self):
        self.value = random.randint(1, 6)

class Player():
    def __init__(self, name):
        global PLAYER_ID_COUNTER
        self.name = name
        self.total_score = 0
        self.turn_score = 0
        self.ID = PLAYER_ID_COUNTER
        PLAYER_ID_COUNTER += 1
    
    def reset_turn_score(self):
        self.turn_score = 0
    
    def bank(self):
        self.total_score += self.turn_score
        self.turn_score = 0

class Game():
    def __init__(self, score_to_win):
        self.score_to_win = score_to_win
        self.players = [Player("Farkler"), Player("Swine")]                     #Create 2 players
        self.available_dice = [Dice() for _ in range(6)]                        #Create 6 dice
        self.selected_dice = []
        self.player_index = 0
        self.game_over = 0

    def roll_available_dice(self):
        for dice in self.available_dice:
            dice.roll()

    def switch_players(self):
        self.player_index = (self.player_index + 1) % len(self.players)

    def check_winner(self):
        for player in self.players:
            if player.total_score > self.score_to_win:
                self.game_over = 1
                print(f"{player.name} wins with a score of {str(player.total_score)}")

    def print_roll(self):
        values = []
    
        for dice in self.available_dice:
            values.append(dice.value)
        values.sort()

        string = ""

        for value in values:
            string += str(value) + ", "
        return string[:-2]

    def select_dice_by_selection(self, selection):
        selected_dice = []
        available_dice = self.available_dice.copy()

        for value in selection:                                                 #For each value in the list find the first dice with the corresponding value
            for dice in available_dice:
                if dice.value == value:                                         #Once the corresponding dice has been found move it from available_dice to selected_dice
                    selected_dice.append(dice)
                    available_dice.remove(dice)
                    break
        return [selected_dice, available_dice]

    def get_mends(self, selected_dice):
        """
        Melds:
        5               50
        1               100
        triple 2        200
        triple 3        300
        triple 4        400
        triple 5        500
        triple 6        600
        triple 1        1000
        four of a kind  1000
        three pair      1500
        five of a kind  2000
        full run        2500
        six of a kind   3000
        """
        mends = []
        selection = [dice.value for dice in selected_dice]                      #Convert the selected_dice into a list of integers
        selection_counts = Counter(selection)                                   #Count how many times each value appears in selection

        if len(selection) == 6:                                                 #Only check for six of a kind, full run and three pairs if 6 dice have been selected
            #Check for six of a kind
            for value, count in selection_counts.items():
                if count == 6:
                    return (f"six_of_a_kind_{value}s", 3000)

            #Check for full run
            all_values_once = True
            for value, count in selection_counts.items():
                if count != 1:
                    all_values_once = False
                    break
            if all_values_once:
                return ("full_run", 2500)

            #Check for three pairs
            pair_count = 0
            for value, count in selection_counts.items():
                if count == 2:
                    pair_count += 1
            if pair_count == 3:
                return ("three_pairs", 1500)

        #Check for scorable combinations
        for value, count in selection_counts.items():
            if count == 5:
                mends.append((f"five_of_a_kind_{value}s", 2000))
            elif count == 4:
                mends.append((f"four_of_a_kind_{value}s", 1000))
            elif count == 3 and value == 1:
                mends.append(("three_of_a_kind_1s", 1000))
            elif count == 3:
                mends.append((f"three_of_a_kind_{value}s", value * 100))
            elif value == 1:
                mends.append((f"ones_{count}", count * 100))
            elif value == 5:
                mends.append((f"fives_{count}", count * 50))
            else:
                return []                                                           #If no other condition is met the input is invalid (e.g. 1114, because you can't score a single 4)
        return mends

    def is_valid_scoring(self, selected_dice):                                      #Checks whether there is at least one mend in the selection
        mends = self.get_mends(selected_dice)
        if len(mends) > 0:
            return True
        else:
            return False

    def is_valid_input(self, dice_input_string):
        if not dice_input_string.isdigit():                                         #Check if all characters are digits
            return False
        
        selection = [int(digit) for digit in dice_input_string]                     #Convert the string into a list of integers ("12225" --> [1, 2, 2, 2, 5])
        selection_counts = Counter(selection)                                       #Count how many times each value appears in selection
        current_roll_values = [dice.value for dice in self.available_dice]          #Put the values of the rolled dice into a list
        rolled_counts = Counter(current_roll_values)                                #Count how many times each value appears in the current roll

        for value in selection_counts:                                              #Check whether there are more occurrences of a value in the selection than the current roll
            if selection_counts[value] > rolled_counts.get(value, 0):
                return False
        [selected_dice, available_dice] = self.select_dice_by_selection(selection)  #The dice are selected after it's confirmed that there's a dice for each digit in the dice_input_string
        if self.is_valid_scoring(selected_dice):                                    #Check whether the selected dice make valid mends (no lone 2s, 3s, 4s, and 6s)
            self.selected_dice = selected_dice
            self.available_dice = available_dice
            return True

    def is_farkle(self):                                                            #Returns True when there are no possible mends (=Farkle)
        roll_values = [dice.value for dice in self.available_dice]
        roll_values_count = Counter(roll_values)

        if len(roll_values) == 6:                                                   #Only check for full run and three pairs if 6 dice were thrown
            if all(count == 1 for count in roll_values_count.values()):
                return False    #full run
            if list(roll_values_count.values()).count(2) == 3:
                return False    #three pairs

        for value, count in roll_values_count.items():
            if count >= 3:
                return False    #at least three of a kind
            if value == 1 or value == 5:
                return False    #at least one 1 or 5 
        return True             #no scorable dice

    def score_selection(self, selected_dice):                                       #Returns the score for the selection
        mends = self.get_mends(selected_dice)
        score = 0
        for (mend_name, mend_score) in mends:
            score += mend_score
        return score

    def play_turn(self):
        player = self.players[self.player_index]
        self.available_dice = [Dice() for _ in range(6)]  # Start with fresh 6 dice
        self.selected_dice = []
        player.reset_turn_score()

        while True:
            self.roll_available_dice()
            print(player.name + " rolls: " + self.print_roll())

            if self.is_farkle():
                print("Farkle! Turn score lost.")
                player.reset_turn_score()
                break

            dice_input_string = input("Enter the dice you want to score: ")
            while not self.is_valid_input(dice_input_string):
                dice_input_string = input("Invalid input. Try again: ")

            score = self.score_selection(self.selected_dice)
            player.turn_score += score
            print(f"Turn score: {player.turn_score}")

            remaining_dice_count = len(self.available_dice)

            if remaining_dice_count == 0:
                self.available_dice = [Dice() for _ in range(6)]
                print("🔥 Hot dice! You get to roll all six again.")
            else:
                action = input(f"Roll remaining {remaining_dice_count} dice (r) or bank {player.turn_score} points (b)? ")
                while action not in ["r", "b"]:
                    action = input("Invalid input. Type 'r' to roll or 'b' to bank: ")

                if action == "b":
                    player.bank()
                    break

    def play(self):
        print("Welcome to Farkle!")
        while self.game_over != 1:
            self.play_turn()
            self.switch_players()
            self.check_winner()

farkle = Game(10000)
farkle.play()