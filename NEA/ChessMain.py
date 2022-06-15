import ChessEngine
import Puzzles
import pygame
import sys
from pygame.locals import *

# Imported to allow the use of event.type and event.key Line 56-65
# https://www.pygame.org/docs/ref/locals.html

width = height = 500
dim = 8 #Dimensions (8x8)
sqsize =  50      ##height // dim
maxfps = 60

images = {}
# defines an empty dictionary which can be used to Load the Images into by
# giving each piece a name like "pW" and the corrosponding key of the image

mainClock = pygame.time.Clock()
pygame.init()
pygame.display.set_caption("James' Chess Game")
screen = pygame.display.set_mode((500, 500), 0, 32)
smallfont = pygame.font.SysFont('freesansbold.ttf', 30)
midfont = pygame.font.SysFont('freesansbold.ttf', 40)
bigfont = pygame.font.SysFont('freesansbold.ttf', 50)

keyPressed = pygame.key.get_pressed()

#Colours RGB format
black = (0, 0, 0)
blue = (0, 20, 50)
white = (255, 255, 255)
red = (255, 0 , 0)
lightred = (255, 204, 203)
green = (0, 255, 0)
backgroundblue = (0, 20, 50)

# file name for each piece must follow the formatting "wP" + .png as
# I have used an iteration through the list "pieces" + .png to initialse each image for each piece
def loadImages():
    pieces = ["wP","wR","wN","wB","wQ","wK","bP","bR","bN","bB","bQ","bK"]
    for piece in pieces:
        images[piece] = pygame.transform.scale(pygame.image.load("images/" + piece +".png"),(sqsize,sqsize))

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def main_menu():
   while True:

        screen.fill(backgroundblue)
        button_main = (50, 300, 200, 50)
        button_main_center = (55, 315)
        button_puzzle  = (300, 300, 150, 50)
        button_puzzle_center = (320, 312)
        button_quit = (50, 450, 75, 30)
        button_quit_center = (65, 455)
        draw_text("James' Chess Game", bigfont, white, screen, 85, 50)

        mouse = pygame.mouse.get_pos()

        width = screen.get_width()
        height = screen.get_height()
        textchessmain = smallfont.render('Chess vs Computer', True, white)
        textpuzzle = midfont.render('Puzzles', True, white)
        textquit = smallfont.render('Quit', True, white)

        click = False

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                   pygame.quit()
                   sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                   click = True

        # Button to activate Chess Main
        if 50 + 200 >= mouse[0] >= 50 and 300 + 50 >= mouse[1] >= 300:
            pygame.draw.rect(screen, green, (button_main))
            screen.blit(textchessmain, (button_main_center))
            if click:
                main()
        else:
            pygame.draw.rect(screen, red, (button_main))
            screen.blit(textchessmain, (button_main_center))

        # Button to Activate Puzzles
        if 300 + 150 >= mouse[0] >= 300 and 300 + 50 >= mouse[1] >= 300:
            pygame.draw.rect(screen, green, button_puzzle)
            screen.blit(textpuzzle, (button_puzzle_center))
            if click:
                puzzles()
        else:
            pygame.draw.rect(screen, red, button_puzzle)
            screen.blit(textpuzzle, (button_puzzle_center))

        # Button to Quit the Game
        if 50 + 75 >= mouse[0] >= 50 and 450 + 30 >= mouse[1] >= 450:
            pygame.draw.rect(screen, green, button_quit)
            screen.blit(textquit, (button_quit_center))
            if click:
                sys.exit()
                Running = False
        else:
            pygame.draw.rect(screen, red, button_quit)
            screen.blit(textquit, (button_quit_center))

        if keyPressed[pygame.K_ESCAPE]:
            print("Thanks for Playing")
            Running = False

        pygame.display.update()
        mainClock.tick(60)

