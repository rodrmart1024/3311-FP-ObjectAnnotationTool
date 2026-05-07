import maya.cmds as cmds
import maya.OpenMayaUI as omui
from PySide6 import QtWidgets, QtCore
from shiboken6 import wrapInstance

def get_maya_main_window():
    main_win_address = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_win_address), QtWidgets.QWidget)


class CurveBookmarkManager(QtWidgets.QDialog):

    def __init__(self):
        '''Creating the Window and calling out to functions'''
        super().__init__(parent=get_maya_main_window())
        self.setWindowTitle("Curve Bookmark Manager")
        self.resize(800, 800)
        window_layout = QtWidgets.QHBoxLayout(self)

        left_pannel = QtWidgets.QWidget()
        left_pannel.setFixedWidth(200)
        self.left_layout = QtWidgets.QVBoxLayout(left_pannel)
        window_layout.addWidget(left_pannel)

        right_pannel = QtWidgets.QWidget()
        self.right_layout = QtWidgets.QVBoxLayout(right_pannel)
        window_layout.addWidget(right_pannel)

        self.selected_curve = None
        self.curve_list_ui()
        self.loadup_curve_list()

    def curve_list_ui(self):
        '''Creates the pannel for curves on the leff'''
        curve_group = QtWidgets.QGroupBox('Curves:')
        curve_layout = QtWidgets.QVBoxLayout()

        self.curve_list = QtWidgets.QListWidget()
        curve_layout.addWidget(self.curve_list)

        curve_group.setLayout(curve_layout)
        self.left_layout.addWidget(curve_group)
        self.curve_list.itemClicked.connect(self.when_curve_selected)

    def loadup_curve_list(self):
        '''Loads the curves in the scene into the pannel'''
        self.curve_list.clear()

        shape_node = cmds.ls(type="nurbsCurve")
        transform_node = cmds.listRelatives(shape_node, parent=True)
        transform_node = sorted(set(transform_node))

        for curve_name in transform_node:
            self.curve_list.addItem(curve_name)
    
    def show_bookmark_view(self):
        '''Wipes right panel and displays selected curve bookmarks'''
        self.clear_right_panel()
        curve_bookmark_header = QtWidgets.QLabel(f"{self.selected_curve} Bookmarks:")
        self.right_layout.addWidget(curve_bookmark_header)

        create_bookmark_button = QtWidgets.QPushButton("New Bookmark")
        create_bookmark_button.clicked.connect(self.new_bookmark_form)
        self.right_layout.addWidget(create_bookmark_button)
        self.right_layout.addStretch()

    def new_bookmark_form(self):
        '''Creates a window for new bookmark information name, frames, desc'''
        pass
    
    def when_curve_selected(self, item):
        '''When a curve is selected it calls the bookmark view'''
        self.selected_curve = item.text()
        self.show_bookmark_view()

    def clear_right_panel(self):
        '''Removes all widgets on the rigtht panel'''
        while self.right_layout.count():
            bookmarks = self.right_layout.takeAt(0)
            if bookmarks.widget():
                bookmarks.widget().deleteLater()



def show_ui():
    ui = CurveBookmarkManager()
    ui.show()

show_ui()


'''
Creating the UI:
Make two pannels with one having a seprate pop-up pannel.
One Pannel = List if NURBS curves in the scene
Second Pannel = View Selected Curve Bookmarks
Second Pannel Pop-Uo = Create a New Bookmark of Selected Curve

Creating the Logic:
Get only curves to appear on the List.
Bookedmaked Curves appear at the top of list while rest are sorted alpha.
Save frames to second pannel.
When creating new Bookmark defualt current frame as saved frame on second pannel.

Persistence of Bookmarks:
When Bookmark is saved use JSON write.
Save the .json file next to maya scene.
When scene is reopened JSON read.
'''