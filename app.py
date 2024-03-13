from tkinter import *
import tkinter as tk
from tkinter import ttk
import re
from countries import *
from graph import *
from source import *


class CurrencyConverter:
    """An application to convert currencies and generate exchange rate graph."""
    # Initialize the app
    def __init__(self, source):
        self.data = requests.get(source).json()
        self.currencies = self.data['rates']

    # Function to calculate converted amount.
    def convert(self, from_currency, to_currency, amount):
        # if not converting from USD, divide by from_currency rates to find to currency amount
        # if converting from USD, to_currency is the amount because it was quoted based on USD
        if from_currency != 'USD':
            amount = amount / self.currencies[from_currency]
        # rounding the result
        amount = round(amount * self.currencies[to_currency], 2)
        return amount


class App(tk.Tk):
    """A class to run the app using Tkinter"""
    def __init__(self, *args, **kwargs):
        # initialize the class
        tk.Tk.__init__(self, *args, **kwargs)
        self.converter = converter

        # creating a container to switch between pages
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # app dimensions and frames
        self.geometry("400x700")
        self.frames = {}

        # moving between pages of the app using a for loop
        for page in (Convert, Graph):
            frame = page(container, self)
            self.frames[page] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(Convert)    # default is Converter page

    # to show the current frame
    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()


class Convert(tk.Frame):
    """A class for the Convert page with buttons for its functions and to go Graph page."""
    def __init__(self, parent, controller):
        """Initialize Frame"""
        tk.Frame.__init__(self, parent)
        self.converter = converter
        # creating and placing converter button
        button1 = ttk.Button(self, text="Converter")
        button1.place(x=130, y=70)

        # creating and placing graph button
        button2 = ttk.Button(self, text="Graph", command=lambda: controller.show_frame(Graph))
        button2.place(x=210, y=70)

        # declaring variables to be used by multiple methods
        self.amount_field = None
        self.converted_amount_field = None
        self.from_currency_variable = None
        self.to_currency_variable = None
        self.from_currency_dropdown = None
        self.to_currency_dropdown = None

        # initialize components of the frame
        self.description()
        self.currency_entry_boxes()
        self.amount_entry_boxes()
        self.convert_button()
        self.look_up()

    def validator(self, action, string):
        """To validate entry as amount only."""
        # validate that input is only numbers
        regex = re.compile(r"\d*?(\.)?\d,*$")
        result = regex.match(string)
        return string == "" or (string.count('.') <= 1 and result is not None)

    def description(self):
        """Function for page intro and From/To labels"""
        # Page intro
        intro_box = Label(self, text=' CURRENCY CONVERTER', fg='black')
        intro_box.config(font=('Cambria', 25, 'bold', 'italic'))
        intro_box.place(relx=0.5, rely=0.05, anchor=CENTER)

        # from and to amount description
        from_amount_text = Label(self, text=' Original', fg='black')
        from_amount_text.config(font=('Cambria', 10, 'bold', 'italic'))
        from_amount_text.place(x=210, y=130)
        to_amount_text = Label(self, text=' Converted', fg='black')
        to_amount_text.config(font=('Cambria', 10, 'bold', 'italic'))
        to_amount_text.place(x=210, y=180)

    def currency_entry_boxes(self):
        """Function for currency entry boxes"""
        # dropdowns
        self.from_currency_variable = StringVar(self)
        self.from_currency_variable.set("CAD")  # default value
        self.to_currency_variable = StringVar(self)
        self.to_currency_variable.set("GBP")  # default value
        font = ("Cambria", 12, "bold")
        self.option_add('*TCombobox*Listbox.background', 'aquamarine')
        self.option_add('*TCombobox*Listbox.font', font)
        self.from_currency_dropdown = ttk.Combobox(self, textvariable=self.from_currency_variable,
                                                   values=list(self.converter.currencies.keys()), font=font,
                                                   state='readonly', width=10, justify=tk.CENTER)

        self.to_currency_dropdown = ttk.Combobox(self, textvariable=self.to_currency_variable,
                                                 values=list(self.converter.currencies.keys()), font=font,
                                                 state='readonly', width=10, justify=tk.CENTER)
        # placing boxes
        self.from_currency_dropdown.place(x=60, y=150)
        self.to_currency_dropdown.place(x=60, y=200)

    def amount_entry_boxes(self):
        """Function for amount entry and converted amount boxes"""
        # Currency entry boxes
        valid = (self.register(self.validator), '%d', '%P')  # to validate numbers entered

        self.amount_field = Entry(self, bd=3, bg='turquoise1', relief=tk.SUNKEN, font='Cambria', justify=tk.RIGHT,
                             width=15, validate='key', validatecommand=valid)
        self.converted_amount_field = Label(self, text='', fg='black', bg='sienna1', relief=tk.SUNKEN,
                                       font='Cambria', width=15, borderwidth=3, anchor='e')
        # placing boxes
        self.amount_field.place(x=210, y=150)
        self.converted_amount_field.place(x=210, y=200)

    def convert_button(self):
        """Function to generate convert button"""
        # Convert button
        convert_button = Button(self, text="Convert", fg="black", command=self.execute)
        convert_button.config(font=('Cambria', 12, 'bold'))
        convert_button.place(relx=0.5, y=255, anchor=CENTER)

    def execute(self):
        """Function to execute conversion"""
        amount = float(self.amount_field.get())
        from_curr = self.from_currency_variable.get()
        to_curr = self.to_currency_variable.get()
        converted_amount = round(self.converter.convert(from_curr, to_curr, amount),2)
        converted_amount = "{:,}".format(converted_amount)
        self.converted_amount_field.config(text=str(converted_amount), justify=tk.RIGHT)

    def look_up(self):
        """Function for currency look up feature, with sub functions."""
        # Currency lookup labels
        look_up = Label(self, text='Look up currency by country name', fg='black')
        look_up.config(font=('Cambria', 9, 'bold', 'italic'), fg='red')
        look_up.place(x=60, y=280)

        def update(data):
            """Update list as user inputs"""
            curr_list.delete(0, END)
            for country in data:
                curr_list.insert(END, country)

        def fillout(event):
            """Add clicked item to list box"""
            # delete what's in the search box
            search_box.delete(0, END)
            # add clicked list item to entry box
            search_box.insert(0, curr_list.get(ANCHOR))

        def check(event):
            """Function to check user entry vs listbox"""
            typed = search_box.get()
            if typed == '':
                data = countries
            else:
                data = []
                for country in countries:
                    if typed.lower() in country.lower():
                        data.append(country)
            # update listbox with selected country
            update(data)

        # Search box
        search_box = Entry(self, font=('Cambria', 12), width=33)
        search_box.place(x=60, y=300)

        # List box
        curr_list = Listbox(self, width=50)
        curr_list.place(x=60, y=330)
        update(countries)
        # create binding on listbox onclick
        curr_list.bind("<<ListboxSelect>>", fillout)
        search_box.bind("<KeyRelease>", check)


