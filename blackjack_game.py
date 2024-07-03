import random
# import redis


class BlackjackGame:
    def __init__(self):
        self.player_hand = []
        self.dealer_hand = []
        self.player_score = 0
        self.dealer_score = 0
        self.player_chips = 10000
        self.bet = 0
        self.continue_betting = True
        self.deck = self.card_deck()
        self.winner = None  # In reference to the player winning
        self.deal_initial_hands()

    class card_deck:
        def __init__(self):
            self.card_categories = ['hearts', 'diamonds', 'clubs', 'spades']
            self.cards_list = ["2", "3", "4", "5", "6", "7",
                               "8", "9", "10", "jack", "queen", "king", "ace"]
            self.deck = [([card, category])
                         for category in self.card_categories for card in self.cards_list]

    @staticmethod
    def card_value(card):
        if card[0] in ['jack', 'queen', 'king']:
            return 10
        elif card[0] == 'ace':
            return 1
        else:
            return int(card[0])

    # this needs to be invoked from front end each action
    def game_loop(self, bet=0):
        random.shuffle(self.deck.deck)
        if self.player_chips == 0:
            print("You have no more chips to bet. Game Over.")
            return
        if self.winner != 'dealer':
            print("Player Chips:", self.player_chips)
            self.bet = bet  # Assuming bet is passed correctly and validation is handled elsewhere
            self.result(self.deck.deck, self.bet, self.continue_betting)

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

    def result(self, bet, continue_betting=True):
        game_over = False
        message = ""

        action = self.get_action()

        # Check for Ace adjustment before any action
        if 'ace' in [card[0] for card in self.player_hand] and self.player_score + 10 <= 21:
            self.player_score += 10

        if action == "hit":
            # Add a new card to the player's hand
            new_card = self.deck.deck.pop()
            self.player_hand.append(new_card)
            # Recalculate player's score after adding the new card
            self.player_score = sum(self.card_value(card)
                                    for card in self.player_hand)
            # Check if player busts after hitting
            if self.player_score > 21:
                game_over = True
                message = "Bust! Dealer wins."
                self.player_chips -= bet
        elif action == "stay":
            # Process dealer's actions after player decides to stay
            while self.dealer_score < 17:
                new_card = self.deck.deck.pop()
                self.dealer_hand.append(new_card)
                self.dealer_score += self.card_value(new_card)
            # Determine the outcome after both player and dealer have finished their actions
            game_over = True
            if self.dealer_score > 21 or self.player_score > self.dealer_score:
                message = "Player wins!"
                self.player_chips += bet
            elif self.dealer_score > self.player_score:
                message = "Dealer wins."
                self.player_chips -= bet
            else:
                message = "Push. It is a tie."

        # Return game state and message for frontend to display
        return self.return_result(message)

    def who_wins(self, winner):
        self.winner = winner
        print(self.winner, "wins")

    def return_result(self, message):
        # handles missing or optional data
        game_state = {
            'player_hand': self.player_hand or "",
            'dealer_hand': self.dealer_hand or "",
            'player_score': self.player_score or "",
            'dealer_score': self.dealer_score or "",
            'player_chips': self.player_chips or "",
            "message": message,
            'bet_amount': self.bet or "",
            'winner': self.winner or "",

        }
        # Serialize the dictionary to a JSON string

        # game_state_json = json.dumps(game_state)

        # Store the JSON string in Redis, using a unique key for the game state
        # blackjack_redis_client.set('game_state_key', game_state_json)
        return game_state


def test_blackjack_games(num_games, bet_amount):
    game = BlackjackGame()
    for _ in range(num_games):
        # Reset and shuffle the deck

        while True:
            print("Dealer's First Card:", game.dealer_hand[0])
            print("Player's Hand:", game.player_hand)
            print("Player's Score:", game.player_score)

            action = input("Player action (hit/stay): ").lower()
            if action not in ['hit', 'stay']:
                print("Invalid action. Please type 'hit' or 'stay'.")
                continue

            # Assuming get_or_set_action correctly updates the game state with the new action
            game.set_action(action)

            # Process the action and get the result
            result = game.result(bet_amount)
            print(result)
            print(f"Final chip count: {game.player_chips}")


# Example usage
test_blackjack_games(2, 100)


def main():
    # game = BlackjackGame()
    # game.game_loop(10000)
    test_blackjack_games(10, 100)


if __name__ == '__main__':
    main()
