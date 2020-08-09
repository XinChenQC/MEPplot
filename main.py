import numpy as np
from scipy.interpolate import griddata,interp2d
import sys
from io import StringIO
# PyQt5 
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication,QWidget,QGroupBox,QLabel
from PyQt5.QtWidgets import QPushButton,QTextBrowser,QFileDialog
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import QFile
# matplotlib
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

## Global PES and MEP variables
PESdata = 0                # Original PES data provided by User [2D array, 3*N_points]
MaxValueInit = 1.0         # Maximum value of PES 
MinValueInit = 0.0         # Minimum value of PES 
xi = 0                     # interpolated Grid data X 100 [Grid_data]
yi = 0                     # interpolated Grid data Y 100 [Grid_data]
zi = 0                     # interpolated Grid data Z 100 [Grid_data]
Guess_beads = 0            # initGuess Beads [2D array, 2*N_guessbeads]
FuncInter = None           # interpolate function

stepsize=1                 # Optimize stepsize
max_iter=60                # maximum interation
nbeads=20                  #


## Matplotlib Canvas initialization
class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, constrained_layout=True)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)
## Guess beads input Class
class GuessBox(QWidget):
    def __init__(self,CanvasIn,LableIn):
        super(GuessBox,self).__init__()       
        loadUi("ui/GuessDia.ui",self)
        ## Initial Click events
        self.Click()
        self.Canvas = CanvasIn
        self.label2 = LableIn

    def Click(self):
        self.ok.clicked.connect(self.okReadin)
        self.reset.clicked.connect(self.resetData)
    def okReadin(self):
        global Guess_beads
        text = self.data.toPlainText()
        f = StringIO(text)
        Guess_beads = np.loadtxt(f)
        if (len(Guess_beads) == 0): return
        self.Canvas.axes.plot(Guess_beads[:,0],Guess_beads[:,1],'o-',color='k')
        self.Canvas.draw()
        self.label2.setText("Guess finished")
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
        self.guessb = GuessBox(self.Canvas,self.label2)

        #toolbar = NavigationToolbar(self.Canvas,self.plotWindows)
        layout = QVBoxLayout()
        #layout.addWidget(toolbar)
        layout.addWidget(self.Canvas)
        self.plotWindows.setLayout(layout)

    def Click(self):
        self.openB.clicked.connect(self.readFile)
        self.Rgen.clicked.connect(self.plotReGen)
        self.Rset.clicked.connect(self.plotReset)
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

        ## Interpolate Griddata to function
        FuncInter = interp2d(xi,yi,zi,kind='cubic') 
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
        print(self.cb)
        self.Canvas.axes.clear()
        self.Canvas.draw()
<<<<<<< HEAD
        try:
            maxV = float(self.Vmax.text())
            minV = float(self.Vmin.text())
            level = int(self.Level.text())
        except:
            self.cb = self.Canvas.axes.figure.colorbar(mappable=cf,boundaries=np.linspace(0,1,140))
            print("wrong input format")
            return
=======

        maxV = float(self.Vmax.text())
        minV = float(self.Vmin.text())
        level = int(self.Level.text())
>>>>>>> parent of 677beec... add exception
        Cmap = self.cmap.currentText()
        maskLine = []

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
        self.guessb.show()
        self.Nbeads.setText(str(20))

        stepsize = (MaxValueInit-MinValueInit)/30.0
        max_iter = 60
        nbeads = 20

        self.Stepsize.setText(str(round((MaxValueInit-MinValueInit)/30.0,3)))
        self.Maxiter.setText(str(60))
        #self.cb.remove()  

    def plotReset(self):
        self.Canvas.axes.clear()
        #self.cb.remove() 
        self.Canvas.draw()


app = QApplication(sys.argv)
demo1 = MainWindow()
demo1.show()
sys.exit(app.exec_())