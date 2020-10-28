## Player v/s cpu rock paper scissor game
from random import randint
name=input("Please Enter your name:")
print(f"WELCOME TO ROCK PAPER SCISSOR GAME {name}")
while True:
    print("-----------------------------------------------------")
    c=int(input("Enter 1 to play 0 to Exit: "))

    y =randint(0,2)
    if (c==0):
      print("thanks for playing")
      break
    else:
        inputs=["rock","paper","scissor"]
        z=0
        while True:
            x=str(input("SELECT YOUR CHOICE rock paper scissor: "))    
            if x not in inputs:
                print("That's not a valid play. Check your spelling!")
            else:
                break
            
        if (x=="rock" and y==0):
          print("computer move is rock")
          print("Result= TIE")    
        elif (x=="rock" and y==1):
          print("computer move is paper")
          print("Result= CPU WON ")   
        elif (x=="rock" and y==2): 
          print("computer move is scissor")
          print(f"Result= {name} WON")    
        elif (x=="paper" and y==0):
          print("computer move is rock")
          print(f"Result= {name} WON")   
        elif (x=="paper" and y==1):
          print("computer move is paper")
          print("Result= TIE ")    
        elif (x=="paper" and y==2):
          print("computer move is scissor")
          print("Result= CPU WON")    
        elif (x=="scissor" and y==0):
          print("computer move is rock")
          print("Result= CPU WON")    
        elif (x=="scissor" and y==1):
          print("computer move is paper")
          print(f"Result= {name} WON ")   
        elif (x=="scissor" and y==2):
          print("computer move is scissor")
          print("Result= TIE")  
        
