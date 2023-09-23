import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage,QPainter
from PyQt5.QtWidgets import QApplication, QMainWindow


class Img(QMainWindow):
    def __init__(self, img_path,img_path_2, parent=None):
        super().__init__(parent)
        
        self.img_1 = QImage(img_path)
        self.img_2 = QImage(img_path_2)
        self.img_current = self.img_1
        
        #self.setWindowFlags(Qt.WindowType.FramelessWindowHint) 

    def paintEvent(self, qpaint_event):
        # event handler of QWidget triggered when, for ex, painting on the widget’s background.
        painter = QPainter(self)
        rect: QRectF = qpaint_event.rect() # Returns the rectangle that needs to be updated
        painter.drawImage(rect, self.img_current)
        
        
        


    def swap_image(self):
        if self.img_current is self.img_1:
            self.img_current.swap(self.img_2)
        else:
            self.img_current.swap(self.img_1)
        self.repaint()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_F5:
            self.swap_image()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    img_path = '/home/fvbakel//tmp/test_2.jpg'
    img_path_2 = '/home/fvbakel//tmp/test.jpg'

    window = Img(img_path,img_path_2)
    window.show()
    #self.showFullScreen()
    #self.showMaximized()
    print("Ready")


    sys.exit(app.exec())
