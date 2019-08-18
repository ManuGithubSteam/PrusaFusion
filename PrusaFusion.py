# Author-Patrick Rainsberry
# Description-Directly publish to OctoPrint

# Referenced heavily from: https://github.com/boboman/Octonomous/blob/master/Octonomous.py


from .prusaFusionCommand import prusaFusionCommand


commands = []
command_defs = []

# Define parameters for command
cmd = {
        'commandName': 'PrusaFusion',
        'commandDescription': 'Export model to PrusaSlicer over SSH to another (linux) machine.',
        'commandResources': './Resources/PrusaFusion',
        'cmdId': 'PrusaFusion_CmdId',
        'workspace': 'FusionSolidEnvironment',
        'toolbarPanelID': 'SolidMakePanel',
        'class' : prusaFusionCommand
}
command_defs.append(cmd)

# Set to True to display various useful messages when debugging your app
debug = False

for cmd_def in command_defs:
    # Creates the commands for use in the Fusion 360 UI
    command = cmd_def['class'](cmd_def, debug)
    commands.append(command)

def run(context):
    for command in commands:
        command.onRun()


def stop(context):
    for command in commands:
        command.onStop()


