import tkinter as tk
# from tkinter import ttk
import random

import customtkinter as ctk
from PIL import Image, ImageTk

from data import cards_dictionary


# random.seed(5)
class PlayerFrame(ctk.CTkFrame):
    def __init__(self, parent, name):
        super().__init__(master=parent, width=1400, height=500)
        self.main_app = parent
        self.name = name
        self.card_width = parent.card_width
        self.card_height = parent.card_height
        self.cards_top_left_coords = []
        self.player_score = []

        self.player_canvas = tk.Canvas(self, background='green', width=1700, height=400, borderwidth=0,
                                       highlightthickness=0)
        self.player_canvas.pack(expand=True, fill='both')
        self.create_place_holders()
        self.player_canvas.create_text(10, 10, text=name, font=('Helvetica', 22), anchor='nw')
        self.score_label = ctk.CTkLabel(self, text='0', font=('Helvetica', 22), bg_color='green')
        self.player_canvas.create_window(10, 250, anchor='nw', window=self.score_label)
        if name == 'Player':
            # Deal 2 cards to player at the start
            self.place_a_card()
            self.place_a_card()
        else:
            # Deal 1 card for Dealer
            self.place_a_card()

    def create_place_holders(self):
        x_padding = 100
        y_padding = 80
        card_width = self.card_width
        card_height = self.card_height
        for _ in range(7):
            self.player_canvas.create_rectangle(
                (x_padding, y_padding, card_width + x_padding, card_height + y_padding),
                outline='dark green',
                width=10)
            self.cards_top_left_coords.append((x_padding, y_padding))
            x_padding += (30 + card_width)
        self.cards_top_left_coords = iter(self.cards_top_left_coords)

    def place_a_card(self):
        try:
            if not self.main_app.game_ended:
                card_coord = next(self.cards_top_left_coords)
                random_card = self.main_app.deck.get(next(self.main_app.chosen_card))
                random_card_path = random_card[0]
                self.player_canvas.create_image(card_coord, image=random_card_path, anchor='nw')

                random_card_score = random_card[1]
                self.update_score(random_card_score)
                self.update_title()
                self.check_ending()

        except StopIteration:
            pass

    def dealer_playing(self):
        if not self.main_app.game_ended:
            self.main_app.dealer_frame.place_a_card()
            self.list_of_dealer_points = self.main_app.dealer_frame.player_score
            self.list_of_user_points = self.main_app.player_frame.player_score
            if sum(self.list_of_dealer_points) < 17:
                self.after(500, self.dealer_playing)
            else:
                self.game_over()
                self.check_ending()
        else:
            self.check_ending()

    def update_score(self, score=0):
        self.player_score.append(score)
        self.score_label.configure(text=sum(self.player_score))

    def update_title(self):
        self.main_app.number_of_cards_left -= 1
        self.main_app.title(f'{self.main_app.number_of_cards_left} Cards Left in the Deck')

    def busted(self):
        list_of_points = self.player_score
        if sum(list_of_points) > 21:
            if 11 in list_of_points:
                list_of_points.remove(11)
                list_of_points.append(1)
                self.update_score()
                self.busted()
            else:
                return True
        return False

    def game_over(self):
        self.main_app.game_ended = True

    def check_ending(self):
        if self.busted() and not self.main_app.game_ended:

            if self.name == 'Player':
                self.main_app.result_label.configure(text='Busted.. Dealer Won!')
            else:
                self.main_app.result_label.configure(text='Dealer Busted. You Won')
            self.main_app.game_ended = True
            self.main_app.new_game_btn.grid(row=0, column=3, padx=5)
        elif self.main_app.game_ended:
            # game ended . decide a winner
            number_of_dealer_points = sum(self.main_app.dealer_frame.player_score)
            number_of_player_points = sum(self.main_app.player_frame.player_score)
            if number_of_dealer_points > 21:
                self.main_app.result_label.configure(text='Dealer Busted. You Won')
            elif number_of_dealer_points > number_of_player_points:
                self.main_app.result_label.configure(text='Dealer Won')
            elif number_of_dealer_points < number_of_player_points:
                self.main_app.result_label.configure(text='You won!')
            else:
                self.main_app.result_label.configure(text='Draw!')
            self.main_app.new_game_btn.grid(row=0, column=3, padx=5)


def main():
    class BlackJack(ctk.CTk):
        def __init__(self):
            super().__init__(fg_color='green')
            self.card_width = 150
            self.card_height = 218
            self.initialize_game()

        def initialize_game(self):
            self.number_of_cards_left = 52
            self.game_ended = False
            self.title(f'{self.number_of_cards_left} Cards Left in the Deck')
            self.geometry('1400x1000+50+50')
            self.configure(padx=10)

            self.deck = {
                card: (ImageTk.PhotoImage(
                    Image.open(cards_dictionary.get(card)[0]).resize(size=(self.card_width, self.card_height))),
                       cards_dictionary.get(card)[1])
                for card in random.sample(tuple(cards_dictionary.keys()), k=20)
            }
            self.chosen_card = iter(self.deck.keys())

            # Clear previous frames if they exist
            for widget in self.winfo_children():
                widget.destroy()

            self.dealer_frame = PlayerFrame(self, name='Dealer')
            self.dealer_frame.pack()

            self.result_label = ctk.CTkLabel(self, text='', font=('Helvetica', 40), bg_color='green')
            self.result_label.pack()

            self.player_frame = PlayerFrame(self, name='Player')
            self.player_frame.pack()

            self.buttons_frame = ctk.CTkFrame(self, fg_color='transparent')
            self.buttons_frame.pack()
            self.buttons_font = ('Helvetica', 30)

            self.button = ctk.CTkButton(self.buttons_frame, text='Dealer', command=self.dealer_frame.place_a_card,
                                        font=self.buttons_font)
            self.button.grid(row=0, column=0, padx=5)

            self.button2 = ctk.CTkButton(self.buttons_frame, text='Hit me!', command=self.player_frame.place_a_card,
                                         font=self.buttons_font)
            self.button2.grid(row=0, column=1, padx=5)

            self.button3 = ctk.CTkButton(self.buttons_frame, text='Stand', command=self.player_frame.dealer_playing,
                                         font=self.buttons_font)
            self.button3.grid(row=0, column=2, padx=5)

            self.new_game_btn = ctk.CTkButton(self.buttons_frame, text='Start New game', command=self.restart_game,
                                              font=self.buttons_font)

        def restart_game(self):
            self.initialize_game()

    app = BlackJack()
    app.mainloop()


main()
