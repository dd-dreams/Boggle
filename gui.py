from tkinter import *
from tkinter import messagebox
from main import *  # including time library

BOARD = Board()
GAME = Game(BOARD)
TITLE = "Boggle"
STARTUP_RESOLUTION = "600x600+300+300"
INGAME_RESOLUTION = "1000x600+300+300"
STARTUP_BACKGROUND_LOCATION = "images/background.gif"
FADEOUT_BACKGROUND_LOCATION = "images/fadeout_background.gif"
FADEIN_LOGO_LOCATION = "images/fadein_logo.gif"
LOGO_LOCATION = "images/logo.png"
STARTUP_FRAMES_NUM = 24
FADEOUT_FRAMES_NUM = 30
FADEIN_LOGO_FRAMES = 6

MINUTES = 2
SECS = 60

# MESSAGES
TIME_FINISHED = "Time finished.\nDo you want to play again?"
USED_CHAR_MSG = "You already used this char in this place."


class StartMenu:
    def __init__(self):
        self.__root = Tk()
        self.index = 0
        self.fadein_index = 0

        # Background
        self.__logo = PhotoImage(file=LOGO_LOCATION)
        self.__background_generator = (PhotoImage(file=STARTUP_BACKGROUND_LOCATION,
                                                  format=f"gif -index {i}") for i in range(STARTUP_FRAMES_NUM))
        self.__background_frames = [next(self.__background_generator)]
        self.__fadein_bg_generator = (PhotoImage(file=FADEIN_LOGO_LOCATION,
                                                 format=f"gif -index {i}") for i in range(FADEIN_LOGO_FRAMES))
        self.__fadein_bg_frames = [next(self.__fadein_bg_generator)]

        self.__background_frame = Frame(self.__root, height=600, width=600)
        self.__background_canvas = Canvas(self.__background_frame, width=600, height=600)
        self.tmp_bg = self.__background_frames[0]

        # Buttons
        self.__exit_button = Button(self.__root, width=20, text="Exit", bd=1,
                                    height=2, fg='black', command=sys.exit, font=('Courier New', 10))
        self.__start_button = Button(self.__root, width=20, command=self.fadeout_background, text="Start", bd=1,
                                     height=2, font=('Courier New', 10))
        self.is_start_button_pressed = False

    # ENDING
    def spawn_logo(self):
        self.__background_canvas.delete(self.tmp_bg)
        self.__background_canvas.create_image(0, 0, image=self.__logo, anchor=NW)
        self.__background_canvas.pack(fill=BOTH, expand=True)
        self.__root.after(3000, self.__root.destroy)

    def fadeout_background(self):
        """

        :return:
        """
        self.delete_buttons()
        self.is_start_button_pressed = True
        frame = self.__fadein_bg_frames[self.fadein_index]
        self.fadein_index += 1
        self.__background_canvas.delete(self.tmp_bg)
        self.tmp_bg = self.__background_canvas.create_image(0, 0, image=frame, anchor=NW)
        self.__background_canvas.pack(fill=BOTH, expand=True)
        if self.fadein_index == FADEIN_LOGO_FRAMES:
            self.fadein_index = 0
            self.spawn_logo()
            return
        self.__fadein_bg_frames.append(next(self.__fadein_bg_generator))
        self.__root.after(100, self.fadeout_background)

    def delete_buttons(self):
        self.__exit_button.destroy()
        self.__start_button.destroy()

    # BACKGROUND
    def spawn_background(self):
        """

        :return:
        """
        if self.is_start_button_pressed:
            return
        frame = self.__background_frames[self.index]
        self.index += 1
        self.__background_canvas.delete(self.tmp_bg)
        self.tmp_bg = self.__background_canvas.create_image(0, 0, image=frame, anchor=NW)
        self.__background_canvas.pack(fill=BOTH, expand=True)
        if self.index == STARTUP_FRAMES_NUM:
            self.index = 0
        try:
            self.__background_frames.append(next(self.__background_generator))
            self.__root.after(1, self.spawn_background)
        except StopIteration:
            self.__root.after(100, self.spawn_background)

    def handle_bg_frame(self):
        self.__background_frame.pack(fill=BOTH, expand=True)
        self.__background_canvas.pack(fill=BOTH, expand=True)
        self.spawn_background()

    # BUTTONS
    def handle_buttons(self):
        # only possible i could find way to put buttons on Canvas widgets
        self.__background_canvas.create_window(70, 500, anchor=NW, window=self.__exit_button)
        self.__background_canvas.create_window(350, 500, anchor=NW, window=self.__start_button)

    def customize_start_menu(self):
        self.__root.title(TITLE)
        self.__root.geometry(STARTUP_RESOLUTION)
        self.__root.resizable(False, False)
        self.handle_bg_frame()
        self.__root.after(1000, self.handle_buttons)

    def start_gui(self):
        self.__root.mainloop()


