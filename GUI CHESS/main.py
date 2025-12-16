import pygame
import chess
import math

# ---------------- INIT ----------------
pygame.init()
pygame.mixer.init()

move_sound = pygame.mixer.Sound("sounds/move.wav")
move_sound.set_volume(0.6)

screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)
pygame.display.set_caption("Chess Game By~Atharv Raiii (Ver 1.0)")
clock = pygame.time.Clock()
FPS = 60

WIDTH, HEIGHT = screen.get_size()
BOTTOM_PANEL = 80
SQUARE_SIZE = min(WIDTH, HEIGHT - BOTTOM_PANEL) // 8

BOARD_PIXEL_SIZE = SQUARE_SIZE * 8
BOARD_ORIGIN_X = (WIDTH - BOARD_PIXEL_SIZE) // 2
BOARD_ORIGIN_Y = (HEIGHT - BOTTOM_PANEL - BOARD_PIXEL_SIZE) // 2

# ---------------- COLORS ----------------
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT = (186, 202, 68)

BUTTON_COLOR = (70, 70, 70)
BUTTON_TEXT = (255, 255, 255)

font = pygame.font.SysFont(None, 30)
big_font = pygame.font.SysFont(None, 56)

# ---------------- DATA ----------------
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

difficulty_depth = 3

# ---------------- LOAD PIECES ----------------
PIECE_IMAGES = {}
for c in ["w", "b"]:
    for p in ["p","r","n","b","q","k"]:
        PIECE_IMAGES[c + p] = pygame.transform.scale(
            pygame.image.load(f"pieces/{c}{p}.png"),
            (SQUARE_SIZE, SQUARE_SIZE)
        )

# ---------------- ENGINE ----------------
def evaluate_board(board):
    if board.is_checkmate():
        return -99999 if board.turn else 99999
    if board.is_stalemate():
        return 0
    score = 0
    for p in PIECE_VALUES:
        score += len(board.pieces(p, chess.WHITE)) * PIECE_VALUES[p]
        score -= len(board.pieces(p, chess.BLACK)) * PIECE_VALUES[p]
    return score


def minimax(board, depth, alpha, beta, maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)
    if maximizing:
        val = -math.inf
        for m in board.legal_moves:
            board.push(m)
            val = max(val, minimax(board, depth-1, alpha, beta, False))
            board.pop()
            alpha = max(alpha, val)
            if beta <= alpha: break
        return val
    else:
        val = math.inf
        for m in board.legal_moves:
            board.push(m)
            val = min(val, minimax(board, depth-1, alpha, beta, True))
            board.pop()
            beta = min(beta, val)
            if beta <= alpha: break
        return val


def get_best_move(board, depth):
    best, val = None, math.inf
    for m in board.legal_moves:
        board.push(m)
        v = minimax(board, depth-1, -math.inf, math.inf, True)
        board.pop()
        if v < val:
            val, best = v, m
    return best

# ---------------- ANIMATION ----------------
def animate_move(board, move):
    piece = board.piece_at(move.from_square)
    if not piece:
        return
    img = PIECE_IMAGES[("w" if piece.color else "b") + piece.symbol().lower()]
    fx, fy = chess.square_file(move.from_square), 7 - chess.square_rank(move.from_square)
    tx, ty = chess.square_file(move.to_square), 7 - chess.square_rank(move.to_square)
    start = pygame.Vector2(BOARD_ORIGIN_X + fx*SQUARE_SIZE, BOARD_ORIGIN_Y + fy*SQUARE_SIZE)
    end = pygame.Vector2(BOARD_ORIGIN_X + tx*SQUARE_SIZE, BOARD_ORIGIN_Y + ty*SQUARE_SIZE)
    for i in range(1, 16):
        screen.fill((0,0,0))
        draw_board(None)
        draw_pieces(board)
        screen.blit(img, start.lerp(end, i/15))
        pygame.display.flip()
        clock.tick(60)

