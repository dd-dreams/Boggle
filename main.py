import time
from boggle_board_randomizer import *
import sys


MINUTES = 2
SECS = 60

# MESSAGES
INPUT_MSG = "Input the character your seeking: "
WORDS_FILE = "boggle_dict.txt"
CHAR_WARNING = "The char you selected is out of bounds or not correct.\n"
INPUT_NOT_IN_RANGE_OF_CHAR = "The char you selected is not in range of the previous char.\n"
FOUND_WORD_MSG = "You found a word!\n"
WORD_NOT_FOUND_MSG = "The word is not in the dictionary."
USED_CHAR_MSG = "You already used this char in this place."
TIMER_END_MSG = "\nTimer finished!\n"
TIME_MSG = "Time left: {}:{}".format(MINUTES, SECS)
EXIT_MSG = "Thanks for playing!\nPress CTRL+C to exit."
TIMER_LEFT_MSG = "Time left: {}:{}".format(MINUTES, SECS)
WORD_ALREADY_FOUND = "Word already found."


def import_words(filename):
    """
    this function will yield a word from the dictionary file,
    instead of using a list which can overload memory.
    :param filename: wordlist
    :return: true if reached the end of file
    """

    with open(filename) as file:
        read_file = file.readlines()
        for word in read_file:
            yield word.strip()
    return True


def check_timer():
    global MINUTES, SECS
    while True:
        time.sleep(1)
        if not MINUTES:
            print(TIMER_END_MSG)
            sys.exit()
        elif SECS == 0:
            MINUTES -= 1
            SECS = 60
            continue
        SECS -= 1


class Board:
    def __init__(self):
        self.__board = randomize_board()
        self.__row = 0

    def print_board(self):
        print()
        for row in self.__board:
            print(row)

    def return_rows(self):
        return [row for row in self.__board]

    def return_chars(self):
        chars = []
        for row in self.__board:
            for char in row:
                chars.append(char)
        return chars

    def return_board(self):
        return self.__board

    def __iter__(self):
        return iter(self.__board)

    def __len__(self):
        return len(self.__board)

    def __getitem__(self, item):
        return self.__board[item]


