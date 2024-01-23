import random
import tkinter as tk
from tkinter import Button, Label, Entry, Canvas, Frame, Scrollbar, VERTICAL, LEFT, Y, RIGHT, messagebox
import Bingo  # Import the core Bingo code
import pandas as pd
from turtle import RawTurtle
import turtle
import tkinter.font as tkFont

# Function to close the application
def quit_application():
    root.destroy()


# Callback function for canvas resizing
def on_configure(config):
    config.configure(scrollregion=config.bbox('all'))


# Function to validate positive integers within a specified range
def validate_positive_int(entry, field_name, min_value, max_value):
    value_str = entry.get()

    if value_str.isdigit():
        value = int(value_str)

        if min_value <= value <= max_value:
            return value
        else:
            messagebox.showerror("Error", f"{field_name} should be between {min_value} and {max_value}."
                                          f" Please enter a valid positive integer.")
    else:
        messagebox.showerror("Error", f"Please enter a valid positive integer for {field_name}.")

    return None


# Function to clear entry fields
def clear_entry_fields():
    num_simulations_entry.delete(0, 'end')
    num_cards_per_simulation_entry.delete(0, 'end')


# Main Tkinter window setup
root = tk.Tk()
root.title("Bingo Simulation")
root.geometry("800x800")
root.configure(bg='lightblue')

# Create a custom font with specific properties
heading_font = tkFont.Font(family="Helvetica", size=36, weight="bold", slant="italic", underline=False)

# Add a heading to the main window with the specified font properties
heading_label = tk.Label(root, text="Bingo 75", font=heading_font, bg='coral', fg='white',
                    bd=3, relief="solid", width=8, height=1, highlightbackground='white')
heading_label.pack(pady=5)

global_cards = []  # Initialize an empty list to store global cards


# Function to plot standard deviation graph
def standard_dev_plot(num_simulations, num_cards_per_simulation):
    cards = Bingo.plot_graph(num_simulations, num_cards_per_simulation)
    return cards


# Function to plot histogram
def histogram_plot():
    hist_plot = Bingo.histogram_plot()
    return hist_plot


# Function to display initial cards in a separate window
def display_initial_cards():
    # Read the generated cards from the CSV file
    cards_df = pd.read_csv('generated_cards.csv')

    # Use the correct column name to access the cards
    global global_cards
    global_cards = cards_df['Bingo Cards'].apply(eval).tolist()

    # Create a new window to display initial cards with a scrollable frame
    initial_cards_window = tk.Toplevel(root)
    initial_cards_window.title("Initial Bingo Cards")

    canvas_frame = Frame(initial_cards_window)
    canvas_frame.pack(side=LEFT)

    # Use a different name for the local canvas variable
    local_canvas = Canvas(canvas_frame, width=1200, height=800)
    local_canvas.pack(side=LEFT, fill=Y)

    scrollbar = Scrollbar(canvas_frame, orient=VERTICAL, command=local_canvas.yview, width=20)
    scrollbar.pack(side=RIGHT, fill=Y)

    local_canvas.configure(yscrollcommand=scrollbar.set)

    local_canvas.bind('<Configure>', lambda event, canvas=local_canvas: on_configure(canvas))

    frame = Frame(local_canvas)
    local_canvas.create_window((0, 0), window=frame, anchor='nw')

    cards_per_row = 10
    row_height = 150
    card_spacing = 30

    for i, card in enumerate(global_cards):
        column_num = i % cards_per_row
        row_num = i // cards_per_row

        frame_column = column_num * (2 + card_spacing)
        frame_row = row_num * (row_height + card_spacing)

        label = Label(frame, text=f"Player {i + 1}")
        label.grid(row=frame_row + 1, column=frame_column + 1, pady=5, padx=5)

        for row_index, row in enumerate(card):
            row_label = Label(frame, text=' | '.join(map(lambda x: str(x).rjust(2), row)))
            row_label.grid(row=frame_row + row_index * 2 + 3, column=frame_column + 1, pady=2, padx=5)

    initial_cards_window.after(100, lambda: local_canvas.update_idletasks())
    initial_cards_window.after(200, lambda: local_canvas.configure(scrollregion=local_canvas.bbox('all')))


