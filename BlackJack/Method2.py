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

def print_dealt_cards(dealt_cards):
    for card in dealt_cards:
        print(f"Dealt card: {card['rank']} of {card['suit']}")

# Shuffle the deck
shuffle_deck(deck)

# Deal four cards
dealt_cards = deal(deck, 4)

# Print the dealt cards' suit and rank
print_dealt_cards(dealt_cards)
