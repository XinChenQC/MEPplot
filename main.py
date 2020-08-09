import numpy as np
from scipy.interpolate import griddata
import sys
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

# Global setting

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, constrained_layout=True)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class dataTempl():
    PESdata = None 
    MaxValueInit = 1
    MinValueInit = 0
    xi = None
    yi = None
    zi = None

class MainWindow(QWidget):
    cb = None
    def __init__(self):
        super(MainWindow,self).__init__()       
        loadUi("ui/main.ui",self)
        ## PES and MEP Data Initial
        self.interData = dataTempl()

        ## Initial Click events
        self.Click()

        ## Canvas define
        self.Canvas = MplCanvas(self.plotWindows, width=5, height=4, dpi=100)
        #toolbar = NavigationToolbar(self.Canvas,self.plotWindows)
        layout = QVBoxLayout()
        #layout.addWidget(toolbar)
        layout.addWidget(self.Canvas)
        self.plotWindows.setLayout(layout)

    def Click(self):
        self.openB.clicked.connect(self.readFile)
        self.Rgen.clicked.connect(self.plotReGen)
        self.Rset.clicked.connect(self.plotReset)


    def readFile(self):
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
        print(PESfile)
        self.interData.PESdata = PESdata
        self.interData.MaxValueInit = maxD
        self.interData.MinValueInit = minD
        self.Vmax.setText(str(round(maxD,3)))
        self.Vmin.setText(str(round(minD,3)))
        self.Level.setText(str(24))
        self.plotPES_int()
        
    # Initial plot
    def plotPES_int(self):
        if(self.cb != None ): self.cb.remove()
        self.Canvas.axes.clear()
        X_max = np.max(self.interData.PESdata[:,0])
        X_min = np.min(self.interData.PESdata[:,0])
        Y_max = np.max(self.interData.PESdata[:,1])
        Y_min = np.min(self.interData.PESdata[:,1])
        self.interData.xi = np.linspace(X_min,X_max,100)
        self.interData.yi = np.linspace(Y_min,Y_max,100)
        self.interData.zi = griddata(
                        (self.interData.PESdata[:,0],self.interData.PESdata[:,1]),
                         self.interData.PESdata[:,2],
                        (self.interData.xi[None,:],self.interData.yi[:,None]),method='cubic')

        self.Canvas.axes.contour(self.interData.xi,self.interData.yi,self.interData.zi,
                                levels=24,linewidths=0.5,colors='k')

        cf = self.Canvas.axes.contourf(self.interData.xi,self.interData.yi,self.interData.zi,
                                    levels=140,cmap="bwr")
        # Get color bar
        self.cb = self.Canvas.axes.figure.colorbar(mappable=cf)
        self.Canvas.draw()

    # Regenerate plot
    def plotReGen(self):
        self.cb.remove()
        self.Canvas.axes.clear()
        self.Canvas.draw()
        try:
            maxV = float(self.Vmax.text())
            minV = float(self.Vmin.text())
            level = int(self.Level.text())
        except:
            print("wrong input format")
            return
        Cmap = self.cmap.currentText()
        maskLine = []

        self.Canvas.axes.contour(
                self.interData.xi, 
                self.interData.yi,
                self.interData.zi,
                vmax=maxV,vmin=minV,
                linewidths=0.5,colors='k',levels=np.linspace(minV,maxV,level))

        cf = self.Canvas.axes.contourf(
                self.interData.xi, 
                self.interData.yi,
                self.interData.zi,
                vmax=maxV,vmin=minV,
                levels=np.linspace(minV,maxV,140),cmap=Cmap)
        self.cb = self.Canvas.axes.figure.colorbar(mappable=cf,boundaries=np.linspace(minV,maxV,140))
        self.Canvas.draw()

    # Plot Guess dot on Canvas
    def plotGuessDot(self):
        self.cb.remove()  
        self.Canvas.axes.plot([0], [1],'o',color='k')
        self.Canvas.draw()
    
    def plotReset(self):
        self.Canvas.axes.clear()
        #self.cb.remove() 
        self.Canvas.draw()


app = QApplication(sys.argv)
demo1 = MainWindow()
demo1.show()
sys.exit(app.exec_())