# Colors for fireworks animation
colors = ['blue', 'red', 'yellow', 'orange', 'purple', 'magenta', 'pink', 'lime',
          'green', 'gold', 'silver', 'violet']


# Function for fireworks animation
def fireworks_animation(t):
    x = random.randint(-200, 200)
    y = random.randint(-200, 200)
    t.penup()
    t.goto(x, y)
    t.pendown()
    t.color(random.choice(colors))
    d = random.randint(20, 100)

    for i in range(36):
        t.forward(d)
        t.backward(d)
        t.right(10)


# Function to start the simulation
def start_simulation():
    num_simulations = validate_positive_int(num_simulations_entry, "Number of Simulations", 1, 110)
    num_cards_per_simulation = validate_positive_int(
        num_cards_per_simulation_entry, "Number of Cards per simulation", 3, 60)

    if num_simulations is not None and num_cards_per_simulation is not None:
        print(f"Number of simulations: {num_simulations}")
        print(f"Number of cards per simulation: {num_cards_per_simulation}")

        # Run Bingo game simulations
        Bingo.main(num_cards_per_simulation, num_simulations)

        # Create a frame to hold the buttons in a row
        buttons_frame = tk.Frame(frame, bg='light blue')
        buttons_frame.pack(pady=10)

        # Create and pack buttons in the new frame
        display_initial_cards_button = Button(
            buttons_frame,
            text="Display Initial Cards",
            command=display_initial_cards, fg="white", bg="grey")
        display_initial_cards_button.pack(side=tk.LEFT, padx=10)

        make_graph_button = Button(
            buttons_frame,
            text="Display Bingo vs Turn Graph",
            command=lambda: standard_dev_plot(num_simulations, num_cards_per_simulation),
            fg="white", bg="grey")
        make_graph_button.pack(side=tk.LEFT, padx=10)

        make_hist_button = Button(
            buttons_frame,
            text="Display Histogram",
            command=histogram_plot, fg="white", bg="grey")
        make_hist_button.pack(side=tk.LEFT, padx=10)

        # Tkinter canvas for fireworks
        canvas_for_fireworks = Canvas(frame, width=800, height=500, bg='black')
        canvas_for_fireworks.pack()

        # Turtle canvas for fireworks
        turtle_screen = turtle.TurtleScreen(canvas_for_fireworks)
        turtle_screen.bgcolor('black')

        myturtle = RawTurtle(turtle_screen)
        myturtle.speed(0)
        myturtle.hideturtle()

        for i in range(4):
            fireworks_animation(myturtle)

        myturtle.penup()
        myturtle.goto(0, 100)
        myturtle.color('white')
        myturtle.write("Simulation Complete!", align="center", font=("Verdana", 24, "normal"))

        clear_entry_fields()


# Main frame setup
frame = tk.Frame(root, bg='light blue')
frame.pack()

# Labels, entry fields, and buttons setup
num_cards_per_simulation_label = Label(
    frame,
    text="Number of Bingo Cards per simulation: (+ve integer, 3-60)",
    fg="white", bg="grey")
num_cards_per_simulation_label.pack()

num_cards_per_simulation_entry = Entry(frame)
num_cards_per_simulation_entry.pack()

num_simulations_label = Label(frame, text="Number of Simulations: (+ve integer, 1-110)",  fg="white", bg="grey")
num_simulations_label.pack()

num_simulations_entry = Entry(frame)
num_simulations_entry.pack()

start_button = Button(frame, text="Start Simulation", command=start_simulation,  fg="white", bg="grey")
start_button.pack()

quit_button = Button(frame, text="Quit", command=quit_application,  fg="white", bg="red")
quit_button.pack()

# Start Tkinter main loop
root.mainloop()
