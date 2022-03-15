#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        newWorkspace = ui.workspaces.add('DesignProductType','idCustomWorkspace','NAME of workspace','')
        ui.messageBox(str(newWorkspace))


    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        ui.workspaces.itemById('FusionSolidEnvironment').activate()
        ui.workspaces.itemById('idCustomWorkspace').deleteMe()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
