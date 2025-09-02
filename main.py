import pygame as p
from pathlib import Path
import chessengine

width=height=400
dimension=8
squaredimention=height//dimension
bar_width=60
AI_ENABLED=True
AI_PLAYS_WHITE=False
AI_DEPTH=5
EVAL_DEPTH=5
Image={}
fps=15

_BASE_DIR = Path(__file__).resolve().parent
_IMAGES_DIR = _BASE_DIR / "images"

def loadimage():
    pieces=["wr","wb","wn","wq","wk","wp","bp","br","bb","bn","bq","bk"]
    for piece in pieces:
        img_path=_IMAGES_DIR/(piece+".png")
        Image[piece]=p.transform.scale(p.image.load(str(img_path)),(int(squaredimention),int(squaredimention)))

def main():
    p.init()
    loadimage()
    screen=p.display.set_mode((width+bar_width,height))
    clock=p.time.Clock()
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
            if AI_ENABLED and game.whitetomove==AI_PLAYS_WHITE and len(validmove)>0:
                ai_move,_=game.find_best_move(depth=AI_DEPTH)
                if ai_move is not None:
                    game.makemove(ai_move)
                    validmove=game.validmoves()
            current_eval=game.evaluate_minimax(depth=EVAL_DEPTH)
            calculate=False            
        clock.tick(15)
        drawboard(game.board,screen,game,validmove,seqsq,current_eval)
        p.display.flip()

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
    max_cp=1000
    cp=int(max(-max_cp,min(max_cp,current_eval)))
    white_height=(cp+max_cp)*height//(2*max_cp)
    p.draw.rect(screen,p.Color('white'),p.Rect(width,0,bar_width,white_height))
    p.draw.rect(screen,p.Color('black'),p.Rect(width,white_height,bar_width,height))
    p.draw.rect(screen,p.Color('gray'),p.Rect(width,0,bar_width,height),1)
    try:
        font=p.font.SysFont(None,16)
        txt=("+" if current_eval>=0 else "")+str(round(current_eval/100.0,2))
        text_surf=font.render(txt,True,p.Color('blue'))
        screen.blit(text_surf,(width+5,5))
    except Exception:
        pass

if __name__=="__main__":
    main()


