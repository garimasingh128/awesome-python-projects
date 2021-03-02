from tkinter import *
import wikipedia
from tkinter import messagebox

class searchwiki:
    def __init__(self,root):
        self.root=root
        self.root.title("The Searching and Editing App")
        self.root.geometry("1360x740+0+0")
        self.root.config(bg="#262626")

        title=Label(self.root,text="SEARCH and EDIT",font=("times new roman",35,"bold"),bg="white",fg="black").place(x=0,y=0,relwidth=1)

        frame1=Frame(self.root,bd=2,relief=RIDGE)
        frame1.place(x=20,y=130,width=1330,height=550)

        self.var_search=StringVar()
        txt_word=Entry(self.root,textvariable=self.var_search,font=("times new roman",20)).place(x=100,y=82,width=500)

        btn_search=Button(self.root,text="Search",command=self.searchword,font=("times new roman",15,"bold"),bg="#262626",fg="white").place(x=620,y=80,height=40,width=120)
        btn_clear=Button(self.root,text="Clear",command=self.clear,font=("times new roman",15,"bold"),bg="#262626",fg="white").place(x=750,y=80,height=40,width=120)
        btn_enable=Button(self.root,text="Enable Editor",command=self.enable,font=("times new roman",15,"bold"),bg="#262626",fg="white").place(x=880,y=80,height=40,width=210)
        btn_disable=Button(self.root,text="Disable Editor",command=self.disable,font=("times new roman",15,"bold"),bg="#262626",fg="white").place(x=1100,y=80,height=40,width=210)

        scrolly=Scrollbar(frame1,orient=VERTICAL)
        scrolly.pack(side=RIGHT,fill="y")

        self.txt_area=Text(frame1,font=("times new roman",15),yscrollcommand=scrolly.set)
        self.txt_area.pack(fill=BOTH,expand=1)
        scrolly.config(command=self.txt_area.yview)

    def enable(self):
        self.txt_area.config(state=NORMAL)

    def disable(self):
        self.txt_area.config(state=DISABLED)

    def clear(self):
        self.var_search.set("")
        self.txt_area.delete('1.0',END)

    def searchword(self):
        if self.var_search.get()=="":
            messagebox.showerror("ERROR","Search box shouldn't be empty")
        else:
            fetch_data=wikipedia.summary(self.var_search.get())
            self.txt_area.insert('1.0',fetch_data)
                
root=Tk()
obj=searchwiki(root)
root.mainloop()