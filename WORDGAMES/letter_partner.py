import sys
list1=['a','b','c','d','e','f','g','h','i','j','k','l','m']
list2=['n','o','p','q','r','s','t','u','v','w','x','y','z']
w=input("Enter a word ")
prepartner=prepartner1=[]
postpartner1=postpartner=[]
for i in w:
    if(i in list1):
        prepartner.append(i)
    if(i in list2):
        postpartner.append(i)
for j in prepartner:
    list1index=list1.index(j)
    if(list2[list1index] in postpartner):#testing if all prepartners has postpartners
        pass
    else:
        print("YOU LOST")
        sys.exit()
prepartner1=prepartner
postpartner1=postpartner
for k in prepartner:
    x=prepartner.index(k)
    y=postpartner.index(list2[list1.index(k)])
    if(w.index(prepartner[x])<w.index(postpartner[y])):
        if(w.index(postpartner[y])-w.index(prepartner[x])==1):#testing3a
            prepartner1.pop(x)
            postpartner1.pop(y)
    else:
        print("YOU LOST")
        sys.exit()
postpartner1.reverse()
count=0
for l in prepartner1:
    if(prepartner1.index(l)==postpartner1.index(list2[list1.index(l)])):#testing3b
        count+=1
if(count==len(prepartner1)):
    print("GAME WON")
else:
    print("GAME LOST")

