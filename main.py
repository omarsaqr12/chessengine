"""Pygame chess board and computer opponent."""

from pathlib import Path

import pygame as p
from verified_engine import GameState

BOARD_SIZE = 400
SQUARE = BOARD_SIZE // 8
BAR_WIDTH = 70
AI_ENABLED = True
AI_PLAYS_WHITE = False
AI_DEPTH = 2
EVAL_DEPTH = 1
ASSETS = Path(__file__).resolve().parent / 'images'


def load_images():
    return {color + kind: p.transform.scale(
        p.image.load(str(ASSETS / (color + kind + '.png'))), (SQUARE, SQUARE))
        for color in 'wb' for kind in 'rnbqkp'}


def select_move(moves, start, end):
    return next((m for m in moves
                 if (m.startrow, m.startcol) == start
                 and (m.endrow, m.endcol) == end), None)


def draw_board(screen, state, moves, selected, images, evaluation):
    for r in range(8):
        for c in range(8):
            rect = p.Rect(c * SQUARE, r * SQUARE, SQUARE, SQUARE)
            p.draw.rect(screen, (235, 236, 208) if (r + c) % 2 == 0
                        else (119, 149, 86), rect)
            piece = state.board[r][c]
            if piece != '??':
                screen.blit(images[piece], rect)
    if selected is not None:
        r, c = selected
        if state.board[r][c][0] == ('w' if state.whitetomove else 'b'):
            overlay = p.Surface((SQUARE, SQUARE), p.SRCALPHA)
            overlay.fill((60, 90, 220, 85))
            screen.blit(overlay, (c * SQUARE, r * SQUARE))
            overlay.fill((50, 150, 80, 95))
            for move in moves:
                if (move.startrow, move.startcol) == selected:
                    screen.blit(overlay, (move.endcol * SQUARE, move.endrow * SQUARE))
    value = int(max(-1000, min(1000, evaluation)))
    white_height = (value + 1000) * BOARD_SIZE // 2000
    p.draw.rect(screen, (245, 245, 245), (BOARD_SIZE, 0, BAR_WIDTH, white_height))
    p.draw.rect(screen, (25, 25, 25),
                (BOARD_SIZE, white_height, BAR_WIDTH, BOARD_SIZE - white_height))
    p.draw.rect(screen, (110, 110, 110), (BOARD_SIZE, 0, BAR_WIDTH, BOARD_SIZE), 1)
    font = p.font.SysFont(None, 19)
    if state.check_mate:
        text = 'Mate'
    elif state.stale_mate:
        text = 'Draw'
    else:
        text = f'{evaluation / 100:+.1f}'
    screen.blit(font.render(text, True, (60, 100, 210)), (BOARD_SIZE + 5, 6))


def main():
    p.init()
    screen = p.display.set_mode((BOARD_SIZE + BAR_WIDTH, BOARD_SIZE))
    p.display.set_caption('Chess engine')
    clock = p.time.Clock()
    images = load_images()
    state = GameState()
    moves = state.validmoves()
    selected = None
    evaluation = state.evaluate()
    changed = AI_ENABLED and AI_PLAYS_WHITE
    running = True
    while running:
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
            elif event.type == p.KEYDOWN and event.key == p.K_z:
                if AI_ENABLED and len(state.movelog) >= 2:
                    state.undo_move()
                    state.undo_move()
                    changed = True
                elif not AI_ENABLED and state.movelog:
                    state.undo_move()
                    changed = True
                selected = None
            elif event.type == p.MOUSEBUTTONDOWN and event.button == 1:
                if AI_ENABLED and state.whitetomove == AI_PLAYS_WHITE:
                    continue
                x, y = event.pos
                if not (0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE):
                    continue
                square = (y // SQUARE, x // SQUARE)
                if square == selected:
                    selected = None
                    continue
                if selected is not None:
                    move = select_move(moves, selected, square)
                    if move is not None:
                        state.makemove(move)
                        changed = True
                        selected = None
                        continue
                selected = square
        if changed:
            moves = state.validmoves()
            if AI_ENABLED and state.whitetomove == AI_PLAYS_WHITE and moves:
                ai_move, _ = state.find_best_move(AI_DEPTH)
                if ai_move is not None:
                    state.makemove(ai_move)
                    moves = state.validmoves()
            evaluation = state.evaluate_minimax(EVAL_DEPTH)
            changed = False
        draw_board(screen, state, moves, selected, images, evaluation)
        p.display.flip()
        clock.tick(30)
    p.quit()


if __name__ == '__main__':
    main()
