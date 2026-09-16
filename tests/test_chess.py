"""Known-position regression checks for the GUI's game-state adapter."""

import unittest

from verified_engine import GameState


def play(state, algebraic):
    moves = [m for m in state.validmoves() if m.getnotation() == algebraic]
    if len(moves) != 1:
        raise AssertionError(f'{algebraic}: expected one legal move, found {len(moves)}')
    state.makemove(moves[0])
    return moves[0]


def perft(state, depth):
    if depth == 0:
        return 1
    count = 0
    for move in state.validmoves():
        state.makemove(move)
        count += perft(state, depth - 1)
        state.undo_move()
    return count


class ChessTests(unittest.TestCase):
    def test_known_initial_position_counts_and_undo(self):
        state = GameState()
        initial = state._board_key()
        self.assertEqual(perft(state, 1), 20)
        self.assertEqual(perft(state, 2), 400)
        self.assertEqual(state._board_key(), initial)
        self.assertEqual(len(state.movelog), 0)

    def test_en_passant_capture_and_undo(self):
        state = GameState()
        for name in ('e2e4', 'a7a6', 'e4e5', 'd7d5'):
            play(state, name)
        before = state._board_key()
        move = play(state, 'e5d6')
        self.assertTrue(move.is_enpassant)
        self.assertEqual(state.board[3][3], '??')
        self.assertEqual(state.board[2][3], 'wp')
        state.undo_move()
        self.assertEqual(state._board_key(), before)

    def test_castling_and_undo(self):
        state = GameState()
        state.board = [['??'] * 8 for _ in range(8)]
        state.board[7][4] = 'wk'
        state.board[0][4] = 'bk'
        state.board[7][0] = state.board[7][7] = 'wr'
        before = state._board_key()
        self.assertIn('e1g1', {m.getnotation() for m in state.validmoves()})
        self.assertIn('e1c1', {m.getnotation() for m in state.validmoves()})
        move = play(state, 'e1g1')
        self.assertTrue(move.is_castle)
        self.assertEqual(state.board[7][5], 'wr')
        state.undo_move()
        self.assertEqual(state._board_key(), before)

    def test_promotion_auto_queen_and_undo(self):
        state = GameState()
        state.board = [['??'] * 8 for _ in range(8)]
        state.board[7][4] = 'wk'
        state.board[0][4] = 'bk'
        state.board[1][0] = 'wp'
        before = state._board_key()
        move = play(state, 'a7a8')
        self.assertTrue(move.is_pawn_promo)
        self.assertEqual(state.board[0][0], 'wq')
        state.undo_move()
        self.assertEqual(state._board_key(), before)

    def test_checkmate_at_leaf(self):
        state = GameState()
        for name in ('f2f3', 'e7e5', 'g2g4', 'd8h4'):
            play(state, name)
        self.assertEqual(state.validmoves(), [])
        self.assertTrue(state.check_mate)
        self.assertLess(state.negamax(0, -10**9, 10**9, 1, 0), -90000)

    def test_kings_cannot_be_captured(self):
        state = GameState()
        state.board = [['??'] * 8 for _ in range(8)]
        state.board[7][7] = 'wk'
        state.white_king_location = (7, 7)
        state.board[0][4] = 'bk'
        state.board[1][4] = 'wq'
        self.assertNotIn('e7e8', {m.getnotation() for m in state.validmoves()})

    def test_pawn_advancement_has_correct_white_orientation(self):
        state = GameState()
        state.board = [['??'] * 8 for _ in range(8)]
        state.board[7][4] = 'wk'
        state.board[0][4] = 'bk'
        state.board[6][3] = 'wp'
        before = state.evaluate()
        state.board[6][3] = '??'
        state.board[4][3] = 'wp'
        self.assertGreater(state.evaluate(), before)


if __name__ == '__main__':
    unittest.main()
