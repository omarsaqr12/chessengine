# this is responisble for storing the current state of the game ie the moves that were played till now. I will also be responsible for checking the validity of the moves, rules like the 50 move rule, and enable the user to takeback a move
class gameState():
    def __init__(self):
        self.whitetomove=True
        self.movelog=[]
        self.funcmove={'p':self.getPawnMoves,'r':self.getrockmoves,'q':self.getqueenmoves,'k':self.getkingmoves,'b':self.getbishopmoves,'n':self.getknightmoves}
        self.board=[
["br","bb","bn","bq","bk","bn","bb","br"],
["bp","bp","bp","bp","bp","bp","bp","bp"],
["??","??","??","??","??","??","??","??"], 
["??","??","??","??","??","??","??","??"], 
["??","??","??","??","??","??","??","??"], 
["??","??","??","??","??","??","??","??"], 
["wp","wp","wp","wp","wp","wp","wp","wp"], 
["wr","wb","wn","wq","wk","wn","wb","wr"]                   
        ]

    def makemove(self,movin):
      self.board[movin.startrow][movin.startcol]="??"
      self.board[movin.endrow][movin.endcol]=movin.piecemovec
      self.movelog.append(movin)
      self.whitetomove=not self.whitetomove
    def undo_move(self):
        if(len(self.movelog)!=0):
            movin=self.movelog.pop()
            self.board[movin.startrow][movin.startcol]=movin.piecemovec
            self.board[movin.endrow][movin.endcol]=movin.picecaptured
            self.whitetomove=not self.whitetomove
    def validmoves(self):
        return self.getallmoves()
    def getallmoves(self):
        move=[]
        for r in range(8):
            for c in range(8):
                det=self.board[r][c][0]
                p=self.board[r][c][1]
                if(det=='w'and self.whitetomove or (det=='b' and not self.whitetomove)):
                    self.funcmove[p](r,c,move)
                    
        return move
    def getPawnMoves(self,r,c,move):
        if self.whitetomove:
            if self.board[r][c][0]=='w':
                if r-1>=0 and self.board[r-1][c][1]=='?':
                   move.append(moving((r,c),(r-1,c),self.board))
                   if r==6 and self.board[r-2][c][1]=='?':
                       move.append(moving((r,c),(r-2,c),self.board))
                if r-1>=0 and c-1>=0 and self.board[r-1][c-1][0]=='b':
                    move.append(moving((r,c),(r-1,c-1),self.board))
                if r-1>=0 and c+1<=7 and self.board[r-1][c+1][0]=='b':
                    move.append(moving((r,c),(r-1,c+1),self.board))
        if not self.whitetomove:
            if self.board[r][c][0]=='b':
                if r+1<=7 and self.board[r+1][c][1]=='?':
                   move.append(moving((r,c),(r+1,c),self.board))
                   if r==1 and self.board[r+2][c][1]=='?':
                       move.append(moving((r,c),(r+2,c),self.board))
                if r+1<=7 and c-1>=0 and self.board[r+1][c-1][0]=='w':
                    move.append(moving((r,c),(r+1,c-1),self.board))
                if r+1<=7 and c+1<=7 and self.board[r+1][c+1][0]=='w':
                    move.append(moving((r,c),(r+1,c+1),self.board))

                  
    def getrockmoves(self,r,c,move):
        directions=[(1,0),(0,1),(-1,0),(0,-1)]
        enemy='b' if (self.whitetomove and self.board[r][c][0]=='w') else 'w'
        for d in directions:
            startrow=r
            startcol=c
            while startrow>=0 and startrow<=7 and startcol>=0 and startcol<=7:
                startrow+=d[0]
                startcol+=d[1]
                if startrow>=0 and startrow<=7 and startcol>=0 and startcol<=7:
                    if self.board[startrow][startcol][0]==enemy:
                        move.append(moving((r,c),(startrow,startcol),self.board)) 
                        break
                    elif self.board[startrow][startcol][0]=='?':
                        move.append(moving((r,c),(startrow,startcol),self.board))
                    else: break

            
    def getbishopmoves(self,r,c,move):
        directions=[(1,1),(1,-1),(-1,1),(-1,-1)]
        enemy='b' if (self.whitetomove and self.board[r][c][0]=='w') else 'w'
        for d in directions:
            startrow=r
            startcol=c
            while startrow>=0 and startrow<=7 and startcol>=0 and startcol<=7:
                startrow+=d[0]
                startcol+=d[1]
                if startrow>=0 and startrow<=7 and startcol>=0 and startcol<=7:
                    if self.board[startrow][startcol][0]==enemy:
                        move.append(moving((r,c),(startrow,startcol),self.board)) 
                        break
                    elif self.board[startrow][startcol][0]=='?':
                        move.append(moving((r,c),(startrow,startcol),self.board))
                    else: break

                    
                
    def getkingmoves(self,r,c,move):
        if self.whitetomove:
            if self.board[r][c][0]=='w':
                if self.board[r][c+1][0]!='w' and c+1<=7:
                    move.append(moving((r,c),(r,c+1),self.board))
                if self.board[r][c-1][0]!='w'and c-1>=0:
                    move.append(moving((r,c),(r,c+1),self.board))
                if r+1<=7:
                    if self.board[r+1][c][0]!='w':
                        move.append(moving((r,c),(r+1,c),self.board))
                    if c-1>=0 and self.board[r+1][c-1][0]!='w':
                        move.append(moving((r,c),(r+1,c-1),self.board))
                    if c+1<=7 and self.board[r+1][c+1][0]!='w':
                        move.append(moving((r,c),(r+1,c+1),self.board))  
                if r-1>=0:
                    if self.board[r-1][c][0]!='w':
                        move.append(moving((r,c),(r-1,c),self.board))
                    if c-1>=0 and self.board[r-1][c-1][0]!='w':
                        move.append(moving((r,c),(r-1,c-1),self.board))
                    if c+1<=7 and self.board[r-1][c+1][0]!='w':
                        move.append(moving((r,c),(r-1,c+1),self.board)) 
        if not self.whitetomove:
            if self.board[r][c][0]=='b':
                if self.board[r][c+1][0]!='b' and c+1<=7:
                    move.append(moving((r,c),(r,c+1),self.board))
                if self.board[r][c-1][0]!='b'and c-1>=0:
                    move.append(moving((r,c),(r,c+1),self.board))
                if r+1<=7:
                    if self.board[r+1][c][0]!='b':
                        move.append(moving((r,c),(r+1,c),self.board))
                    if c-1>=0 and self.board[r+1][c-1][0]!='b':
                        move.append(moving((r,c),(r+1,c-1),self.board))
                    if c+1<=7 and self.board[r+1][c+1][0]!='b':
                        move.append(moving((r,c),(r+1,c+1),self.board))  
                if r-1>=0:
                    if self.board[r-1][c][0]!='b':
                        move.append(moving((r,c),(r-1,c),self.board))
                    if c-1>=0 and self.board[r-1][c-1][0]!='b':
                        move.append(moving((r,c),(r-1,c-1),self.board))
                    if c+1<=7 and self.board[r-1][c+1][0]!='b':
                        move.append(moving((r,c),(r-1,c+1),self.board))                
    def getqueenmoves(self,r,c,move):
        directions=[(1,0),(0,1),(-1,0),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
        enemy='b' if (self.whitetomove and self.board[r][c][0]=='w') else 'w'
        for d in directions:
            startrow=r
            startcol=c
            while startrow>=0 and startrow<=7 and startcol>=0 and startcol<=7:
                startrow+=d[0]
                startcol+=d[1]
                if startrow>=0 and startrow<=7 and startcol>=0 and startcol<=7:
                    if self.board[startrow][startcol][0]==enemy:
                        move.append(moving((r,c),(startrow,startcol),self.board)) 
                        break
                    elif self.board[startrow][startcol][0]=='?':
                        move.append(moving((r,c),(startrow,startcol),self.board))
                    else: break
         
    def getknightmoves(self,r,c,move):
        directions=[(1,2),(1,-2),(2,1),(2,-1),(-2,1),(-2,-1),(-1,2),(-1,-2)]
        enemy='b' if (self.whitetomove and self.board[r][c][0]=='w') else 'w'
        for d in directions:
            startrow=r
            startcol=c
            
            startrow+=d[0]
            startcol+=d[1]
            if startrow>=0 and startrow<=7 and startcol>=0 and startcol<=7:
                if self.board[startrow][startcol][0]==enemy:
                    move.append(moving((r,c),(startrow,startcol),self.board)) 
                elif self.board[startrow][startcol][0]=='?':
                        move.append(moving((r,c),(startrow,startcol),self.board))
         
             

class moving():
        
    files2col={"a":0,"b":1,"c":2,"d":3,"e":4,"f":5,"g":6,"h":7}
    col2file={v:k for k,v in files2col.items()}
    rank2row={"8":0,"7":1,"6":2,"5":3,"4":4,"3":5,"2":6,"1":7}
    row2rank={v:k for k,v in rank2row.items()}

    def __init__(self,startsq,endsq,board):
        self.startrow=int(startsq[0])
        self.startcol=int(startsq[1])
        self.endrow=int(endsq[0])
        self.endcol=int(endsq[1])
        self.piecemovec=board[self.startrow][self.startcol]
        self.picecaptured=board[self.endrow][self.endcol]
        self.moveid=1000*self.startrow+100*self.startcol+10*self.endrow+self.endcol
        print(self.getnotation())
    def __eq__(self, object):
        if(isinstance(object,moving)):
            return object.moveid==self.moveid
        



    def getnotation(self):
        return self.getrankfile(self.startrow,self.startcol)+self.getrankfile(self.endrow,self.endcol)
    def getrankfile(self,r,c):
        return self.col2file[c]+self.row2rank[r]
    

