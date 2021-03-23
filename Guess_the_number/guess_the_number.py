import random

number_to_guess = random.randint(0, 20)
count_of_tries = 1
print("----------------WELCOME---------------")
print("\nYou only have 5 turns.Good Luck!")
print(" ")
print(" ")
play = True
guess = int(input("Enter a number to guess : "))

while guess != number_to_guess:
    print("Sorry wrong number")
    print(" ")
    if count_of_tries == 5:
        break
    elif guess == -1:
        print("cheat mode activated your number is :", number_to_guess)
        print(" ")
    elif guess < number_to_guess:
        print("Try higher number")
        print(" ")

    else:
        print("Try lower number")
        print(" ")
    guess = int(input("Enter a number to guess : "))
    count_of_tries += 1

if guess == number_to_guess:
    print("Well done")
    print(" ")
    print("You took", count_of_tries)
    print(" ")
else:
    print("Oh no")
    print(" ")
    print("Number is", number_to_guess)
    print(" ")

print("-----------------GAME ENDS-------------- ")
