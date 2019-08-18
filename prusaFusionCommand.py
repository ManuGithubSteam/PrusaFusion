import adsk.core, traceback
import adsk.fusion

import tempfile
import json
import webbrowser
from .packages import requests
from .packages.requests_toolbelt import MultipartEncoder

from xml.etree import ElementTree
from xml.etree.ElementTree import SubElement

from os.path import expanduser
import os
import sys
import subprocess
import time

from .Fusion360CommandBase import Fusion360CommandBase


# Creates directory and returns file name for settings file
def get_file_name():
    # Get Home directory
    home = expanduser("~")
    home += '/PrusaFusion/'

    # Create if doesn't exist
    if not os.path.exists(home):
        os.makedirs(home)

    # Create file name in this path
    xmlFileName = home + 'settings.xml'
    return xmlFileName


# Writes user settings to a file in local home directory
def write_settings(xml_file_name, key, host):
    # If file doesn't exist create it
    if not os.path.isfile(xml_file_name):
        new_file = open(xml_file_name, 'w')
        new_file.write('<?xml version="1.0"?>')
        new_file.write("<PrusaFusion /> ")
        new_file.close()
        tree = ElementTree.parse(xml_file_name)
        root = tree.getroot()
    # Otherwise delete existing settings
    else:
        tree = ElementTree.parse(xml_file_name)
        root = tree.getroot()
        root.remove(root.find('settings'))

    # Write settings
    settings = SubElement(root, 'settings')
    SubElement(settings, 'host', value=host)
    SubElement(settings, 'key', value=key)
    tree.write(xml_file_name)


# Read user settings in from XML file 
def read_settings(xmlFileName):
    # Get the root of the XML tree
    tree = ElementTree.parse(xmlFileName)
    root = tree.getroot()

    # Get the settings values
    host = root.find('settings/host').attrib['value']
    key = root.find('settings/key').attrib['value']

    return host, key

# Export an STL file of selection to local temp directory
def export_file(stl_refinement, selection, filename):

    # Get the ExportManager from the active design.
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    export_mgr = design.exportManager

    # Set model units to mm for export to cura engine
    fusion_units_manager = design.fusionUnitsManager
    current_units = fusion_units_manager.distanceDisplayUnits
    fusion_units_manager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits

    # Create a temporary directory.
    temp_dir = tempfile.mkdtemp()

    # If you want to randomize the file name
    # resultFilename = tempDir + '//' + str(uuid.uuid1())

    # Create temp file name 
    result_filename = temp_dir + '//' + filename
    result_filename = result_filename + '.stl'

    # Create export options for STL export    
    stl_options = export_mgr.createSTLExportOptions(selection, result_filename)

    # Set export options based on refinement drop down: 
    if stl_refinement == 'Low':
        stl_options.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementLow
    elif stl_refinement == 'Medium':
        stl_options.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementMedium
    elif stl_refinement == 'High':
        stl_options.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh

    # Execute Export command
    export_mgr.execute(stl_options)

    fusion_units_manager.distanceDisplayUnits = current_units

    return result_filename


# Get the current values of the command inputs.
def get_inputs(inputs):
    try:
        stlRefinementInput = inputs.itemById('stlRefinement')
        stlRefinement = stlRefinementInput.selectedItem.name

        selection = inputs.itemById('selection').selection(0).entity
        if selection.objectType == adsk.fusion.Occurrence.classType():
            selection = selection.component

     
        key = inputs.itemById('key').text
      
        host = inputs.itemById('host').text
        saveSettings = inputs.itemById('saveSettings').value

        return stlRefinement, selection, key, host, saveSettings
    except:
        app = adsk.core.Application.get()
        ui = app.userInterface
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


############# Create your Actions Here #################################################
class prusaFusionCommand(Fusion360CommandBase):
    # Runs when when any input in the command dialog is changed
    def onInputChanged(self, command, inputs, changedInput):

        # Get current input values
        host = inputs.itemById('host').text
        key = inputs.itemById('key').text

    # Runs when the user presses ok button
    def onExecute(self, command, inputs):

        # Get the inputs.
        (stlRefinement, selection, key, host, saveSettings) = get_inputs(
            inputs)
        filename = selection.name

        # Export the selected file as an STL to temp directory            
        result_filename = export_file(stlRefinement, selection, filename)

        # Optionally save the users settings to a local XML
        if saveSettings:
            xml_file_name = get_file_name()
            write_settings(xml_file_name, key, host)

        # Connect to the host server and upload the new file
        pscpPath = os.getcwd() + '\\Api\\InternalAddins\\PrusaFusion\\Resources\\'
        subprocess.call([pscpPath + 'pscp.exe', '-pw', key , result_filename, host +':/tmp'],shell=True)
        # let the daemon know there is a new file.
        username,ip = host.split("@")
        helperPath= '/home/'+username+'/.PrusaSlicer/fusion_helper.sh'
        subprocess.call([pscpPath + 'plink.exe','-batch', '-pw', key , host, helperPath, filename+'.stl'  ],shell=True)
        

    # Runs when user selects your command from Fusion UI, Build UI here
    def onCreate(self, command, inputs):

        inputs.addImageCommandInput('image1', '', './/Resources//octoprint-logo.png')
        inputs.addTextBoxCommandInput('labelText2', '',
                                      '<a href="http://github.org">Github</a></span> Export from am Virtual Machine to Prusa Slicer on a Linux Host',
                                      4, True)
        inputs.addTextBoxCommandInput('labelText3', '',
                                      'Choose the file type and selection to send to Octoprint for quotes.', 2, True)

        stldropDown = inputs.addDropDownCommandInput('stlRefinement', 'STL refinement',
                                                     adsk.core.DropDownStyles.LabeledIconDropDownStyle)
        stldropDown.listItems.add('Low', False)
        stldropDown.listItems.add('Medium', False)
        stldropDown.listItems.add('High', True)

        selection = inputs.addSelectionInput('selection', 'Selection', 'Select the component to print')
        selection.addSelectionFilter('Occurrences')
        selection.addSelectionFilter('RootComponents')
        #            selection.addSelectionFilter('SolidBodies')

        host_input = inputs.addTextBoxCommandInput('host', 'SSH to host: ', 'user@192.168.0.155',
                                                   1, False)
        key_input = inputs.addTextBoxCommandInput('key', 'Password: ', 'Password for user', 1, False)

        inputs.addBoolValueInput("saveSettings", 'Save settings?', True)

        command.setDialogInitialSize(300, 300)
        command.setDialogMinimumSize(300, 300)

        command.okButtonText = 'Ok'

        # Get filename for settings file
        xml_file_name = get_file_name()

        # If there is a local settings file apply the values
        if os.path.isfile(xml_file_name):
            (host, key) = read_settings(xml_file_name)
            host_input.text = host
            key_input.text = key

           
