import adsk.core, adsk.fusion, traceback

handlers = [] 

# Removes the command control and definition 
def cleanUpNavDropDownCommand(cmdId, DC_CmdId):
    
    objArrayNav = []
    dropDownControl_ = commandControlById_in_NavBar(DC_CmdId)
    commandControlNav_ = commandControlById_in_DropDown(cmdId, dropDownControl_)
        
    if commandControlNav_:
        objArrayNav.append(commandControlNav_)
    
    commandDefinitionNav_ = commandDefinitionById(cmdId)
    if commandDefinitionNav_:
        objArrayNav.append(commandDefinitionNav_)
        
    for obj in objArrayNav:
        destroyObject(obj)


# Finds command definition in active UI
def commandDefinitionById(cmdId):
    app = adsk.core.Application.get()
    ui = app.userInterface
    
    if not cmdId:
        ui.messageBox('Command Definition:  ' + cmdId + '  is not specified')
        return None
    commandDefinitions_ = ui.commandDefinitions
    commandDefinition_ = commandDefinitions_.itemById(cmdId)
    return commandDefinition_
    
def commandControlById_in_NavBar(cmdId):
    app = adsk.core.Application.get()
    ui = app.userInterface
    
    if not cmdId:
        ui.messageBox('Command Control:  ' + cmdId + '  is not specified')
        return None
    
    toolbars_ = ui.toolbars
    Nav_toolbar = toolbars_.itemById('NavToolbar')
    Nav_toolbarControls = Nav_toolbar.controls
    cmd_control = Nav_toolbarControls.itemById(cmdId)
    
    if cmd_control is not None:
        return cmd_control

# Get a commmand Control in a Nav Bar Drop Down    
def commandControlById_in_DropDown(cmdId, dropDownControl):   
    cmd_control = dropDownControl.controls.itemById(cmdId)
    
    if cmd_control is not None:
        return cmd_control

# Destroys a given object
def destroyObject(tobeDeleteObj):
    app = adsk.core.Application.get()
    ui = app.userInterface
    
    if ui and tobeDeleteObj:
        if tobeDeleteObj.isValid:
            tobeDeleteObj.deleteMe()
        else:
            ui.messageBox(tobeDeleteObj.id + 'is not a valid object')

# Returns the id of a Toolbar Panel in the given Workspace
def toolbarPanelById_in_Workspace(myWorkspaceID, myToolbarPanelID):
    app = adsk.core.Application.get()
    ui = app.userInterface
        
    Allworkspaces = ui.workspaces
    thisWorkspace = Allworkspaces.itemById(myWorkspaceID)
    allToolbarPanels = thisWorkspace.toolbarPanels
    ToolbarPanel_ = allToolbarPanels.itemById(myToolbarPanelID)
    
    return  ToolbarPanel_

# Returns the Command Control from the given panel
def commandControlById_in_Panel(cmdId, ToolbarPanel):
    
    app = adsk.core.Application.get()
    ui = app.userInterface
    
    if not cmdId:
        ui.messageBox('Command Control:  ' + cmdId + '  is not specified')
        return None
    
    cmd_control = ToolbarPanel.controls.itemById(cmdId)
    
    if cmd_control is not None:
        return cmd_control

