from copy import deepcopy
import random
import numpy as np
from random import shuffle
from statistics import stdev


piece_types = ['J', 'L', 'I', 'T', 'S', 'Z', 'O']
piece_layouts = dict(J=np.array([[0, 1, 1],
                                 [0, 0, 1],
                                 [0, 0, 1]]),
                     L=np.array([[0, 0, 1],
                                 [0, 0, 1],
                                 [0, 1, 1]]),
                     I=np.array([[0, 0, 1, 0],
                                 [0, 0, 1, 0],
                                 [0, 0, 1, 0],
                                 [0, 0, 1, 0]]),
                     T=np.array([[0, 0, 1],
                                 [0, 1, 1],
                                 [0, 0, 1]]),
                     S=np.array([[0, 1, 0],
                                 [0, 1, 1],
                                 [0, 0, 1]]),
                     Z=np.array([[0, 0, 1],
                                 [0, 1, 1],
                                 [0, 1, 0]]),
                     O=np.array([[1, 1],
                                 [1, 1]]))

piece_colors = dict(
    J=(0, 0, 255),
    L=(255, 127, 0),
    I=(0, 255, 255),
    T=(128, 0, 128),
    S=(0, 255, 0),
    Z=(255, 0, 0),
    O=(255, 255, 0)
)




class Tetris:
    def __init__(self):
        self.board = [[None] * 24 for i in range(10)]
        self.score = 0
        self.level = 0
        self.frames = 0
        self.bag = None
        self.bag_index = 0
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.holes = None
        self.clear_q = []
        self.row_score = 0
        self.height_diff = None
        self.alive = True
        # print('Current Piece' + str(self.current_piece))
        # print('Next piece' + str(self.next_piece))

    def down(self):
        if self.collides(self.current_piece, [0, -1]):
            self.freeze()
        else:
            self.current_piece.move([0, -1])

    def side(self, direction):
        if not self.collides(self.current_piece, direction):
            self.current_piece.move(direction)

    def rotate_clockwise(self):
        test_piece = deepcopy(self.current_piece)
        test_piece.rotate_clockwise()
        if not self.collides(test_piece):
            self.current_piece.rotate_clockwise()
        else:
            test_moves = [[1, 0], [-1, 0], [0, 1], [1, 1], [-1, -1], [1, -1], [-1, 1]]
            for move in test_moves:
                if not self.collides(test_piece, move):
                    self.current_piece.move(move)
                    self.current_piece.rotate_clockwise()
                    break


    def drop(self):
        test_piece = deepcopy(self.current_piece)
        distance = 0
        for i in range(24):
            if self.collides(test_piece, [0, -1]):
                distance = i
                break
            test_piece.move([0, -1])
        self.current_piece.move([0, -distance])
        self.freeze()

    def freeze(self):
        try:
            for square in self.current_piece.squares:
                self.board[square[0]][square[1]] = self.current_piece.color
        except:
            self.alive = False
        self.super_update()
        

    def collides(self, piece, move=[0, 0]):
        test_piece = deepcopy(piece)
        test_piece.move(move)
        for coord in test_piece.squares:
            if coord[1] < 0 or coord[0] < 0 or coord[0] >= 10:
                return True
            try:
                if self.board[coord[0]][coord[1]] is not None:
                    return True
            except:
                return False
        return False


        

    def clear_rows(self):
        counter = 0
        for i in self.clear_q:
            for column in self.board:
                column.pop(i - counter)
                column.append(None)
    
    def new_piece(self):
        if self.bag_index == 0:
            x = [Piece(type) for type in piece_types]
            shuffle(x)
            self.bag = iter(x) # reset the bag
        if self.bag_index == 6:
            self.bag_index = 0
        else:
            self.bag_index+=1
        return next(self.bag)

    def restart(self):
        self.board = [[None] * 24 for i in range(10)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()

    def clear_scoring(self, rows_cleared):
        # TODO: Make scoring count the amount the piece has been dropped
        if rows_cleared == 1:
            return 40 * (self.level + 1)
        if rows_cleared == 2:
            return 100 * (self.level + 1)
        if rows_cleared == 3:
            return 300 * (self.level + 1)
        if rows_cleared == 4:
            return 1200 * (self.level + 1)
        else:
            return 0

    #TODO: make_move, takes in tuple of actions and applies them
    def make_move(self, move):
        for i in range(move[0]):
            self.rotate_clockwise()
        if move[1]:
            direction = np.sign(move[1])
            moves = abs(move[1])
            for i in range(moves):
                self.side([direction, 0])
        self.drop()

    def super_update(self):
        # Update pieces
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()

        # Get row scores and clear rows
        full_rows = []
        for i in range(24):
            counter = 0
            for j in range(10):
                if self.board[j][i] is not None:
                    counter += 1
            if counter == 10:
                full_rows.append(i)
        self.clear_q = full_rows
        self.row_score = self.clear_scoring(len(self.clear_q))
        self.score += self.row_score
        self.clear_rows()

        # Get holes/heights scores
        self.holes = 0
        heights = []
        for col in self.board:
            i=23
            #checks if below highest block
            flag = False
            while i>=0:
                # Finds highest block
                if not flag and col[i]:
                    heights.append(i+1)
                    flag = True
                # If below highest block
                elif flag and not col[i]:
                    self.holes += 1
                i-=1
            #If no highest block was found (0 height)
            if not flag:
                heights.append(0)
        self.height_diff = stdev(heights)



class Piece:
    def __init__(self, type, column=4, row=20):
        self.x = column
        self.y = row
        self.type = type
        self.color = piece_colors[type]
        self.rotation = 0
        self.layout = piece_layouts[type]
        self.squares = []
        self.generate_squares()

    def generate_squares(self):
        self.squares = []
        for i in range(len(self.layout)):
            for j in range(len(self.layout[0])):
                if self.layout[i][j] != 0:
                    x = i + self.x
                    y = j + self.y
                    self.squares.append([x, y])

    def move(self, vector):
        self.x += vector[0]
        self.y += vector[1]
        self.generate_squares()

    def rotate_clockwise(self):
        self.layout = np.rot90(self.layout, 3, axes=(0, 1))
        self.generate_squares()