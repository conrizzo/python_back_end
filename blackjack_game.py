import random


class BlackjackGame:
    def __init__(self):
        self.player_chips = 10000
        self.bet = 0
        self.continue_betting = True
        self.deck = self.card_deck()

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

    def game_loop(self):
        random.shuffle(self.deck.deck)

        if self.player_chips == 0:
            print("You have no more chips to bet. Game Over.")
            return

        while True:
            print("Player Chips:", self.player_chips)
            try:
                self.bet = int(input('Enter an amount to bet: '))
                if self.bet > self.player_chips:
                    print(
                        "You don't have enough chips to bet that amount. Please try again.")
                else:
                    self.result(self.deck.deck, self.bet,
                                self.continue_betting)
                continue  # Exit the loop if the input is successfully converted to an integer
            except ValueError:
                print("Error: Please enter an integer value for the bet.")
                continue
            else:
                break

    def result(self, the_deck, bet, action, continue_betting=True):
        while True:
            player_hand = [the_deck.pop(), the_deck.pop()]
            dealer_hand = [the_deck.pop(), the_deck.pop()]
            player_score = 0
            dealer_score = 0
            while continue_betting:
                player_score = sum(self.card_value(card)
                                   for card in player_hand)
                if 'ace' in [card[0] for card in player_hand] and player_score + 10 <= 21:
                    player_score += 10
                dealer_score = sum(self.card_value(card)
                                   for card in dealer_hand)
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
                    self.player_chips -= bet
                    print(self.return_result(player_hand, dealer_hand,
                          dealer_score, player_score, self.player_chips))
            while dealer_score < 17:
                new_card = the_deck.pop()
                dealer_hand.append(new_card)
                dealer_score += self.card_value(new_card)
            print("\n")
            if player_score > 21:
                print("Dealer wins")
                self.player_chips -= bet
                print(self.return_result(player_hand, dealer_hand,
                      dealer_score, player_score, self.player_chips))
            elif player_score == 21 and len(player_hand) == 2:
                print("Player wins (<> <> <> Blackjack <> <> <> )")
                self.player_chips += (bet * 1.5)
            elif dealer_score > 21 and player_score <= 21:
                print("Player wins (Dealer Busts)")
                self.player_chips += bet
            elif player_score > dealer_score:
                print("Player Wins")
                self.player_chips += bet
            elif dealer_score > player_score:
                print("Dealer Wins")
                self.player_chips -= bet
                print(self.return_result(player_hand, dealer_hand,
                      dealer_score, player_score, self.player_chips))
            else:
                print("Push. It is a tie (no one wins)")
            # Call game_loop() once after all conditions
            if self.player_chips == 0:
                print("You have no more chips to bet. Game Over.")
                return
            print(self.return_result(player_hand, dealer_hand,
                  dealer_score, player_score, self.player_chips))
            self.game_loop()

    def return_result(self, player_hand, dealer_hand, dealer_score, player_score, player_chips):
        return {
            'player_hand': player_hand,
            'dealer_hand': dealer_hand,
            'dealer_score': dealer_score,
            'player_score': player_score,
            'player_chips': player_chips,
        }


if __name__ == '__main__':
    game = BlackjackGame()
    game.game_loop()
