import random
from os import system
import time

buy_in = 100

class Cards:
    deck = []

    def __init__(self, value, suit):
        self.value = value
        if value == 14:
            self.low_ace_value = 1
        else:
            self.low_ace_value = value
        self.suit = suit
        self.active = False
        __class__.deck.append(self)


class Game:
    speed = 1.5
    players = []
    active_players = []
    min_bet = 2
    dealer_index = -1
    turn_index = 0
    table_cards = []
    pot = 0
    first_bet = False
    call_stake = 0
    turn_counter = 0

    def __init__(self, name, is_human, stack):
        self.name = name
        self.is_human = is_human
        self.active = True
        self.is_dealer = False
        self.is_all_in = False
        self.cards = []
        self.best_combination = []
        self.stack = stack
        self.stake = 0  # this is only the amount staked in the current betting round
        __class__.players.append(self)

    # no need to check if amount is greater than stack as this will be checked already
    # Sets the players stake to the input value
    def set_stake(self, amount):
        increase = amount - self.stake
        self.stake = amount
        self.stack -= increase
        Game.pot += increase
        print_bet(self, increase)
        if self.stake > Game.call_stake:
            Game.call_stake = self.stake

    # returns the amount required to raise the call_stake by the input amount, or whatever amount will take the player all_in
    def raise_amount(self, prompt):
        amount = input_int(prompt)
        new_stake = Game.call_stake + amount
        stake_increase = new_stake - self.stake
        if Game.call_stake + amount > self.stack:
            return self.all_in
        elif 0 <= stake_increase < self.stack:
            return new_stake
        else:
            print("Unexpected error")
            self.raise_amount() 
            
    def fold(self):
        self.active = False
        Game.active_players.remove(self)
        print(self.name + " folds their cards")

    def all_in(self):
        print(self.name + " is all in!")
        self.is_all_in = True
        return self.stack + self.stake

    def leave_game(self):
        time.sleep(1 * Game.speed)
        print(self.name + " leaves the game")
        Game.players.remove(self)
    
    def place_first_bet(self):
        if self.is_all_in or not self.active:
            return
        print("\n" + self.name + " Please choose from the following:")
        choice = input("1 -> Check\n2 -> Bet\n3 -> Fold\n")
        if choice == "1":
            return
        elif choice == "2":
            self.set_stake(self.raise_amount("\nEnter bet amount: "))
            Game.first_bet = False
            return
        elif choice == "3":
            self.fold()
            return
        else:
            print("Invalid Selection")
            self.place_first_bet()
            
    def place_bet(self):
        if self.is_all_in or not self.active:
            return
        print("\n" + self.name + " Please choose from the following:")
        choice = input("1 -> Call\n2 -> Raise\n3 -> Fold\n")
        if choice == "1":
            print()
            if self.stack > Game.call_stake - self.stake:
                self.set_stake(Game.call_stake)
            else:
                self.set_stake(self.all_in())
        elif choice == "2":
            self.set_stake(self.raise_amount("\nEnter raise amount: "))
            return
        elif choice == "3":
            self.fold()
            return
        else:
            print("Invalid Selection")
            self.place_bet()


def number_of_players():
    number_of_players = input_int("Select number of players from 2 to 10.\t")
    if 2 <= number_of_players <= 10:
        return int(number_of_players)
    else:
        print("Input is out of acceptable range.")
        number_of_players()


def new_player_name(player_number):
    name = input("Please enter a name for Player " + str(player_number) + "\t")
    if name == "":
        name = str("Player " + str(player_number))
    name_exists = False
    for player in Game.players:
        if player.name == name:
            name_exists = True
    if name_exists:
        print("That name is taken!\n")
        name = new_player_name(player_number)
    return name


def create_players(number_of_players):
    players = []
    for i in range(number_of_players):
        name = new_player_name(i + 1)
        Game(name, True, buy_in)
    return


# creates the deck
# numbers are used for picture card to simplify the scoring logic
# the get_card_name function will enable picture card names to be printed
def set_up_game():
    suits = ("diamonds", "hearts", "clubs", "spades")
    for i in range(4):
        for j in range(2, 15):
            Cards(j, suits[i])


