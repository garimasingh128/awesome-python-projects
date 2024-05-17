import random

# Define the suits and ranks
suits = ["Spades", "Clubs", "Hearts", "Diamonds"]
ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

# Create the deck of cards
deck = [{"suit": suit, "rank": rank} for suit in suits for rank in ranks]

def shuffle_deck(deck):
    random.shuffle(deck)

def deal(deck, num_cards):
    dealt_cards = []
    for _ in range(num_cards):
        card = deck.pop()
        dealt_cards.append(card)
    return dealt_cards

def display_cards(cards):
    for card in cards:
        print(f"{card['rank']} of {card['suit']}")

def blackjack_game(num_players=1, num_cards_per_player=2):
    shuffle_deck(deck)
    players_hands = []

    # Deal cards to players
    for _ in range(num_players):
        player_hand = deal(deck, num_cards_per_player)
        players_hands.append(player_hand)

    # Display each player's hand
    for i, player_hand in enumerate(players_hands):
        print(f"Player {i + 1}'s hand:")
        display_cards(player_hand)
        print()

if __name__ == "__main__":
    blackjack_game(num_players=2, num_cards_per_player=2)
