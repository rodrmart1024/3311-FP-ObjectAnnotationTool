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
        self.resize(600, 600)

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