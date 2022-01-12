#include <iostream>
/*#include <qapplication.h>
#include <qpushbutton.h>
#include <qimage.h>
*/
#include <QtWidgets>

int main(int argc, char **argv) {
    std::cout << "Hello, world!\n";
    QApplication a( argc, argv );
    QImage imageDisplay("/home/fvbakel/Documenten/nonogram/picture_puzzles/tiny.png");
    QWidget window;
    window.resize(320, 240);
    window.show();
    window.setWindowTitle(
        QApplication::translate("toplevel", "Top-level widget")
    );
    QPushButton hello( "Hello world!", 0 );
    hello.resize( 100, 30 );
    hello.show();

    return a.exec();
}
