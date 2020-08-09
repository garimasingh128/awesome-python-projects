from random import randint
 
print("WELCOME TO ROCK PAPER SCISSOR GAME")
player=False
while player==False:
    print("-----------------------------------------------------")
    print("Enter 1 to play 0 to Exit")
    c=int(input())
    
    y =randint(0,2)
    if (c==0):
      print("thanks for playing")
      break
    else:        
        print("SELECT YOUR CHOICE rock paper scissor")
        x=str(input())        
        if y==0:
          print("computer move is rock")
        elif y==1:
          print("computer move is paper")    
        elif y==2:
          print("computer move is scissor")    
        if (x=="rock" and y==0):
          print("Result= TIE")    
        elif (x=="rock" and y==1):
          print("Result= CPU WON ")   
        elif (x=="rock" and y==2): 
          print("Result= YOU WON")    
        elif (x=="paper" and y==0):
          print("Result= YOU WON")   
        elif (x=="paper" and y==1):
          print("Result= TIE ")    
        elif (x=="paper" and y==2): 
          print("Result= CPU WON")    
        elif (x=="scissor" and y==0):
          print("Result= CPU WON")    
        elif (x=="scissor" and y==1):
          print("Result= YOU WON ")   
        elif (x=="scissor" and y==2): 
          print("Result= TIE")  
        else:
          print("That's not a valid play. Check your spelling!")
          player = False
          y =randint(0,2)