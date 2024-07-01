import random

PLAYER_CHIPS = 10000
BET = 0
continue_betting = True


class card_deck():
    def __init__(self):
        self.card_categories = [
            'hearts', 'diamonds', 'clubs', 'spades']
        self.cards_list = ["2", "3", "4", "5", "6", "7",
                           "8", "9", "10", "jack", "queen", "king", "ace"]
        self.deck = [([card, category])
                     for category in self.card_categories for card in self.cards_list]


def card_value(card):
    if card[0] in ['jack', 'queen', 'king']:
        return 10
    elif card[0] == 'ace':
        return 1
    else:
        return int(card[0])


def game_loop():
    global BET
    global PLAYER_CHIPS
    global continue_betting

    deck = card_deck()
    random.shuffle(deck.deck)

    if PLAYER_CHIPS == 0:
        print("You have no more chips to bet. Game Over.")
        return

    while True:
        print("Player Chips:", PLAYER_CHIPS)
        try:
            BET = int(input('Enter an amount to bet: '))
            if BET > PLAYER_CHIPS:
                print(
                    "You don't have enough chips to bet that amount. Please try again.")
            else:
                result(deck.deck, BET, continue_betting)
            continue  # Exit the loop if the input is successfully converted to an integer
        except ValueError:
            print("Error: Please enter an integer value for the bet.")
            continue

        else:
            break


def result(the_deck, BET: int, ACTION: bool, continue_betting: bool = True):
    global PLAYER_CHIPS
    while True:

        player_hand = [the_deck.pop(), the_deck.pop()]
        dealer_hand = [the_deck.pop(), the_deck.pop()]

        while continue_betting:

            def update_game_info():
                print("Dealer Cards:", dealer_hand)
                print("Dealer Total:", dealer_score)
                print("Player Cards:", player_hand)
                print("Player Total:", player_score)

            player_score = sum(card_value(card) for card in player_hand)
            if 'ace' in [card[0] for card in player_hand] and player_score + 10 <= 21:
                player_score += 10
            dealer_score = sum(card_value(card) for card in dealer_hand)

            print("Dealer First card:", dealer_hand[0])
            print("Player Cards:", player_hand)
            print("Player Total:", player_score)
            print("\n")
            choice = input(
                '["hit" for another card, "stay" to stop (no more cards)]:').lower()
            if choice == "h" or choice == "hit":
                new_card = the_deck.pop()
                player_hand.append(new_card)
            elif choice == "s" or choice == "stay":
                break
            else:
                print("Invalid choice. Please try again.")
                continue

            if player_score > 21:
                print("Dealer wins")
                PLAYER_CHIPS -= BET
                break

        while dealer_score < 17:
            new_card = the_deck.pop()
            dealer_hand.append(new_card)
            dealer_score += card_value(new_card)

        print("\n")
        if player_score > 21:
            print("Dealer wins")
            PLAYER_CHIPS -= BET
            break

        elif dealer_score > 21 and player_score <= 21:
            print("Player wins (Dealer Busts)")
            PLAYER_CHIPS += BET

        elif player_score > dealer_score:

            if player_score == 21 and len(player_hand) == 2:
                print("Player wins (<> <> <> Blackjack <> <> <> )")
                PLAYER_CHIPS += (BET * 1.5)
            else:
                print("Player Wins")
                PLAYER_CHIPS += BET

        elif dealer_score > player_score:

            print("Dealer Wins")
            PLAYER_CHIPS -= BET

        else:

            print("Push. It is a tie (no one wins)")

        # Call game_loop() once after all conditions
        if PLAYER_CHIPS == 0:
            print("You have no more chips to bet. Game Over.")
            return

        update_game_info()
        game_loop()


"""
        return {
            'player_hand': player_hand,
            'dealer_hand': dealer_hand,
            'status': 'playing',  # Updated game status
            'message': 'You hit. Place your next move.',  # Updated message
        }
"""

if __name__ == '__main__':

    game_loop()
