#this file will be used to take the input from the user, his moves.
import pygame as p
import chessengine
width=height=400
dimension=8
squaredimention=height//dimension #this is why we chose a height and width divsible by 8
bar_width=60
AI_ENABLED=True
AI_PLAYS_WHITE=False
AI_DEPTH=5
EVAL_DEPTH=5
Image={}
fps=15
#then we will make our main funciton
def loadimage():
    pieces=["wr","wb","wn","wq","wk","wp","bp","br","bb","bn","bq","bk"]
    for piece in pieces:
        Image[piece]=p.transform.scale(p.image.load("images/"+piece+".png"),(int(squaredimention),int(squaredimention)))# trasnform.scale to resize to a new resolution
            
# now we will create the main function which will be used to handle the user input and draw the board and the pieces
def main():
    p.init()
    loadimage()
    screen=p.display.set_mode((width+bar_width,height))#Initialize a window or screen for display
    clock=p.time.Clock() #create an object to help track time
    running =True
    seqsq=()
    movi=[]
    game=chessengine.gameState()
    validmove=game.validmoves()
    calculate=False
    current_eval=game.evaluate_minimax(depth=EVAL_DEPTH)
    while running:
        for e in p.event.get():
            if e.type==p.QUIT:
                running=False
            elif e.type==p.MOUSEBUTTONDOWN:
                location=p.mouse.get_pos()
                y=location[0]//squaredimention
                x=location[1]//squaredimention
                if x<dimension and y<dimension:
                    if seqsq==(x,y):
                        seqsq=()
                        movi=[]
                    else:
                        seqsq=(x,y)
                        movi.append(seqsq)
                    if len(movi)==2:
                        # use engine-generated move object to preserve special move flags
                        start=movi[0]; end=movi[1]
                        move_to_play=None
                        for mv in validmove:
                            if mv.startrow==start[0] and mv.startcol==start[1] and mv.endrow==end[0] and mv.endcol==end[1]:
                                move_to_play=mv
                                break
                        if move_to_play is not None:
                            game.makemove(move_to_play)
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
            # AI move if enabled
            if AI_ENABLED and game.whitetomove==AI_PLAYS_WHITE and len(validmove)>0:
                ai_move,_=game.find_best_move(depth=AI_DEPTH)
                if ai_move is not None:
                    game.makemove(ai_move)
                    validmove=game.validmoves()
            current_eval=game.evaluate_minimax(depth=EVAL_DEPTH)
            calculate=False            
        clock.tick(15)
        drawboard(game.board,screen,game,validmove,seqsq,current_eval)
        p.display.flip() #Update the full display Surface to the screen, this is why this is put inside a while loop
def highlight(game, screen,validmoves,seqsq):
    if seqsq!=():
        r,c=seqsq
        r=int(r)
        c=int(c)
        if game.board[r][c][0]==('w' if game.whitetomove else 'b'):
            s=p.Surface((squaredimention,squaredimention))
            s.set_alpha(100)
            s.fill(p.Color('black'))
            screen.blit(s,(c*squaredimention,r*squaredimention))
            s.fill(p.Color('blue'))
            for move in validmoves:
                if move.startrow==r and move.startcol==c:
                    screen.blit(s,(squaredimention*move.endcol,squaredimention*move.endrow))

        
def drawboard(board,screen,game,validmoves,seqsq,current_eval):
    colro=[p.Color("green"), p.Color("red")]
    for r in range(dimension):
        for c in range(dimension):
            p.draw.rect(screen,colro[(r+c)%2],p.Rect(c*squaredimention,r*squaredimention,squaredimention,squaredimention))
            piece=board[r][c]
            if(piece!="??"):
                screen.blit(Image[piece], p.Rect(c*squaredimention,r*squaredimention,squaredimention,squaredimention))
    highlight(game,screen,validmoves,seqsq)
    draw_eval_bar(screen,current_eval)

def draw_eval_bar(screen,current_eval):
    # current_eval is white-centric centipawns from minimax
    max_cp=1000
    cp=int(max(-max_cp,min(max_cp,current_eval)))
    white_height=(cp+max_cp)*height//(2*max_cp)
    # background
    p.draw.rect(screen,p.Color('white'),p.Rect(width,0,bar_width,white_height))
    p.draw.rect(screen,p.Color('black'),p.Rect(width,white_height,bar_width,height))
    # border
    p.draw.rect(screen,p.Color('gray'),p.Rect(width,0,bar_width,height),1)
    # text
    try:
        font=p.font.SysFont(None,16)
        txt=("+" if current_eval>=0 else "")+str(round(current_eval/100.0,2))
        text_surf=font.render(txt,True,p.Color('blue'))
        screen.blit(text_surf,(width+5,5))
    except Exception:
        pass
main()