import tkinter as tk
from tkinter import StringVar
import map_change
from tkinter import messagebox
import sys


def run(*pargs):
    print(*pargs)
    if searchWord.get() in ('',' ',None):
        messagebox.showinfo('Search error','No Keyword is entered')
    else:
        print("Word:", searchWord.get())
        map_change.main(searchWord.get())

def close(event):
    form.withdraw()
    sys.exit()        

form = tk.Tk()
searchWord= StringVar(form) 

windowWidth = form.winfo_reqwidth()
windowHeight = form.winfo_reqheight()
positionRight = int(form.winfo_screenwidth()/2 - windowWidth/2)
positionDown = int(form.winfo_screenheight()/2 - windowHeight/2)
form.geometry("+{}+{}".format(positionRight, positionDown))

form.minsize(300, 150)
label_search=tk.Label(form, text="Enter Keyword: ",fg='blue')
label_search.grid(row=3, padx=8, pady=8)

entry = tk.Entry(form, textvariable = searchWord)
entry.configure(background='peach puff')
entry.grid(row=3, column=1, pady=30)
entry.focus_set()

form.configure(background='dark turquoise')

form.title("Twitter keyword search")
form.bind('<Return>', run)
button=tk.Button(form, text='Search', command=run, height=2, width=5).grid(row=4, column=1, pady=5) 

form.bind('<Escape>',close)
   
tk.mainloop()