# Base Class for creating Fusion 360 Commands
class Fusion360CommandBase:
    
    def __init__(self, cmd_def, debug):

        self.commandName = cmd_def.get('commandName', 'Default Command Name')
        self.commandDescription = cmd_def.get('commandDescription', 'Default Command Description')
        self.commandResources = cmd_def.get('commandResources', './resources')
        self.cmdId = cmd_def.get('cmdId', 'Default Command ID')
        self.workspace = cmd_def.get('workspace', 'FusionSolidEnvironment')
        self.toolbarPanelID = cmd_def.get('toolbarPanelID', 'SolidScriptsAddinsPanel')
        self.DC_CmdId = cmd_def.get('DC_CmdId', 'Default_DC_CmdId')
        self.DC_Resources = cmd_def.get('DC_Resources', './resources')
        self.command_in_nav_bar = cmd_def.get('command_in_nav_bar', False)
        self.debug = debug

        
        # global set of event handlers to keep them referenced for the duration of the command
        self.handlers = []
        
        try:
            self.app = adsk.core.Application.get()
            self.ui = self.app.userInterface

        except:
            if self.ui:
                self.ui.messageBox('Couldn\'t get app or ui: {}'.format(traceback.format_exc()))
    
    def onPreview(self, command, inputs):
        pass 
    def onDestroy(self, command, inputs, reason_):    
        pass   
    def onInputChanged(self, command, inputs, changedInput):
        pass
    def onExecute(self, command, inputs):
        pass
    def onCreate(self, command, inputs):
        pass
     
    def onRun(self):
        global handlers

        try:
            app = adsk.core.Application.get()
            ui = app.userInterface
            commandDefinitions_ = ui.commandDefinitions
            
            # Add command to drop down in nav bar
            if self.command_in_nav_bar:
                
                toolbars_ = ui.toolbars
                navBar = toolbars_.itemById('NavToolbar')
                toolbarControlsNAV = navBar.controls
                
                dropControl = toolbarControlsNAV.itemById(self.DC_CmdId) 
                
                if not dropControl:             
                    dropControl = toolbarControlsNAV.addDropDown(self.DC_CmdId, self.DC_Resources, self.DC_CmdId) 
                
                controls_to_add_to = dropControl.controls
                
                newControl_ = toolbarControlsNAV.itemById(self.cmdId)
            
            # Add command to workspace panel
            else:
                toolbarPanel_ = toolbarPanelById_in_Workspace(self.workspace, self.toolbarPanelID)              
                controls_to_add_to = toolbarPanel_.controls               
                newControl_ = controls_to_add_to.itemById(self.cmdId)
            
            # If control does not exist, create it
            if not newControl_:
                commandDefinition_ = commandDefinitions_.itemById(self.cmdId)
                if not commandDefinition_:
                    commandDefinition_ = commandDefinitions_.addButtonDefinition(self.cmdId, self.commandName, self.commandDescription, self.commandResources)
                
                onCommandCreatedHandler_ = CommandCreatedEventHandler(self)
                commandDefinition_.commandCreated.add(onCommandCreatedHandler_)
                handlers.append(onCommandCreatedHandler_)
                
                newControl_ = controls_to_add_to.addCommand(commandDefinition_)
                newControl_.isVisible = True
        
        except:
            if ui:
                ui.messageBox('AddIn Start Failed: {}'.format(traceback.format_exc()))

    def onStop(self):
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface

            # Remove command from nav bar
            if self.command_in_nav_bar:
                dropDownControl_ = commandControlById_in_NavBar(self.DC_CmdId)
                commandControlNav_ = commandControlById_in_DropDown(self.cmdId, dropDownControl_)
                commandDefinitionNav_ = commandDefinitionById(self.cmdId)
                destroyObject(commandControlNav_)
                destroyObject(commandDefinitionNav_)
                
                if dropDownControl_.controls.count == 0:
                    commandDefinition_DropDown = commandDefinitionById(self.DC_CmdId)
                    destroyObject(dropDownControl_)
                    destroyObject(commandDefinition_DropDown)
            
            # Remove command from workspace panel
            else:
                toolbarPanel_ = toolbarPanelById_in_Workspace(self.workspace, self.toolbarPanelID)         
                commandControlPanel_ = commandControlById_in_Panel(self.cmdId, toolbarPanel_)
                commandDefinitionPanel_ = commandDefinitionById(self.cmdId)
                destroyObject(commandControlPanel_)
                destroyObject(commandDefinitionPanel_)

        except:
            if ui:
                ui.messageBox('AddIn Stop Failed: {}'.format(traceback.format_exc()))

