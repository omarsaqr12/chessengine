# this is responisble for storing the current state of the game ie the moves that were played till now. I will also be responsible for checking the validity of the moves, rules like the 50 move rule, and enable the user to takeback a move
class gameState():
    def __init__(self):
        self.whitetomove = True
        self.movelog = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.in_check = False
        self.pins = []
        self.checks = []
        self.check_mate = False
        self.stale_mate = False

        # correct chess initial setup
        self.board = [
            ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["??", "??", "??", "??", "??", "??", "??", "??"],
            ["??", "??", "??", "??", "??", "??", "??", "??"],
            ["??", "??", "??", "??", "??", "??", "??", "??"],
            ["??", "??", "??", "??", "??", "??", "??", "??"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wr", "wn", "wb", "wq", "wk", "wb", "wn", "wr"],
        ]

        self.funcmove = {
            'p': self.getPawnMoves,
            'r': self.getrockmoves,
            'q': self.getqueenmoves,
            'k': self.getkingmoves,
            'b': self.getbishopmoves,
            'n': self.getknightmoves,
        }

    def makemove(self, movin):
        self.board[movin.startrow][movin.startcol] = "??"
        self.board[movin.endrow][movin.endcol] = movin.piecemovec
        self.movelog.append(movin)
        if movin.piecemovec == 'wk':
            self.white_king_location = (movin.endrow, movin.endcol)
        elif movin.piecemovec == 'bk':
            self.black_king_location = (movin.endrow, movin.endcol)
        self.whitetomove = not self.whitetomove

    def undo_move(self):
        if len(self.movelog) != 0:
            movin = self.movelog.pop()
            self.board[movin.startrow][movin.startcol] = movin.piecemovec
            self.board[movin.endrow][movin.endcol] = movin.picecaptured
            if movin.piecemovec == 'wk':
                self.white_king_location = (movin.startrow, movin.startcol)
            elif movin.piecemovec == 'bk':
                self.black_king_location = (movin.startrow, movin.startcol)
            self.whitetomove = not self.whitetomove

    def validmoves(self):
        # generate pseudo-legal moves first (with current pins info), then filter by king safety
        self.in_check, self.pins, self.checks = self.checkForPinsAndChecks()
        pseudo_moves = self.getallmoves()
        legal_moves = []
        for mv in pseudo_moves:
            self.makemove(mv)
            moved_white = (not self.whitetomove)
            if moved_white:
                kr, kc = self.white_king_location
                still_in_check = self.is_square_attacked(kr, kc, 'b')
            else:
                kr, kc = self.black_king_location
                still_in_check = self.is_square_attacked(kr, kc, 'w')
            self.undo_move()
            if not still_in_check:
                legal_moves.append(mv)
        # check game end states
        if len(legal_moves) == 0:
            if self.inCheck():
                self.check_mate = True
                self.stale_mate = False
            else:
                self.stale_mate = True
                self.check_mate = False
        else:
            self.check_mate = False
            self.stale_mate = False
        return legal_moves

    def inCheck(self):
        """
        Determine if the current player to move is in check.
        """
        if self.whitetomove:
            kr, kc = self.white_king_location
            return self.is_square_attacked(kr, kc, 'b')
        else:
            kr, kc = self.black_king_location
            return self.is_square_attacked(kr, kc, 'w')

    def is_square_attacked(self, row, col, attacker_color):
        """
        Return True if square (row, col) is attacked by any piece of attacker_color ('w' or 'b').
        """
        board = self.board
        # pawn attacks
        if attacker_color == 'w':
            for dc in (-1, 1):
                rp = row + 1
                cp = col + dc
                if 0 <= rp <= 7 and 0 <= cp <= 7 and board[rp][cp] == 'wp':
                    return True
        else:
            for dc in (-1, 1):
                rp = row - 1
                cp = col + dc
                if 0 <= rp <= 7 and 0 <= cp <= 7 and board[rp][cp] == 'bp':
                    return True
        # knight attacks
        knight_steps = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        for dr, dc in knight_steps:
            rn, cn = row + dr, col + dc
            if 0 <= rn <= 7 and 0 <= cn <= 7:
                piece = board[rn][cn]
                if piece[0] == attacker_color and piece[1] == 'n':
                    return True
        # sliding attacks: rook/queen (orthogonal)
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            rn, cn = row + dr, col + dc
            while 0 <= rn <= 7 and 0 <= cn <= 7:
                piece = board[rn][cn]
                if piece == '??':
                    rn += dr
                    cn += dc
                    continue
                if piece[0] == attacker_color and (piece[1] == 'r' or piece[1] == 'q'):
                    return True
                # any piece blocks further scanning
                break
        # sliding attacks: bishop/queen (diagonal)
        for dr, dc in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
            rn, cn = row + dr, col + dc
            while 0 <= rn <= 7 and 0 <= cn <= 7:
                piece = board[rn][cn]
                if piece == '??':
                    rn += dr
                    cn += dc
                    continue
                if piece[0] == attacker_color and (piece[1] == 'b' or piece[1] == 'q'):
                    return True
                break
        # king attacks (adjacent squares)
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                rn, cn = row + dr, col + dc
                if 0 <= rn <= 7 and 0 <= cn <= 7:
                    piece = board[rn][cn]
                    if piece[0] == attacker_color and piece[1] == 'k':
                        return True
        return False

    def checkForPinsAndChecks(self):
        pins = []  # squares pinned and the direction it's pinned from
        checks = []  # squares where enemy is applying a check
        in_check = False
        if self.whitetomove:
            enemy_color = "b"
            ally_color = "w"
            start_row = self.white_king_location[0]
            start_col = self.white_king_location[1]
        else:
            enemy_color = "w"
            ally_color = "b"
            start_row = self.black_king_location[0]
            start_col = self.black_king_location[1]
        # check outwards from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            direction = directions[j]
            possible_pin = ()  # reset possible pins
            for i in range(1, 8):
                end_row = start_row + direction[0] * i
                end_col = start_col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != "k":
                        if possible_pin == ():  # first allied piece could be pinned
                            possible_pin = (end_row, end_col, direction[0], direction[1])
                        else:  # 2nd allied piece - no check or pin from this direction
                            break
                    elif end_piece[0] == enemy_color:
                        enemy_type = end_piece[1]
                        # 5 possibilities in this complex conditional
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) 1 square away diagonally from king and piece is a pawn
                        # 4.) any direction and piece is a queen
                        # 5.) any direction 1 square away and piece is a king
                        if (0 <= j <= 3 and enemy_type == "r") or (4 <= j <= 7 and enemy_type == "b") or (i == 1 and enemy_type == "p" and ((enemy_color == "w" and 6 <= j <= 7) or (enemy_color == "b" and 4 <= j <= 5))) or (enemy_type == "q") or (i == 1 and enemy_type == "k"):
                            if possible_pin == ():  # no piece blocking, so check
                                in_check = True
                                checks.append((end_row, end_col, direction[0], direction[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possible_pin)
                                break
                        else:  # enemy piece not applying checks
                            break
                else:
                    break  # off board
        # check for knight checks
        knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        for move in knight_moves:
            end_row = start_row + move[0]
            end_col = start_col + move[1]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == "n":  # enemy knight attacking a king
                    in_check = True
                    checks.append((end_row, end_col, move[0], move[1]))
        return in_check, pins, checks

    def getallmoves(self):
        move = []
        for r in range(8):
            for c in range(8):
                det = self.board[r][c][0]
                p = self.board[r][c][1]
                if (det == 'w' and self.whitetomove) or (det == 'b' and not self.whitetomove):
                    self.funcmove[p](r, c, move)
        return move

    def getPawnMoves(self, r, c, move):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        if self.whitetomove:
            if self.board[r][c][0] == 'w':
                if r - 1 >= 0 and self.board[r - 1][c][1] == '?' and (not piece_pinned or pin_direction == (-1, 0)):
                    move.append(moving((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c][1] == '?' and self.board[r - 1][c][1] == '?' and (not piece_pinned or pin_direction == (-1, 0)):
                    move.append(moving((r, c), (r - 2, c), self.board))
                if r - 1 >= 0 and c - 1 >= 0 and self.board[r - 1][c - 1][0] == 'b' and (not piece_pinned or pin_direction == (-1, -1)):
                    move.append(moving((r, c), (r - 1, c - 1), self.board))
                if r - 1 >= 0 and c + 1 <= 7 and self.board[r - 1][c + 1][0] == 'b' and (not piece_pinned or pin_direction == (-1, 1)):
                    move.append(moving((r, c), (r - 1, c + 1), self.board))
        else:
            if self.board[r][c][0] == 'b':
                if r + 1 <= 7 and self.board[r + 1][c][1] == '?' and (not piece_pinned or pin_direction == (1, 0)):
                    move.append(moving((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c][1] == '?' and self.board[r + 1][c][1] == '?' and (not piece_pinned or pin_direction == (1, 0)):
                    move.append(moving((r, c), (r + 2, c), self.board))
                if r + 1 <= 7 and c - 1 >= 0 and self.board[r + 1][c - 1][0] == 'w' and (not piece_pinned or pin_direction == (1, -1)):
                    move.append(moving((r, c), (r + 1, c - 1), self.board))
                if r + 1 <= 7 and c + 1 <= 7 and self.board[r + 1][c + 1][0] == 'w' and (not piece_pinned or pin_direction == (1, 1)):
                    move.append(moving((r, c), (r + 1, c + 1), self.board))

    def getrockmoves(self, r, c, move):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "q":
                    self.pins.remove(self.pins[i])
                break

        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        enemy = 'b' if (self.whitetomove and self.board[r][c][0] == 'w') else 'w'
        for d in directions:
            startrow = r
            startcol = c
            while startrow >= 0 and startrow <= 7 and startcol >= 0 and startcol <= 7:
                startrow += d[0]
                startcol += d[1]
                if startrow >= 0 and startrow <= 7 and startcol >= 0 and startcol <= 7:
                    if self.board[startrow][startcol][0] == enemy and (not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1])):
                        move.append(moving((r, c), (startrow, startcol), self.board))
                        break
                    elif self.board[startrow][startcol][0] == '?' and (not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1])):
                        move.append(moving((r, c), (startrow, startcol), self.board))
                    else:
                        break
                else:
                    break

    def getbishopmoves(self, r, c, move):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        enemy = 'b' if (self.whitetomove and self.board[r][c][0] == 'w') else 'w'
        for d in directions:
            startrow = r
            startcol = c
            while startrow >= 0 and startrow <= 7 and startcol >= 0 and startcol <= 7:
                startrow += d[0]
                startcol += d[1]
                if startrow >= 0 and startrow <= 7 and startcol >= 0 and startcol <= 7:
                    if self.board[startrow][startcol][0] == enemy and (not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1])):
                        move.append(moving((r, c), (startrow, startcol), self.board))
                        break
                    elif self.board[startrow][startcol][0] == '?' and (not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1])):
                        move.append(moving((r, c), (startrow, startcol), self.board))
                    else:
                        break
                else:
                    break

    def getkingmoves(self, r, c, move):
        if self.whitetomove:
            if self.board[r][c][0] == 'w':
                # horizontal
                if c + 1 <= 7 and self.board[r][c + 1][0] != 'w':
                    move.append(moving((r, c), (r, c + 1), self.board))
                if c - 1 >= 0 and self.board[r][c - 1][0] != 'w':
                    move.append(moving((r, c), (r, c - 1), self.board))
                # vertical and diagonals downwards
                if r + 1 <= 7:
                    if self.board[r + 1][c][0] != 'w':
                        move.append(moving((r, c), (r + 1, c), self.board))
                    if c - 1 >= 0 and self.board[r + 1][c - 1][0] != 'w':
                        move.append(moving((r, c), (r + 1, c - 1), self.board))
                    if c + 1 <= 7 and self.board[r + 1][c + 1][0] != 'w':
                        move.append(moving((r, c), (r + 1, c + 1), self.board))
                # vertical and diagonals upwards
                if r - 1 >= 0:
                    if self.board[r - 1][c][0] != 'w':
                        move.append(moving((r, c), (r - 1, c), self.board))
                    if c - 1 >= 0 and self.board[r - 1][c - 1][0] != 'w':
                        move.append(moving((r, c), (r - 1, c - 1), self.board))
                    if c + 1 <= 7 and self.board[r - 1][c + 1][0] != 'w':
                        move.append(moving((r, c), (r - 1, c + 1), self.board))
        else:
            if self.board[r][c][0] == 'b':
                # horizontal
                if c + 1 <= 7 and self.board[r][c + 1][0] != 'b':
                    move.append(moving((r, c), (r, c + 1), self.board))
                if c - 1 >= 0 and self.board[r][c - 1][0] != 'b':
                    move.append(moving((r, c), (r, c - 1), self.board))
                # vertical and diagonals downwards
                if r + 1 <= 7:
                    if self.board[r + 1][c][0] != 'b':
                        move.append(moving((r, c), (r + 1, c), self.board))
                    if c - 1 >= 0 and self.board[r + 1][c - 1][0] != 'b':
                        move.append(moving((r, c), (r + 1, c - 1), self.board))
                    if c + 1 <= 7 and self.board[r + 1][c + 1][0] != 'b':
                        move.append(moving((r, c), (r + 1, c + 1), self.board))
                # vertical and diagonals upwards
                if r - 1 >= 0:
                    if self.board[r - 1][c][0] != 'b':
                        move.append(moving((r, c), (r - 1, c), self.board))
                    if c - 1 >= 0 and self.board[r - 1][c - 1][0] != 'b':
                        move.append(moving((r, c), (r - 1, c - 1), self.board))
                    if c + 1 <= 7 and self.board[r - 1][c + 1][0] != 'b':
                        move.append(moving((r, c), (r - 1, c + 1), self.board))

    def getqueenmoves(self, r, c, move):
        # SINCE THE QUEEN IS BISHOP AND ROOK
        self.getbishopmoves(r, c, move)
        self.getrockmoves(r, c, move)

    def getknightmoves(self, r, c, move):
        directions = [(1, 2), (1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1), (-1, 2), (-1, -2)]
        enemy = 'b' if (self.whitetomove and self.board[r][c][0] == 'w') else 'w'
        for d in directions:
            startrow = r
            startcol = c
            startrow += d[0]
            startcol += d[1]
            if startrow >= 0 and startrow <= 7 and startcol >= 0 and startcol <= 7:
                if self.board[startrow][startcol][0] == enemy:
                    move.append(moving((r, c), (startrow, startcol), self.board))
                elif self.board[startrow][startcol][0] == '?':
                    move.append(moving((r, c), (startrow, startcol), self.board))


class moving():

    files2col = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    col2file = {v: k for k, v in files2col.items()}
    rank2row = {"8": 0, "7": 1, "6": 2, "5": 3, "4": 4, "3": 5, "2": 6, "1": 7}
    row2rank = {v: k for k, v in rank2row.items()}

    def __init__(self, startsq, endsq, board):
        self.startrow = int(startsq[0])
        self.startcol = int(startsq[1])
        self.endrow = int(endsq[0])
        self.endcol = int(endsq[1])
        self.piecemovec = board[self.startrow][self.startcol]
        self.picecaptured = board[self.endrow][self.endcol]
        self.moveid = 1000 * self.startrow + 100 * self.startcol + 10 * self.endrow + self.endcol
        # print(self.getnotation())

    def __eq__(self, object):
        if (isinstance(object, moving)):
            return object.moveid == self.moveid

    def getnotation(self):
        return self.getrankfile(self.startrow, self.startcol) + self.getrankfile(self.endrow, self.endcol)

    def getrankfile(self, r, c):
        return self.col2file[c] + self.row2rank[r]
