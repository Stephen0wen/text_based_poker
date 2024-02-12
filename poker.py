import random
from os import system
import time


buy_in = 100
# the first term is the player name, while the second term is to determine if the player is human or AI
new_players = ("Player 1", True, buy_in), \
              ("Player 2", True, buy_in), \
              ("Player 3", True, buy_in), \
              ("Player 4", True, buy_in)


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
    min_bet = 2
    dealer_index = -1
    turn_index = 0
    table_cards = []
    pot = 0
    first_bet = False
    call_stake = 0

    def __init__(self, name, is_human, money):
        self.name = name
        self.is_human = is_human
        self.active = True
        self.is_dealer = False
        self.is_all_in = False
        self.cards = []
        self.best_combination = []
        self.money = money
        self.stake = 0  # this is only the amount staked in the current betting round
        __class__.players.append(self)

    # no need to check if amount is greater than money as this will be checked already
    def set_stake(self, amount):
        increase = amount - self.stake
        self.stake = amount
        self.money -= increase
        Game.pot += increase
        print_bet(self, increase)
        if self.stake > Game.call_stake:
            Game.call_stake = self.stake

    def raise_amount(self):
        amount = int(input("\nEnter bet amount: "))
        if type(amount) != int:
            print("Invalid Input")
            self.raise_amount()
        increase = amount + Game.call_stake - self.stake
        if increase >= self.money:
            return self.all_in()
        elif self.money > amount >= 0:
            return increase
        else:
            print("Unexpected error")
            self.raise_amount()
            
    def fold(self):
        self.active = False
        print(self.name + " folds their cards")

    def all_in(self):
        print(self.name + " is all in!")
        self.is_all_in = True
        return self.money

    def leave_game(self):
        time.sleep(1 * Game.speed)
        print(self.name + " leaves the game")
        Game.players.remove(self)
    
    def place_first_bet(self):
        if not self.active:
            return
        print("\n" + self.name + " Please choose from the following:")
        choice = int(input("1 -> Check\n2 -> Bet\n3 -> Fold\n"))
        if choice == 1:
            return
        elif choice == 2:
            amount = self.stake + self.raise_amount()
            print()
            self.set_stake(amount)
            Game.first_bet = False
            return
        elif choice == 3:
            self.fold()
            return
        else:
            print("Invalid Selection")
            self.place_first_bet()
            
    def place_bet(self):
        if self.is_all_in or not self.active:
            return
        print("\n" + self.name + " Please choose from the following:")
        choice = int(input("1 -> Call\n2 -> Raise\n3 -> Fold\n"))
        if choice == 1:
            print()
            if self.money > Game.call_stake - self.stake:
                self.set_stake(Game.call_stake)
            else:
                self.set_stake(self.all_in())
        elif choice == 2:
            print()
            amount = Game.call_stake + self.raise_amount()
            self.set_stake(amount)
            return
        elif choice == 3:
            self.fold()
            return
        else:
            print("Invalid Selection")
            self.place_bet()


# creates the deck
# numbers are used for picture card to simplify the scoring logic
# the get_card_name function will enable picture card names to be printed
def set_up_game(player_info):
    suits = ("diamonds", "hearts", "clubs", "spades")
    for i in range(4):
        for j in range(2, 15):
            Cards(j, suits[i])
    for i in range(len(player_info)):
        Game(player_info[i][0], player_info[i][1], player_info[i][2])


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


# increases the given index by one, or resets to zero once it passes the length of Game.players
def next_player(index, increment):
    for i in range(increment):
        if index + 1 < len(Game.players):
            index += 1
        else:
            index = 0
    return index


def next_turn():
    Game.turn_index = next_player(Game.turn_index, 1)


def new_round():
    print("\n\nStarting new round...\n\n")
    time.sleep(1 * Game.speed)
    Game.table_cards = []
    Game.pot = 0
    for player in Game.players:
        player.active = True
        player.is_all_in = False
        player.cards = []
        player.best_combination = []
        player.stake = 0
    for card in Cards.deck:
        card.active = False
    Game.players[Game.dealer_index].is_dealer = False
    Game.dealer_index = next_player(Game.dealer_index, 1)
    Game.players[Game.dealer_index].is_dealer = True
    print(Game.players[Game.dealer_index].name + " is the dealer.\n")


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
        print("\n" + player.name)
        print_cards(player.cards)


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
    five_cards.reverse()
    five_cards_values = (five_cards[0].value,
                         five_cards[1].value,
                         five_cards[2].value,
                         five_cards[3].value,
                         five_cards[4].value)
    if is_straight and is_flush:
        if five_cards[0].value == 10:
            return "Royal Flush", 10, [five_cards_values[2]]
        else:
            return "Straight Flush", 9, [five_cards_values[2]]
    elif max_kind == 4:
        return "Four of a Kind", 8, [value_of_kinds[kinds.index(4)]]
    elif max_kind == 3 and min_kind == 2:
        return "Full House", 7, (value_of_kinds[kinds.index(3)], value_of_kinds[kinds.index(2)])
    elif is_flush:
        return "Flush", 6, five_cards_values
    elif is_straight:
        return "Straight", 5, [five_cards_values[2]]
    elif max_kind == 3:
        return "Three of a Kind", 4, [value_of_kinds[kinds.index(3)]]
    elif kinds.count(2) == 2:
        value_of_kinds.pop(kinds.index(1))
        return "Two Pair", 3, (max(value_of_kinds), min(value_of_kinds))
    elif kinds.count(2) == 1:
        return "Pair", 2, [value_of_kinds[kinds.index(2)]]
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
    highest_score = Game.players[0].best_combination[1]
    winner_index = 0
    for i in range(len(Game.players)):
        if Game.players[i].active:
            candidate_score = Game.players[i].best_combination[1]
            if hands_identical(candidate_score, highest_score):
                continue
            elif first_hand_best(candidate_score, highest_score):
                highest_score = candidate_score
                winner_index = i
    print(Game.players[winner_index].name + " is the winner")
    return winner_index


def print_bet(player, amount):
    print(player.name + " bets £" + str(amount) + "\t\t Stake: £" + str(player.stake) + "\t\t\tPot: £" + str(Game.pot))


def blind_bets():
    Game.turn_index = Game.dealer_index
    next_turn()
    Game.players[Game.turn_index].set_stake(Game.min_bet)
    next_turn()
    Game.players[Game.turn_index].set_stake(Game.min_bet * 2)
    Game.first_bet = False


def betting_round():
    next_turn()
    while Game.first_bet:
        Game.players[Game.turn_index].place_first_bet()
        next_turn()
    for i in range(len(Game.players) - 1):
        Game.players[Game.turn_index].place_bet()
        next_turn()
    continue_round = True
    while continue_round:
        Game.players[Game.turn_index].place_bet()
        next_turn()
        continue_round = False
        for player in Game.players:
            if player.active and not player.is_all_in and player.stake < Game.call_stake:
                continue_round = True
    Game.first_bet = True


def main():
    set_up_game(new_players)
    new_round()
    blind_bets()
    deal_hole_cards()
    betting_round()
    Game.table_cards = draw_cards(3)
    print("\nCommunity Cards:")
    print_cards(Game.table_cards)
    betting_round()
    Game.table_cards += draw_cards(1)
    print("\nCommunity Cards:")
    print_cards(Game.table_cards)
    betting_round()
    Game.table_cards += draw_cards(1)
    best_combinations()
    decide_winner()


main()
