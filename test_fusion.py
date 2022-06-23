import adsk.core, adsk.fusion, traceback

from queue import Queue

from .fusion_addin_framework import fusion_addin_framework as faf

handlers = []
cmd = None
ctrl = None
ui = None

command = None
execution_queue = Queue()

event_registered = False


# def _update_camera():
#     adsk.core.Application.get().activeViewport.camera = (
#         adsk.core.Application.get().activeViewport.camera
#     )
#     print("camera")


# # def trigger_execution_queue():
# #     execution_queue.put(_update_camera)
# #     command.doExecute(False)


# class TestFusionCustomHandler(adsk.core.CustomEventHandler):
#     def __init__(self):
#         super().__init__()

#     def notify(self, eventArgs: adsk.core.EventArgs):
#         print("started TestFusionCustomHandler")
#         try:
#             print("custom")
#             # execution_queue.put(_update_camera)
#             # command.doExecute(False)
#         except:
#             if ui:
#                 ui.messageBox(traceback.format_exc())


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

            # app = adsk.core.Application.get()
            # event = app.registerCustomEvent("eventid123")
            # custom_handler = TestFusionCustomHandler()
            # handlers.append(custom_handler)
            # event.add(custom_handler)
            # global event_registered
            # event_registered = True

            global command
            command = eventArgs.command

        except:
            if ui:
                ui.messageBox(traceback.format_exc())


class TestfusionInputChangedHandler(adsk.core.InputChangedEventHandler):
    def notify(self, eventArgs: adsk.core.InputChangedEventArgs):
        print("started TestfusionInputChangedHandler")
        try:
            faf.utils.execute_as_event(lambda: print("custom"))
            # global event_registered
            # if not event_registered:
            #     custom_event = adsk.core.Application.get().registerCustomEvent(
            #         "eventid123"
            #     )
            #     custom_handler = TestFusionCustomHandler()
            #     custom_event.add(custom_handler)
            #     event_registered = True

            # adsk.core.Application.get().fireCustomEvent("eventid123")

        except:
            if ui:
                ui.messageBox(traceback.format_exc())


class TestfusionExecuteHandler(adsk.core.CommandEventHandler):
    def notify(self, eventArgs: adsk.core.CommandEventArgs):
        print("started TestfusionExecuteHandler")
        try:
            # command = eventArgs.firingEvent.sender
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
        # adsk.core.Application.get().unregisterCustomEvent("eventid123")
        faf.stop()
    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
