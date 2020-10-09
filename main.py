import numpy as np
from scipy.interpolate import griddata,interp2d,SmoothBivariateSpline,CloughTocher2DInterpolator
import sys
from os import environ
from io import StringIO
import time
from copy import deepcopy
# PyQt5 
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication,QWidget,QGroupBox,QLabel
from PyQt5.QtWidgets import QPushButton,QTextBrowser,QFileDialog
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import QFile,Qt
# matplotlib
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
#import matplotlib.pyplot as plt


from Calc import *
## Global PES and MEP variables
PESdata = 0                # Original PES data provided by User [2D array, 3*N_points]
MaxValueInit = 1.0         # Maximum value of PES 
MinValueInit = 0.0         # Minimum value of PES 
xi = 0                     # Initial interpolated Grid data X 100 [Grid_data]
yi = 0                     # Initial interpolated Grid data Y 100 [Grid_data]
zi = 0                     # Initial interpolated Grid data Z 100 [Grid_data]
Guess_beads = 0            # initGuess Beads [2D array, 2*N_guessbeads]

stepsize=1.00                 # Optimize stepsize
max_iter=60                # maximum interation
nbeads=20                  # Number of beads

regul_scale = [[0,1],[0,1]] # regularization factors for X and Y.
xi_r = 0                     # Regularized interpolated Grid data X 100 [Grid_data]
yi_r = 0                     # Regularized interpolated Grid data Y 100 [Grid_data]
Guess_beads_r  = 0           # Regularized Beads [2D array, 2*N_guessbeads]

PES_f = None                     # Fitted function for PES

beads = None
## Matplotlib Canvas initialization
class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, constrained_layout=True)
        #plt.ion()
        self.axes = self.fig.add_subplot(1,1,1)
        super(MplCanvas, self).__init__(self.fig)
    def draw_beads(self,beads_x, beads_y):
        line = self.axes.plot(beads_x, beads_y,'o-',color='r',markersize=1.3,lw=1)
        #plt.pause(0.1)
        self.fig.canvas.flush_events()
        self.draw()
        line.pop(0).remove()

## Guess beads input Class

class GuessBox(QWidget):
    def __init__(self,CanvasIn,LableIn,BrowserIn):
        super(GuessBox,self).__init__()       
        loadUi("ui/GuessDia.ui",self)
        ## Initial Click events
        self.Click()
        self.Canvas = CanvasIn
        self.label2 = LableIn
        self.browser = BrowserIn

    def Click(self):
        self.ok.clicked.connect(self.okReadin)
        self.reset.clicked.connect(self.resetData)
    def okReadin(self):
        global Guess_beads
        text = self.data.toPlainText()
        f = StringIO(text)
        try:
            Guess_beads = np.loadtxt(f)
            if (len(Guess_beads) == 0):
                self.browser.append("No beads")
                return
            if Guess_beads.ndim == 1: 
                self.browser.append("At least 2 guess beads")
                return 
            self.Canvas.axes.plot(Guess_beads[:,0],Guess_beads[:,1],'o-',color='k')
            self.Canvas.draw()
            self.label2.setText("Guess finished")
        except:
            self.browser.append("Guess beads input format error")

        self.close()
    def resetData(self):
        self.data.clear()
    

