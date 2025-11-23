import tkinter as tk
from tkinter import messagebox, ttk
import random
import sqlite3
import pygame

# --- Sound setup ---
pygame.mixer.init()

MAIN_MUSIC = "HANGMAN_MAIN_MUS.wav"
WIN_SOUND = "HANGMAN_WIN_SOUND2.wav"
LOSE_SOUND = "HANGMAN_LOSS_SOUND.wav"
CLICK_SOUND = "HANGMAN_CLICK_SOUND.wav"

music_enabled = True

# --- Database setup ---
conn = sqlite3.connect("words.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS wordsmysql (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL,
    category TEXT NOT NULL
)
""")

# Populate table if empty
c.execute("SELECT COUNT(*) FROM wordsmysql")
if c.fetchone()[0] == 0:
    c.executemany("INSERT INTO wordsmysql (word, category) VALUES (?, ?)", [
        ("python", "Programming"),
        ("java", "Programming"),
        ("dog", "Animals"),
        ("cat", "Animals"),
        ("turkey", "Countries"),
        ("bulgaria", "Countries")
    ])
conn.commit()
conn.close()

# --- Get random word ---
def get_random_word(category):
    try:
        conn = sqlite3.connect("words.db")
        cursor = conn.cursor()
        if category and category != "All":
            cursor.execute("SELECT word, category FROM wordsmysql WHERE category=? ORDER BY RANDOM() LIMIT 1", (category,))
        else:
            cursor.execute("SELECT word, category FROM wordsmysql ORDER BY RANDOM() LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0].lower(), result[1]
        else:
            return "default", "General"
    except Exception as e:
        messagebox.showinfo("Database Error", str(e))
        return "error", "General"

# --- Hangman Game ---
window = tk.Tk()
window.title("Hangman Game with SQLite + Categories")
window.geometry("500x800")
window.resizable(False, False)

def show_silent_message(title, message):
    win = tk.Toplevel(window)
    win.title(title)
    win.resizable(False, False)
    
    tk.Label(win, text=message, padx=20, pady=20).pack()
    tk.Button(win, text="OK", width=10, command=win.destroy).pack(pady=10)
    
    win.grab_set()
    win.transient(window)
    
    win.update_idletasks()
    w = win.winfo_width()
    h = win.winfo_height()
    ws = window.winfo_x() + window.winfo_width() // 2
    hs = window.winfo_y() + window.winfo_height() // 2
    x = ws - w // 2
    y = hs - h // 2
    win.geometry(f"{w}x{h}+{x}+{y}")
# --- Global variables ---
word_to_guess = ""
word_category = ""
guessed_letters = []
attempts = 6
max_attempts = 6

def play_main_music():
    if music_enabled:
        pygame.mixer.music.load(MAIN_MUSIC)
        pygame.mixer.music.play(-1)


def stop_main_music():
    pygame.mixer.music.stop()


def toggle_music():
    global music_enabled
    music_enabled = not music_enabled

    if music_enabled:
        play_main_music()
        music_button.config(text="🔊")
    else:
        stop_main_music()
        music_button.config(text="🔇")


def play_click():
    pygame.mixer.Sound(CLICK_SOUND).play()


def play_win_sound():
    stop_main_music()
    pygame.mixer.Sound(WIN_SOUND).play()
    window.after(2000, lambda: play_main_music() if music_enabled else None)


def play_loss_sound():
    stop_main_music()
    pygame.mixer.Sound(LOSE_SOUND).play()
    window.after(2000, lambda: play_main_music() if music_enabled else None)

# --- Functions ---
def update_word_display():
    display_word = " ".join(letter if letter in guessed_letters else "_" for letter in word_to_guess)
    word_label.config(text=display_word)

def update_attempts_display():
    attempts_label.config(text=f"Attempts left: {attempts}")

def update_guessed_letters_display():
    if guessed_letters:
        guessed_label.config(text="Guessed letters: " + ", ".join(guessed_letters))
    else:
        guessed_label.config(text="Guessed letters: None")

def draw_hangman():
    canvas.delete("Hangman")
    if attempts < max_attempts:
        canvas.create_oval(125,125,175,175, width=4, tags="Hangman") # Head
    if attempts < max_attempts-1:
        canvas.create_line(150,175,150,225,width=4, tags="Hangman") # Body
    if attempts < max_attempts-2:
        canvas.create_line(150,200,125,175,width=4, tags="Hangman") # Left Arm
    if attempts < max_attempts-3:
        canvas.create_line(150,200,175,175,width=4, tags="Hangman") # Right Arm
    if attempts < max_attempts-4:
        canvas.create_line(150,225,125,250,width=4, tags="Hangman") # Left Leg
    if attempts < max_attempts-5:
        canvas.create_line(150,225,175,250,width=4, tags="Hangman") # Right Leg

def check_win():
    return all(letter in guessed_letters for letter in word_to_guess)

def check_loss():
    return attempts == 0

# --- Unified guess processing ---
def process_guess(letter):
    global attempts
    letter = letter.lower()
    
    if not letter.isalpha() or len(letter) != 1:
        return
    
    if letter in guessed_letters:
        return  # silently ignore duplicates
    
    guessed_letters.append(letter)
    
    if letter in btns:
        btns[letter].config(state="disabled")
    
    if letter in word_to_guess:
        update_word_display()
        update_guessed_letters_display()
        if check_win():
            play_win_sound()
            show_silent_message("Hangman", "Congrats! You won!")
            reset_game()
    else:
        attempts -= 1
        update_attempts_display()
        update_guessed_letters_display()
        draw_hangman()
        if attempts == max_attempts - 3 and len(word_to_guess) > 3:
            hint_button.config(state=tk.NORMAL)
        if check_loss():
            play_loss_sound()
            show_silent_message("Hangman", f"You lose! The word was: {word_to_guess}")
            reset_game()

# --- Entry and keyboard handlers ---
def guess_letter():
    letter = letter_entry.get()
    letter_entry.delete(0, tk.END)
    process_guess(letter)

def on_key_press(ch):
    letter_entry.delete(0, tk.END)
    letter_entry.insert(0, ch)
    process_guess(ch)

# --- Hint ---
def give_hint():
    hidden_letters = [letter for letter in word_to_guess if letter not in guessed_letters]
    if len(word_to_guess) > 3 and hidden_letters:
        hint_letter = random.choice(hidden_letters)
        guessed_letters.append(hint_letter)
        update_word_display()
        update_guessed_letters_display()
        messagebox.showinfo("Hint", f"A hint was given! The letter '{hint_letter}' is revealed.", icon=None)
        hint_button.config(state=tk.DISABLED)

# --- Game start/reset ---
def start_game():
    global word_to_guess, word_category, guessed_letters, attempts
    selected_category = category_choice.get()
    word_to_guess, word_category = get_random_word(selected_category)
    guessed_letters = []
    attempts = max_attempts
    category_label.config(text=f"Category: {word_category}")
    update_word_display()
    update_attempts_display()
    update_guessed_letters_display()
    draw_hangman()
    reset_keyboard()
    hint_button.config(state=tk.DISABLED)
    play_main_music()

def reset_game():
    start_game()

# --- GUI ---
category_label = tk.Label(window, text="Select a category to start", font=("Arial",16), fg="purple")
category_label.pack()

# Music toggle button (top-right)
music_button = tk.Button(window, text="🔊", font=("Arial", 16), command=toggle_music)
music_button.place(x=450, y=10)

categories = ["All", "Programming", "Animals", "Countries"]
category_choice = ttk.Combobox(window, values=categories)
category_choice.current(0)
category_choice.pack()

start_button = tk.Button(window, text="Start Game", command=lambda: (play_click(), start_game()))
start_button.pack()

word_label = tk.Label(window, text="", font=("Arial",24))
word_label.pack()

attempts_label = tk.Label(window, text=f"Attempts left: {attempts}", font=("Arial",16))
attempts_label.pack()

guessed_label = tk.Label(window, text="Guessed letters: None", font=("Arial",14), fg="blue")
guessed_label.pack()

letter_entry = tk.Entry(window, width=5, font=("Arial",16))
letter_entry.bind("<Return>", lambda e: guess_letter())
letter_entry.pack()

guess_button = tk.Button(window, text="Guess", command=lambda: (play_click(), guess_letter()))
guess_button.pack()

reset_button = tk.Button(window, text="Reset", command=lambda: (play_click(), reset_game()))
reset_button.pack()

hint_button = tk.Button(window, text="Hint", command=lambda: (play_click(), give_hint()), state=tk.DISABLED)
hint_button.pack(pady=5)

canvas = tk.Canvas(window, width=300, height=300)
canvas.create_line(50,250,250,250, width=4) # Base
canvas.create_line(200,250,200,100, width=4) # Post
canvas.create_line(100,100,200,100, width=4) # Beam
canvas.create_line(150,100,150,120, width=4) # Rope
canvas.pack()

# --- Virtual keyboard ---
keyboard_frame = tk.Frame(window)
keyboard_frame.pack(pady=10)

qwerty_rows = [
    "q w e r t y u i o p",
    "a s d f g h j k l",
    "z x c v b n m"
]

btns = {}
for row_keys in qwerty_rows:
    row_frame = tk.Frame(keyboard_frame)
    row_frame.pack()
    for ch in row_keys.split():
        btn = tk.Button(row_frame, text=ch.upper(), width=4, height=2,
                        command=lambda c=ch: (play_click(), on_key_press(c)))
        btn.pack(side=tk.LEFT, padx=2, pady=2)
        btns[ch] = btn

def reset_keyboard():
    for b in btns.values():
        b.config(state="normal")

# --- Start ---
start_game()
window.mainloop()
