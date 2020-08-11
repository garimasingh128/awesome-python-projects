from Question import Question
print('----------------------------')
print('            QUIZ            ')
print('----------------------------')
print('INSTRUCTIONS\n(1) Quiz consists of 5 questions.\n(2) Each question will have 4 options (a)(b)(c)(d)\n(3) You need to input the correct option below each question.')
print('(4) Each question carries 1 mark.\n(5) Multiple selection of option will not be considered.\n(6) ENTER yes AFTER READING ALL THE INSTRUCTIONS TO TAKE QUIZ\n ')
question_prompt = [
    "Q1) Who is founder of PYTHON programming language ?\n (a) Guido Rangephiller \n (b) Guido van Rossum\n (c) Guido mark Rossum\n (d) JetBrains\n\n",
    "\nQ2) What will be the output of the following code :\nprint type(type(int)) \n (a) type'int'\n (b) type'type'\n (c) Error\n (d) 0\n\n",
    "\nQ3) What is the output of the following code :\nL = ['a','b','c','d']\nprint "".join(L) \n (a) Error\n (b) None\n (c) abcd\n (d) [‘a’,’b’,’c’,’d’]\n\n",
    "\nQ4) What is the output of the following code :\ny = 8\nz = lambda x : x * y\nprint z(6)\n (a) 48\n (b) 14\n (c) 64\n (d) None of the above\n\n",
    "\nQ5) What is called when a function is defined inside a class?:\n (a) Module\n (b) class\n (c) Another Function\n (d) Method\n\n",
]
question=[
    Question(question_prompt[0],"b"),
    Question(question_prompt[1],"b"),
    Question(question_prompt[2],"c"),
    Question(question_prompt[3],"a"),
    Question(question_prompt[4],"d"),
]
def run_test(questions):
    score=0
    for question in questions:
        answer = input(question.prompt)
        print('Your Response is ==> ', answer)
        if answer == question.answer:
            score+=1
    print("You got " + str(score) + " / " + str(len(questions)) + " correct")
    print("--------------")
    print("YOUR SCORE = ",score)
    print("--------------")
    if score <= 2:
        print("Try again,Keep yourself updated")
    elif score >2 and score <= 4:
        print("WELL DONE!!")   
    else:
        print("EXCELLENT!!")    

p= input("ARE U READY TO START??!!  ")
q=p.lower()
if q=="yes":
    print('Enter your name')
    name=input()
    print("Enter login ID")
    Id = input()

    run_test(question)            
    a=input("TYPE 'yes' to see correct ANSWERS ")
    b=a.lower()
    if b=="yes":
        print('\n------CORRECT ANSWERS-------')
        print("\nQ1.b) Guido van Rossum\nQ2.b) type'type'\nQ3.c) abcd\nQ4.a) 48\nQ5.d) Method\n")
        print('THANKS FOR ATTENDING '+ name.upper()) 
    else:
        print('THANKS FOR ATTENDING '+ name)
else:
    print("yes ==> to start")    