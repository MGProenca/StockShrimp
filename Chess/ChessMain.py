import pygame as p
import ChessEngine

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 60  # For animations
IMAGES = {}
COLORS = [p.Color("white"), p.Color("gray")]

def load_images():
    pieces = ['bK', 'bN', 'bB', 'bR', 'bQ', 'bp','wK', 'wN', 'wB', 'wR', 'wQ', 'wp']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(f"images/{piece}.png"), (SQ_SIZE, SQ_SIZE))


def draw_board(screen):
    # colors = [p.Color("white"), p.Color("gray")]
    
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = COLORS[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':  # If there is a piece at this square
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def highlight_squares(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):  # Highlight only if the selected square has the player's piece
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(85)  # Set transparency
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            s.set_alpha(50)  # Set transparency
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.startRow == r and move.startCol == c:  # Highlight valid moves from the selected square
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))

def draw_gamestate(screen, gs, valid_moves, sq_selected):
    draw_board(screen)
    highlight_squares(screen, gs, valid_moves, sq_selected)
    draw_pieces(screen, gs.board)


def animate_move(move, screen, board, clock):
    dr = move.endRow - move.startRow
    dc = move.endCol - move.startCol
    framesPerSquare = 1  # Number of frames to animate each square
    frameCount = (abs(dr) + abs(dc)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dr*frame/frameCount, move.startCol+dc * frame/frameCount)
        draw_board(screen)
        draw_pieces(screen, board)
        # Erase end piece
        color = COLORS[((move.endRow + move.endCol) % 2)]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != '--':  # If there is a captured piece
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # Draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()  # Update the display
        clock.tick(MAX_FPS)  # Control the frame rate

def drawText(text, screen):
    font = p.font.SysFont("Arial", 32, True, False)
    textObject = font.render(text, 0, p.Color('Black'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2, HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    p.display.flip()
    # p.time.wait(2000)  # Wait for 2 seconds before continuing


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()  # Initialize the game state
    valid_moves = gs.getValidMoves()  # Get valid moves for the initial state
    print("Valid moves at start:", valid_moves)
    move_made = False  # Flag if a move has been made
    animate = False
    game_over = False
    load_images()
    # print(gs.board)
    running = True
    sq_selected = ()  # No square is selected initially
    player_clicks = []  # Keep track of player clicks (two tuples)
    
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:  # Only allow clicks if the game is not over
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    print(f"Mouse clicked at: {row}, {col}")
                    if sq_selected == (row, col): # Reset the clicks if the same square is clicked
                        sq_selected = ()
                        player_clicks = []  
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected)
                    if len(player_clicks) == 2:  # If two squares are selected
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                        print(f"Move made: {move.getChessNotation()}")
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                print('AAA: ', move)
                                print('BBB: ', valid_moves[i])
                                gs.makeMove(valid_moves[i])  # Make the move in the game state
                                move_made = True
                                animate = True
                                sq_selected = () # reset clicks
                                player_clicks = []
                        if not move_made:  # If the move was not valid
                            player_clicks = [sq_selected]
            
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    move_made = True
                    animate = False
                if e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    valid_moves = gs.getValidMoves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    
            

        if move_made: # only calcualtes possible moves when clicks
            print("Move made, recalculating valid moves")
            if animate:
                animate_move(gs.moveLog[-1], screen, gs.board, clock)
            valid_moves = gs.getValidMoves()
            move_made = False
            animate = False

        
        draw_gamestate(screen, gs, valid_moves, sq_selected)
        
        if gs.checkmate:
            game_over = True
            if gs.whiteToMove:
                drawText('Black wins by checkmate!', screen)
            else:
                drawText('White wins by checkmate!', screen)
        elif gs.stalemate:
            game_over = True
            drawText('Stalemate!', screen)

        clock.tick(MAX_FPS)
        p.display.flip()  # Update the display
    

if __name__ == "__main__":
    main()
