import numpy as np
from scipy.interpolate import interp1d 
def trans_back(x,y,trans):
    x = (x/trans[0][1])+trans[0][0]
    y = (y/trans[1][1])+trans[1][0]
    return x,y


def InitBeads(Guess,f,nBeads):
    nGuess = len(Guess)
    ds = np.linspace(0,1,nGuess)
    ds[0] = 0

    if (np.max(Guess[:,0]) > 5):
        for bead in Guess:
            if bead[0] > 5:
                bead[0] = 4.0
    if (np.max(Guess[:,1]) > 5):
        for bead in Guess:
            if bead[1] > 5:
                bead[1] = 4.0
    if (np.min(Guess[:,0]) < 0):
        for bead in Guess:
            if bead[0] < 0:
                bead[0] = 1.0

    if (np.min(Guess[:,1]) < 0):
        for bead in Guess:
            if bead[1] < 0:
                bead[1] = 1.0

    for i in range(1,nGuess):
        ds[i] = ((Guess[i][0]-Guess[i-1][0])**2+(Guess[i][1]-Guess[i-1][1])**2)**0.5
    
    Sum = 0
    ds_cum= list(range(nGuess))
    for i in range(nGuess):
        Sum = Sum + ds[i]
        ds_cum[i] = Sum 
	
    DS = list(range(nGuess))
    for i in range(len(ds_cum)):
        DS[i] = ds_cum[i]/Sum

    h = list(range(nBeads))
    for i in range(nBeads):
        h[i] = h[i]/float(nBeads-1)

    x = list(range(nGuess))
    y = list(range(nGuess))
    for i in range(nGuess):
        x[i] = Guess[i][0]
        y[i] = Guess[i][1]

    interX = interp1d(DS,x,kind='slinear')
    interY = interp1d(DS,y,kind='slinear')

    S_new = list(range(nBeads))

    X_new = interX(h)
    Y_new = interY(h)
    Z_new = f(X_new,Y_new)
    S_new = np.column_stack((X_new,Y_new))

	
    return np.column_stack((S_new,Z_new))

def grad(beads,f):
    dx = 0.01
    dy = 0.01
    grad_x = (f(beads[:,0]-dx,beads[:,1])-beads[:,2])/dx
    grad_y = (f(beads[:,0],beads[:,1]-dy)-beads[:,2])/dy
    return grad_x,grad_y

def walkdown(beads,step,f):
    nbeads = len(beads)
    gradientX, gradientY =  grad(beads,f)
    factorX = 1.0
    factorY = 1.0
    if (max(gradientX*step) > 0.2): factorX = 0.2/(max(gradientX*step))
    if (max(gradientY*step) > 0.2): factorY = 0.2/(max(gradientY*step))
    beads[:,0] = beads[:,0] + gradientX*step*factorX
    beads[:,1] = beads[:,1] + gradientY*step*factorY
    if (np.max(beads[:,0]) > 5):
        for bead in beads:
            if bead[0] > 5:
                bead[0] = 4.0
    if (np.max(beads[:,1]) > 5):
        for bead in beads:
            if bead[1] > 5:
                bead[1] = 4.0
    if (np.min(beads[:,0]) < 0):
        for bead in beads:
            if bead[0] < 0:
                bead[0] = 1.0

    if (np.min(beads[:,1]) < 0):
        for bead in beads:
            if bead[1] < 0:
                bead[1] = 1.0

    beads[:,2] = f(beads[:,0],beads[:,1])
    scale = 1
    if (factorX < 1 or factorY < 1): scale = 0.9
    if (factorX < 0.5 or factorY < 0.5): scale = 0.7
    if (factorX < 0.1 or factorY < 0.1): scale = 0.3
    if (factorX < 0.01 or factorY < 0.01): scale = 0.1
    if (factorX < 0.001 or factorY < 0.001): scale = 0.01
    if (factorX < 0.0001 or factorY < 0.0001 ): scale = 0.001
    if (factorX < 0.00001 or factorY < 0.00001) : scale = 0.0001

    return beads,scale

def redist(beads,f):
    nbeads = len(beads)
    ds = np.linspace(0,1,nbeads)
    ds[0] = 0
    for i in range(1,nbeads):
        ds[i] = ((beads[i][0]-beads[i-1][0])**2+(beads[i][1]-beads[i-1][1])**2)**0.5
    
    Sum = 0
    ds_cum= list(range(nbeads))
    for i in range(nbeads):
        Sum = Sum + ds[i]
        ds_cum[i] = Sum 
	
    DS = list(range(nbeads))
    for i in range(len(ds_cum)):
        DS[i] = ds_cum[i]/Sum

    h = list(range(nbeads))
    for i in range(nbeads):
        h[i] = h[i]/float(nbeads-1)

    x = list(range(nbeads))
    y = list(range(nbeads))
    for i in range(nbeads):
        x[i] = beads[i][0]
        y[i] = beads[i][1]

    interX = interp1d(DS,x,kind='slinear')
    interY = interp1d(DS,y,kind='slinear')

    S_new = list(range(nbeads))

    X_new = interX(h)
    Y_new = interY(h)
    Z_new = f(X_new,Y_new)
    S_new = np.column_stack((X_new,Y_new))

    return np.column_stack((S_new,Z_new))

def calcDiff(beads,beads2):
    nbeads = len(beads)
    Sum = np.sum((beads[:,0]-beads2[:,0])**2+(beads[:,1]-beads2[:,1])**2)/nbeads
    diff = np.sqrt(Sum)
    return diff