### Hangman Game Project 

# Hangman game is just a word guessing game by guess the character of the word. In this game, there is a list of words present, out of which our interpreter will choose 1 random word.

# The user first has to input their names and then, will be asked to guess any alphabet. If the random word contains that alphabet, it will be shown as the output(with correct placement) else the program will ask you to guess another alphabet. Users will be given 10 turns(can be changed accordingly) to guess the complete word.

### TODO
# Change the turns that you want to give the player
# Change the list containing Secret word list



from os import system
import random

def cls():
    system ('cls')

def hangman_game():
    cls()
    
    print("\nWelcome")
    print("Lets play Hangman\n")

    name = input("What is your name?")
    name = name.capitalize()
    print("Hello " + name + ", It is time to play HamgMan")
    print("Start Guessing...")
    guessed_word = []

    # Creats a variable with an empty value
    guesses = ""

    # Determine the Number of turns
    turns = 10                                  #ToDo : Change the turns that you want to give the player

    # Here we set the Secret
    words = [
        "Forrest Gump",
        "Hangman Project",
        "The Godfather",
        "The Green Mile",
        "Hotel Rwanda",
        "Goodfellas",
        "Scarface",
        "The Terminal",
        "Million Dollar Baby",
        "Driving Miss Daisy",
        "Catch Me If You Can",
        "Chinatown",
        "The Departed",
        "Dances with Wolves",
        "Ford v Ferrari",
        "Little Women",
        "A Star Is Born",
        "Dear Basketball"
    ]

    word = random.choice(words)
    word = word.upper()

    while turns > 0:
        failed = 0

        for char in word:
            if char in guesses:
                print(char, end=" ")

            elif char == " ":
                print(' / ', end=" ")
                
            else:
                print("_", end=" ")
                failed += 1

        if failed == 0:
            print("\n" + name + " you WON!     :)")
            break

        guess = input("\nGuess a Character : ")
        guess = guess.upper()

        if len(guess) > 1:
            break

        guesses += guess
        if (guess not in word) and (guess not in guessed_word):
            turns -= 1
            guessed_word.append(guess)
            print("\nWrong Guess :/")
        cls()

        print("\nYou have ", + turns, "more guesses")
        print("\nWrong Character's Entered : ", guessed_word)

        if turns == 0:
            print("\nGame is OVER, you LOST :o")

    check = input("\nDo you want to play again Y/N?")

    if check == "Y" or check == "y" :
        hangman_game()


hangman_game()