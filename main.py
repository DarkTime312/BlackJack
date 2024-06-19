import tkinter as tk
from tkinter import ttk
import random

import customtkinter as ctk
from PIL import Image, ImageTk

from data import cards_dictionary, cards


def frame_generator(parent, *, name):
    class PlayerFrame(ctk.CTkFrame):
        def __init__(self, parent):
            super().__init__(master=parent, width=1700, height=500)
            self.main_app = parent
            self.card_width = parent.card_width
            self.card_height = parent.card_height
            self.cards_top_left_coords = []
            self.player_score = []

            self.player_canvas = tk.Canvas(self, background='green', width=1700, height=500, borderwidth=0,
                                           highlightthickness=0)
            self.player_canvas.pack(expand=True, fill='both')
            self.create_place_holders()
            self.player_canvas.create_text(10, 10, text=name, font=('Helvetica', 22), anchor='nw')
            self.score_label = ctk.CTkLabel(self, text='0', font=('Helvetica', 22), bg_color='green')
            self.player_canvas.create_window(10, 250, anchor='nw', window=self.score_label)

            # self.place_a_card()

        def create_place_holders(self):
            x_padding = 100
            y_padding = 80
            card_width = self.card_width
            card_height = self.card_height
            for _ in range(5):
                self.player_canvas.create_rectangle(
                    (x_padding, y_padding, card_width + x_padding, card_height + y_padding),
                    outline='dark green',
                    width=10)
                self.cards_top_left_coords.append((x_padding, y_padding))
                x_padding += (30 + card_width)
            self.cards_top_left_coords = iter(self.cards_top_left_coords)

        def place_a_card(self):
            try:
                card_coord = next(self.cards_top_left_coords)
                random_card = self.main_app.deck.get(next(self.main_app.chosen_card))
                random_card_path = random_card[0]
                random_card_score = random_card[1]
                self.player_canvas.create_image(card_coord, image=random_card_path, anchor='nw')
                self.player_score.append(random_card_score)
                self.score_label.configure(text=sum(self.player_score))
            except StopIteration:
                pass

    return PlayerFrame(parent)


class BlackJack(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color='green')

        self.title('Black Jack Game')
        self.geometry('1800x1200')
        self.card_width = 250
        self.card_height = 360
        self.deck = {
            card: (ImageTk.PhotoImage(Image.open(cards_dictionary.get(card)[0]).resize(size=(250, 360))),
                   cards_dictionary.get(card)[1])
            for card in random.sample(cards, k=20)
        }
        self.chosen_card = iter(self.deck.keys())
        print(self.deck)

        self.dealer_frame = frame_generator(self, name='Dealer')
        self.dealer_frame.pack()

        self.player_frame = frame_generator(self, name='Player')
        self.player_frame.pack()

        self.button = ctk.CTkButton(self, text='Deal a card', command=self.dealer_frame.place_a_card)
        self.button.pack()

        self.button2 = ctk.CTkButton(self, text='Deal player', command=self.player_frame.place_a_card)
        self.button2.pack()
        print(self.deck)




app = BlackJack()
app.mainloop()
