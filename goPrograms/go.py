import numpy as np
from copy import deepcopy
import networkGoGA as ng
from functools import reduce
import os
if not os.path.exists("./Data"):
    os.makedirs("./Data")

def mag(vec):
    return sum([el**2 for el in vec])**.5
def dif(vec1,vec2):
    dif=abs(mag([a-b for a,b in zip(vec1,vec2)]))
    print("between {},{}: dif={}".format(vec1,vec2,dif))
    return dif




def near(pt1,pt2):
    return any(pt1[i]==pt2[i] and abs(pt1[1-i]-pt2[1-i])==1 for i in (0,1))
def far(pt1,pt2):
    return abs(pt1[0]-pt2[0])>1 or abs(pt1[1]-pt2[1])>1
def closed(pt1,pt2):
    return all(abs(pt1[i]-pt2[i])<2 for i in (0,1))
def nbh(loc):
    return [(loc[0]+a,loc[1]+b) for a in (0,-1,1) for b in (0,-1,1)][1:]
def nbhp(loc):
    return [(loc[0]+1,loc[1]),(loc[0]-1,loc[1]),(loc[0],loc[1]+1),(loc[0],loc[1]-1)]

class game():
    def __init__(self,dim):
        self.dim=dim
        self.reset()

        self.fname="goGame"
        i=0
        while os.path.exists("./Data/"+self.fname+str(i)):
            i+=1
        self.fname=self.fname+str(i)

        self.leftright=[(i,e) for i in range(dim) for e in (-1,dim)]
        np.set_printoptions(linewidth=150)
        
        sides=[[(0,i),(dim-1,i),(i,0),(i,dim-1)] for i in range(dim)]
        sidec=[[(-1,i),(dim,i),(i,-1),(i,dim)] for i in range(dim)]
        self.sides=[[sides[i][e] for i in range(dim)] for e in range(4)]
        self.sidec=[[sidec[i][e] for i in range(dim)] for e in range(4)]

        self.prevdata=self.data()

    def display(self):
        maxlen=str(len(str(self.dim-1)))
        labelsh=[["-"]]+[[str(i)] for i in range(self.dim)]
        labelsv=[str(i) for i in range(self.dim)]
        disp_board=np.hstack([labelsh,np.vstack([labelsv,self.board])])
        for line in [[("{:>"+maxlen+"}").format(x) for x in line] for line in disp_board]:
            print(line)

        
    def go_back(self):
        self.captures=self.prevdata["captures"]
        self.board=self.prevdata["board"]
        self.lines=self.prevdata["lines"]
        self.covered=self.prevdata["covered"]
        self.turn=self.prevdata["turn"]

    def reset(self):
        self.board=np.full([self.dim,self.dim],"-",dtype="object")
        self.lines=[[],[]]#[[[xy1,xy2,...],line2,...],[]]
        self.captures=[0,0]
        self.covered=[[],[0,0]]#[]==pieces on board; [0,0]==1-territories for each player
        self.end=False
        self.turn=0
        
        
        print("\n"*10+"----RESETTING----"+"\n"*10)

    def board_tolist(self):
        return [-1 if el=="-" else 1 if el=="1" else 0 for el in reduce(lambda x,y:x+y,self.board.tolist())]
    
    def mk_score(self):
        self.pieces=[(self.turn+1)//2-self.captures[1],self.turn//2-self.captures[0]]
        self.score=[p+t+c for p,t,c in zip(self.pieces,self.covered[1],self.captures)]
        return self.score
        
        
    def save(self):
        self.fdata=self.data()
        self.fdata.update({"dim":self.dim,"fname":self.fname})
        f=open("./Data/"+self.fname,"w")
        f.write(str(self.fdata).replace("array","np.array"))
        f.close()
        return self.fdata
        
    def setGame(self,ddata):
        self.__init__(ddata["dim"])
        self.captures=ddata["captures"]
        self.board=ddata["board"]
        self.lines=ddata["lines"]
        self.covered=ddata["covered"]
        self.turn=ddata["turn"]
        self.fname=ddata["fname"]

    
    def data(self):
        return {"captures":deepcopy(self.captures),"board":deepcopy(self.board),"lines":deepcopy(self.lines),"covered":deepcopy(self.covered),"turn":self.turn}
        
    def inside(self,pt):
        sides=[]
        for i in range(2):
            for j,e in enumerate((0,self.dim-1)):
                if pt[i]==e:
                    sides.append(2*i+j)
        return sides
    
    def find_cats(self,line):
        sort=sorted(line,key=lambda yx:yx[0])
        y=sort[0][0]
        cats=[[sort[0]]]
        for yx in sort[1:]:
            if yx[0]==y:
                for i,yxi in enumerate(cats[-1]+[yx]):
                    if yx[1]<yxi[1]:
                        break
                cats[-1].insert(i,yx)
            else:
                y=yx[0]
                cats.append([yx])
        return cats
        
    def find_territory(self,line):
        cats=self.find_cats(line)
        #print("cats:",cats)
        ters=[]
        merges=[]
        checkter=[]
        for cat in cats:
            newct=[]
            #print("newct:",newct,"checkter:",checkter)
            a=cat[0]
            y0=a[0]
            for b in cat[1:]:
                #print("checking:ab:",a,b)
                if b[1]-a[1]>1:
                    new=[(y0,i) for i in range(a[1]+1,b[1])]
                    its=[]
                    for x1,x2,it in checkter:
                        if it not in its and b[1]-x1>0 and x2-a[1]>0:
                            #print("In this one:",(x1,x2,it))
                            its.append(it)
                    if its:
                        #print("\nters:",ters,"its:",its)
                        if len(its)>1:
                            #print("beginning update of merges:",merges)
                            removal=[]
                            inmerge=False
                            for j,merge in enumerate(merges):
                                #print("checking this merge:",merge)
                                if any( i in its for i in merge):
                                    #print("found something! inmerge:",inmerge,"merge:",merge)
                                    if inmerge:
                                        #print("removing",merge,"updating inmerge:",inmerge)
                                        inmerge.update(merge)
                                        removal.append(j)
                                    else:
                                        #print("updating this merge:",merge,"with this its:",its)
                                        merge.update(its)
                                        inmerge=merge
                            if inmerge: merges=[el for j,el in enumerate(merges) if j not in removal]
                            else: merges.append(set(its))
                        #print("merge after update:",merges)
                        it=its[0]
                        ters[it].extend(new)
                    else:
                        #print("\nmade a ter!",new)
                        ters.append(new)
                        it=len(ters)-1
                        merges.append(set([it]))
                    newct.append((new[0][1],new[-1][1],it))
                a=b
            checkter=newct
        #print("\n\nmerges final:",merges)
        oldters=ters
        ters=[reduce(lambda x,y:x+y,[ter for i,ter in enumerate(oldters) if i in merge]) for merge in merges]
        
        #print("newter:",ters)
        #print("terlens:",[len(ter) for ter in ters])
        pmax=self.dim**2//2
        for ter in ters:
            #print("len check of ter:",ter)
            if len(ter)>pmax:
                ters.remove(ter)
                break
        #print("\nFinal ters:",ters)
        #input()
        pieces_in=[]
        for ter in ters:
            pieces_in.append(len(ter))
            for pt in ter:
                if self.board[pt]!="-":
                    pieces_in[-1]-=1
        return (ters,pieces_in)
        

    def move_eval(self,loc,player,write=True):#players 0,1
        #self.display()
        ##initialization
        self.prevdata=self.data()
        self.turn+=1
        
        ##error inputs
        if any(el>self.dim-1 or el<0 for el in loc):
            print("Out of bounds.")
            return "Error"
        loc=tuple(loc)
        if self.board[loc]!="-":
            print("Error: piece already here.")
            return "Error"
        
        ##changing board state
        self.board[loc]=str(player)
        self.covered[0].append(loc)
        
        ##which groups border loc
        in_groups=set()
        nbh_l=nbh(loc)
        for nb in nbh_l:
            for i,line in enumerate(self.lines[player]):
                if nb in line[0]:
                    in_groups.update([i])
        
        if not in_groups:
            self.lines[player].append([[loc],[],[]])
        else:
            keys=list(in_groups)
            i_cat=keys[0]
            
            line=self.lines[player][i_cat]
            lin0=line[0]
            if len(in_groups)>1:
                for linj in [self.lines[player][i] for i in keys[1:]]:
                    line[0].extend(linj[0])
                    line[1].extend(linj[1])
                    line[2].extend(linj[2])
            line[0].append(loc)
            
            #print("Checking for enc")
            
            ##updating territory if necessary:
            pts=[nb for nb in nbh_l if nb in lin0[:-1]]
            loc_on=self.inside(loc)
            #print("loc_on:",loc_on)
            enclosed=False
            
            
            if self.inside(loc) and any(self.inside(pt) for pt in lin0[:-1]):
                enclosed=True
            else:
                for i,pta in enumerate(pts):#checking for enclosure or boundary
                    for ptb in pts[i+1:]:
                        #print("incheck")
                        if far(pta,ptb) or loc_on:
                            enclosed=True
                            break #only check territory once
                    if enclosed: break
            if enclosed:
                #print("enclosed!")
                line[1:]=self.find_territory(lin0+self.leftright)
            self.lines[player]=[lin for i,lin in enumerate(self.lines[player]) if i not in keys[1:]]
            
        ##exiting in_group statements
            
        ##checking for eaten data
        
        some_eaten=False
        self.covered[1]=[0,0]
        updatethese=set()
        for play in (player,1-player):
            for lin in self.lines[play]:
                if len(lin[0])>self.dim**2:
                    print("Problem detected!")
                    print("line:",lin)
                    self.display()
                    print(self.lines)
                    input()
                print("checking if line has eaten:",lin)
                for i,lin1i in enumerate(lin[1]):#lin[1]=ters; lin[2]=pieces
                    if loc in lin1i:
                        lin[2][i]-=1#if loc is in an existing territory: -1 from open spaces
                    if len(lin1i)==1:
                        self.covered[1][play]+=1
                    if (play==player or not some_eaten) and lin1i and not lin[2][i]:
                        for eaten in lin1i:
                            if self.board[eaten]==str(1-play):
                                some_eaten=True
                                self.captures[play]+=1
                                self.board[eaten]="-"
                                self.covered[0].remove(eaten)
                                lin[2][i]+=1 #resetting piece stat
                                for j,linj in enumerate(self.lines[1-play]):#checking what is eaten
                                    if eaten in linj[0]:
                                        linj[0].remove(eaten)
                                        updatethese.update({(1-play,j)})
                                        #if some piece is eaten from linj but it still exists, reupdate linj
                                        break #an eaten pt can only be in one linj[0]
        
        print("\n\n\nUPDATING LINES AFTER MEAL\n\n\n")
        for p,j in updatethese:
            linj=self.lines[p][j]
            if linj[0]:
                cats=self.find_cats(linj[0])
                lins=[]
                merges=[]
                checklin=[[],-2]
                for cat in cats:
                    print("checklin:",checklin)
                    a=cat[0]
                    ygroups=[[a]]
                    for b in cat[1:]:
                        print("consec: a:{}; b:{}".format(a,b))
                        if b[1]-a[1]==1:
                            ygroups[-1].append(b)
                        else:
                            ygroups.append([b])
                        a=b
                    print("ygroups:",ygroups)
                    newcl=[]
                    for ygp in ygroups:
                        its=[]
                        if ygp[0][0]-checklin[1]==1:
                            print("checking:ygp:",ygp)
                            for x1,x2,it in checklin[0]:
                                print("vs: x1={} and x2={}".format(x1,x2))
                                if it not in its and ygp[-1][1]-x1+1>=0 and x2-ygp[0][1]+1>=0:
                                    print("Neighboring this one:",(x1,x2,it))
                                    its.append(it)
                        if its:
                            print("\nlins:",lins,"its:",its)
                            if len(its)>1:
                                removal=[]
                                inmerge=False
                                for j,merge in enumerate(merges):
                                    if any(i in its for i in merge):
                                        if inmerge:
                                            inmerge.update(merge)
                                            removal.append(j)
                                        else:
                                            print("updating this merge:",merge,"with this its:",its)
                                            merge.update(its)
                                            inmerge=merge
                                            print("result merge:",merge)
                                if inmerge: merges=[el for j,el in enumerate(merges) if j not in removal]
                                else: merges.append(set(its))
                            it=its[0]
                            lins[it].extend(ygp)
                        else:
                            print("\nmade a lin!",ygp)
                            lins.append(ygp)
                            it=len(lins)-1
                            merges.append(set([it]))
                        newcl.append((ygp[0][1],ygp[-1][1],it))
                    checklin=[newcl,ygp[0][0]]
                
                oldlins=lins
                lins=[]
                print("\n\nmerges final:",merges)
                for merge in merges:
                    lins.append(reduce(lambda x,y:x+y,[lin for i,lin in enumerate(oldlins) if i in merge]))
                print("linsfinal:",lins)
                if len(lins)>1:
                    linj[0]=[]
                    for lin in lins:
                        self.lines[p].append([lin,*self.find_territory(lin+self.leftright)])
                else:
                    linj[1:]=self.find_territory(linj[0]+self.leftright)
                    
                    
        for p in (0,1):
            removal=[]
            for j,linj in enumerate(self.lines[p]):
                if not linj[0]:
                    removal.append(j)
            self.lines[p]=[el for i,el in enumerate(self.lines[p]) if i not in removal]
            
        print("\n\n\n\nFinal lines:",self.lines)
        #print("covered:",len(self.covered[0]))
        if write: self.save()
        if len(self.covered[0])+sum(self.covered[1])==self.dim**2:
            #print("Game Over.")
            self.end=True
            self.mk_score()
            return "End"
    

def list_to_latex(listy):
    return "{"+str(listy)[1:-1].replace(", ","&")+"}"

def play_go(humans=0,ais=[],dim=5,gg=None,printb=True,write=True):
    if humans+len(ais)!=2:
        print("Player error.")
        return "Error"
    if not gg:
        gg=game(dim)
    else:
        dim=gg.dim
    play=0
    move_loc=[0,0]

    stay=True
    while stay:
        if printb:
            gg.display()
            print(gg.lines)
            print("\nCaptured state:",gg.captures)
            print("covered:",gg.covered)
        if ais and play==0:
            board_initl=gg.board_tolist()
            move_locs=[]
            for ai in ais:
                move_locs.append(divmod(ai.mk_move(gg.board_tolist(),play),dim))
                move_res=gg.move_eval(move_locs[-1],play)
                if move_res=="End":
                    stay=False
                    break
                play=1-play
                #gg.display()
            if printb:
                print("ai time")
                print("Moves:",move_locs)
                gg.display()
                if len(ais)==2: input("Press enter to continue...")
            if gg.board_tolist()==board_initl or gg.turn>dim**2*4:
                print("Stalemate on turn {} vs max {}".format(gg.turn,dim**2*4))
                turn=stay=False
                return [el//2 for el in gg.mk_score()]
                #break
        if not stay: break
        if humans:
            turn=True
            #play=0
            print("Player {}'s turn:".format(play))
            for i in range(2):
                while True:
                    move_loc[i]=input("Move location "+"yx"[i]+": ")
                    if move_loc[i].isdigit():
                        move_loc[i]=int(move_loc[i])
                        break
                    elif move_loc[i]=="back":
                        print("Going back a turn...")
                        gg.go_back()
                        turn=False
                        break
                    elif move_loc[i]=="reset":
                        print("Resetting...")
                        gg.reset()
                        play=1
                        turn=False
                        break
                    elif move_loc[i]=="quit":
                        print("Quitting")
                        gg.save()
                        stay=turn=False
                        break
                    elif move_loc[i]=="tolist":
                        print(list_to_latex(gg.board_tolist()))
                    elif move_loc[i]=="save":
                        gg.save()
                        print("Saved to",gg.fname)
                if not turn: break
            if type(move_loc[0])==type(move_loc[1])==int:
                print("Player moving on:",move_loc)
                move_res=gg.move_eval(move_loc,play,write=write)
                if move_res=="Error":
                    print("Restarting turn.")
                    play=1-play
                if move_res=="End":
                    stay=False
                    break
            play=1-play
                    
    

            
    gg.mk_score()
    if printb:
        print("\n\nFinal State:")
        gg.display()
        print("Final score: {}\nPieces: {}\nTerritories: {}\nCaptures: {}".format(gg.score,
            gg.pieces,gg.covered[1],gg.captures))
    return gg.score


if __name__=="__main__":
    dim=10
    g=game(dim)
    ai1,ai2=[ng.Network_Go([100,100],dim) for i in range(2)]

    if False:
        f=open("./Data/bug01","r")
        saved=eval(f.read())
        f.close()
        g.setGame(saved)
        g.fname="example"
        dim=g.dim
    
    if False:
        
        f=open("./Data/nets4","r")
        data=eval(f.read())
        f.close()
        
        
        net=ng.Network_Go([1],1)
        net.setData(data[0][0])
        #ai1=net
    
    ais=[ai1,ai2]

    play_go(2,gg=g)
    #play_go(1,[ais[0]],dim=dim)
    #play_go(0,ais,gg=g,printb=False)
    print("\n\nFinal State:")
    g.display()






