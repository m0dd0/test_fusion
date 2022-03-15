import logging
from uuid import uuid4
import traceback
from pathlib import Path

import adsk.core, adsk.fusion, adsk.cam

from .fusion_addin_framework import fusion_addin_framework as faf
from .src.ui import InputIds, CommandWindow


# settings / constants #########################################################
LOGGING_ENABLED = True
RESOURCE_FOLDER = (
    Path(__file__).parent
    / "fusion_addin_framework"
    / "fusion_addin_framework"
    / "default_images"
)
# RESOURCE_FOLDER = Path(__file__).parent / "resources"


# globals ######################################################################
addin = None
ao = faf.utils.AppObjects()


# handlers #####################################################################
def on_created(event_args: adsk.core.CommandCreatedEventArgs):
    command = event_args.command

    command_window = CommandWindow(command, RESOURCE_FOLDER)


def on_execute(event_args: adsk.core.CommandEventArgs):
    pass


def on_input_changed(event_args: adsk.core.InputChangedEventArgs):
    # !!! do NOT use this because of bug # (will only contain changed inputs of the same input group)
    # inputs = event_args.inputs
    # use instead:
    inputs = event_args.firingEvent.sender.commandInputs

    if event_args.input.id == InputIds.Button1.value:
        event_args.input.value = False

        # ao.userInterface.messageBox(inputs.itemById(InputIds.Text.value).formattedText)
        faf.utils.set_camera_viewcube(inputs.itemById(InputIds.Text.value).text)


def on_destroy(event_args: adsk.core.CommandEventArgs):
    pass


### entry point ################################################################
def run(context):
    try:
        ui = ao.userInterface

        if LOGGING_ENABLED:
            faf.utils.create_logger(
                __name__,  # also applies to faf since its a submodule
                [logging.StreamHandler(), faf.utils.TextPaletteLoggingHandler()],
            )

        global addin
        addin = faf.FusionAddin()
        workspace = faf.Workspace(addin, id="FusionSolidEnvironment")
        tab = faf.Tab(workspace, id="ToolsTab")
        panel = faf.Panel(tab, id="SolidScriptsAddinsPanel")
        control = faf.Control(panel)
        cmd = faf.AddinCommand(
            control,
            resourceFolder="lightbulb",
            name="test_camera_views",
            commandCreated=on_created,
            inputChanged=on_input_changed,
            execute=on_execute,
            destroy=on_destroy,
        )

    except:
        msg = "Failed:\n{}".format(traceback.format_exc())
        if ui:
            ui.messageBox(msg)
        print(msg)


def stop(context):
    try:
        ui = ao.userInterface
        addin.stop()
    except:
        msg = "Failed:\n{}".format(traceback.format_exc())
        if ui:
            ui.messageBox(msg)
        print(msg)