def new_round():
    print("\n\nStarting new round...\n\n")
    time.sleep(1 * Game.speed)
    Game.table_cards = []
    Game.pot = 0
    Game.call_stake = 0
    Game.active_players = []
    for player in Game.players:
        player.active = True
        player.is_all_in = False
        player.cards = []
        player.best_combination = []
        player.stake = 0
        Game.active_players.append(player)
    for card in Cards.deck:
        card.active = False
    Game.players[Game.dealer_index].is_dealer = False
    Game.dealer_index = next_player(Game.dealer_index, 1)
    Game.players[Game.dealer_index].is_dealer = True


# This is needed as a function for the scoring process
def get_value(card):
        return card.value


def get_card_name(card):
    value = card.value
    suit = str(card.suit)
    if value == 11:
        value = "jack"
    elif value == 12:
        value = "queen"
    elif value == 13:
        value = "king"
    elif value == 14:
        value = "ace"
    return str(value) + " of " + suit


def print_card(card):
    print(get_card_name(card))


def print_cards(cards_array):
    for i in range(len(cards_array)):
        print_card(cards_array[i])


# This function is useful for checking that drawn cards have been "removed from the deck"
# by virtue of being set to active
def print_deck():
    for i in range(len(Cards.deck)):
        if not Cards.deck[i].active:
            print_card(Cards.deck[i])


def print_monies():
    for player in Game.players:
        print(player.name + "'s stack is £" + str(player.stack))


def print_stakes():
    for player in Game.players:
        if player.active and not player.is_all_in:
            print(player.name + "'s current bet is £" + str(player.stake))
        elif player.active and player.is_all_in:
            print(player.name + "'s current bet is £" + str(player.stake) + " (All in)")
        elif not player.active:
            print(player.name + "'s current bet is £" + str(player.stake) + " (Folded)")
        else:
            print("Could not find " + player.name + "'s information.")


def print_bet(player, amount):
    print(player.name + " bets £" + str(amount) + "\t\t Stake: £" + str(player.stake) + "\t\t\tPot: £" + str(Game.pot))


def input_int(prompt):
    integer = None
    while integer is None:
        try:
            integer = int(input(prompt))
        except ValueError:
            print("Invalid input.")
    return integer


# increases the given index by the increment, or resets to zero once it passes the length of Game.players
def next_player(index, increment):
    Game.turn_counter += 1
    for i in range(increment):
        if index + 1 < len(Game.players):
            index += 1
        else:
            index = 0
    if not Game.players[index].active:
        return next_player(index, 1)
    return index


def next_turn():
    input("\nPress the ENTER key to continue.")
    Game.turn_index = next_player(Game.turn_index, 1)
    system("clear")
    input(Game.players[Game.turn_index].name + " press ENTER to begin your turn.")
    system("clear")
    print("***" + Game.players[Game.turn_index].name + "'s turn***\n")
    print_monies()
    print()
    print_stakes()
    print("\nCommunity Cards:")
    print_cards(Game.table_cards)
    print("\n\nYour Cards:")
    print_cards(Game.players[Game.turn_index].cards)
    print("\n")


# returns a random inactive card and sets it to active
# setting to active ensures it is not inappropriately selected again
def draw_card():
    random_index = random.randrange(len(Cards.deck))
    if not Cards.deck[random_index].active:
        Cards.deck[random_index].active = True
        return Cards.deck[random_index]
    else:
        return draw_card()


def draw_cards(number_of_cards):
    drawn_cards = []
    for i in range(number_of_cards):
        drawn_cards.append(draw_card())
    return drawn_cards


def deal_hole_cards():
    for player in Game.players:
        player.cards += (draw_cards(2))


def order_cards(cards):
    return cards.sort(key=get_value)


