import tkinter as tk
from capstoneFunctions import sql_connection, check_db, drug_data, check_update_db

#DB_PATH = 'C:/Users/ianmc/aws_python_course/Capstone/SQL/test1.db'
DB_PATH = ':memory:'
COMMON_DRUGS = ['asprin']

class drugLookup(tk.Frame):
    def __init__(self, master, con):
        self.con = con
        tk.Frame.__init__(self, master)
        self.configure(bg="#232f3e")
        self.current_selection = tk.LabelFrame(self)
        # Init radiobutton var
        self.rb_val = tk.StringVar(self, "SPL")
        # Init entry
        self.entry_a = tk.Entry(self, width=30, font=('Helvetica', 12))
        self.entry_a.bind("<Double-1>",
                          lambda cl: self.entry_a.delete(0, "end"))
        self.entry_a.insert("0", "Search")
        # Init buttons
        self.button_a = tk.Button(self, text="Search", command=self.search,
                                  font=('Helvetica', 12, 'bold'),
                                  bg='#e47911', fg='white',
                                  activebackground='white',
                                  activeforeground='#e47911')
        self.entry_a.grid(row=0, column=0, columnspan=2)
        self.button_a.grid(row=0, column=2)
        self.current_selection.grid(row=1, column=0, columnspan=3)
        self.grid()
        
    def search(self):
        input_string = self.entry_a.get().upper()
        if input_string in COMMON_DRUGS:
            check_update_db(self.con, input_string) # If you want to update db with new searchs
        self.column_names, self.info_list = drug_data(self.con, input_string)
        self.display()
        
    def display(self):
        self.current_selection.destroy()
        self.current_selection = tk.LabelFrame(self, text='Current Selection',
                                            padx=10, pady=10, 
                                            bg='#e47911', fg='white',
                                            font=('Helvetica', 10, 'bold'))
        self.current_selection.grid(row=3, column=0, sticky=tk.NSEW)
        # Add a canvas in that frame.
        canvas = tk.Canvas(self.current_selection)
        canvas.grid(row=0, column=0)
        # Create a vertical scrollbar linked to the canvas.
        vsbar = tk.Scrollbar(self.current_selection,
                             orient=tk.VERTICAL,
                             command=canvas.yview)
        vsbar.grid(row=0, column=1, sticky=tk.NS)
        canvas.configure(yscrollcommand=vsbar.set)
        # Create a horizontal scrollbar linked to the canvas.
        hsbar = tk.Scrollbar(self.current_selection,
                             orient=tk.HORIZONTAL,
                             command=canvas.xview)
        hsbar.grid(row=1, column=0, sticky=tk.EW)
        canvas.configure(xscrollcommand=hsbar.set)
        # Create a frame on the canvas to contain the buttons.
        table = tk.Frame(canvas)
        # Add Column Names
        for index in range(len(self.column_names)):
            cell = tk.Entry(table, width=len(self.column_names[index]))
            cell.grid(row=0, column=index, sticky=tk.NSEW)
            cell.insert(tk.END, self.column_names[index])
        i=1 # row value inside the loop 
        for row in self.info_list:
            for j in range(len(row)):
                
                if len(str(row[j])) > 50:
                    e_width = 50
                else:
                    e_width = len(str(row[j]))
                
                cell = tk.Entry(table, width=e_width) 
                cell.grid(row=i, column=j, sticky=tk.NSEW) 
                cell.insert(tk.END, row[j])
            i+=1
        # Create canvas window to hold the buttons_frame.
        canvas.create_window((0,0), window=table, anchor=tk.NW)

        table.update_idletasks()  # Needed to make bbox info available.
        bbox = canvas.bbox(tk.ALL)  # Get bounding box of canvas with table.
        canvas.configure(scrollregion=bbox, width=1010, height=250)
        
        if len(self.info_list) == 0:
            self.label = tk.Label(self.current_selection, text="No Items Found.")
            self.label.pack()
        self.current_selection.grid(columnspan=3)
        

if __name__ == "__main__":
    try:
        root = tk.Tk()
        root.title("Drug Database")
        root.iconbitmap('AWS_Logo.ico')
        con = sql_connection(DB_PATH)
        check_db(con)
        app = drugLookup(root, con)
        app.mainloop()
    except:
        print('The application failed to run.')
    finally:
        con.close()