import time
string = "Python is an interpreted,high-level programming language"
word_count = len(string.split())
while str(input('enter "yes" when you are ready :')):
    t0 = time.time()
    inputText = str(input('enter the phrase :"%s" as fast as possible :' % string))
    t1 = time.time()
    accuracy = len(set(inputText.split()) & set(string.split()))
    accuracy = accuracy/word_count
    timeTaken = t1 - t0
    wordsperminute = (word_count/timeTaken)
    print(wordsperminute,accuracy,timeTaken)
