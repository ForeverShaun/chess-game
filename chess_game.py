import pygame
import chess
import chess.engine
import time

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
SQUARE_SIZE = WIDTH // 8
WHITE = (240, 217, 181)
BROWN = (181, 136, 99)
FPS = 60  # Smooth animation

# Load Stockfish engine
STOCKFISH_PATH = r"C:\Users\shaun\Downloads\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe"
engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

# Load images
pieces = {}
for piece in ["P", "N", "B", "R", "Q", "K", "p", "n", "b", "r", "q", "k"]:
    filename = f"images/{'w' if piece.isupper() else 'b'}{piece.lower()}.png"
    pieces[piece] = pygame.image.load(filename)
    pieces[piece] = pygame.transform.scale(pieces[piece], (SQUARE_SIZE, SQUARE_SIZE))


# Pygame setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess AI")

# Initialize board
board = chess.Board()
selected_square = None
running = True
clock = pygame.time.Clock()

def check_game_over():
    if board.is_checkmate():
        show_game_over_screen("Checkmate! You lost!")
        return True
    elif board.is_stalemate():
        show_game_over_screen("Stalemate! It's a draw.")
        return True
    elif board.is_insufficient_material():
        show_game_over_screen("Draw due to insufficient material.")
        return True
    elif board.is_seventyfive_moves():
        show_game_over_screen("Draw: 75-move rule.")
        return True
    elif board.is_fivefold_repetition():
        show_game_over_screen("Draw: Fivefold repetition.")
        return True
    return False

def show_game_over_screen(message):
    screen.fill((0, 0, 0))  # Black background
    font = pygame.font.Font(None, 40)
    text = font.render(message, True, (255, 255, 255))
    restart_text = font.render("Press R to restart or Q to quit", True, (255, 255, 255))

    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()

    # Wait for user input (R to restart, Q to quit)
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Restart the game
                    reset_game()
                    return
                elif event.key == pygame.K_q:  # Quit the game
                    pygame.quit()
                    exit()

def reset_game():
    global board, selected_square
    board = chess.Board()  # Reset chess board
    selected_square = None
    screen.fill((0, 0, 0))  # Clear screen
    draw_board()
    draw_pieces()
    pygame.display.flip()



def draw_board():
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else BROWN
            pygame.draw.rect(screen, color, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces():
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            col = square % 8
            row = 7 - (square // 8)
            screen.blit(pieces[piece.symbol()], (col * SQUARE_SIZE, row * SQUARE_SIZE))

def animate_move(start_square, end_square, piece_symbol):
    """Animate piece moving from start_square to end_square."""
    start_col, start_row = start_square % 8, 7 - (start_square // 8)
    end_col, end_row = end_square % 8, 7 - (end_square // 8)
    
    start_x, start_y = start_col * SQUARE_SIZE, start_row * SQUARE_SIZE
    end_x, end_y = end_col * SQUARE_SIZE, end_row * SQUARE_SIZE
    
    frames = 10  # Number of frames for smooth animation
    for i in range(frames + 1):
        alpha = i / frames  # Interpolation factor (0 to 1)
        x = (1 - alpha) * start_x + alpha * end_x
        y = (1 - alpha) * start_y + alpha * end_y

        draw_board()
        draw_pieces()
        screen.blit(pieces[piece_symbol], (x, y))  # Moving piece
        pygame.display.flip()
        clock.tick(FPS)

def ai_move():
    if check_game_over():
        return  # Stop AI move if the game is already over
    
    result = engine.play(board, chess.engine.Limit(time=1.0))
    board.push(result.move)
    
    if check_game_over():
        return  # Stop game if AI checkmates the player


def get_square(pos):
    x, y = pos
    col = x // SQUARE_SIZE
    row = 7 - (y // SQUARE_SIZE)
    return chess.square(col, row)

needs_update = True  # Flag to control screen updates



while running:
    draw_board()
    draw_pieces()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if check_game_over():  # Prevent moves only when the game is over
                continue  

            square = get_square(pygame.mouse.get_pos())  # Get the clicked square
            if selected_square is None:
                selected_square = square  # Select a piece to move
            else:
                move = chess.Move(selected_square, square)  # Create a move

                if move in board.legal_moves:  # Check if the move is legal
                    board.push(move)  # Apply the move

                    if check_game_over():  # Check if the game is over after player's move
                        continue  # Stop processing if game ended

                    ai_move()  # AI makes a move

                    if check_game_over():  # Check if the game is over after AI's move
                        continue  # Stop processing if game ended

                selected_square = None  # Reset selection




engine.quit()
pygame.quit()