def get_score(five_cards):
    is_flush = True
    is_straight = True
    kinds = []
    value_of_kinds = []  # tells you which value the 3 or 4 of a kinds are etc (for tie breaking purposes)
    current_kind = 1
    order_cards(five_cards)
    for i in range(1, 5):
        if five_cards[i].suit != five_cards[i - 1].suit:
            is_flush = False
        if five_cards[i].value == five_cards[i - 1].value:
            current_kind += 1
            is_straight = False
        elif five_cards[i].value == five_cards[i - 1].low_ace_value + 1:
            if five_cards[i].value == 14 and i != 4:
                is_straight = False
            kinds.append(current_kind)
            current_kind = 1
            value_of_kinds.append(five_cards[i - 1].value)
        else:
            is_straight = False
            kinds.append(current_kind)
            current_kind = 1
            value_of_kinds.append(five_cards[i-1].value)
    kinds.append(current_kind)
    value_of_kinds.append(five_cards[i].value)
    max_kind = max(kinds)
    min_kind = min(kinds)
    kinds.sort()
    kinds.reverse()
    five_cards.reverse()
    five_cards_values = (five_cards[0].value,
                         five_cards[1].value,
                         five_cards[2].value,
                         five_cards[3].value,
                         five_cards[4].value)
    if is_straight and is_flush:
        if five_cards[0].value == 10:
            return "Royal Flush", 10, five_cards_values
        else:
            return "Straight Flush", 9, five_cards_values
    elif max_kind == 4:
        return "Four of a Kind", 8, value_of_kinds
    elif max_kind == 3 and min_kind == 2:
        return "Full House", 7, value_of_kinds
    elif is_flush:
        return "Flush", 6, five_cards_values
    elif is_straight:
        return "Straight", 5, five_cards_values
    elif max_kind == 3:
        return "Three of a Kind", 4, value_of_kinds
    elif kinds.count(2) == 2:
        return "Two Pair", 3, value_of_kinds
    elif kinds.count(2) == 1:
        return "Pair", 2, value_of_kinds
    else:
        return "High Card: " + get_card_name(five_cards[0]), 1, five_cards_values


# must be used before first_hand_best
# using these two functions allows boolean output from both
# scores are inputted rather than hands to prevent rerunning the get_score function unnecessarily
def hands_identical(hand1_score, hand2_score):
    if hand1_score[1] != hand2_score[1]:
        return False
    else:
        for i in range(len(hand1_score[2])):
            if hand1_score[2][i] != hand2_score[2][i]:
                return False
    return True


# requires hands_identical to be checked first
# using these two functions allows boolean output from both
# scores are inputted rather than hands to prevent rerunning the get_score function unnecessarily
def first_hand_best(hand1_score, hand2_score):
    if hand1_score[1] > hand2_score[1]:
        return True
    elif hand1_score[1] < hand2_score[1]:
        return False
    else:
        for i in range(len(hand1_score[2])):
            if hand1_score[2][i] > hand2_score[2][i]:
                return True
            elif hand1_score[2][i] < hand2_score[2][i]:
                return False


# the highest score stays on approach here avoids repeated calling on the get_score function
# hands are inputted, but the highest score is outputted with the best combination of cards
# this means that the score can be stored and used again later, rather than being recalculated
def best_hand_score(hands):
    highest_score = get_score(hands[0])
    highest_score_index = 0
    for i in range(1, len(hands)):
        candidate_score = get_score(hands[i])
        if hands_identical(candidate_score, highest_score):
            continue
        elif first_hand_best(candidate_score, highest_score):
            highest_score = candidate_score
            highest_score_index = i
    return hands[highest_score_index], highest_score


def possible_hands(cards):
    hands = []
    working_cards = cards[:]
    for i in range(0, len(cards)):
        for j in range(0, len(cards) - 1):
            working_cards.pop(i)
            working_cards.pop(j)
            hands.append(working_cards)
            working_cards = cards[:]
    return hands


def best_combinations():
    print("\nTable")
    print_cards(Game.table_cards)
    print()
    for player in Game.players:
        if player.active:
            print(player.name)
            print_cards(player.cards)
            player.best_combination = best_hand_score(possible_hands(player.cards + Game.table_cards))
            print(player.best_combination[1][0] + "\n")


