import numpy as np
import random
import math
import go
import bisect
import os
from copy import *
import matplotlib as mpl
mpl.use("agg")
import matplotlib.pyplot as plt
import os
from copy import *
import results as re
if not os.path.exists("./Graphs"):
    os.makedirs("./Graphs")

if not os.path.exists("./Data"):
    os.makedirs("./Data")


def sigmoid(z):
    return 1.0/(1.0+np.exp(-z))

def cgf(weights):
    tot=sum(weights)
    inters=[]
    cumsum=0
    for w in weights:
        cumsum+=w/tot
        inters.append(cumsum)
    return inters

def cgfpick(pop,cgfv):
    if set(cgfv)=={0}:
        print("No distribution.")
        return pop[0]
    return pop[bisect.bisect(cgfv,random.random())]


class Network_Go(object):
    def __init__(self,struc,dim):#struc=list of # of neurons in each layer
        struc=[dim**2]+struc+[dim**2]
        self.struc=struc
        self.dim=dim
        self.weight=[np.random.randn(j,k) for j,k in zip(struc[1:],struc[:-1])]
        self.bias=[np.random.randn(j,1) for j in struc[1:]]
    def mk_move(self,layer,player):
        board_state=np.array([[.5 if x==-1 else 1 if x==player else 0 for x in layer]]).T
        layer=board_state
        for weight,bias in zip(self.weight,self.bias):
            layer=sigmoid(np.dot(weight,layer)+bias)
        return max([(i,ef) for i,ei,ef in zip(range(self.dim**2),board_state[:,0],layer[:,0]) if ei==.5],key=lambda f:f[1])[0]
    def data(self):
        return deepcopy({"struc":self.struc,"dim":self.dim,"weight":self.weight,"bias":self.bias,})
    def setData(self,ddata):
        self.struc=ddata["struc"]
        self.dim=ddata["dim"]
        self.weight=ddata["weight"]
        self.bias=ddata["bias"]
        return self

