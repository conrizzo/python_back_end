import random
import json
# import redis


class BlackjackGame:

    def __init__(self, state=None):
        if state:
            self.load_state(state)
        else:
            self.initialize_new_game()

    def initialize_new_game(self):
        self.player_hand = []
        self.dealer_hand = []
        self.player_score = 0
        self.dealer_score = 0
        self.player_chips = 0
        self.bet = 0
        self.continue_betting = True
        self.deck = self.card_deck()
        self.winner = None  # In reference to the player winning
        self.message = ""

    def load_state(self, state):
        self.player_hand = state.get('player_hand', [])
        self.dealer_hand = state.get('dealer_hand', [])
        self.player_score = state.get('player_score', 0)
        self.dealer_score = state.get('dealer_score', 0)
        self.player_chips = state.get('player_chips', 0)
        self.bet = state.get('bet', 0)
        self.continue_betting = state.get('continue_betting', True)
        # Ensure deck is properly initialized
        deck_data = state.get('deck', None)
        if deck_data is not None and isinstance(deck_data, list):
            self.deck = self.card_deck(deck_data)
        else:
            self.deck = self.card_deck()
        self.winner = state.get('winner')
        self.message = state.get('message')

    def serialize_state(self):
        return {
            'player_hand': self.player_hand,
            'dealer_hand': self.dealer_hand,
            'player_score': self.player_score,
            'dealer_score': self.dealer_score,
            'player_chips': self.player_chips,
            'bet': self.bet,
            'continue_betting': self.continue_betting,
            'deck': self.deck.deck,
            'winner': self.winner,
            'message': self.message or '',
        }

    class card_deck:
        def __init__(self, deck=None):
            self.card_categories = ['hearts', 'diamonds', 'clubs', 'spades']
            self.cards_list = ["2", "3", "4", "5", "6", "7",
                               "8", "9", "10", "jack", "queen", "king", "ace"]
            if deck is None:
                self.deck = [([card, category])
                             for category in self.card_categories for card in self.cards_list]
            else:
                self.deck = deck

    @staticmethod
    def card_value(card):
        if card[0] in ['jack', 'queen', 'king']:
            return 10
        elif card[0] == 'ace':
            return 1
        else:
            return int(card[0])

    # Imagine a dealer is shuffling the deck and dealing the cards here ---
    def deal_initial_hands(self):
        random.shuffle(self.deck.deck)
        self.player_hand = [self.deck.deck.pop(), self.deck.deck.pop()]
        self.dealer_hand = [self.deck.deck.pop(), self.deck.deck.pop()]
        self.player_score = sum(self.card_value(card)
                                for card in self.player_hand)
        self.dealer_score = sum(self.card_value(card)
                                for card in self.dealer_hand)

    def get_action(self):
        return self.action

    def set_action(self, action):
        self.action = action
        return self.action

    def result(self, bet):
        if self.continue_betting is False:
            return

        message = ""
        action = self.get_action()
        self.serialize_state()
        # Check for Ace adjustment before any action for player and dealer
        if 'ace' in [card[0] for card in self.player_hand] and self.player_score + 10 <= 21:
            self.player_score += 10
        if 'ace' in [card[0] for card in self.dealer_hand] and self.dealer_score + 10 < 17:
            self.dealer_score += 10

        if action == "hit":
            # Add a new card to the player's hand
            new_card = self.deck.deck.pop()
            self.player_hand.append(new_card)
            # Recalculate player's score after adding the new card
            self.player_score = sum(self.card_value(card)
                                    for card in self.player_hand)
            # Check if player busts after hitting
            if self.player_score > 21:
                self.message = "Bust! Dealer wins."
                self.player_chips -= bet
                # disallow more hitting or bets with FALSE below
                self.continue_betting = False
                self.serialize_state()

        elif action == "stay":
            while self.dealer_score < 17:
                new_card = self.deck.deck.pop()
                self.dealer_hand.append(new_card)
                self.dealer_score += self.card_value(new_card)
                if 'ace' in [card[0] for card in self.dealer_hand] and self.dealer_score + 10 < 17:
                    self.dealer_score += 10
                self.serialize_state()
            if self.player_score == 21 and len(self.player_hand) == 2:
                if self.dealer_score == 21 and len(self.dealer_hand) == 2:
                    self.message = "Push. It is a tie."
                else:
                    self.message = "Blackjack! Player wins!"
                    self.player_chips += bet * 1.5
            elif self.dealer_score > 21 or self.player_score > self.dealer_score:
                self.message = "Player wins!"
                self.player_chips += bet
            elif self.dealer_score > self.player_score:
                self.message = "Dealer wins."
                self.player_chips -= bet
            else:
                self.message = "Push. It is a tie."
            self.continue_betting = False
            self.serialize_state()

    def who_wins(self, winner):
        self.winner = winner
        print(self.winner, "wins")
        return game_state


""" Everything below this is only for testing purposes """


def test_blackjack_games(chips):
    game = BlackjackGame()
    game.player_chips = chips
    game.deal_initial_hands()
    print("Player Chips:", game.player_chips)
    bet = int(input("Amount to bet: "))

    ## the front end will make these queries ##
    player_stayed_flag = False
    while True:
        # print(game.deck.deck)

        state = game.serialize_state()
        # Serialize the state to a JSON string
        state_json = json.dumps(state)

        # print(state_json)
        # Save the JSON string to a file

        print("Player Chips:", state['player_chips'])

        print(bet)

        print("Dealer's First Card:", state['dealer_hand'][0])
        print("Player's Hand:", state['player_hand'])
        print("Player's Score:", state['player_score'])
        # print("state", state)
        # Check if the player has not stayed yet
        if not player_stayed_flag and state['player_score'] <= 21:
            action = input("Player action (hit/stay): ").lower()
            if action not in ['hit', 'stay']:
                print("Invalid action. Please type 'hit' or 'stay'.")
                continue
            game.set_action(action)
            if action == 'stay':
                player_stayed_flag = True  # Set the flag if the player chooses to stay

        # Process the action and get the result
        game.result(bet)  # play hand
        print(state['message'])
        print(state['player_score'])
        print(state['dealer_score'])

        print(f"Final chip count: {state['player_chips']}")

        if int(state['player_chips']) <= 0:
            test_blackjack_games(11000)  # new game

        if state['message'] != '':
            break

    test_blackjack_games(state['player_chips'])


def main():
    # game = BlackjackGame()
    test_blackjack_games(10000)


if __name__ == '__main__':
    main()
