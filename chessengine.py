# this is responisble for storing the current state of the game ie the moves that were played till now. I will also be responsible for checking the validity of the moves, rules like the 50 move rule, and enable the user to takeback a move
class CastleRights:
    def __init__(self, wks, wqs, bks, bqs):
        self.wks = wks
        self.wqs = wqs
        self.bks = bks
        self.bqs = bqs


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
        self.enpassant_possible = ()
        self.current_castling_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(True, True, True, True)]

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
        # snapshot special-state for undo
        movin.prev_enpassant = self.enpassant_possible
        movin.prev_castle_rights = CastleRights(
            self.current_castling_rights.wks,
            self.current_castling_rights.wqs,
            self.current_castling_rights.bks,
            self.current_castling_rights.bqs,
        )

        self.board[movin.startrow][movin.startcol] = "??"
        self.board[movin.endrow][movin.endcol] = movin.piecemovec
        self.movelog.append(movin)
        if movin.piecemovec == 'wk':
            self.white_king_location = (movin.endrow, movin.endcol)
        elif movin.piecemovec == 'bk':
            self.black_king_location = (movin.endrow, movin.endcol)

        # handle en passant capture
        if getattr(movin, 'is_enpassant', False):
            if movin.piecemovec[0] == 'w':
                self.board[movin.endrow + 1][movin.endcol] = "??"
            else:
                self.board[movin.endrow - 1][movin.endcol] = "??"

        # handle castling rook move
        if getattr(movin, 'is_castle', False):
            if movin.endcol - movin.startcol == 2:  # king side
                if movin.piecemovec == 'wk':
                    self.board[7][5] = 'wr'
                    self.board[7][7] = '??'
                else:
                    self.board[0][5] = 'br'
                    self.board[0][7] = '??'
            elif movin.endcol - movin.startcol == -2:  # queen side
                if movin.piecemovec == 'wk':
                    self.board[7][3] = 'wr'
                    self.board[7][0] = '??'
                else:
                    self.board[0][3] = 'br'
                    self.board[0][0] = '??'

        # handle pawn promotion (auto-queen)
        if getattr(movin, 'is_pawn_promo', False):
            color = movin.piecemovec[0]
            self.board[movin.endrow][movin.endcol] = color + getattr(movin, 'promotion_piece', 'q')

        # update en passant square
        self.enpassant_possible = ()
        if movin.piecemovec == 'wp' and movin.startrow == 6 and movin.endrow == 4:
            self.enpassant_possible = (5, movin.endcol)
        elif movin.piecemovec == 'bp' and movin.startrow == 1 and movin.endrow == 3:
            self.enpassant_possible = (2, movin.endcol)

        # update castling rights based on move and capture
        self.updateCastleRights(movin)
        self.castle_rights_log.append(CastleRights(
            self.current_castling_rights.wks,
            self.current_castling_rights.wqs,
            self.current_castling_rights.bks,
            self.current_castling_rights.bqs,
        ))
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
            # undo en passant capture
            if getattr(movin, 'is_enpassant', False):
                if movin.piecemovec[0] == 'w':
                    self.board[movin.endrow + 1][movin.endcol] = 'bp'
                else:
                    self.board[movin.endrow - 1][movin.endcol] = 'wp'
                self.board[movin.endrow][movin.endcol] = '??'
            # undo castling rook move
            if getattr(movin, 'is_castle', False):
                if movin.endcol - movin.startcol == 2:  # king side
                    if movin.piecemovec == 'wk':
                        self.board[7][7] = 'wr'
                        self.board[7][5] = '??'
                    else:
                        self.board[0][7] = 'br'
                        self.board[0][5] = '??'
                elif movin.endcol - movin.startcol == -2:  # queen side
                    if movin.piecemovec == 'wk':
                        self.board[7][0] = 'wr'
                        self.board[7][3] = '??'
                    else:
                        self.board[0][0] = 'br'
                        self.board[0][3] = '??'
            # restore special-state
            self.enpassant_possible = getattr(movin, 'prev_enpassant', ())
            self.current_castling_rights = getattr(movin, 'prev_castle_rights', CastleRights(True, True, True, True))
            if len(self.castle_rights_log) > 0:
                self.castle_rights_log.pop()
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
                    m = moving((r, c), (r - 1, c), self.board)
                    if r - 1 == 0:
                        m.is_pawn_promo = True
                        m.promotion_piece = 'q'
                    move.append(m)
                if r == 6 and self.board[r - 2][c][1] == '?' and self.board[r - 1][c][1] == '?' and (not piece_pinned or pin_direction == (-1, 0)):
                    move.append(moving((r, c), (r - 2, c), self.board))
                if r - 1 >= 0 and c - 1 >= 0 and (not piece_pinned or pin_direction == (-1, -1)):
                    if self.board[r - 1][c - 1][0] == 'b':
                        m = moving((r, c), (r - 1, c - 1), self.board)
                        if r - 1 == 0:
                            m.is_pawn_promo = True
                            m.promotion_piece = 'q'
                        move.append(m)
                    elif self.enpassant_possible == (r - 1, c - 1) and self.board[r][c - 1] == 'bp':
                        m = moving((r, c), (r - 1, c - 1), self.board)
                        m.is_enpassant = True
                        m.picecaptured = 'bp'
                        move.append(m)
                if r - 1 >= 0 and c + 1 <= 7 and (not piece_pinned or pin_direction == (-1, 1)):
                    if self.board[r - 1][c + 1][0] == 'b':
                        m = moving((r, c), (r - 1, c + 1), self.board)
                        if r - 1 == 0:
                            m.is_pawn_promo = True
                            m.promotion_piece = 'q'
                        move.append(m)
                    elif self.enpassant_possible == (r - 1, c + 1) and self.board[r][c + 1] == 'bp':
                        m = moving((r, c), (r - 1, c + 1), self.board)
                        m.is_enpassant = True
                        m.picecaptured = 'bp'
                        move.append(m)
        else:
            if self.board[r][c][0] == 'b':
                if r + 1 <= 7 and self.board[r + 1][c][1] == '?' and (not piece_pinned or pin_direction == (1, 0)):
                    m = moving((r, c), (r + 1, c), self.board)
                    if r + 1 == 7:
                        m.is_pawn_promo = True
                        m.promotion_piece = 'q'
                    move.append(m)
                if r == 1 and self.board[r + 2][c][1] == '?' and self.board[r + 1][c][1] == '?' and (not piece_pinned or pin_direction == (1, 0)):
                    move.append(moving((r, c), (r + 2, c), self.board))
                if r + 1 <= 7 and c - 1 >= 0 and (not piece_pinned or pin_direction == (1, -1)):
                    if self.board[r + 1][c - 1][0] == 'w':
                        m = moving((r, c), (r + 1, c - 1), self.board)
                        if r + 1 == 7:
                            m.is_pawn_promo = True
                            m.promotion_piece = 'q'
                        move.append(m)
                    elif self.enpassant_possible == (r + 1, c - 1) and self.board[r][c - 1] == 'wp':
                        m = moving((r, c), (r + 1, c - 1), self.board)
                        m.is_enpassant = True
                        m.picecaptured = 'wp'
                        move.append(m)
                if r + 1 <= 7 and c + 1 <= 7 and (not piece_pinned or pin_direction == (1, 1)):
                    if self.board[r + 1][c + 1][0] == 'w':
                        m = moving((r, c), (r + 1, c + 1), self.board)
                        if r + 1 == 7:
                            m.is_pawn_promo = True
                            m.promotion_piece = 'q'
                        move.append(m)
                    elif self.enpassant_possible == (r + 1, c + 1) and self.board[r][c + 1] == 'wp':
                        m = moving((r, c), (r + 1, c + 1), self.board)
                        m.is_enpassant = True
                        m.picecaptured = 'wp'
                        move.append(m)

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
                # castling
                self.getCastleMoves(r, c, move)
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
                # castling
                self.getCastleMoves(r, c, move)

    def getCastleMoves(self, r, c, move):
        if self.inCheck():
            return
        if self.whitetomove and self.board[r][c] == 'wk':
            # king side
            if self.current_castling_rights.wks:
                if self.board[7][5] == '??' and self.board[7][6] == '??':
                    if not self.is_square_attacked(7, 5, 'b') and not self.is_square_attacked(7, 6, 'b'):
                        if self.board[7][7] == 'wr':
                            m = moving((7, 4), (7, 6), self.board)
                            m.is_castle = True
                            move.append(m)
            # queen side
            if self.current_castling_rights.wqs:
                if self.board[7][3] == '??' and self.board[7][2] == '??' and self.board[7][1] == '??':
                    if not self.is_square_attacked(7, 3, 'b') and not self.is_square_attacked(7, 2, 'b'):
                        if self.board[7][0] == 'wr':
                            m = moving((7, 4), (7, 2), self.board)
                            m.is_castle = True
                            move.append(m)
        if (not self.whitetomove) and self.board[r][c] == 'bk':
            # king side
            if self.current_castling_rights.bks:
                if self.board[0][5] == '??' and self.board[0][6] == '??':
                    if not self.is_square_attacked(0, 5, 'w') and not self.is_square_attacked(0, 6, 'w'):
                        if self.board[0][7] == 'br':
                            m = moving((0, 4), (0, 6), self.board)
                            m.is_castle = True
                            move.append(m)
            # queen side
            if self.current_castling_rights.bqs:
                if self.board[0][3] == '??' and self.board[0][2] == '??' and self.board[0][1] == '??':
                    if not self.is_square_attacked(0, 3, 'w') and not self.is_square_attacked(0, 2, 'w'):
                        if self.board[0][0] == 'br':
                            m = moving((0, 4), (0, 2), self.board)
                            m.is_castle = True
                            move.append(m)

    def updateCastleRights(self, movin):
        # lose rights when king moves
        if movin.piecemovec == 'wk':
            self.current_castling_rights.wks = False
            self.current_castling_rights.wqs = False
        elif movin.piecemovec == 'bk':
            self.current_castling_rights.bks = False
            self.current_castling_rights.bqs = False
        # lose rights when rook moves from corners
        elif movin.piecemovec == 'wr':
            if movin.startrow == 7 and movin.startcol == 0:
                self.current_castling_rights.wqs = False
            elif movin.startrow == 7 and movin.startcol == 7:
                self.current_castling_rights.wks = False
        elif movin.piecemovec == 'br':
            if movin.startrow == 0 and movin.startcol == 0:
                self.current_castling_rights.bqs = False
            elif movin.startrow == 0 and movin.startcol == 7:
                self.current_castling_rights.bks = False
        # lose rights when rook is captured on corners
        if movin.picecaptured == 'wr':
            if movin.endrow == 7 and movin.endcol == 0:
                self.current_castling_rights.wqs = False
            elif movin.endrow == 7 and movin.endcol == 7:
                self.current_castling_rights.wks = False
        elif movin.picecaptured == 'br':
            if movin.endrow == 0 and movin.endcol == 0:
                self.current_castling_rights.bqs = False
            elif movin.endrow == 0 and movin.endcol == 7:
                self.current_castling_rights.bks = False

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
        # special move flags (default False)
        self.is_enpassant = False
        self.is_pawn_promo = False
        self.promotion_piece = 'q'
        self.is_castle = False
        # history snapshots for undo
        self.prev_enpassant = ()
        self.prev_castle_rights = None

    def __eq__(self, object):
        if (isinstance(object, moving)):
            return object.moveid == self.moveid

    def getnotation(self):
        return self.getrankfile(self.startrow, self.startcol) + self.getrankfile(self.endrow, self.endcol)

    def getrankfile(self, r, c):
        return self.col2file[c] + self.row2rank[r]

    # ---------- Simple evaluation and search ----------
    def __repr__(self):
        return f"{self.getnotation()}"


