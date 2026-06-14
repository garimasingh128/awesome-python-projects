# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 20:39:00 2024

@author: quint
"""

#Game Station
import random



#go-ahead

#R/P/S
def Rock_Paper_Scissors():
        print('Game 1 = Rock/Paper/Scissors')
        print('1 for rock')
        print('2 for scissors')
        print('3 for paper')
        me = int(input())
        ai = random.randint(1,3)
        print(ai)
        if me >=1 and me <=3:
                if me ==1:
                  print('me: Rock')
                elif me ==2:
                  print('me: Paper')
                else:
                  print('me: Scissors')
                if ai ==1:
                  print('ai: Rock')
                elif ai ==2:
                  print('ai: Paper')
                else:
                  print('ai: Scissors')
                
        #Outcome
                
                if me==1 and ai==3:
                  print('U win')
                elif me==2 and ai==1:
                  print('U win')
                elif me==3 and ai==2:
                  print('U win')
                elif ai==2 and me==1:
                  print('U lose')
                elif ai==1 and me==3:
                  print('U lose')
                elif ai==3 and me==2:    
                  print('U lose')
                else:
                  print('Tie!')
        else:
            print('only enter numbers between 1 and 3')
        
        


     
#cars
def fast_cars():
    
    car1=random.randint(5,20)
    car2=random.randint(5,20)
    print(' Do you think car 1 or 2 is faster?')
    print()
    print('Only enter 1 or 2; all other numbers and words are invalid.')
    print()
    
#car1
    print('car1')
    print('\t\t________|')
    print('\t\t/-------\\')
    print('\t________________')
    print('\t|\t__\t|\t__\t|')
    print('\t\to\t\to\t')
    print()
    print('car2')
#car2
    print('\t--------------------')
    print('\t|___________________|\\')
    print('\t\\__________________///')
    print('\t\t\t0\t\t\to\t\t')
    bet=int(input())
    try:
        if bet<1 or bet>2:
            print('There are only two cars; Only numbers pls to avoid errors!')
            bet=int(input())
    except:
        bet=int(input())
    
    print('\t'*car1,'\t\t________|')
    print('\t'*car1,'\t\t/-------\\')
    print('\t'*car1,'\t________________')
    print('\t'*car1,'\t|\t__\t|\t__\t|')
    print('\t'*car1,'\t\to\t\to\t')
    
    print('\t'*car2,'\t--------------------')
    print('\t'*car2,'\t|___________________|\\')
    print('\t'*car2,'\t\\__________________///')
    print('\t'*car2,'\t\t\t0\t\t\to\t\t')
    if bet==1 and car1>car2:
        print('U were right congratulations')
    elif bet==2 and car1<car2:
        print('U were right congratulations')
    else:
        print('U were wrong!!!')
    print('car1 was going at',car1*5,'mph')
    print('car2 was going at',car2*5,'mph')
    
#cars
def deck_o_cards():
    print()
    print('Warning')
    print('PLS ONLY ENTER NUMBERS THAT U CURRENTLY SEE IN THE DECK')
    print('also if youve already entered a number such as 2, you cant type it again')
    print()
    print('failing to do so will result in an error!!!')
    print()
    print('Pick from Deck')
    deck = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    draw=0
    while draw<=13:
        
        print(deck)
        print() 
        r=random.choice(deck)
        p=input('enter your card:')
        deck.remove(p)
        print()
       
        draw+=1
        if p!=r:
            print('incorrect')
            print(p)
            print()
            continue    
        else:
            print()
            print('U got it!')
            break
        
        
               
    print(p)
    print(r)
    print('It took u',draw,'tries')
    
#pokemon
def Pokemon():
    num1=random.randint(112,344)
    num2=random.randint(112,344)
    num3=random.randint(77,504)
    num4=random.randint(77,504)
    flame=['charmander','vulpix','arcanine','ninetales','ponyta','charizard']
    wave=['squirtle','lumineon','tapu fini','vaporeon','palkia','milotic']
    thunder=['jolteon','zapdos','electabuzz','pikachu','raikou','electivire']
    my_Team=[]
    enemy_Team=[]
    round=0
    print('fire Pokemon:')
    for i in range(0, len(flame)):
        print('\t',(i),flame[i])
    print('water Pokemon:')    
    for i in range(0, len(wave)):
        print('\t',(i),wave[i])
    print('thunder Pokemon:')
    for i in range(0, len(thunder)):
        print('\t',(i),thunder[i])
    while round <=2:
        p1=int(input())
        p2=random.randint(0,4)
        round+=1
        if round==1:
            
            if p1 >=0 and p1 <=5:
                print(flame[p1])
                my_Team.append(flame[p1])
                flame.remove(flame[p1])
                print(flame[p2])
                enemy_Team.append(flame[p2])
                flame.remove(flame[p2])
            else:
                print('error...there are only 6 pokemon; choose 0-5')
                break
            
        elif round==2:
            
            if p1 >=0 and p1 <=5:
                print(wave[p1])
                my_Team.append(wave[p1])
                wave.remove(wave[p1])
                print(wave[p2])
                enemy_Team.append(wave[p2])
                wave.remove(wave[p2])
            else:
                print('error...there are only 6 pokemon; choose 0-5')
                break
        else:
            
            if p1 >=0 and p1 <=5:
                print(thunder[p1])
                my_Team.append(thunder[p1])
                thunder.remove(thunder[p1])
                print(thunder[p2])
                enemy_Team.append(thunder[p2])
                thunder.remove(thunder[p2])
            else:
                print('error...there are only 6 pokemon; choose 0-5')
                break
    print('Your team:',my_Team,'----Total health=',num1,'Total attack power=',num3)
    print('Rival team:',enemy_Team,'----Total health=',num2,'Total attack power=',num4)
    


#calculator
def calculator():
    count=0
    c=random.randint(2,5)
    y=random.randint(2,5)
    cc=random.randint(7,800)
    yy=random.randint(7,800)
    ccc=random.randint(3,30)
    yyy=random.randint(3,30)
    c4=random.randint(5,35)
    y4=random.randint(5,35)
    fc=random.randint(1,10)
    fy=random.randint(1,10)
    while count <= 5:
        print()
        print("Enter a number between 1 and 60:")
        p1=int(input())
        p2=random.randint(1,60)
        print(p2)
        count+=1
        if p1>0 and p1<=60:
            if count==1:
                   print('Round 1--multiplication')
                   v=p1*c
                   print('Your product=',v)
                   z=p2*y
                   print('aI product=',z)
                   if v>z:
                       print('u win round 1')
                   elif v<z:
                       print('u lose round 1')
                   else:
                       print('tie')
            elif count==2:
                   print('Round 2--addition')
                   v=p1+cc
                   print('Your sum=',v)
                   z=p2+yy
                   print('aI sum=',z)
                   if v>z:
                       print('u win round 2')
                   elif v<z:
                       print('u lose round 2')
                   else:
                       print('tie')
            elif count==3:
                   print('Round 3--division')
                   v=p1//ccc
                   print('Your quotient=',v)
                   z=p2//yyy
                   print('aI quotient=',z)
                   if v>z:
                       print('u win round 3')
                   elif v<z:
                       print('u lose round 3')
                   else:
                       print('tie')
            elif count==4:
                   print('Round 4--subtraction')
                   v=p1-c4
                   print('Your difference=',v)
                   z=p2-y4
                   print('aI difference=',z)
                   if v>z:
                       print('u win round 4')
                   elif v<z:
                       print('u lose round 4')
                   else:
                       print('tie')
            elif count==5:
                   print('Round 5--exponent')
                   v=p1*p1
                   print('Your square number=',v)
                   z=p2*p2
                   print('aI square number=',z)
                   if v>z:
                       print('u win round 5')
                   elif v<z:
                       print('u lose round 5')
                   else:
                       print('tie')
            else:
                print('Round 6--modulus')
                v=p1%fc
                print('Your remainder=',v)
                z=p2%fy
                print('aI remainder=',z)
                if v>z:
                    print('u win the final round')
                elif v<z:
                    print('u lose the final round')
                else:
                    print('tie')
        
        else:
            print('ERROR:...only numbers between 1 and 60--TRY AGAIN')
            break
        
        
#riddler--next game later

def main():      
#MENU
    c=0
    while c!=6:
        print("Welcome to the Game Hub!")
        
        print(' 1:','\t','Rock, Paper, Scissors Game' )
        print(' 2:','\t','Racing Cars Game')
        print(' 3:','\t','Deck of Cards Game' )
        print(' 4:','\t','Pokemon Game' )
        print(' 5:','\t','Random Calculator Game')
        print(' 6:','\t','Exit')
        print()
        print("What do you want to play:")
        print('only enter numbers between 1 and 6 please:', end='')
        c = int(input())
        if c>=1 and c<=6:
            print('Get Ready To Play Game',c)
            
            if c==1:
                 print('Welcome to Rock, Paper, Scissors!')
                 round=0
                 while round<3:
                     Rock_Paper_Scissors()
                     print()
                     round +=1 
            elif c==2:
                print('Do you know how to drive?')
                fast_cars()
            elif c==3:
                print('draw your card!')
                deck_o_cards()
                print()
            elif c ==4:
                print('Pokemon Go!')
                print()
                Pokemon()
                print()    
            elif c==5:
                print('Calculator Games--Random Values')
                print('For each round, enter a random number to play')
                print()
                calculator()
                print()
            elif c==6:
                print('\nGame ended!')
            else:
                print('Only numbers between 1 and 6 pls')
                print('Try Again...')
                print()
                print()
        
        

#launch main if this is not a support file
if __name__=="__main__":
    main()
        
        