# Need to figure out a way for pot splitting to be determined
# Returns the winners index, so it can be used for the settling up process
def decide_winner():
    highest_score = [], 0, []
    winner_index = 0
    for i in range(len(Game.players)):
        if Game.players[i].active:
            candidate_score = Game.players[i].best_combination[1]
            if hands_identical(candidate_score, highest_score):
                print("The pot must be split")
                return [winner_index, i]
            elif first_hand_best(candidate_score, highest_score):
                highest_score = candidate_score
                winner_index = i
    return winner_index


def last_player():
    if len(Game.active_players) == 1:
        system("clear")
        winner_index = next_player(0, 1)
        print("\n" + Game.players[winner_index].name + " wins the round!")
        move_chips(winner_index)
        players_for_next_round()
    return


def blind_bets():
    Game.turn_index = Game.dealer_index
    system("clear")
    print(Game.players[Game.turn_index].name + " you are the dealer.\n")
    next_turn()
    print("You are the small blind.\n")
    Game.players[Game.turn_index].set_stake(Game.min_bet)
    next_turn()
    print("You are the big blind.\n")
    Game.players[Game.turn_index].set_stake(Game.min_bet * 2)
    Game.first_bet = False


def check_round(player_index):
    Game.turn_index = player_index - 1
    Game.first_bet = True
    Game.turn_counter = 0
    while Game.first_bet and Game.turn_counter < len(Game.players):
        last_player()
        next_turn()
        Game.players[Game.turn_index].place_first_bet()
    Game.call_stake += Game.min_bet


def all_bets_equal_call():
    for player in Game.players:
        if player.active and not player.is_all_in and player.stake != Game.call_stake:
            return False
    return True


def betting_round():
    for i in range(len(Game.players)):
        if Game.players[next_player(Game.turn_index, 1)].active:
            last_player()
            next_turn()
            Game.players[Game.turn_index].place_bet()
        else:
            i += 1
            Game.turn_index = next_player(Game.turn_index)
    while not all_bets_equal_call():
        last_player()
        next_turn()
        Game.players[Game.turn_index].place_bet()


def move_chips(winner_index):
    if type(winner_index) == int:
        winner_stake = Game.players[winner_index].stake
        for player in Game.players:
            if player.stake <= winner_stake:
                Game.players[winner_index].stack += player.stake
                player.stake = 0
            elif player.stake > winner_stake:
                Game.players[winner_index].stack += winner_stake
                player.stake -= winner_stake
                Game.players[winner_index].is_active = False
        if not Game.players[winner_index].active:
            move_chips(winner_index)
    else:
        Game.players[winner_index[0]].stack += Game.pot / 2
        Game.players[winner_index[1]].stack += Game.pot / 2
    

def player_continue_choice(player):
    decision = input(player.name + " would you like to continue? (Y/N)")
    if decision.upper() == "Y":
        print()
    elif decision.upper() == "N":                
        player.leave_game()
    else:
        print("Invalid Input")
        player_continue_choice(player)


def players_for_next_round():
    print()
    print_monies()
    print()
    for player in Game.players:
        if len(Game.players) == 1:
            print(Game.players[0].name + " is the winner!")
            exit
        elif player.stack <= 2 * Game.min_bet:
            player.leave_game()
        else:
            player_continue_choice(player)
    else:
        round()


# need to find a way of escaping this code when Game.active_players == 1
def round():
    new_round()
    blind_bets()
    deal_hole_cards()
    betting_round()
    Game.table_cards = draw_cards(3)
    check_round(Game.dealer_index + 1)
    betting_round()
    Game.table_cards += draw_cards(1)
    check_round(Game.dealer_index + 1)
    betting_round()
    Game.table_cards += draw_cards(1)
    check_round(Game.dealer_index + 1)
    betting_round()
    system("clear")
    best_combinations()
    winner_index = decide_winner()
    if type(winner_index) == int:
        print("\n" + Game.players[winner_index].name + " wins the round!")
    else:
        print("\n" + Game.players[winner_index[0]].name + " and "+ Game.players[winner_index[1]].name + " split the pot!")
    move_chips(winner_index)
    players_for_next_round()
    

def main():
    system("clear")
    print("*****WELCOME TO TEXT BASED POKER*****\n\n\n")
    input("Press ENTER to begin")
    system("clear")
    create_players(number_of_players())
    set_up_game()
    round()
    

main()