def _piece_value(piece: str) -> int:
    if piece == '??' or piece == '':
        return 0
    color = piece[0]
    t = piece[1]
    values = {'p': 100, 'n': 320, 'b': 330, 'r': 500, 'q': 900, 'k': 0}
    v = values.get(t, 0)
    return v if color == 'w' else -v


# Absolute base values (centipawns)
_BASE_VALUES = {'p': 100, 'n': 320, 'b': 330, 'r': 500, 'q': 900, 'k': 0}


def _piece_abs_value(t: str) -> int:
    return _BASE_VALUES.get(t, 0)


# Piece-Square Tables (white perspective; mirror rows for black)
_PST_PAWN = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [5, 5, 10, 25, 25, 10, 5, 5],
    [0, 0, 0, 20, 20, 0, 0, 0],
    [5, -5, -10, 0, 0, -10, -5, 5],
    [5, 10, 10, -20, -20, 10, 10, 5],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

_PST_KNIGHT = [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20, 0, 0, 0, 0, -20, -40],
    [-30, 0, 10, 15, 15, 10, 0, -30],
    [-30, 5, 15, 20, 20, 15, 5, -30],
    [-30, 0, 15, 20, 20, 15, 0, -30],
    [-30, 5, 10, 15, 15, 10, 5, -30],
    [-40, -20, 0, 5, 5, 0, -20, -40],
    [-50, -40, -30, -30, -30, -30, -40, -50],
]