class Gui:
    def __init__(self, game_obj, board_obj):
        self.__root = Tk()
        self.game = game_obj
        self.board = board_obj
        self.__ingame_background = PhotoImage(file=LOGO_LOCATION)
        self.submit_button_pressed = False
        self.__minutes = MINUTES
        self.__secs = SECS

        # BOARD STUFF
        self.len_board = len(self.board)
        self.__rows = self.board.return_rows()

        # Widgets
        self.__left_frame = Frame(self.__root, width=250, height=600)
        self.__left_canvas = Canvas(self.__left_frame, width=250, height=600, bg='grey', relief=GROOVE)
        self.__characters_frame = Frame(self.__root, width=750, height=600, bg='white')
        self.time_label = Label(self.__left_frame, width=13, height=3, bd=4, font=('Courier New', 10))
        self.__background_canvas = Canvas(self.__characters_frame, width=1000, height=1000, bd=0, bg='white')
        self.__found_words_label = Label(self.__left_frame, width=20, height=20, font=('Courier New', 10),
                                         relief=GROOVE)

        # BUTTONS
        self.__exit_button = Button(self.__root, width=20, text="Exit", bd=1, bg='red',
                                    height=2, fg='black', command=self.__root.destroy, font=('Courier New', 10))
        self.__submit_button = Button(self.__root, width=20, text="Submit", bd=1, bg='white',
                                      height=2, fg='black', command=self.submit_button,  font=('Courier New', 10))
        self.__char_buttons = []

    def add_and_edit_left_widget(self):
        self.__left_frame.pack(side=RIGHT)
        self.__left_canvas.pack(side=RIGHT)
        self.__left_canvas.create_window(130, 50, window=self.time_label)
        self.__left_canvas.create_window(130, 550, window=self.__exit_button)
        self.__left_canvas.create_window(130, 470, window=self.__submit_button)
        self.__left_canvas.create_window(130, 250, window=self.__found_words_label)

    def add_words(self):
        """
        this method will add the found words in found words label.
        :return:
        """
        tmp = ""
        found_words = self.game.return_found_words()
        for word in found_words:
            tmp += word
        self.__found_words_label.configure(text=tmp)

    def submit_button(self):
        self.submit_button_pressed = True
        self.check_input(self.__submit_button)

    @staticmethod
    def time_finished():
        result = messagebox.askyesno("Time's up!", TIME_FINISHED)
        return result

    def check_what_buttons_are_pressed(self):
        for button in self.__char_buttons:
            if button[1]:
                button[0].configure(highlightthickness=2, highlightbackground="red")
            else:
                button[0].configure(highlightthickness=1, highlightbackground="white")

    def reset_everything(self):
        """
        this method will reset everything. used for when the time has finished.
        :return:
        """
        # resetting buttons
        self.board = Board()
        self.game = Game(self.board)
        for button, char in zip(self.__char_buttons, self.board.return_chars()):
            button[0].configure(text=char)
        # resetting timer
        self.__minutes = 2
        self.__secs = 60
        self.update_timer()

    def update_timer(self):
        if not self.__minutes and not self.__secs:
            if self.time_finished():
                self.reset_everything()
                return
            else:
                sys.exit()
        if not self.__secs:
            self.__secs = 60
            self.__minutes -= 1
        self.__secs -= 1
        current_time = f"{self.__minutes}:{self.__secs}"
        self.time_label.configure(text=current_time)
        self.__root.after(1000, self.update_timer)

    @staticmethod
    def get_button_input(button):
        """

        :param button: button object
        :return: return the button text, and coordinate
        """

        return button[-1]

    @staticmethod
    def show_alert(msg):

        messagebox.showinfo("IMPORTANT", message=msg)

    def reset_buttons(self):
        for button in self.__char_buttons:
            button[1] = False
            button[0].configure(highlightthickness=1, highlightbackground="white")

    def check_input(self, button):
        if self.submit_button_pressed:
            inp = 'SUBMIT'
            self.submit_button_pressed = False
        else:
            inp = self.get_button_input(button)
            if inp in self.game.return_used_chars():
                self.show_alert(USED_CHAR_MSG)
                return
        user_input = self.game.get_input(inp=inp)
        final = react_to_input(user_input, self.game)
        if final == WORD_ALREADY_FOUND or final == WORD_NOT_FOUND_MSG:
            self.show_alert(msg=final)
            self.game.used_chars = []
            self.reset_buttons()
            return
        if final == FOUND_WORD_MSG:
            self.add_words()
            self.reset_buttons()
        if final is not None or final is False:  # if there is an error
            self.show_alert(final)
            if inp != 'SUBMIT':
                button[1] = False
                button[0].configure(highlightthickness=1, highlightbackground="white")

    def button_pressed(self, butt):
        """
        this method will change the button state from has not being pressed to pressed.
        :param butt: the button that has been pressed
        :return:
        """

        for button in self.__char_buttons:
            if button[0] == butt:
                button[1] = True
                self.check_what_buttons_are_pressed()
                self.check_input(button)
                return

    def add_character_buttons(self):
        self.__characters_frame.pack(side=LEFT)
        self.__background_canvas.place(x=0, y=0)
        self.__background_canvas.create_image(380, 300, image=self.__ingame_background)
        for y, row in enumerate(self.board.return_rows()):
            for x, char in enumerate(row):
                char_button = Button(self.__characters_frame, width=10, text=char, bd=1,
                                     height=5, fg='black', font=('Courier New', 10), highlightbackground="white")
                char_button.configure(command=lambda button=char_button: self.button_pressed(button))
                char_button.place(x=x*213, y=y*168)
                # appending the button object, if he is pressed or not, and the char (text) he's holding.
                # and his (row,column) coordinate
                self.__char_buttons.append([char_button, False, (char, y, x)])

    def customize_game(self):
        self.__root.title(TITLE)
        self.__root.geometry(INGAME_RESOLUTION)
        self.__root.resizable(False, False)
        self.add_and_edit_left_widget()
        self.update_timer()
        self.add_character_buttons()

    def start_gui(self):
        self.__root.mainloop()
