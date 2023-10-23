#this file will be used to take the input from the user, his moves.
import pygame as p
import chessengine
width=height=400
dimension=8
squaredimention=height/dimension #this is why we chose a height and width divsible by 8
Image={}
fps=15
#then we will make our main funciton
def loadimage():
    pieces=["wr","wb","wn","wq","wk","wp","bp","br","bb","bn","bq","bk"]
    for piece in pieces:
        Image[piece]=p.transform.scale(p.image.load("images/"+piece+".png"),(squaredimention,squaredimention))# trasnform.scale to resize to a new resolution
            
# now we will create the main function which will be used to handle the user input and draw the board and the pieces
def main():
    p.init()
    loadimage()
    screen=p.display.set_mode((width,height))#Initialize a window or screen for display
    clock=p.time.Clock() #create an object to help track time
    running =True
    seqsq=()
    movi=[]
    game=chessengine.gameState()
    validmove=game.validmoves()
    calculate=False
    while running:
        for e in p.event.get():
            if e.type==p.QUIT:
                running=False
            elif e.type==p.MOUSEBUTTONDOWN:
                location=p.mouse.get_pos()
                y=location[0]//squaredimention
                x=location[1]//squaredimention
                if seqsq==(x,y):
                    seqsq=()
                    movi=[]
                else:
                    seqsq=(x,y)
                    movi.append(seqsq)
                if len(movi)==2:
                    movin=chessengine.moving(movi[0],movi[1],game.board)
                    if(movin in validmove):
                        game.makemove(movin)
                        calculate=True
                        seqsq=()
                        movi=[]
                    else:
                        movi=[seqsq]
            elif e.type ==p.KEYDOWN:
                if e.key==p.K_z:
                    game.undo_move()
                    calculate=True
        if(calculate):
            validmove=game.validmoves()
            calculate=False            
        clock.tick(15)
        drawboard(game.board,screen)
        p.display.flip() #Update the full display Surface to the screen, this is why this is put inside a while loop
        
def drawboard(board,screen):
    colro=[p.Color("green"), p.Color("red")]
    for r in range(dimension):
        for c in range(dimension):
            p.draw.rect(screen,colro[(r+c)%2],p.Rect(c*squaredimention,r*squaredimention,squaredimention,squaredimention))
            piece=board[r][c]
            if(piece!="??"):
                screen.blit(Image[piece], p.Rect(c*squaredimention,r*squaredimention,squaredimention,squaredimention))
main()