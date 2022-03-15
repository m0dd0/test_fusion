import adsk.core, adsk.fusion, traceback, adsk

handlers = []
cmd = None
ctrl = None
ui = None
i = 0


class Test_input_addingCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args: adsk.core.CommandCreatedEventArgs):
        print("started Test_input_addingCreatedHandler")
        try:
            inputChangedHandler = Test_input_addingInputChangedHandler()
            handlers.append(inputChangedHandler)
            args.command.inputChanged.add(inputChangedHandler)

            executeHandler = Test_input_addingExecuteHandler()
            handlers.append(executeHandler)
            args.command.execute.add(executeHandler)

            args.command.commandInputs.addBoolValueInput(
                "test_input_addingBoolInputId",
                "bool input",
                False,
            )
        except:
            if ui:
                ui.messageBox(traceback.format_exc())


class Test_input_addingInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        print("started Test_input_addingInputChangedHandler")
        try:
            command: adsk.core.Command = args.firingEvent.sender
            cmdInput = args.input

            if cmdInput.id == "test_input_addingBoolInputId":
                print("pressed orig button")
                command.doExecute(False)
                # global i
                # i += 1
                # input = command.commandInputs.addBoolValueInput(
                #     f"{i} input id", f"{i} input", False
                # )
                # input.isVisible = True
            else:
                print(f"##### {cmdInput.id}")

        except:
            if ui:
                ui.messageBox(traceback.format_exc())


class Test_input_addingExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        print("started Test_input_addingExecuteHandler")
        try:
            command = args.firingEvent.sender

            global i
            i += 1
            input = command.commandInputs.addBoolValueInput(
                f"{i} input id", f"{i} input", False
            )
            input.isEnabled = True
            input.isVisible = True
        except:
            if ui:
                ui.messageBox(traceback.format_exc())


def run(context):
    try:
        global ui
        global cmd
        global ctrl

        app: adsk.core.Application = adsk.core.Application.get()
        ui = app.userInterface

        ws = ui.workspaces.itemById("FusionSolidEnvironment")
        tab = ws.toolbarTabs.itemById("ToolsTab")
        panel = tab.toolbarPanels.itemById("SolidScriptsAddinsPanel")
        cmd = ui.commandDefinitions.addButtonDefinition(
            "test_input_addingcommandid", "test_input_adding", ""
        )
        ctrl = panel.controls.addCommand(cmd)

        onCreated = Test_input_addingCreatedHandler()
        cmd.commandCreated.add(onCreated)
        handlers.append(onCreated)

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))


def stop(context):
    try:
        global cmd
        global ctrl

        ctrl.deleteMe()
        cmd.deleteMe()
    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