_PST_BISHOP = [
    [-20, -10, -10, -10, -10, -10, -10, -20],
    [-10, 5, 0, 0, 0, 0, 5, -10],
    [-10, 10, 10, 10, 10, 10, 10, -10],
    [-10, 0, 10, 10, 10, 10, 0, -10],
    [-10, 5, 5, 10, 10, 5, 5, -10],
    [-10, 0, 5, 10, 10, 5, 0, -10],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-20, -10, -10, -10, -10, -10, -10, -20],
]

_PST_ROOK = [
    [0, 0, 5, 10, 10, 5, 0, 0],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [5, 10, 10, 10, 10, 10, 10, 5],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

_PST_QUEEN = [
    [-20, -10, -10, -5, -5, -10, -10, -20],
    [-10, 0, 5, 0, 0, 0, 0, -10],
    [-10, 5, 5, 5, 5, 5, 0, -10],
    [-5, 0, 5, 5, 5, 5, 0, -5],
    [0, 0, 5, 5, 5, 5, 0, -5],
    [-10, 0, 5, 5, 5, 5, 0, -10],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-20, -10, -10, -5, -5, -10, -10, -20],
]

_PST_KING_MG = [
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-20, -30, -30, -40, -40, -30, -30, -20],
    [-10, -20, -20, -20, -20, -20, -20, -10],
    [20, 20, 0, 0, 0, 0, 20, 20],
    [20, 30, 10, 0, 0, 10, 30, 20],
]