class Graph(tk.Frame):
    """A Class for Graph frame."""
    def __init__(self, parent, controller):
        """ Initialize the frame."""
        tk.Frame.__init__(self, parent)
        # creating and placing converter button
        button1 = ttk.Button(self, text="Converter",
                             command=lambda: controller.show_frame(Convert))
        button1.place(x=130, y=70)
        # creating and placing non-working graph button
        button2 = ttk.Button(self, text="Graph",)
        button2.place(x=210, y=70)
        # for converter to work
        self.converter = converter

        # declaring variables to be used by page
        self.from_currency_variable = None
        self.to_currency_variable = None
        self.from_currency_dropdown = None
        self.to_currency_dropdown = None
        self.from_date = None
        self.to_date = None
        self.memory_button = None

        # initializing frame components
        self.description()
        self.date_entry_boxes()
        self.currency_entry_boxes()
        self.generate_button()
        self.save_button()
        self.run_button()
        self.memory()
        self.clear_memory_button()

    def generate_button(self):
        """ Function to generate Generate Graph button."""
        # Graph generate button
        generate_button = Button(self, text="Generate Graph", fg="black", command=self.execute)
        generate_button.config(font=('Cambria', 12, 'bold'))
        generate_button.place(relx=0.5, rely=0.4, anchor=CENTER)

    def save_button(self):
        """ Function to generate save/show button."""
        # Save button
        save_button = Button(self, text="SAVE/SHOW", fg="blue", command=lambda: self.save(self.memory_button.get()))
        save_button.config(font=('Cambria', 10, 'bold'))
        save_button.place(x=250, y=550, anchor=CENTER)

    def run_button(self):
        """ Function to generate run button."""
        # Load button
        run_button = Button(self, text="RUN", fg="blue",
                                  command=lambda: self.run_saved(self.memory_button.get()))
        run_button.config(font=('Cambria', 10, 'bold'))
        run_button.place(x=320, y=550, anchor=CENTER)

    def memory(self):
        """ Function to generate select memory button."""
        # Saved data select button
        self.memory_button = StringVar(self)
        font = ("Cambria", 10, "bold")

        self.memory_button = ttk.Combobox(self, textvariable=self.memory_button,
                                          values=[x for x in range(1,9)], font=font, state='readonly',
                                          width=15, justify=tk.CENTER)
        self.memory_button.set('Select memory')
        self.memory_button.place(x=60, y=540)

    def clear_memory_button(self):
        """ Function to generate clear memory button."""
        # Clear memory button
        clear_button = Button(self, text="CLEAR MEMORY", fg="blue", command=lambda: self.save(0))
        clear_button.config(font=('Cambria', 10, 'bold'))
        clear_button.place(x=275, y=580, anchor=CENTER)

    def description(self):
        """ Function to generate intro and date labels."""
        # Page intro
        intro_box = Label(self, text=' GRAPH GENERATOR', fg='black')
        intro_box.config(font=('Cambria', 25, 'bold', 'italic'))
        intro_box.place(relx=0.5, rely=0.05, anchor=CENTER)

        # from and to date labels
        from_date_text = Label(self, text=' From date (YYYY-MM-DD)', fg='black')
        from_date_text.config(font=('Cambria', 9, 'bold', 'italic'))
        from_date_text.place(x=210, y=130)
        to_date_text = Label(self, text=' To date (YYYY-MM-DD)', fg='black')
        to_date_text.config(font=('Cambria', 9, 'bold', 'italic'))
        to_date_text.place(x=210, y=180)

    def currency_entry_boxes(self):
        """ Function to generate currency entry boxes."""
        # dropdown
        self.from_currency_variable = StringVar(self)
        self.from_currency_variable.set("CAD")  # default value
        self.to_currency_variable = StringVar(self)
        self.to_currency_variable.set("GBP")  # default value

        font = ("Cambria", 12, "bold")
        self.option_add('*TCombobox*Listbox.background', 'indian red')
        self.option_add('*TCombobox*Listbox.font', font)
        self.from_currency_dropdown = ttk.Combobox(self, textvariable=self.from_currency_variable,
                                                   values=list(currency_list.keys()), font=font,
                                                   state='readonly', width=10, justify=tk.CENTER)
        self.to_currency_dropdown = ttk.Combobox(self, textvariable=self.to_currency_variable,
                                                 values=list(currency_list.keys()), font=font,
                                                 state='readonly', width=10, justify=tk.CENTER)
        # placing
        self.from_currency_dropdown.place(x=40, y=150)
        self.to_currency_dropdown.place(x=40, y=200)

    def date_entry_boxes(self):
        """ Function to generate date entry boxes."""
        # Date Entry box
        self.from_date = Entry(self, bd=3, bg='turquoise1', relief=tk.SUNKEN, font='Cambria', justify=tk.CENTER,
                               width=17, validate='key')
        self.to_date = Entry(self, bd=3, bg='sienna1', relief=tk.SUNKEN, font='Cambria', justify=tk.CENTER,
                             width=17, validate='key')
        # placing
        self.from_date.place(x=210, y=150)
        self.to_date.place(x=210, y=200)

    def save(self, x):
        """ Function to save current parameters to memory"""
        # if selection is not a memory slot, show memory list
        if x == 'Select memory':
            x = x
            infile = open('save.txt', 'r')
            data = infile.readlines()
        # if selection is a memory slot
        else:
            x = int(x)
            # if x = zero (passed from clear memory function), clear memory
            if x == 0:
                f = open('save.txt', 'w')
                data = ['Empty\n' for x in range(8)]
                f.writelines(data)
            # if 1 to 8, write to the selected line in the text file
            else:
                from_curr = self.from_currency_variable.get()
                to_curr = self.to_currency_variable.get()
                from_date = self.from_date.get()
                to_date = self.to_date.get()
                to_save = str([from_curr, to_curr, from_date, to_date])

                # write to file
                infile = open('save.txt', 'r')
                data = infile.readlines()
                data[x-1] = to_save + '\n'
                outfile = open('save.txt', 'w')
                outfile.writelines(data)

        # display data in a list
        saved_list = Listbox(self, height=9, width=45, borderwidth=1)
        saved_list.insert(END, 'Saved graphs\n')
        counter = 1
        for line in data:
            saved_list.insert(END, str(counter) + '/ ' + line + '\n')
            counter += 1
        saved_list.place(x=60, y=350)

    def run_saved(self, y):
        """Function to run graph from saved parameters"""
        # read data from specific line in text file
        f = open('save.txt', 'r')
        y = int(y)
        data = f.readlines()[y-1]
        from_curr = data[2:5]
        to_curr = data[9:12]
        from_date = data[16:26]
        to_date = data[30:40]

        # pass parameters to generate graph
        source = getDataFromAPI(from_curr, to_curr, from_date, to_date)
        graph = Make_Graph(from_curr, to_curr, from_date, to_date, source)
        graph.make_graph()

    def execute(self):
        """Function to run graph from input"""
        from_curr = self.from_currency_variable.get()
        to_curr = self.to_currency_variable.get()
        from_date = self.from_date.get()
        to_date = self.to_date.get()
        # getting data from API
        source = getDataFromAPI(from_curr, to_curr, from_date, to_date)
        # run graph
        graph = Make_Graph(from_curr, to_curr, from_date, to_date, source)
        graph.make_graph()


if __name__ == '__main__':
    url = 'https://api.exchangerate-api.com/v4/latest/USD'
    converter = CurrencyConverter(url)
    App()
    mainloop()

