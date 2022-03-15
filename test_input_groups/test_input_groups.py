# Author-
# Description-

import adsk.core, adsk.fusion, adsk.cam, traceback

cmd_def = None
ctrl = None

handlers = []


class MyInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args: adsk.core.InputChangedEventArgs):
        print("############")
        for inp in args.inputs:
            print(inp.id)

        print("####")
        for inp in args.firingEvent.sender.commandInputs:
            print(inp.id)


class MyCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args: adsk.core.CommandCreatedEventArgs):
        group_1 = args.command.commandInputs.addGroupCommandInput(
            "group_1_input_id", "Group 1"
        )
        group_1.children.addBoolValueInput("bool_1_a_id", "bool_1_a", True)
        group_1.children.addBoolValueInput("bool_1_b_id", "bool_b_a", True)
        group_2 = args.command.commandInputs.addGroupCommandInput(
            "group_2_input_id", "Group 2"
        )
        group_2.children.addBoolValueInput("bool_2_a_id", "bool_2_a", True)
        group_2.children.addBoolValueInput("bool_2_b_id", "bool_b_a", True)

        on_input_changed = MyInputChangedHandler()
        args.command.inputChanged.add(on_input_changed)
        handlers.append(on_input_changed)


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        global ctrl
        global cmd_def
        global handlers

        cmd_def = ui.commandDefinitions.addButtonDefinition(
            "MyCmdDefId",
            "test button",
            "tooltip",
        )

        onCreated = MyCreatedHandler()
        cmd_def.commandCreated.add(onCreated)
        handlers.append(onCreated)

        panel = ui.allToolbarPanels.itemById("SolidScriptsAddinsPanel")

        ctrl = panel.controls.addCommand(cmd_def)

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))


def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        ctrl.deleteMe()
        cmd_def.deleteMe()

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