class Game:
    def __init__(self, board, is_gui=False):
        self.board = board
        self.__is_gui = is_gui
        self.__prev_input = None
        self.__input = None
        self.chars = ""
        self.used_chars = []
        self.__found_words = []
        self.__points = 0
        self.start = True
        self.end = False

    def print_pattern(self):
        pattern = ""
        for char in self.chars:
            pattern += char
        print("\nYour current pattern:", pattern, '\n')

    def return_used_chars(self):
        return self.used_chars

    def return_found_words(self):
        return self.__found_words

    # ----HELPERS----
    def check_if_char_in_sides(self, char):
        """
        this method will check if the inputted char is in the sides,
        for future it will be useful.
        :param char: inputted char
        :return: true if its in the sides else false
        """

        sides_rows = [row[0] for row in self.board] + [row[-1] for row in self.board]
        tmp_board = self.board.return_board()
        for up_row, bottom_row in zip(tmp_board[0], tmp_board[-1]):  # get the top and bottom rows
            sides_rows.extend((up_row, bottom_row))
        return True if char in sides_rows else False

    def get_all_chars_around_a_char(self, char, row, column):
        """
        this method will find all the chars around a specific char.
        they can be 3x3 around him (3 above/left/right/under him).
        :param char: the char you want to get all chars around him
        :param row: what row is that char in
        :param column: what column is that char in
        :return:
        """

        chars = []
        for ind_row, tmp_row in enumerate(self.board):
            # check if the row is on top/below of the current row
            if ind_row == row - 1 or ind_row == row + 1 or ind_row == row:
                for ind_char, tmp_char in enumerate(tmp_row):
                    # check if the char is on the top/below/left/right of the current column
                    if ind_char == column - 1 or ind_char == column + 1 or ind_char == column and tmp_char != char:
                        chars.append((tmp_char, ind_row, ind_char))
        return chars

    def check_if_char_in_board(self, char):
        for row in self.board:
            if char in row:
                return True
        return False

    def check_location_of_char(self):
        """
        the user might choose incorrect character for a specific (x,y) location,
        this method will prevent this.
        :return: true if it isn't an incorrect char, false if it is
        """

        char, row, column = self.__input
        row = int(row)
        column = int(column)
        if char == self.board[row][column]:
            return True
        return False

    # ----HANDLE INPUT----
    def small_input_checks(self):
        global TIMER_LEFT_MSG
        if self.__input[0] == 'TIMER':
            TIMER_LEFT_MSG = "Time left: {}:{}".format(MINUTES, SECS)  # updating
            return TIMER_LEFT_MSG
        if self.__input[0] == 'POINTS':
            return "You have {} points.\n".format(self.__points)
        if self.__input[0] == 'EXIT':
            return EXIT_MSG
        if self.__input[0] == 'SUBMIT':
            return 'SUBMIT'
        if len(self.__input) != 3 or not self.__input[0].isalpha():
            return False
        if not self.check_location_of_char():
            return False
        return 1

    def get_input(self, inp=None):
        """
        a method to get an input from the user, and check for basic checking.
        :return: true if the char is in the board, false is isn't.
        """
        if inp is not None:
            if inp == 'SUBMIT':
                if self.chars + '\n' in self.__found_words:
                    return 'FOUND'
                return 'SUBMIT'
            self.__input = inp
        else:
            self.__input = tuple(input(INPUT_MSG).strip().upper().split(','))  # tuple to make it immutable
            small_checks = self.small_input_checks()
            if small_checks != 1:
                return small_checks
        if self.start:
            if not self.check_if_char_in_board(self.__input[0]):
                return False
            self.used_chars.append(self.__input)
            self.start = False
            self.__prev_input = self.__input
            self.chars += self.__input[0]
            return None
        return self.check_if_char_in_board(self.__input[0])

    def check_input(self, submit=False):
        """
        this method will check the input
        :param submit: did the user want to check if the pattern is in the wordlist
        :return:
        """

        if submit:  # check if he found a word
            # there was a problem if he pressed the submit button, it could not after-
            # press any other character button outside of the previous range, this will fix it.
            self.start = True
            for word in import_words(WORDS_FILE):
                if self.chars == word:
                    self.__found_words.append(self.chars + '\n')
                    self.__points += len(self.chars) ** 2
                    self.chars = ""
                    self.used_chars = []
                    return FOUND_WORD_MSG
            return WORD_NOT_FOUND_MSG

        if self.__input in self.used_chars:
            return USED_CHAR_MSG
        prev_char, prev_row, prev_column = self.__prev_input
        row = int(prev_row)
        column = int(prev_column)
        range_of_char = self.get_all_chars_around_a_char(prev_char, row, column)
        if self.__input not in range_of_char:
            return INPUT_NOT_IN_RANGE_OF_CHAR
        self.chars += self.__input[0]
        self.used_chars.append(self.__input)
        self.__prev_input = self.__input
        self.__input = None


def react_to_input(inp, game_obj):
    if inp == 'FOUND':
        game_obj.chars = ""
        return WORD_ALREADY_FOUND
    if inp is False:
        return CHAR_WARNING
    if inp == 'SUBMIT':
        return game_obj.check_input(submit=True)
    if inp:
        result = game_obj.check_input()
        if result is not None:
            return result
        return
    if inp is not None and 'points' in inp or inp == TIMER_LEFT_MSG:
        return inp
    if inp == EXIT_MSG:
        return True
    if inp is None:
        return
    return CHAR_WARNING


def main(board_obj, game_obj):  # only for no gui
    while True:
        board_obj.print_board()
        game_obj.print_pattern()
        user_input = game_obj.get_input()
        final = react_to_input(user_input, game_obj)
        if final is None:
            continue
        print(final)
