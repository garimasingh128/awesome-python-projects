import  random
board=list()
move=1

def createboard():
    board = list()
    for i in range(0, 9):
        board.append(' ')
    return board

def displayBoard(board):
    print(board[0]+' | '+board[1]+' | '+board[2])
    print('---------')
    print(board[3]+' | '+board[4]+' | '+board[5])
    print('---------')
    print(board[6]+' | '+board[7]+' | '+board[8])

def playermove(board,letter,playerno):  #'X' for player
    while True:
        try:
            position=int(input("Player "+str(playerno)+" input your next move ("+letter+") position (1-9) : "))
            if board[position-1]==' ':
                board[position-1]=letter
                break
            else:
                print("Position already occupied! Try entering again :")
        except:
            print("Enter a valid move : ")

def iswon(board):
    if (board[0] == 'X' and board[1] == 'X' and board[2] == 'X') or (board[3] == 'X' and board[4] == 'X' and board[5] == 'X') or (board[6] == 'X' and board[7] == 'X' and board[8] == 'X') or (board[0] == 'X' and board[3] == 'X' and board[6] == 'X') or (board[1] == 'X' and board[4] == 'X' and board[7] == 'X') or (board[2] == 'X' and board[5] == 'X' and board[8] == 'X') or (board[0] == 'X' and board[4] == 'X' and board[8] == 'X') or (board[2] == 'X' and board[4] == 'X' and board[6] == 'X'):
        return True

    if (board[0] == 'O' and board[1] == 'O' and board[2] == 'O') or (board[3] == 'O' and board[4] == 'O' and board[5] == 'O') or (board[6] == 'O' and board[7] == 'O' and board[8] == 'O') or (board[0] == 'O' and board[3] == 'O' and board[6] == 'O') or (board[1] == 'O' and board[4] == 'O' and board[7] == 'O') or (board[2] == 'O' and board[5] == 'O' and board[8] == 'O') or (board[0] == 'O' and board[4] == 'O' and board[8] == 'O') or (board[2] == 'O' and board[4] == 'O' and board[6] == 'O'):
        return True

    return False

def computermove(board,letter): #'O' for computer
    vacantplaces=list()
    move=0

    for i in range(0,9):
        if board[i]!='X' and board[i]!='O':
            vacantplaces.append(i)

    boardCopy = board[:]

    for i in vacantplaces:
        boardCopy[i]=letter
        if iswon(boardCopy):
            board[i]=letter
            print("Computer's move1 (O) at position (1-9) : "+str(i+1))
            move=1
            break
        else:
            boardCopy[i]=' '

    if move==0:
        for i in vacantplaces:
            boardCopy[i]='X'
            if iswon(boardCopy):
                board[i]=letter
                print("Computer's move2 (O) at position (1-9) : " + str(i+1))
                move=1
                break
            else:
                boardCopy[i]=' '

    if move==0:
        possible_moves = []
        if board[0]=='X' and board[8]=='X':
            if 1 in vacantplaces:
                possible_moves.append(1)
            if 7 in vacantplaces:
                possible_moves.append(7)
            position=random.choice(possible_moves)
            board[position]=letter
            move=1

    if move==0:
        if board[4]=='X':
            positions=[]
            if 0 in vacantplaces:
                positions.append(0)
            if 2 in vacantplaces:
                positions.append(2)
            if 6 in vacantplaces:
                positions.append(6)
            if 8 in vacantplaces:
                positions.append(8)
            if len(positions)>=1:
                position=random.choice(positions)
                board[position]='O'
                print("Computer's move3 (O) at position (1-9) : " + str(position + 1))
            move=1

    if move==0:
        if 4 in vacantplaces:
            board[4]=letter
            print("Computer's move4 (O) at position (1-9) : " + str(5))
            move=1

    if move==0:
        i=random.randrange(0,len(vacantplaces))
        board[vacantplaces[i]]=letter
        print("Computer's move5 (O) at position (1-9) : " + str(vacantplaces[i]+1))
        move=1

def isfull(board):
    if board.count(' ')>=1:
        return False
    else:
        return True

def main():
    print("Welcome to Tic Tac Toe !")
    print("'X' is your key and 'O' is computer's key in case you play against computer.\n")
    computer_score = 0
    player1_score = 0
    player2_score = 0
    player_score = 0
    match_tie=0
    ch='y'
    while ch.lower() == 'y':
        print("Enter 1 to play against player")
        print("Enter 2 to play against computer")
        option = int(input("Enter your choice: "))
        print()
        if option == 2:
            board=createboard()
            while True:
                displayBoard(board)
                if not isfull(board):
                    if not iswon(board):
                        playermove(board,'X',1)
                        if not iswon(board):
                            if not isfull(board):
                                computermove(board,'O')
                            else:
                                match_tie+=1
                                print("Match Tie !")
                                break
                        else:
                            player_score=player_score+1
                            print("You Won... Good Job")
                            break
                    else:
                        computer_score = computer_score + 1
                        print("Computer won..... Nice Try!")
                        break
                else:
                    match_tie += 1
                    print("Match Tie !")
                    break
        elif option == 1:
            board=createboard()
            while True:
                displayBoard(board)
                if not isfull(board):
                    if not iswon(board):
                        playermove(board,'X',1)
                        if not iswon(board):
                            if not isfull(board):
                                displayBoard(board)
                                playermove(board,'O',2)
                            else:
                                match_tie += 1
                                print("Match Tie !")
                                break
                        else:
                            player1_score=player1_score+1
                            print("Player 1 Won... Good Job")
                            break
                    else:
                        player2_score=player2_score+1
                        print("Player 2 Won..... Good Job")
                        break
                else:
                    match_tie += 1
                    print("Match Tie !")
                    break
        else:
            print("Invalid input: ")
        ch=input("Want to play again (y/any key) : ")
    print()
    print("Final Scores are : ")
    print("===================")
    print()
    print(" : Against computer : ")
    print("----------------------")
    print("Computer Score = "+str(computer_score)+"         Your Score = "+str(player_score))
    print(" : Player Against Player : ")
    print("---------------------------")
    print("Player 1 Score = " + str(player1_score)+"        Player 2 Score = " + str(player2_score))
    print("--------------------")
    print("Match Tied = "+str(match_tie))

main()