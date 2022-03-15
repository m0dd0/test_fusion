import logging
from uuid import uuid4
import traceback
from pathlib import Path
from enum import auto

import adsk.core, adsk.fusion, adsk.cam

from .fusion_addin_framework import fusion_addin_framework as faf
from .src.ui import InputIds, CommandWindowTable


# settings / constants #########################################################
LOGGING_ENABLED = True
# RESOURCE_FOLDER = (
#     Path(__file__).parent
#     / "fusion_addin_framework"
#     / "fusion_addin_framework"
#     / "default_images"
# )
RESOURCE_FOLDER = Path(__file__).parent / "resources"


# globals ######################################################################
addin = None
ao = faf.utils.AppObjects()
queue_table: adsk.core.TableCommandInput = None
# deleted_row_ids = []
invalid_deletion = False
second_row_id = None


class InputIds(faf.utils.InputIdsBase):
    MainTable = auto()


# handlers #####################################################################
def on_created(event_args: adsk.core.CommandCreatedEventArgs):
    command = event_args.command

    global queue_table
    queue_table = command.commandInputs.addTableCommandInput(
        InputIds.MainTable.value, "Render queue", 3, "3:1:1"
    )

    for i in range(5):
        i_row = queue_table.rowCount

        input_id = f"cancel_{i}__" + str(uuid4())
        if i_row == 2:
            second_row_id = input_id

        cancel_button = command.commandInputs.addBoolValueInput(
            input_id,
            "",
            False,
            str(RESOURCE_FOLDER / "cancel_button"),
            False,
        )
        queue_table.addCommandInput(cancel_button, i_row, 1)


def on_execute(event_args: adsk.core.CommandEventArgs):
    pass


def on_input_changed(event_args: adsk.core.InputChangedEventArgs):
    # command = event_args.firingEvent.sender
    global invalid_deletion

    print(event_args.input.id)
    if invalid_deletion:  # event_args.input.id in deleted_row_ids:
        print("invalid deletion")
        invalid_deletion = False
        return

    if event_args.input.id.startswith("cancel"):  # and event_args.input.value:
        # event_args.input.value = False
        invalid_deletion = True
        # deleted_row_ids.append(event_args.input.id)
        _, i_row, _, _, _ = queue_table.getPosition(event_args.input)
        # deleting this row retrigger inputchanged handler !!!!
        queue_table.deleteRow(i_row)
        print("deleted")
        return

    print("end")
    # return  # the currently cheged input got deleted so return to avoid error

    # if event_args.input.id == InputIds.UpdateButton.value:
    #     if event_args.input.value:
    #         logging.getLogger(__name__).info("Pressed reload button.")
    #         for _ in range(5):
    #             i_row = queue_table.rowCount

    #             cancel_button = command.commandInputs.addBoolValueInput(
    #                 "cancel" + str(uuid4()),
    #                 f"",  # only for debugging
    #                 False,
    #                 str(RESOURCE_FOLDER / "cancel_button"),
    #                 False,
    #             )
    #             queue_table.addCommandInput(cancel_button, i_row, 1)
    #         event_args.input.value = False


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
            name="test_table_input",
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
