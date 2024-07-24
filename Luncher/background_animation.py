import tkinter as tk
import turtle

def draw_background(root):
    # Create a canvas for turtle graphics
    canvas = tk.Canvas(root, width=root.winfo_screenwidth(), height=root.winfo_screenheight())
    canvas.pack()

    # Create a TurtleScreen embedded in the canvas
    turtle_screen = turtle.TurtleScreen(canvas)
    turtle_screen.bgcolor("#5D5D5D")  # Set background color to #5D5D5D

    # Initialize the turtle
    my_turtle = turtle.RawTurtle(turtle_screen)
    my_turtle.speed(0)
    my_turtle.pensize(2)  # Increase pen size to 2
    my_turtle.color("#1A472A")  # Change turtle color to #1A472A (green)

    # Function to draw the turtle graphic
    def draw_background():
        distance = 10
        for i in range(68):
            for _ in range(4):
                my_turtle.forward(distance)
                my_turtle.right(90)
            my_turtle.right(10)
            distance += 20

    # Draw the turtle graphic as background
    draw_background()

    # Function to close the window when Escape key is pressed
    def close_window(event):
        root.destroy()

    # Bind the Escape key to close the window
    root.bind("<Escape>", close_window)