class Evolution():
    def __init__(self,net_num,struc,dim,mut_rate):
        if net_num%2:
            print("Net must be even")
            return "Error"
        self.dim=dim
        self.mut_rate=mut_rate
        self.nets=[Network_Go(struc,dim) for i in range(net_num)]
        self.g=go.game(dim)
        self.fits=[]
        
    def inter_comp(self,matches=-1):
        random.shuffle(self.nets)
        a=self.nets[-1]
        fitness=np.zeros([max([matches,len(self.nets)])])
        for i,b in enumerate(self.nets):
            self.g.reset()
            res=go.play_go(ais=[a,b],gg=self.g,printb=False)
            fitness[i]+=res[1]
            fitness[i-1]+=res[0]
            a=b
            if i==matches: break
        print("average fit:",sum(fitness)/len(fitness),"fitness:",fitness)
        self.fits.append(sum(fitness)/len(fitness))

        cgfit,new_nets=cgf(fitness),[]
        for i in self.nets:
            new_nets.append(self.reproduce(*[cgfpick(self.nets,cgfit) for i in (0,1)]))
        for net,nnet in zip(self.nets,new_nets):
            net.weights=nnet[0]
            net.bias=nnet[1]

    def vs_comp(self,vs_func,matches=-1):
        random.shuffle(self.nets)
        fitness=np.zeros([max([matches,len(self.nets)])])
        for i,net in enumerate(self.nets):
            self.g.reset()
            res=go.play_go(ais=[net,vs_func],gg=self.g,printb=False)
            fitness[i]+=res[0]
            if i==matches: break
        print("average fit:",sum(fitness)/len(fitness),"fitness:",fitness)
        self.fits.append(sum(fitness)/len(fitness))

        cgfit,new_nets=cgf(fitness),[]
        for i in range(len(self.nets)//2):
            new_nets.extend(self.reproduce(*[cgfpick(self.nets,cgfit) for i in (0,1)]))
        for net,nnet in zip(self.nets,new_nets):
            net.weights=nnet[0]
            net.bias=nnet[1]


    def reproduce(self,net1,net2):
        wnews,bnews=[[],[]],[[],[]]
        for w1,w2 in zip(net1.weight,net2.weight):
            if random.getrandbits(1):
                s=w1.shape
                choice=[[random.getrandbits(1) for j in range(s[1])] for i in range(s[0])]
                wnews[0].append(np.array(
                    [[np.random.randn() if random.random()<self.mut_rate 
                    else w1 if c else w2 
                    for w1,w2,c in zip(w1r,w2r,cr)] 
                    for w1r,w2r,cr in zip(w1,w2,choice)]))
                wnews[1].append(np.array(
                    [[np.random.randn() if random.random()<self.mut_rate 
                    else w1 if not c else w2 
                    for w1,w2,c in zip(w1r,w2r,cr)] 
                    for w1r,w2r,cr in zip(w1,w2,choice)]))
            else:
                wnews[0].append(w1)
                wnews[1].append(w2)
        for b1,b2 in zip(net1.bias,net2.bias):
            if random.getrandbits(1):
                choice=[random.getrandbits(1) for i in range(b1.shape[0])]
                bnews[0].append(np.array(
                    [[np.random.randn() if random.random()<self.mut_rate 
                    else b1r[0] if c else b2r[0]] 
                    for b1r,b2r,c in zip(b1,b2,choice)]))
                bnews[1].append(np.array(
                    [[np.random.randn() if random.random()<self.mut_rate 
                    else b1r[0] if not c else b2r[0]] 
                    for b1r,b2r,c in zip(b1,b2,choice)]))
            else:
                bnews[0].append(b1)
                bnews[1].append(b2)
        
        
        
        return [(wnews[0],bnews[0]),(wnews[1],bnews[1])]
    
    def save(self,fname=None,gname=""):
        if not fname:
            i=0
            while os.path.exists("./Data/nets"+str(i)):
                i+=1
            fname="nets"+str(i)
        f=open("./Data/"+fname,"w")
        f.write(str([[net.data() for net in self.nets],self.fits,gname]).replace("array","np.array"))
        f.close()
        return fname
    
    def setNets(self,fname):
        f=open("./Data/"+fname,"r")
        ddatas=eval(f.read())
        f.close()
        print("Imported fits:",ddatas[1])
        for net,newnet in zip(self.nets,ddata[0]):
            net.setData(newnet)

struc,dim=[1000,1000],10
#struc,dim=[27,27,27],3
np.random.seed(42)
vs_ai=Network_Go([dim**2],dim)
np.random.seed()
            
def __main__():
    global vs_ai
    evo=Evolution(20,struc,dim,.01)
    fits=[]
    #evo.reproduce(evo.nets[0],evo.nets[1],.1)
    def multepoch(epochs,num):
        global vs_ai,aspects
        for j in range(epochs):
            for i in range(num):
                evo.vs_comp(vs_ai)
                #evo.inter_comp()
            vs_ai=evo.nets[0]
        aspects=(num,epochs)
        fits.extend([evo.fits[i*num:(i+1)*num] for i in range(epochs)])
    def singepoch(num):
        global vs_ai,aspects
        for i in range(num):
            evo.vs_comp(vs_ai)
            #evo.inter_comp()
        aspects=(num,)
        print(evo.fits)
    #multepoch(200)
    multepoch(3,100)
    #singepoch(100)
    print("fits:",fits)
        
    def datatest():
        global name
        f=open("./Data/"+name,"r")
        ddatas=eval(f.read())
        f.close()
        test=Network_Go([1],1)
        test.setData(ddatas[0][0])
        
    
    

    
    gname="Fitness Evolution of a {} per\nEpoch Population on ({}: {} by {})".format(aspects[0],struc,dim,dim)
    if fits:
        evo.fits=deepcopy(fits)
    else:
        fits=deepcopy(evo.fits)
    name=evo.save(gname=gname)
    

    re.graph(gname,name,fits)


if __name__=="__main__":
    __main__()
    
    




