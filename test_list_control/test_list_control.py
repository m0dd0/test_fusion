# Author-
# Description-

import adsk.core, adsk.fusion, adsk.cam, traceback

ws = None
tab = None
panel = None
cmd = None
ctrl = None

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

        ws = ui.workspaces.itemById("FusionSolidEnvironment")

        tab = ws.toolbarTabs.add("Tool", "my toolbar")

        panel = tab.toolbarPanels.add("verycustompanelid", "my panel")

        cmd = ui.commandDefinitions.addListDefinition(
            # cmd = ui.commandDefinitions.addButtonDefinition(
            "verycustomcommandid",
            "my command",
            # "tooltip"
            adsk.core.ListControlDisplayTypes.RadioButtonlistType,
        )
        cmd.controlDefinition.listItems.add("list item 1", True)
        cmd.controlDefinition.isEnabled = True

        onCreated = MyCreatedHandler()
        cmd.commandCreated.add(onCreated)
        handlers.append(onCreated)

        ctrl = panel.controls.addCommand(cmd)

        # print(cmd.tooltip)
        # print("####")
        # cmd.tooltip = "22222"
        # print(cmd.tooltip)
        # print("####")

        # print(cmd.resourceFolder)
        # # cmd.resourceFolder = r"C:\Users\mohes\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\cmd_attrs_test\cubes"
        # cmd.resourceFolder = r"C:/Users/mohes/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/AddIns/cmd_attrs_test/cubes"

        # print(cmd.resourceFolder)

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
        panel.deleteMe()
        tab.deleteMe()
        # ws.deleteMe()

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