# ---------------- DRAWING ----------------
def draw_board(sel):
    for r in range(8):
        for c in range(8):
            pygame.draw.rect(
                screen,
                LIGHT_SQUARE if (r+c)%2==0 else DARK_SQUARE,
                (BOARD_ORIGIN_X+c*SQUARE_SIZE, BOARD_ORIGIN_Y+r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            )
    if sel is not None:
        c = chess.square_file(sel)
        r = 7 - chess.square_rank(sel)
        pygame.draw.rect(screen, HIGHLIGHT,
            (BOARD_ORIGIN_X+c*SQUARE_SIZE, BOARD_ORIGIN_Y+r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def draw_pieces(board):
    for s in chess.SQUARES:
        p = board.piece_at(s)
        if p:
            c = chess.square_file(s)
            r = 7 - chess.square_rank(s)
            screen.blit(
                PIECE_IMAGES[("w" if p.color else "b") + p.symbol().lower()],
                (BOARD_ORIGIN_X+c*SQUARE_SIZE, BOARD_ORIGIN_Y+r*SQUARE_SIZE)
            )


def draw_button(x, text, w=140):
    r = pygame.Rect(x, HEIGHT-60, w, 40)
    pygame.draw.rect(screen, BUTTON_COLOR, r)
    screen.blit(font.render(text, True, BUTTON_TEXT), (r.x+30, r.y+10))
    return r


def draw_difficulty():
    rects=[]
    for i,(n,d) in enumerate([("Easy",2),("Med",3),("Hard",4)]):
        r=pygame.Rect(20+i*110,HEIGHT-60,100,40)
        pygame.draw.rect(screen,BUTTON_COLOR,r)
        screen.blit(font.render(n,True,BUTTON_TEXT),(r.x+25,r.y+10))
        rects.append((r,d))
    return rects


def show_about():
    overlay=pygame.Surface((WIDTH,HEIGHT))
    overlay.set_alpha(190)
    overlay.fill((0,0,0))
    screen.blit(overlay,(0,0))
    lines=[
        "Chess Game By Atharv Raiii",
        "Version 1.0",
        "",
        "Programming Language used ---> Python + Pygame",
        "Press ESC Button to close This Program",
        "",
        "New Updates SOON!!!",
        "",
        "FOUND A GLITCH? DM ME ON insta-- @not_rai_atharv",
    ]
    for i,t in enumerate(lines):
        txt=font.render(t,True,(255,255,255))
        screen.blit(txt,txt.get_rect(center=(WIDTH//2,HEIGHT//2-80+i*35)))
    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE:
                return
            if e.type==pygame.QUIT:
                pygame.quit(); exit()

# ---------------- MAIN LOOP ----------------
def main():
    global difficulty_depth
    board=chess.Board()
    selected=None
    running=True

    while running:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type==pygame.QUIT: running=False
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_ESCAPE: running=False
                if e.key==pygame.K_u and len(board.move_stack)>=2:
                    board.pop(); board.pop()

            if e.type==pygame.MOUSEBUTTONDOWN:
                x,y=e.pos
                if undo.collidepoint(x,y) and len(board.move_stack)>=2:
                    board.pop(); board.pop()
                if restart.collidepoint(x,y): board.reset()
                if about.collidepoint(x,y): show_about()
                for r,d in diffs:
                    if r.collidepoint(x,y): difficulty_depth=d

                if board.turn==chess.WHITE and BOARD_ORIGIN_X<=x<BOARD_ORIGIN_X+BOARD_PIXEL_SIZE:
                    col=(x-BOARD_ORIGIN_X)//SQUARE_SIZE
                    row=(y-BOARD_ORIGIN_Y)//SQUARE_SIZE
                    if 0<=col<8 and 0<=row<8:
                        sq=chess.square(col,7-row)
                        if selected is None:
                            selected=sq
                        else:
                            mv=chess.Move(selected,sq)
                            if mv in board.legal_moves:
                                animate_move(board,mv)
                                move_sound.play()
                                board.push(mv)

                                ai=get_best_move(board,difficulty_depth)
                                if ai:
                                    animate_move(board,ai)
                                    move_sound.play()
                                    board.push(ai)
                            selected=None

        screen.fill((0,0,0))
        draw_board(selected)
        draw_pieces(board)
        undo=draw_button(WIDTH-160,"UNDO")
        restart=draw_button(WIDTH-330,"RESTART",150)
        about=draw_button(WIDTH-500,"ABOUT")
        diffs=draw_difficulty()
        pygame.display.flip()

    pygame.quit()

if __name__=="__main__":
    main()
