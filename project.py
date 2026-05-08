import maya.cmds as cmds
import maya.OpenMayaUI as omui
import functools
import json
import os
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
        self.selected_curve = None
        self.saved_bookmarks = {}

        window_layout = QtWidgets.QHBoxLayout(self)

        left_pannel = QtWidgets.QWidget()
        left_pannel.setFixedWidth(200)
        self.left_layout = QtWidgets.QVBoxLayout(left_pannel)
        window_layout.addWidget(left_pannel)

        right_pannel = QtWidgets.QWidget()
        self.right_layout = QtWidgets.QVBoxLayout(right_pannel)
        window_layout.addWidget(right_pannel)

        self.curve_list_ui()
        self.loadup_curve_list()
        self.read_json()

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
    
    def when_curve_selected(self, item):
        '''When a curve is selected it calls the bookmark view'''
        self.selected_curve = item.text()
        self.show_bookmark_view()
   
    def show_bookmark_view(self):
        '''Wipes right panel and displays selected curve bookmarks'''
        self.clear_right_panel()
        curve_bookmark_header = QtWidgets.QLabel(f"{self.selected_curve} Bookmarks:")
        self.right_layout.addWidget(curve_bookmark_header)

        new_bookmark_button = QtWidgets.QPushButton("New Bookmark")
        new_bookmark_button.clicked.connect(self.new_bookmark_form)
        self.right_layout.addWidget(new_bookmark_button)

        if self.selected_curve in self.saved_bookmarks:
            for index, bookmark in enumerate(self.saved_bookmarks[self.selected_curve]):
                self.bookmark_card_ui(bookmark, index)

        self.right_layout.addStretch()

    def bookmark_card_ui(self, bookmark, index):
        card_group = QtWidgets.QGroupBox(bookmark["name"])
        card_layout = QtWidgets.QVBoxLayout()
        
        frame_label = QtWidgets.QLabel(f"{bookmark['frames']}")
        card_layout.addWidget(frame_label)

        description_label = QtWidgets.QLabel(f"{bookmark['desc']}")
        description_label.setWordWrap(True)
        card_layout.addWidget(description_label)

        button_actions = QtWidgets.QHBoxLayout()
        frame_jump_button = QtWidgets.QPushButton("Jump to Frame")
        frame_jump_button.clicked.connect(functools.partial(self.jump_to_frame, bookmark))
        button_actions.addWidget(frame_jump_button)

        del_bookmark_button = QtWidgets.QPushButton("Delete Bookmark")
        del_bookmark_button.clicked.connect(functools.partial(self.delete_bookmark, index))
        button_actions.addWidget(del_bookmark_button)

        card_layout.addLayout(button_actions)
        card_group.setLayout(card_layout)
        self.right_layout.addWidget(card_group)

    def jump_to_frame(self, bookmark):
        cmds.currentTime(bookmark["frames"])
        cmds.select(self.selected_curve)

    def delete_bookmark(self, index):
        self.saved_bookmarks[self.selected_curve].pop(index)
        self.write_to_json()
        self.show_bookmark_view()

    def new_bookmark_form(self):
        '''Creates a window for new bookmark information name, frames, desc'''
        self.clear_right_panel()
        form_group = QtWidgets.QGroupBox(f"Creating Bookmark for {self.selected_curve}")
        form_layout = QtWidgets.QFormLayout()
        form_layout.setSpacing(10)

        self.bookmark_name_input = QtWidgets.QLineEdit()
        form_layout.addRow("Bookmark Name: ", self.bookmark_name_input)

        self.frames_input = QtWidgets.QSpinBox()
        self.frames_input.setValue(int(cmds.currentTime(query=True)))
        self.frames_input.setMinimum(-10000)
        self.frames_input.setMaximum(10000)
        form_layout.addRow("Frame or Frame Range: ", self.frames_input)

        self.description_input = QtWidgets.QTextEdit()
        self.description_input.setFixedHeight(80)
        form_layout.addRow("Description: ", self.description_input) 

        form_group.setLayout(form_layout)
        self.right_layout.addWidget(form_group)

        self.bookmark_form_buttons()
        self.right_layout.addStretch()

    def bookmark_form_buttons(self):
        '''Creates the Buttons for the New Bookmark Form'''
        create_bookmark_button = QtWidgets.QPushButton("Create Bookmark")
        create_bookmark_button.clicked.connect(self.saving_bookmarks)
        self.right_layout.addWidget(create_bookmark_button)

        cancel_bookmark_button = QtWidgets.QPushButton("Cancel")
        cancel_bookmark_button.clicked.connect(self.show_bookmark_view)
        self.right_layout.addWidget(cancel_bookmark_button)

    def saving_bookmarks(self):
        bookmark_name = self.bookmark_name_input.text().strip()
        frames = self.frames_input.value()
        description = self.description_input.toPlainText().strip()

        if not bookmark_name:
            QtWidgets.QMessageBox.warning(self, "Missing Name",
                                          "Please enter bookmark name.")
            return
        
        if self.selected_curve not in self.saved_bookmarks:
            self.saved_bookmarks[self.selected_curve] = []
        
        self.saved_bookmarks[self.selected_curve].append(
            {"name": bookmark_name, "frames": frames, "desc": description})
        
        self.write_to_json()        
        self.show_bookmark_view()

    def clear_right_panel(self):
        '''Removes all widgets on the rigtht panel'''
        while self.right_layout.count():
            bookmarks = self.right_layout.takeAt(0)
            if bookmarks.widget():
                bookmarks.widget().deleteLater()

    def create_json_path(self):
        '''Find the path next to the Maya scene'''
        maya_scene_path = cmds.file(query=True, sceneName=True)

        if not maya_scene_path:
            QtWidgets.QMessageBox.warning(self, "Unsaved Scene",
                                          "Please save Maya Scene to store Bookmarks.")
            return None
        
        scene_directory = os.path.dirname(maya_scene_path)
        scene_name = os.path.splitext(os.path.basename(maya_scene_path))[0]
        return os.path.join(scene_directory, f"{scene_name}_curve_bookmarks.json")
    
    def write_to_json(self):
        '''Writes to a JSON file saving the Bookmark information'''
        jason_path = self.create_json_path()

        if not jason_path:
            return
        
        with open(jason_path, "w") as json__file:
            json.dump(self.saved_bookmarks, json__file, indent=4)
    
    def read_json(self):
        json_path = self.create_json_path()

        if not json_path:
            return
        
        if not os.path.exists(json_path):
            return
        
        with open(json_path, "r") as json_file:
            self.saved_bookmarks = json.load(json_file)


def show_ui():
    ui = CurveBookmarkManager()
    ui.show()
    return ui
