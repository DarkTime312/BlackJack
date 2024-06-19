import tkinter as tk
import random

import customtkinter as ctk
from PIL import Image, ImageTk

from data import cards_dictionary


class PlayerFrame(ctk.CTkFrame):
    def __init__(self, parent, name):
        super().__init__(master=parent, width=1400, height=500)
        self.main_app = parent
        self.name = name
        self.card_width = parent.card_width
        self.card_height = parent.card_height
        self.cards_top_left_coords = None  # Coordinates of top left of each card
        self.player_score_list = []

        self.player_canvas = tk.Canvas(self, background='green', width=1700, height=400, borderwidth=0,
                                       highlightthickness=0)
        self.player_canvas.pack(expand=True, fill='both')

        self.create_place_holders()

        self.player_canvas.create_text(10, 10, text=name, font=('Helvetica', 22), anchor='nw')
        self.score_label = ctk.CTkLabel(self, text='0', font=('Helvetica', 22), bg_color='green')
        self.player_canvas.create_window(10, 250, anchor='nw', window=self.score_label)

        # deal the cards at the beginning
        self.initial_deal()

    def initial_deal(self):
        if self.name == 'Player':
            # Deal 2 cards to player at the start
            self.place_a_card()
            self.place_a_card()
        else:
            # Deal 1 card for Dealer
            self.place_a_card()

    def create_place_holders(self):
        """
        Creates the place-holder borders for cards.
        At the end of the loop it will create an iterable of coordinates
        That will be used to place cards later.
        """
        x_padding = 100
        y_padding = 80
        coordinates = []
        for _ in range(7):  # creates 7 place-holders
            self.player_canvas.create_rectangle(
                (x_padding, y_padding, self.card_width + x_padding, self.card_height + y_padding),
                outline='dark green',
                width=10)
            coordinates.append((x_padding, y_padding))  # save the top left corner pos for later
            x_padding += (30 + self.card_width)  # apply padding for next iteration
        self.cards_top_left_coords = iter(coordinates)

    def place_a_card(self):
        try:
            if not self.main_app.game_ended:  # If game is not finished yet
                card_coord = next(self.cards_top_left_coords)  # get the coordinates one at a time
                # select a card from shuffled deck
                random_card = self.main_app.deck.get(next(self.main_app.chosen_card))
                # get the card image's path
                random_card_path = random_card[0]
                # Put the picture at the correct position on table
                self.player_canvas.create_image(card_coord, image=random_card_path, anchor='nw')

                # getting the card score and adding it to the player list of scores.
                random_card_score = random_card[1]
                self.update_score(random_card_score)
                self.update_title()
                self.check_ending()

        except StopIteration:  # No more place-holders left on the table.
            pass

    def dealer_playing(self):
        """Runs the action for dealer when user chooses to stand."""
        if not self.main_app.game_ended:  # If game still has not ended.
            self.main_app.dealer_frame.place_a_card()
            self.list_of_dealer_points = self.main_app.dealer_frame.player_score_list
            self.list_of_user_points = self.main_app.user_frame.player_score_list
            # dealer keeps playing if score is 16 and bellow
            if sum(self.list_of_dealer_points) < 17:
                self.after(500, self.dealer_playing)
            else:  # score is over 16 now
                self.main_app.game_ended = True  # mark the game as finished
                self.check_ending()  # checks the result
        else:  # If game has already been ended.
            self.check_ending()

    def update_score(self, score=None):
        """Updates the score of player on the screen."""
        if score:  # add score only if it's provided
            self.player_score_list.append(score)
        # update the score label
        self.score_label.configure(text=sum(self.player_score_list))

    def update_title(self):
        """Updates the amount of cards left in the deck on the title bar."""
        self.main_app.number_of_cards_left -= 1
        self.main_app.title(f'{self.main_app.number_of_cards_left} Cards Left in the Deck')

    def busted(self):
        """Checks if player passed 21."""
        list_of_points = self.player_score_list
        if sum(list_of_points) > 21:
            if 11 in list_of_points:  # If passed 21 but has an Ace
                # replace 11 with 1 for Ace card
                list_of_points.remove(11)
                list_of_points.append(1)
                self.update_score()  # update label with new score
                return self.busted()       # check for bust once again after the replacement
            else:  # If passed 21 and there's no ace anymore
                return True  # Busted
        return False  # Not busted

    def check_ending(self):
        if self.busted() and not self.main_app.game_ended:  # If user is busted and game is not marked as finished
            # Decide the winner based on which user is busted
            if self.name == 'Player':  # user is busted and dealer won.
                self.main_app.result_label.configure(text='Busted.. Dealer Won!')
            else:  # dealer busted and user won.
                self.main_app.result_label.configure(text='Dealer Busted. You Won')
            self.main_app.game_ended = True  # mark the game as finished
            self.main_app.new_game_btn.grid(row=0, column=2, padx=20)  # make the new game button appear

        elif self.main_app.game_ended:  # If game has ended already
            # Decides the winner based on number of points.
            number_of_dealer_points = sum(self.main_app.dealer_frame.player_score_list)
            number_of_player_points = sum(self.main_app.user_frame.player_score_list)
            # First check if dealer is busted
            if number_of_dealer_points > 21:
                self.main_app.result_label.configure(text='Dealer Busted. You Won')
            elif number_of_dealer_points > number_of_player_points:
                self.main_app.result_label.configure(text='Dealer Won')
            elif number_of_dealer_points < number_of_player_points:
                self.main_app.result_label.configure(text='You won!')
            else:
                self.main_app.result_label.configure(text='Draw!')
            self.main_app.new_game_btn.grid(row=0, column=2, padx=20)


