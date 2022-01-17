import itertools

import pyglet
import classes
from pyglet import shapes
from pyglet.window import key

TIME_INCREMENT = 1 / 30

SCALE = 30
WIDTH = 10
HEIGHT = 20
XOFFSET = 8
YOFFSET = 4

WHITE = 255, 255, 255

game_window = pyglet.window.Window((2 * XOFFSET + WIDTH) * SCALE, (HEIGHT + 2 * YOFFSET) * SCALE, caption='Tetris')
gamestate = classes.Tetris()


def update(dt):
    gamestate.frames += 1
    if gamestate.frames % 30 in [0, 15]:
        gamestate.down()


@game_window.event
def on_draw():
    batch = pyglet.graphics.Batch()
    game_window.clear()

    # Draw all the pieces in the board
    blocks = []
    for i in range(10):
        for j in range(24):
            if gamestate.board[i][j] is not None:
                block = shapes.Rectangle((XOFFSET + i + 0.05) * SCALE, (YOFFSET + j + 0.05) * SCALE, SCALE * 0.9,
                                         SCALE * 0.9,
                                         color=gamestate.board[i][j], batch=batch)
                blocks.append(block)
    # Draw the current piece
    for block in gamestate.current_piece.squares:
        i = block[0]
        j = block[1]
        if j < 20:
            square = shapes.Rectangle((XOFFSET + i + 0.05) * SCALE, (YOFFSET + j + 0.05) * SCALE, SCALE * 0.9,
                                      SCALE * 0.9,
                                      color=gamestate.current_piece.color, batch=batch)
            blocks.append(square)
    # Draw the edges of the game board
    borders = []
    xlist = [XOFFSET * SCALE, (XOFFSET + WIDTH) * SCALE]
    ylist = [YOFFSET * SCALE, (YOFFSET + HEIGHT) * SCALE]
    for x in xlist:
        line = shapes.Line(x, ylist[0], x, ylist[1], color=WHITE, batch=batch)
        borders.append(line)
    for y in ylist:
        line = shapes.Line(xlist[0], y, xlist[1], y, color=WHITE, batch=batch)
        borders.append(line)

    # Draw a box for the next piece
    bottom_left = [SCALE * (XOFFSET + WIDTH + 2), SCALE * (HEIGHT)]
    xlist = [bottom_left[0], bottom_left[0] + 4 * SCALE]
    ylist = [bottom_left[1], bottom_left[1] + 4 * SCALE]
    for x in xlist:
        line = shapes.Line(x, ylist[0], x, ylist[1], color=WHITE, batch=batch)
        borders.append(line)
    for y in ylist:
        line = shapes.Line(xlist[0], y, xlist[1], y, color=WHITE, batch=batch)
        borders.append(line)
    next_piece = []
    for block in gamestate.next_piece.squares:
        i = (block[0] - WIDTH // 2 + 0.05 + 1) * SCALE + bottom_left[0]
        j = (block[1] - HEIGHT + 0.05) * SCALE + bottom_left[1]
        square = shapes.Rectangle(i, j, SCALE * 0.9,
                                  SCALE * 0.9,
                                  color=gamestate.next_piece.color, batch=batch)
        next_piece.append(square)
    # Display the score at the top of the screen
    score = pyglet.text.Label(f'Score: {gamestate.score}',
                              font_name='Times New Roman',
                              font_size=36,
                              x=game_window.width // 2, y=(YOFFSET + HEIGHT) * SCALE,
                              anchor_x='center', anchor_y='bottom',
                              batch=batch)
    batch.draw()


@game_window.event
def on_key_press(symbol, modifiers):
    if symbol in [key.SPACE]:
        gamestate.drop()
    if symbol in [key.S, key.DOWN]:
        gamestate.down()
    if symbol in [key.A, key.LEFT]:
        gamestate.side([-1, 0])
    if symbol in [key.D, key.RIGHT]:
        gamestate.side([1, 0])
    if symbol in [key.W, key.UP]:
        gamestate.rotate_clockwise()
    if symbol == key.Z:
        gamestate.restart()


if __name__ == "__main__":
    pyglet.clock.schedule_interval(update, TIME_INCREMENT)
    pyglet.app.run()
