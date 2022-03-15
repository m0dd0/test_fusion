import traceback

import adsk.core, adsk.fusion


def run(context):  # pylint:disable=unused-argument
    ui = adsk.core.Application.get().userInterface
    try:
        pass

    except:
        msg = "Failed:\n{}".format(traceback.format_exc())
        if ui:
            ui.messageBox(msg)
        print(msg)


def stop(context):  # pylint:disable=unused-argument
    ui = adsk.core.Application.get().userInterface

    try:
        pass
    except:
        msg = "Failed:\n{}".format(traceback.format_exc())
        if ui:
            ui.messageBox(msg)
        print(msg)