class ExecutePreviewHandler(adsk.core.CommandEventHandler):
    def __init__(self, myObject):
        super().__init__()
        self.myObject_ = myObject
    def notify(self, args):
        try:               
            app = adsk.core.Application.get()
            ui = app.userInterface
            command_ = args.firingEvent.sender
            inputs_ = command_.commandInputs
            if self.myObject_.debug:
                ui.messageBox('***Debug *** Preview: {} execute preview event triggered'.format(command_.parentCommandDefinition.id))
    
            self.myObject_.onPreview(command_, inputs_)
        except:
            if ui:
                ui.messageBox('Input changed event failed: {}'.format(traceback.format_exc()))
class DestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self, myObject):
        super().__init__()
        self.myObject_ = myObject
    def notify(self, args):
        # Code to react to the event.
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface
            command_ = args.firingEvent.sender
            inputs_ = command_.commandInputs
            reason_ = args.terminationReason
            if self.myObject_.debug:
                ui.messageBox('***Debug ***Command: {} destroyed'.format(command_.parentCommandDefinition.id))
                ui.messageBox("***Debug ***Reason for termination= " + str(reason_))
            self.myObject_.onDestroy(command_, inputs_, reason_)
            
        except:
            if ui:
                ui.messageBox('Input changed event failed: {}'.format(traceback.format_exc()))

class InputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self, myObject):
        super().__init__()
        self.myObject_ = myObject
    def notify(self, args):
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface
            command_ = args.firingEvent.sender
            inputs_ = command_.commandInputs
            changedInput_ = args.input 
            if self.myObject_.debug:
                ui.messageBox('***Debug ***Input: {} changed event triggered'.format(command_.parentCommandDefinition.id))
                ui.messageBox('***Debug ***The Input: {} was the command'.format(changedInput_.id))
   
            self.myObject_.onInputChanged(command_, inputs_, changedInput_)
        except:
            if ui:
                ui.messageBox('Input changed event failed: {}'.format(traceback.format_exc()))

class CommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self, myObject):
        super().__init__()
        self.myObject_ = myObject
    def notify(self, args):
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface
            command_ = args.firingEvent.sender
            inputs_ = command_.commandInputs
            if self.myObject_.debug:
                ui.messageBox('***Debug ***command: {} executed successfully'.format(command_.parentCommandDefinition.id))
            self.myObject_.onExecute(command_, inputs_)
            
        except:
            if ui:
                ui.messageBox('command executed failed: {}'.format(traceback.format_exc()))

class CommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self, myObject):
        super().__init__()
        self.myObject_ = myObject
    def notify(self, args):
        try:
            global handlers
            
            app = adsk.core.Application.get()
            ui = app.userInterface
            command_ = args.command
            inputs_ = command_.commandInputs
            
            onExecuteHandler_ = CommandExecuteHandler(self.myObject_)
            command_.execute.add(onExecuteHandler_)
            handlers.append(onExecuteHandler_)
            
            onInputChangedHandler_ = InputChangedHandler(self.myObject_)
            command_.inputChanged.add(onInputChangedHandler_)
            handlers.append(onInputChangedHandler_)
            
            onDestroyHandler_ = DestroyHandler(self.myObject_)
            command_.destroy.add(onDestroyHandler_)
            handlers.append(onDestroyHandler_)
            
            onExecutePreviewHandler_ = ExecutePreviewHandler(self.myObject_)
            command_.executePreview.add(onExecutePreviewHandler_)
            handlers.append(onExecutePreviewHandler_)
            
            if self.myObject_.debug:
                ui.messageBox('***Debug ***Panel command created successfully')
            
            self.myObject_.onCreate(command_, inputs_)
        except:
                if ui:
                    ui.messageBox('Panel command created failed: {}'.format(traceback.format_exc()))