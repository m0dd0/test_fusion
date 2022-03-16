import adsk.core, adsk.fusion, traceback

handlers = []
cmd = None
ctrl = None
ui = None


class TestfusionCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def notify(self, eventArgs: adsk.core.CommandCreatedEventArgs):
        print("started TestfusionCreatedHandler")
        try:
            inputChangedHandler = TestfusionInputChangedHandler()
            handlers.append(inputChangedHandler)
            eventArgs.command.inputChanged.add(inputChangedHandler)

            executeHandler = TestfusionExecuteHandler()
            handlers.append(executeHandler)
            eventArgs.command.execute.add(executeHandler)

            eventArgs.command.commandInputs.addBoolValueInput(
                "testfusionBoolInputId", "bool input", True
            )
        except:
            if ui:
                ui.messageBox(traceback.format_exc())


class TestfusionInputChangedHandler(adsk.core.InputChangedEventHandler):
    def notify(self, eventArgs: adsk.core.InputChangedEventArgs):
        print("started TestfusionInputChangedHandler")
        try:
            command = eventArgs.firingEvent.sender
            cmdInput = eventArgs.input

        except:
            if ui:
                ui.messageBox(traceback.format_exc())


class TestfusionExecuteHandler(adsk.core.CommandEventHandler):
    def notify(self, eventArgs: adsk.core.CommandEventArgs):
        print("started TestfusionExecuteHandler")
        try:
            command = eventArgs.firingEvent.sender

        except:
            if ui:
                ui.messageBox(traceback.format_exc())


def run(context):  # pylint:disable=unused-argument
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
            "testfusioncommandid", "testfusion", ""
        )
        ctrl = panel.controls.addCommand(cmd)

        onCreated = TestfusionCreatedHandler()
        cmd.commandCreated.add(onCreated)
        handlers.append(onCreated)

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))


def stop(context):  # pylint:disable=unused-argument
    try:
        ctrl.deleteMe()
        cmd.deleteMe()
    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
