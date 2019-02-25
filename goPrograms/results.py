import matplotlib as mpl
mpl.use("agg")
import matplotlib.pyplot as plt
import os
import numpy as np
import go
import networkGoGA as ng
if not os.path.exists("./Graphs"):
    os.makedirs("./Graphs")

def __main__():



    name=input("Input a name for some nets: ")
    
    f=open("./Data/"+name,"r")
    ddatas=eval(f.read())
    f.close()
    
    nets=ddatas[0]
    fits=ddatas[1]
    if len(ddatas)>2: gname=ddatas[2]

    if False:
        fig=plt.figure()
        plt.plot(range(len(fits)),fits)
        fig.savefig("./Graphs/fitnesses")
    
    
    def play():
        dim=4
        g=go.game(dim)
        net=ng.Network_Go([1],dim)
        np.random.seed(42)
        vs_ai=ng.Network_Go([dim**2],dim)
        np.random.seed()
        #vs_ai=ng.Network_Go([dim**2],dim)


        for ai_data in ddatas[0]:
            g.reset()
            net.setData(ai_data)

            ais=[net,vs_ai]

            #go.play_go(humans=1,ais=[ais[0]],gg=g,write=False)
            go.play_go(ais=ais,gg=g,write=False)
    
    
    graph(gname,name,fits)
        
    
def graph(gname,name,fits):
    colors="rgbcmyk"
    if type(fits[0])==list:
        fig,axes=plt.subplots(1,len(fits),figsize=(4*len(fits),4),sharey=True)
        cumul=0
        for i,fit,ax in zip(range(len(fits)),fits,axes):
            ax.plot(range(cumul,cumul+len(fit)),fit,colors[i%7])
            ax.set_xlabel("Epoch {} (Gen)".format(i),fontsize=16)
            cumul+=len(fit)
        axes[0].set_ylabel("Fitness",fontsize=16)
        fig.suptitle(gname.replace("\n"," "),fontsize=18)
    else:
        fig=plt.figure()
        plt.plot(range(len(fits)),fits)
        plt.xlabel("Generation",fontsize=16)
        plt.ylabel("Fitness",fontsize=16)
        plt.title(gname,fontsize=18)

    fig.tight_layout(rect=[0,0.03,1,.95])
    fig.savefig("./Graphs/"+name)


if __name__=="__main__":
    __main__()
