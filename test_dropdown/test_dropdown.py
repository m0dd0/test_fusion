# Author-
# Description-

import adsk.core, adsk.fusion, adsk.cam, traceback

ws = None
tab = None
panel = None
cmd = None
ctrl = None
dropdown = None

handlers = []


class MyCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        adsk.core.Application.get().userInterface.messageBox("created")


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        global ws
        global tab
        global panel
        global cmd
        global ctrl
        global handlers
        global dropdown

        ws = ui.workspaces.itemById("FusionSolidEnvironment")

        tab = ws.toolbarTabs.add("Tool", "my toolbar")

        panel = tab.toolbarPanels.add("verycustompanelid", "my panel")

        dropdown = panel.controls.addDropDown(
            "text",
            r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/fusion_addin_framework/tests/test_images/one",
        )

        cmd = ui.commandDefinitions.addButtonDefinition(
            "verycustomcommandid", "my command", "tt"
        )
        onCreated = MyCreatedHandler()
        cmd.commandCreated.add(onCreated)
        handlers.append(onCreated)

        ctrl = dropdown.controls.addCommand(cmd)

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))


def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        global ws
        global tab
        global panel
        global cmd

        cmd.deleteMe()
        ctrl.deleteMe()
        dropdown.deleteMe()
        panel.deleteMe()
        tab.deleteMe()
        # ws.deleteMe()

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
