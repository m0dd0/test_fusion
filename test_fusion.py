import adsk.core, adsk.fusion, traceback

from .fusion_addin_framework import fusion_addin_framework as faf

from queue import Queue

handlers = []
cmd = None
ctrl = None
ui = None

command = None
execution_queue = Queue()


def update_camera():
    adsk.core.Application.get().activeViewport.camera = (
        adsk.core.Application.get().activeViewport.camera
    )


def create_cube(center, side_length: float) -> adsk.fusion.BRepBody:
    adsk.core.Application.get().activeDocument.design.rootComponent.bRepBodies.add(
        adsk.fusion.TemporaryBRepManager.get().createBox(
            adsk.core.OrientedBoundingBox3D.create(
                adsk.core.Point3D.create(*center),
                adsk.core.Vector3D.create(1, 0, 0),
                adsk.core.Vector3D.create(0, 1, 0),
                side_length,
                side_length,
                side_length,
            )
        )
    )


class TestFusionCustomHandler(adsk.core.CustomEventHandler):
    def notify(self, eventArgs: adsk.core.EventArgs):
        print("started test_fusionCustomHandler")
        execution_queue.put(lambda: create_cube((0, 0, 0), 1))
        # execution_queue.put(update_camera)
        command.doExecute(False)


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

            eventArgs.command.commandInputs.addIntegerSpinnerCommandInput(
                "testFusionIntegerSpinnerInputId", "spinner input", 1, 5, 1, 3
            )

            app = adsk.core.Application.get()
            event = app.registerCustomEvent("eventid123")
            custom_handler = TestFusionCustomHandler()
            handlers.append(custom_handler)
            event.add(custom_handler)
            # faf.utils.execute_as_event(lambda: print("custom createed"))

            global command
            command = eventArgs.command

        except:
            if ui:
                ui.messageBox(traceback.format_exc())


class TestfusionInputChangedHandler(adsk.core.InputChangedEventHandler):
    def notify(self, eventArgs: adsk.core.InputChangedEventArgs):
        print("started TestfusionInputChangedHandler")
        try:
            # faf.utils.execute_as_event(event_action)
            adsk.core.Application.get().fireCustomEvent("eventid123")
        except:
            if ui:
                ui.messageBox(traceback.format_exc())


class TestfusionExecuteHandler(adsk.core.CommandEventHandler):
    def notify(self, eventArgs: adsk.core.CommandEventArgs):
        print("started TestfusionExecuteHandler")
        try:
            while not execution_queue.empty():
                execution_queue.get()()
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
        adsk.core.Application.get().unregisterCustomEvent("eventid123")
        # faf.stop()
    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