_PST_MAP = {
    'p': _PST_PAWN,
    'n': _PST_KNIGHT,
    'b': _PST_BISHOP,
    'r': _PST_ROOK,
    'q': _PST_QUEEN,
    'k': _PST_KING_MG,
}


def _pst_bonus(piece: str, r: int, c: int) -> int:
    if piece == '??' or piece == '':
        return 0
    color = piece[0]
    t = piece[1]
    table = _PST_MAP.get(t)
    if table is None:
        return 0
    # mirror rows for white so that row 7 (bottom) is rank 1
    rr = 7 - r if color == 'w' else r
    bonus = table[rr][c]
    return bonus if color == 'w' else -bonus


def _clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


def _sign(b):
    return 1 if b else -1


def _inf():
    return 10 ** 9


def _mate_score(ply):
    return 100000 - ply


def _anti_mate_score(ply):
    return -100000 + ply


class gameState(gameState):
    # Extend with evaluation and search utilities
    def __init__(self):
        super().__init__()
        self.tt = {}

    def _board_key(self):
        # simple but effective key; can be replaced with Zobrist if needed
        return (
            self.whitetomove,
            self.white_king_location,
            self.black_king_location,
            self.enpassant_possible,
            self.current_castling_rights.wks,
            self.current_castling_rights.wqs,
            self.current_castling_rights.bks,
            self.current_castling_rights.bqs,
            tuple(tuple(row) for row in self.board),
        )

    def _order_moves(self, moves):
        def score(m):
            s = 0
            # MVV-LVA style ordering
            captured = m.picecaptured
            if captured != '??' and captured != '':
                victim = _piece_abs_value(captured[1])
                attacker = _piece_abs_value(m.piecemovec[1])
                s += 10000 + victim * 10 - attacker
            if getattr(m, 'is_pawn_promo', False):
                s += 900
            if getattr(m, 'is_castle', False):
                s += 100
            return s
        return sorted(moves, key=score, reverse=True)

    def evaluate_simple(self) -> int:
        total = 0
        for r in range(8):
            for c in range(8):
                total += _piece_value(self.board[r][c])
        return total

    def evaluate(self) -> int:
        total = 0
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                total += _piece_value(piece)
                total += _pst_bonus(piece, r, c)
        return total

    def negamax(self, depth: int, alpha: int, beta: int, color: int, ply: int = 0) -> int:
        if depth == 0:
            return color * self.evaluate()

        # Transposition table lookup
        key = self._board_key()
        entry = self.tt.get(key)
        if entry is not None and entry['depth'] >= depth:
            return entry['value']

        moves = self.validmoves()
        if len(moves) == 0:
            if self.inCheck():
                return _anti_mate_score(ply)  # losing for side to move
            return 0  # stalemate

        value = -_inf()
        # Order moves to improve pruning
        for m in self._order_moves(moves):
            self.makemove(m)
            score = -self.negamax(depth - 1, -beta, -alpha, -color, ply + 1)
            self.undo_move()
            if score > value:
                value = score
            if value > alpha:
                alpha = value
            if alpha >= beta:
                break

        # Store into TT (replace-only if deeper)
        if len(self.tt) > 500000:
            self.tt.clear()
        prev = self.tt.get(key)
        if prev is None or prev['depth'] <= depth:
            self.tt[key] = {'depth': depth, 'value': value}
        return value

    def find_best_move(self, depth: int = 2):
        best_move = None
        best_score = -_inf()
        color = 1 if self.whitetomove else -1
        moves = self._order_moves(self.validmoves())
        for m in moves:
            self.makemove(m)
            score = -self.negamax(depth - 1, -_inf(), _inf(), -color, 1)
            self.undo_move()
            if score > best_score:
                best_score = score
                best_move = m
        return best_move, best_score

    def evaluate_minimax(self, depth: int = 2) -> int:
        color = 1 if self.whitetomove else -1
        score = self.negamax(depth, -_inf(), _inf(), color, 0)
        # Convert to White-centric score
        return score if self.whitetomove else -score
