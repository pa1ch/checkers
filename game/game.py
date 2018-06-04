from math import copysign, fabs
from copy import deepcopy


class GameField:
    def __init__(self, dimension):
        self.whose_turn = 'w'
        self.dimension = dimension
        self.white_pawns = []
        self.black_pawns = []
        self.field = [
            [0, 'b', 0, 'b', 0, 'b', 0, 'b', 0, 'b'],
            ['b', 0, 'b', 0, 'b', 0, 'b', 0, 'b', 0],
            [0, 'b', 0, 'b', 0, 'b', 0, 'b', 0, 'b'],
            ['b', 0, 'b', 0, 'b', 0, 'b', 0, 'b', 0],
            [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
            [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
            [0, 'w', 0, 'w', 0, 'w', 0, 'w', 0, 'w'],
            ['w', 0, 'w', 0, 'w', 0, 'w', 0, 'w', 0],
            [0, 'w', 0, 'w', 0, 'w', 0, 'w', 0, 'w'],
            ['w', 0, 'w', 0, 'w', 0, 'w', 0, 'w', 0]
        ]
        for line in range(self.dimension):
            for column in range(self.dimension):
                if self.field[line][column] == 'w':
                    self.white_pawns.append(Pawn(self, 'w', line, column))
                if self.field[line][column] == 'b':
                    self.black_pawns.append(Pawn(self, 'b', line, column))

    def __getitem__(self, x):
        return self.field[x]

    def __setitem__(self, x, value):
        self.field[x] = value

    def make_move(self, command, start_pos_x=None, start_pos_y=None, finish_pos_x=None, finish_pos_y=None):
        try:
            if command == 'move' and self[int(start_pos_x - 1)][int(start_pos_y - 1)] != 0:
                self[int(start_pos_x - 1)][int(start_pos_y - 1)].make_move(self, int(finish_pos_x - 1),
                                                                           int(finish_pos_y - 1))
                self.print_game()
            elif command == 'fight' and self[int(start_pos_x - 1)][int(start_pos_y - 1)] != 0:
                self[int(start_pos_x - 1)][int(start_pos_y - 1)].make_fight(self, int(finish_pos_x - 1),
                                                                            int(finish_pos_y - 1))
                self.print_game()
            elif command == 'whose_turn':
                if self.whose_turn == 'w':
                    turn = 'white'
                else:
                    turn = 'black'
                print("Now {}'s turn".format(turn))
            else:
                print("It is not a pawn")
        except AttributeError:
            print("Now it's not your turn")
        except ValueError:
            print("You can not move to this cell")

    def print_game(self):
        for line in range(self.dimension):
            print('{:2}: {}'.format(line + 1, [str(item) for item in self[line]]))

    def change_turn(self):
        if self.whose_turn == 'w':
            self.whose_turn = 'b'
        else:
            self.whose_turn = 'w'

    def who_win(self):
        if len(self.black_pawns) == 0:
            return 'w'
        elif len(self.white_pawns) == 0:
            return 'b'

    def undo(self):
        with open('gamelog.txt', 'r+', encoding='utf-8') as log:
            pass

    def redo(self):
        pass

class Pawn:
    def __init__(self, field, color, line, column, is_king=False):
        self.color = color
        self.is_king = is_king
        self.line = line
        self.column = column
        self.available_moves = []
        self.available_fights = []
        self.find_available_moves(field)
        field[line][column] = self

    def __str__(self):
        return self.color

    def find_available_moves(self, field):
        if self.is_king:
            self._find_available_moves_for_king(field)
        else:
            if self.color == 'w':
                self._check_for_move(field, -1, -1)
                self._check_for_move(field, -1, 1)
            else:
                self._check_for_move(field, 1, -1)
                self._check_for_move(field, 1, 1)

    def _find_available_moves_for_king(self, field):
            self._check_for_king_move(field, -1, -1)
            self._check_for_king_move(field, -1, 1)
            self._check_for_king_move(field, 1, -1)
            self._check_for_king_move(field, 1, 1)

    def _check_for_move(self, field, line, column):
        if self._cell_is_free(field, self.line + line, self.column + column):
            self.available_moves.append((self.line + line, self.column + column))
        elif (self._enemy_in_cell(field, self.line + line, self.column + column)
              and self._cell_is_free(field, self.line + int(copysign(fabs(line) + 1, line)),
                                     self.column + int(copysign(fabs(column) + 1, column)))):
            self.available_fights.append((self.line + int(copysign(fabs(line) + 1, line)),
                                          self.column + int(copysign(fabs(column) + 1, column))))

    def _check_for_king_move(self, field, line, column):
        enemy = False
        for i in range(1, field.dimension):
            if self._cell_is_free(field, self.line + i * line, self.column + i * column):
                if enemy:
                    self.available_fights.append((self.line + i * line, self.column + i * column))
                else:
                    self.available_moves.append((self.line + i * line, self.column + i * column))
            else:
                if self._enemy_in_cell(field, self.line + i * line, self.column + i * column) and not enemy:
                    enemy = True
                    continue
                else:
                    break

    def make_move(self, field, line, column):
        if field.whose_turn == self.color:
            if self.available_moves.count((line, column)) == 1:
                with open('gamelog.txt', 'r+', encoding='utf-8') as log:
                    log.write('move {} {} {} {}'.format(self.line, self.column, line, column))
                field[line][column] = deepcopy(field[self.line][self.column])
                field[line][column].change_coordinates(line, column)
                field[self.line][self.column] = 0
                self._make_king(field, line)
                field[line][column].find_available_moves(field)
                field.change_turn()
            else:
                raise ValueError
        else:
            raise AttributeError

    def make_fight(self, field, line, column):
        if field.whose_turn == self.color:
            if self.available_fights.count((line, column)) == 1:
                with open('gamelog.txt', 'r+', encoding='utf-8') as log:
                    log.write('fight {} {} {} {} {}'.format(self.line, self.column, line, column,
                                                            field[int((self.line + line) / 2)]
                                                            [int((self.column + column) / 2)].is_king))
                field[line][column] = deepcopy(field[self.line][self.column])
                field[line][column].change_coordinates(line, column)
                field[int((self.line + line) / 2)][int((self.column + column) / 2)] = 0
                field[self.line][self.column] = 0
                self._make_king(field, line)
                field[line][column].find_available_moves(field)
                field.change_turn()
            else:
                raise ValueError
        else:
            raise AttributeError

    def change_coordinates(self, line, column):
        self.line = line
        self.column = column

    def _make_king(self, field, line):
        if (self.color == 'w' and line == 0) or (self.color == 'b' and line == field.dimension - 1):
            self.color = self.color.upper()
            self.is_king = True

    @staticmethod
    def _cell_is_free(field, line, column):
        if column < 0:
            return False
        try:
            return field[line][column] == 0
        except IndexError:
            pass

    def _enemy_in_cell(self, field, line, column):
        if line < 0 or column < 0:
            return False
        try:
            return field[line][column] != 0 and field[line][column] != self.color\
                   and field[line][column] != self.color.upper()
        except IndexError:
            pass


def main():
    game = GameField(10)
    game.print_game()
    while game.who_win() is None:
        next_turn = input().split()
        game.make_move(*next_turn)


if __name__ == '__main__':
    main()
