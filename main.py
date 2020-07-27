import numpy as np
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
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class dataTempl():
    PESdata = None 
    MaxValueInit = 1
    MinValueInit = 0

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow,self).__init__()       
        loadUi("ui/main.ui",self)
        ## DataInitial
        self.interData = dataTempl()
         # Initial Click events
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
        self.Pgen.clicked.connect(self.plotGuessDot)

    def readFile(self):
        fileName = QFileDialog.getOpenFileName(self, "Save", "./","File (*.dat *.txt)")
        self.outBrowser.append("Potential energy surface file selected:   "+fileName[0])
        self.label.setText("File loaded")
        self.PESfile = fileName
        PESfile = open(fileName[0],'r')
        # Process The Data
        PESdata = np.loadtxt(PESfile)
        maxD = np.max(PESdata[:,2])
        minD = np.min(PESdata[:,2])
        self.interData.PESdata = PESdata
        self.interData.MaxValueInit = maxD
        self.interData.MinValueInit = minD
        self.Vmax.setText(str(round(maxD,3)))
        self.Vmin.setText(str(round(minD,3)))
        self.plotPES_int()
        
    # Initial plot
    def plotPES_int(self):
        self.Canvas.axes.tricontour(
                                 self.interData.PESdata[:,0], 
                                 self.interData.PESdata[:,1],
                                 self.interData.PESdata[:,2],levels=24,linewidths=0.5,colors='k')

        cf = self.Canvas.axes.tricontourf(
                                 self.interData.PESdata[:,0], 
                                 self.interData.PESdata[:,1],
                                 self.interData.PESdata[:,2],levels=140,cmap="bwr")
        # Get color bar
        self.cb = self.Canvas.axes.figure.colorbar(cf)
        self.Canvas.draw()
    # Plot guess dot on Canvas
    def plotGuessDot(self):
        self.cb.remove()  
        self.Canvas.axes.plot([0], [1],'o',color='k')
        self.Canvas.draw()


app = QApplication(sys.argv)
demo1 = MainWindow()
demo1.show()
sys.exit(app.exec_())