def main():
    """Function to run our game."""
    class BlackJack(ctk.CTk):
        """Main window."""
        def __init__(self):
            super().__init__(fg_color='green')  # Setting the bg color of our window
            # Setting the size of each card on table
            self.card_width = 150
            self.card_height = 218
            self.geometry('1400x900+500+200')

            self.initialize_game()

        def initialize_game(self):
            """Initialize our app."""
            self.number_of_cards_left = 52
            self.game_ended = False  # A flag to show if game is ended or not.
            # Title of our window which shows the number of available cards in Deck.
            self.title(f'{self.number_of_cards_left} Cards Left in the Deck')
            self.resizable(False, False)
            self.configure(padx=10)  # Adding horizontal padding to our window

            # Shuffles and creates a deck of 20 cards.
            # Produces a dictionary of `card name:(path to resized image, card's point)`
            self.deck = {
                card: (ImageTk.PhotoImage(
                    Image.open((dic_value := cards_dictionary.get(card))[0]).resize(size=(self.card_width, self.card_height))),
                       dic_value[1])
                for card in random.sample(tuple(cards_dictionary.keys()), k=20)
            }
            # Create an Iterable out of our deck of cards.
            self.chosen_card = iter(self.deck.keys())

            # Clear previous frames if they exist
            for widget in self.winfo_children():
                widget.destroy()

            # Frame containing Dealer cards
            self.dealer_frame = PlayerFrame(self, name='Dealer')
            self.dealer_frame.pack()

            # A label that will show the result at the end of the game.
            self.result_label = ctk.CTkLabel(self, text='', font=('Helvetica', 40), bg_color='green')
            self.result_label.pack()

            # Frame containing user cards
            self.user_frame = PlayerFrame(self, name='Player')
            self.user_frame.pack()

            # A frame containing the buttons
            self.buttons_frame = ctk.CTkFrame(self, fg_color='transparent')
            self.buttons_frame.place(relx=0.35, rely=0.9)
            self.buttons_font = ('Helvetica', 30)

            self.hit_me_button = ctk.CTkButton(self.buttons_frame, text='Hit me!', command=self.user_frame.place_a_card,
                                               font=self.buttons_font)
            self.hit_me_button.grid(row=0, column=0, padx=20)

            self.stand_button = ctk.CTkButton(self.buttons_frame, text='Stand', command=self.user_frame.dealer_playing,
                                              font=self.buttons_font)
            self.stand_button.grid(row=0, column=1, padx=20)

            self.new_game_btn = ctk.CTkButton(self.buttons_frame, text='Start New game', command=self.restart_game,
                                              font=self.buttons_font)

        def restart_game(self):
            """Restarts our game by Initializing it from beginning"""
            self.initialize_game()

    # run the app
    app = BlackJack()
    app.mainloop()


main()
