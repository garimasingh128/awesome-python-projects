# importing the required module
import random

#this function will ask the user whether he/she want to play again or not ?.
def roll_dice():
    print('\nDo you want to play again ?')
    print('Enter Yes/No')
    choice = input()

    # if the user doesn't enter anything,he/she will be asked to enter again.
    if choice =='':
        print('Wrong Input !!! Enter again Yes/No')
        choice = roll_dice()
    return choice

if __name__ == '__main__':
    print('Welcome to the Dice Game !!!')
    dice_value = random.randint(1, 6)
    print('You got ', dice_value)
    choice = roll_dice()

    #this while loop will run untill the user doesn't want to play again.
    while choice:
        if choice == 'No' or choice == 'no':
            break
        elif choice == 'Yes' or choice == 'yes':
            dice_value = random.randint(1, 6)
            print('You got ', dice_value)
            choice = roll_dice()
        else:
            print('Wrong Input !!! Enter again Yes/No')
            choice = roll_dice()




