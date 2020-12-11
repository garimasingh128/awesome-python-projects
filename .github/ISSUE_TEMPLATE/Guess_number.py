"""Guess the Number project """
import random
print("Choose a number between 1 to 20")
number=random.randint(0,20)
while True:
    print("Guess a number")
    guessednum=int(input())
    if number < guessednum:
        print("Gueesed number is too high ,Try Aain!!!!")
    elif number > guessednum:
        print("Gueesed number is too low ,Try Again!!!!")
    else:
        break
if guessednum==number:
    print("The number you guessed is correct which is " +str(guessednum))
else:
    print("the number i was thinking was "+str(number))


""" Sample output:
Choose a number between 1 to 20
Guess a number
8
Gueesed number is too high ,Try Aain!!!!
Guess a number
4
The number you guessed is correct which is 4
"""