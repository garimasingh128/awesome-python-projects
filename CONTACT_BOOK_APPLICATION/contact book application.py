from tkinter import *
import sqlite3

root=Tk()
root.geometry('410x450')
root.title("DataBase using Sqlite3 and Tkinter")
root.configure(background="powder blue")

textin=StringVar()
textinn=StringVar()

menu=Menu(root)
root.config(menu=menu)

menu = Menu(root)
root.config(menu=menu)

def helpp():
   help(sqlite3)

subm = Menu(menu)
menu.add_cascade(label="Help",menu=subm)
subm.add_command(label="Sqlite3 Docs",command=helpp)



db = sqlite3.connect('mysq.db')
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS people(name TEXT, phone TEXT)")
db.commit()

lab=Label(root,text='Name:',font=('none 13 bold'))
lab.place(x=0,y=0)

entname=Entry(root,width=20,font=('none 13 bold'),textvar=textin)
entname.place(x=80,y=0)

entphone=Entry(root,width=20,font=('none 13 bold'),textvar=textinn)
entphone.place(x=80,y=40)

lab1=Label(root,text='Phone:',font=('none 13 bold'))
lab1.place(x=0,y=40)

def insert():
   
   name1 = textin.get()
   phone1 = textinn.get()
   conn = sqlite3.connect('mysq.db')
   with conn:
      cursor = conn.cursor()
      cursor.execute('INSERT INTO people(name, phone) VALUES(?,?)',(name1, phone1,))
      db.close()
   

def show():
   connt = sqlite3.connect('mysq.db')
   cursor = connt.cursor()
   cursor.execute('SELECT * FROM people')
   for row in cursor.fetchall():
      print(row)




name=StringVar()
phone=StringVar()
def updateContact():
   nam=name.get()
   ph=phone.get()
  
   
   connnt=sqlite3.connect('mysq.db')
   cursor = connnt.cursor()
   cursor.execute("UPDATE people SET name = ? WHERE phone = ?",(nam,ph))
   connnt.commit()

dell=StringVar()
def det():
   dee=dell.get()
   connnt=sqlite3.connect('mysq.db')
   cursor = connnt.cursor()
   cursor.execute("DELETE FROM people WHERE name = ?",(dee,))
   connnt.commit()

   
 

def drop():
   connnt=sqlite3.connect('mysq.db')
   cursor = connnt.cursor()
   cursor.execute("DROP table people")
   connnt.commit()
   

   
   
buttdrop=Button(root,padx=2,pady=2,text='Drop table',command=drop,font=('none 13 bold'),relief='raise')
buttdrop.place(x=180,y=380)

buttupdate=Button(root,padx=2,pady=2,text='Update',command=updateContact,font=('none 13 bold'),relief='raise')
buttupdate.place(x=80,y=280)
      
labuname=Label(root,text='Update Name :',font=('none 13 bold'))
labuname.place(x=0,y=200)

enttupadtename=Entry(root,width=20,font=('none 13 bold'),textvar=name)
enttupadtename.place(x=160,y=200)

labuphone=Label(root,text='Provide Phone No. :',font=('none 13 bold'))
labuphone.place(x=0,y=240)

entupdatephone=Entry(root,width=20,font=('none 13 bold'),textvar=phone)
entupdatephone.place(x=210,y=240)

labdelete=Label(root,text='Delete :',font=('none 13 bold'))
labdelete.place(x=0,y=340)

endelete=Entry(root,width=20,textvar=dell,font=('none 13 bold'))
endelete.place(x=90,y=340)


butdel=Button(root,padx=2,pady=2,text='Delete',command=det,font=('none 13 bold'))
butdel.place(x=90,y=380)
    

but=Button(root,padx=2,pady=2,text='Submit',command=insert,font=('none 13 bold'))
but.place(x=60,y=100)

res=Button(root,padx=2,pady=2,text='Show',command=show,font=('none 13 bold'))
res.place(x=160,y=100)



root.mainloop()