def main():
    screen = pygame.display.set_mode((width,height))
    clock = pygame.time.Clock()
    screen.fill(pygame.Color("White"))

    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    loadImages()
    sqSelected = ()
    playerClicks = []
    running = True

    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
                print(gs.moveLog)
                
            elif e.type == pygame.MOUSEBUTTONDOWN and gs.whiteToMove:
                location = pygame.mouse.get_pos()
                col = location[0]//sqsize
                row = location[1]//sqsize
                if sqSelected == (row,col):
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (row,col)
                    playerClicks.append(sqSelected)
                    
                if len(playerClicks) == 2:
                    move = ChessEngine.Move(playerClicks[0],playerClicks[1], gs.board)
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            gs.makeMove(validMoves[i])
                            moveMade = True
                            sqSelected = ()
                            playerClicks = []
                    if not moveMade:
                        playerClicks = [sqSelected]
            
                    
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_z:
                    gs.undoMove()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = True
                if e.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                    
        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False
        drawGameState(screen, gs)
        clock.tick(maxfps)
        pygame.display.flip()

        if gs.checkMate and not gs.AIturn:
            print("Black wins by checkmate") if gs.whiteToMove else print("White wins by checkmate")
            running = False
        
        if gs.stalemate and not gs.AIturn:
            print("Draw by stalemate")
            running = False

        if not gs.whiteToMove and len(validMoves) != 0 and not moveMade:
            x = gs.getBestMove(2)
            gs.makeMove(x)
            moveMade = True

def puzzlesmenu():
    while True:

        screen.fill(backgroundblue)
        pygame.display.update()
        button_puzzle1 = (50, 300, 200, 50)
        button_puzzle1_center = (55, 315)
        button_puzzle2 = (300, 300, 150, 50)
        button_puzzle2_center = (320, 312)
        button_back = (50, 450, 75, 30)
        button_back_center = (65, 455)

        mouse = pygame.mouse.get_pos()

        width = screen.get_width()
        height = screen.get_height()

        textpuzzle1 = midfont.render('Puzzle 1', True, white)
        textpuzzle2 = midfont.render('Puzzle 2', True, white)
        textback = smallfont.render('back', True, white)

        click = False

        if 50 + 200 >= mouse[0] >= 50 and 300 + 50 >= mouse[1] >= 300:
            pygame.draw.rect(screen, green, (button_puzzle1))
            screen.blit(textpuzzle1, (button_puzzle1_center))
        if click:
            puzzlesmenu()
        else:
            pygame.draw.rect(screen, red, (button_puzzle1))
            screen.blit(textpuzzle1, (button_puzzle1_center))

        if 300 + 150 >= mouse[0] >= 300 and 300 + 50 >= mouse[1] >= 300:
            pygame.draw.rect(screen, green, button_puzzle2)
            screen.blit(textpuzzle2, (button_puzzle2_center))
            if click:
                puzzlesmenu()
        else:
            pygame.draw.rect(screen, red, button_puzzle2)
            screen.blit(textpuzzle2, (button_puzzle2_center))

        if 50 + 75 >= mouse[0] >= 50 and 450 + 30 >= mouse[1] >= 450:
            pygame.draw.rect(screen, green, button_back)
            screen.blit(textback, (button_back_center))
            if click:
                sys.exit()
        else:
            pygame.draw.rect(screen, red, button_back)
            screen.blit(textback, (button_back_center))

        pygame.display.update()
        mainClock.tick(60)

def puzzles():
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    screen.fill(pygame.Color("White"))

    gs = Puzzles.GameStatePuzzles()
    solution = ((1,7), (1,0), gs.board)
    moveMade = False
    loadImages()
    sqSelected = ()
    playerClicks = []
    running = True

    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
                print(gs.moveLog)

            elif e.type == pygame.MOUSEBUTTONDOWN and gs.whiteToMove:
                location = pygame.mouse.get_pos()
                col = location[0] // sqsize
                row = location[1] // sqsize
                if sqSelected == (row, col):
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)

                if len(playerClicks) == 2:
                    move = Puzzles.Move(playerClicks[0], playerClicks[1], gs.board)
                    if move == solution:
                        gs.makeMove(solution)
                        moveMade = True
                        sqSelected = ()
                        playerClicks = []
                    if not moveMade:
                        playerClicks = [sqSelected]


            elif e.type == pygame.KEYDOWN:
                if e.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        drawGameState(screen, gs)
        clock.tick(maxfps)
        pygame.display.flip()


def drawGameState(screen, gs):
    drawBoard(screen)
    drawPieces(screen, gs.board)

def drawBoard(screen):
    colours = [pygame.Color("white"),pygame.Color("gray")]
    for r in range(dim):
        for c in range(dim):
            colour = colours[((r + c) % 2)]
            pygame.draw.rect(screen, colour, pygame.Rect(c*sqsize, r*sqsize, sqsize, sqsize))

def drawPieces(screen,board):
    for r in range(dim):
        for c in range(dim):
            piece = board[r][c]
            if piece != "--":
                screen.blit(images[piece], pygame.Rect(c*sqsize, r*sqsize, sqsize, sqsize))




if __name__ == "__main__":
    main_menu()