class MainWindow(QWidget):
    cb = None
    def __init__(self):
        super(MainWindow,self).__init__()       
        loadUi("ui/main.ui",self)
        ## Initial Click events
        self.Click()

        ## Canvas define
        self.Canvas = MplCanvas(self.plotWindows, width=6, height=6, dpi=100)
        ## Initial Guess InputBox
        self.guessb = GuessBox(self.Canvas,self.label2,self.outBrowser)

        #toolbar = NavigationToolbar(self.Canvas,self.plotWindows)
        layout = QVBoxLayout()
        #layout.addWidget(toolbar)
        layout.addWidget(self.Canvas)
        self.plotWindows.setLayout(layout)

    def Click(self):
        self.openB.clicked.connect(self.readFile)
        self.Rgen.clicked.connect(self.plotReGen)
        self.Rset.clicked.connect(self.plotReset)
        self.run.clicked.connect(self.runMEPsearch)
        self.guessinp.clicked.connect(self.plotGuessDot)

    def readFile(self):
        global PESdata,MaxValueInit,MinValueInit
        fileName = QFileDialog.getOpenFileName(self, "Save", "./","File (*.dat *.txt)")
        if (len(fileName[0]) == 0): return
        self.outBrowser.append("Potential energy surface file selected:   "+fileName[0])

        self.label.setText("File loaded")
        self.PESfile = fileName
        PESfile = open(fileName[0],'r')
        # Process The Data
        PESdata = np.loadtxt(PESfile)
        maxD = np.max(PESdata[:,2])
        minD = np.min(PESdata[:,2])
        MaxValueInit = maxD
        MinValueInit = minD

        self.outBrowser.append(" \n==== Information of the surface ====")
        self.outBrowser.append(" Xrange:             "+str(round(np.min(PESdata[:,0]),4))\
                                           +" to "+str(round(np.max(PESdata[:,0]),4)))

        self.outBrowser.append(" Yrange:             "+str(round(np.min(PESdata[:,1]),4))\
                                           +" to "+str(round(np.max(PESdata[:,1]),4)))
        self.outBrowser.append(" Maximum Value:  "+str(round(maxD,4)))
        self.outBrowser.append(" Minimum Value:  "+str(round(minD,4)))
        self.outBrowser.append(" ========================")

        self.Vmax.setText(str(round(maxD,3)))
        self.Vmin.setText(str(round(minD,3)))
        self.Level.setText(str(24))
        self.plotPES_int()
        
    # Initial plot
    def plotPES_int(self):
        global PESdata,MaxValueInit,MinValueInit,xi,yi,zi,FuncInter
        if(self.cb != None ): self.cb.remove()
        self.Canvas.axes.clear()
        X_max = np.max(PESdata[:,0])
        X_min = np.min(PESdata[:,0])
        Y_max = np.max(PESdata[:,1])
        Y_min = np.min(PESdata[:,1])
        xi = np.linspace(X_min,X_max,100)
        yi = np.linspace(Y_min,Y_max,100)
        zi = griddata((PESdata[:,0],PESdata[:,1]),PESdata[:,2],
                        (xi[None,:],yi[:,None]),method='cubic')


        self.Canvas.axes.contour(xi,yi,zi,
                                levels=24,linewidths=0.5,colors='k')

        cf = self.Canvas.axes.contourf(xi,yi,zi,
                                    levels=140,cmap="bwr")
        # Get color bar
        self.cb = self.Canvas.axes.figure.colorbar(mappable=cf)
        self.Canvas.draw()

    # Regenerate plot
    def plotReGen(self):
        global PESdata,MaxValueInit,MinValueInit,xi,yi,zi
        self.cb.remove()
        self.Canvas.axes.clear()
        self.Canvas.draw()
        try:
            maxV = float(self.Vmax.text())
            minV = float(self.Vmin.text())
            level = int(self.Level.text())
        except:
            maxV = MaxValueInit
            minV = MinValueInit
            level = 12
            self.Vmax.setText(str(round(MaxValueInit,3)))
            self.Vmin.setText(str(round(MinValueInit,3)))
            self.Level.setText(str(12))
        Cmap = self.cmap.currentText()

        self.Canvas.axes.contour(
                xi,yi,zi,vmax=maxV,vmin=minV,
                linewidths=0.5,colors='k',levels=np.linspace(minV,maxV,level))

        cf = self.Canvas.axes.contourf(
                xi,yi,zi,vmax=maxV,vmin=minV,
                levels=np.linspace(minV,maxV,140),cmap=Cmap)

        self.cb = self.Canvas.axes.figure.colorbar(mappable=cf,boundaries=np.linspace(minV,maxV,140))
        self.Canvas.draw()

    # Plot Guess dot on Canvas
    def plotGuessDot(self):
        global Guess_beads,stepsize,max_iter,nbeads
        
        self.plotReGen()
        self.guessb.show()
        self.Nbeads.setText(str(20))
        
        stepsize = 3.0/((MaxValueInit-MinValueInit))
        max_iter = 60
        nbeads = 20

        self.Stepsize.setText(str(round(stepsize,3)))
        self.Maxiter.setText(str(80))
        #self.cb.remove()  

    def plotReset(self):
        self.Canvas.axes.clear()
        #self.cb.remove() 
        self.Canvas.draw()

    def runMEPsearch(self):
        global Guess_beads,stepsize,max_iter,nbeads,regul_scale,\
               xi_r,yi_r,Guess_beads_r,PES_f,beads
        ## Read MEP optimization options. 
        try:
            stepsize = float(self.Stepsize.text())
            max_iter = int(self.Maxiter.text())
            nbeads = int(self.Nbeads.text())
        except:
            stepsize = 3.0/((MaxValueInit-MinValueInit))
            max_iter = 80
            nbeads = 20
            self.Stepsize.setText(str(round(stepsize,3)))
            self.Maxiter.setText(str(max_iter))
            self.Nbeads.setText(str(80))
        ## Regularization data:
        self.outBrowser.append(" ================= \n Optimization start\n ================= ")
        regul_scale[0][0] = np.amin(PESdata[:,0])
        regul_scale[0][1] = 5.0/(np.amax(PESdata[:,0]) - np.amin(PESdata[:,0]))

        regul_scale[1][0] = np.amin(PESdata[:,1])
        regul_scale[1][1] = 5.0/(np.amax(PESdata[:,1]) - np.amin(PESdata[:,1]))

        xi_r = (PESdata[:,0]-regul_scale[0][0])*regul_scale[0][1]
        yi_r = (PESdata[:,1]-regul_scale[1][0])*regul_scale[1][1]

        Guess_beads_r = deepcopy(Guess_beads)
        Guess_beads_r[:,0] = (Guess_beads[:,0]-regul_scale[0][0])*regul_scale[0][1]
        Guess_beads_r[:,1] = (Guess_beads[:,1]-regul_scale[1][0])*regul_scale[1][1]

        PES_f  = CloughTocher2DInterpolator(np.column_stack((xi_r,yi_r)),PESdata[:,2])
        ## 1. Generate string
        beads = InitBeads(Guess_beads_r,PES_f,nbeads)
        self.plotReGen()
        beads_tx, beads_ty = trans_back(beads[:,0],beads[:,1],regul_scale)
        line = self.Canvas.axes.plot(beads_tx, beads_ty,'o-',color='k',markersize=1)
        
        self.Canvas.draw()
        line.pop(0).remove()
        ## 2. optimaztion loop
        beads_old = deepcopy(beads)
        diff = 1
        Conv_flag = 0
        for i in range(max_iter):
            if (i == 1 and diff < 0.5*10**-3  ): stepsize =stepsize*100
            #if (i == 1 and diff < 0.04 and diff > 0.004): stepsize =stepsize*100
            if (i == 45 and diff > 0.1 ): stepsize =stepsize*0.1
            if (i == 50 and diff > 0.05 ): stepsize =stepsize*0.1
            if (i > 55 and i < 58 and diff > 0.02 ): stepsize =stepsize*0.1
            #if (i > 65 and i < 68 and diff > 0.005 ): stepsize =stepsize*0.5
            beads,scale_step = walkdown(beads,stepsize,PES_f)
            beads = redist(beads,PES_f)
            diff = calcDiff(beads,beads_old)
            stepsize =stepsize*scale_step
            if (i%5 == 0):
                self.outBrowser.append("iteration number:  " \
                                    +str(i)+"   Diff:  "+ str(round(diff,6))\
                                    +"  stepsize: "+str(round(stepsize,6)))
            #print("iteration number:  ",i,"Diff:  ",diff,"  step: ",stepsize)
            if(diff<0.5*10**-3 and i >10):
                self.outBrowser.append("  Converged ! ")
                Conv_flag = 1
                break

            beads_old = deepcopy(beads)
            beads_tx, beads_ty = trans_back(beads[:,0],beads[:,1],regul_scale)
            #line = self.Canvas.axes.plot(beads_tx, beads_ty,'o-',color='r',markersize=1,lw=0.5)
            self.Canvas.draw_beads(beads_tx, beads_ty)
            time.sleep(0.2)
            #self.Canvas.draw()
        if (Conv_flag ==0 ): 
            self.outBrowser.append("  Converge Failed ! ")
        Guess_beads = deepcopy(beads)
        Guess_beads[:,0],Guess_beads[:,1] = trans_back(beads[:,0],beads[:,1],regul_scale)
        beads_tx, beads_ty = trans_back(beads[:,0],beads[:,1],regul_scale)
        self.Canvas.axes.plot(beads_tx, beads_ty,'-',color='r',lw=1.8)
        self.Canvas.draw()

        
        ## RecoverData


app = QApplication(sys.argv)
demo1 = MainWindow()
demo1.show()
sys.exit(app.exec_())