"""Correctness-focused game-state adapter for the interactive chess application.

The original chessengine.py is retained as a legacy implementation. This adapter
fixes illegal king capture, piece-square orientation, and unsafe TT cutoff reuse.
"""

import chessengine


class GameState(chessengine.gameState):
    def validmoves(self):
        moves = [m for m in super().validmoves()
                 if m.picecaptured not in ('wk', 'bk')]
        if not moves:
            self.check_mate = self.inCheck()
            self.stale_mate = not self.check_mate
        return moves

    def evaluate(self):
        score = 0
        for r, row in enumerate(self.board):
            for c, piece in enumerate(row):
                if piece == '??':
                    continue
                score += chessengine._piece_value(piece)
                table = chessengine._PST_MAP.get(piece[1])
                if table:
                    bonus = table[r if piece[0] == 'w' else 7 - r][c]
                    score += bonus if piece[0] == 'w' else -bonus
        return score

    def negamax(self, depth, alpha, beta, color, ply=0):
        """Alpha-beta search without interpreting cutoff bounds as exact TT scores.

        Draw by repetition and automatic game termination on the 50-move rule
        remain unimplemented in the legacy state and are not claimed here.
        """
        moves = self.validmoves()
        if not moves:
            return -100000 + ply if self.inCheck() else 0
        if depth <= 0:
            return color * self.evaluate()
        best = -10**9
        for move in self._order_moves(moves):
            self.makemove(move)
            score = -self.negamax(depth - 1, -beta, -alpha, -color, ply + 1)
            self.undo_move()
            if score > best:
                best = score
            alpha = max(alpha, best)
            if alpha >= beta:
                break
        return best
