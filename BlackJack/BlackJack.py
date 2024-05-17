import random

# Define the suits and ranks
suits = ["Spades", "Clubs", "Hearts", "Diamonds"]
ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
values = {
    "A": 11, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "J": 10, "Q": 10, "K": 10
}

# Define the Card class
class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank} of {self.suit}"

# Define the Deck class
class Deck:
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in suits for rank in ranks]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop()

# Define the Hand class
class Hand:
    def __init__(self):
        self.cards = []
        self.value = 0
        self.aces = 0

    def add_card(self, card):
        self.cards.append(card)
        self.value += values[card.rank]
        if card.rank == 'A':
            self.aces += 1
        self.adjust_for_ace()

    def adjust_for_ace(self):
        while self.value > 21 and self.aces:
            self.value -= 10
            self.aces -= 1

    def __str__(self):
        return f"{' '.join(map(str, self.cards))} (Value: {self.value})"

# Define the Game class
class Game:
    def __init__(self):
        self.deck = Deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()

    def play(self):
        print("Welcome to Blackjack!")
        
        # Initial dealing
        for _ in range(2):
            self.player_hand.add_card(self.deck.deal())
            self.dealer_hand.add_card(self.deck.deal())

        # Show hands
        print(f"Dealer's Hand: {self.dealer_hand.cards[0]} and <hidden>")
        print(f"Player's Hand: {self.player_hand}")

        # Player's turn
        while self.player_hand.value < 21:
            action = input("Do you want to [H]it or [S]tand? ").upper()
            if action == 'H':
                self.player_hand.add_card(self.deck.deal())
                print(f"Player's Hand: {self.player_hand}")
            else:
                break

        # Dealer's turn
        while self.dealer_hand.value < 17:
            self.dealer_hand.add_card(self.deck.deal())

        # Show final hands
        print(f"Dealer's Hand: {self.dealer_hand}")
        print(f"Player's Hand: {self.player_hand}")

        self.check_winner()

    def check_winner(self):
        if self.player_hand.value > 21:
            print("Player busts! Dealer wins.")
        elif self.dealer_hand.value > 21:
            print("Dealer busts! Player wins.")
        elif self.player_hand.value > self.dealer_hand.value:
            print("Player wins!")
        elif self.player_hand.value < self.dealer_hand.value:
            print("Dealer wins!")
        else:
            print("It's a tie!")

# Run the game
if __name__ == "__main__":
    game = Game()
    game.play()
