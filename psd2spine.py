import argparse
import json
import math
import os
import sys
from PIL import Image, ImageSequence
from psd_tools import PSDImage

# ------------------------------------------------------------------------------
def isFolder(layer):
	return hasattr(layer, 'layers')

# ------------------------------------------------------------------------------
def isSlotFolder(layer):
	return str.startswith(str(layer.name), 'slot:') and isFolder(layer)

# ------------------------------------------------------------------------------
def isSkinFolder(layer):
	return str.startswith(str(layer.name), 'skin:') and isFolder(layer)

# ------------------------------------------------------------------------------
def isPngLayer(layer):
	return str.endswith(str(layer.name), '.png')

# ------------------------------------------------------------------------------
def getLayerName(layer):
	if (isSlotFolder(layer)):
		return layer.name[5:]
	if (isSkinFolder(layer)):
		return layer.name[5:]
	return layer.name

# ------------------------------------------------------------------------------
def addAttachment(attachmentName, exportInfo, x1, y1, x2, y2):

	# Set current skin to default if it wasn't set by a layer folder
	if exportInfo['skin'] == '':
		setSkin('default', exportInfo)

	slotName = exportInfo['slot']

	skinName = exportInfo['skin']

	attachments = exportInfo['spine']['skins'][skinName]

	attachments[slotName] = { slotName: {
		'name': attachmentName,
		'x': x1,
		'y': y1,
		'rotation': 0,
		'width': x2 - x1,
		'height': y2 - y1,
	}}

	print 'Added attachment ' + attachmentName + '.'

# ------------------------------------------------------------------------------
def addSlot(slotName, exportInfo):

	slots = exportInfo['spine']['slots']

	for slot in slots:
		if slot['name'] == slotName:
			return

	slots.append({
        'name': slotName,
        'bone': 'root',
        'attachment': slotName,
	})

	print 'Added slot ' + slotName + '.'

# ------------------------------------------------------------------------------
def setSlot(slotName, exportInfo):

	exportInfo['slot'] = slotName

# ------------------------------------------------------------------------------
def setSkin(skinName, exportInfo):

	exportInfo['skin'] = skinName

	skins = exportInfo['spine']['skins']

	# Add skin if it wasn't already added
	if skinName not in skins:
		skins[skinName] = {}
		print 'Added skin ' + skinName + '.'

# ------------------------------------------------------------------------------
def export_json(exportInfo):

	spineInfo = exportInfo['spine']

	# Reverse slots so draw order is correct
	spineInfo['slots'] = list(reversed(spineInfo['slots']))

    # Write the JSON output
	name = os.path.splitext(os.path.basename(exportInfo['psdFilename']))[0]
	with open(os.path.join(exportInfo['outputFolder'], '%s.json' % name), 'w') as json_file:
		json.dump(spineInfo, json_file, indent=4)

	print 'Exported Spine JSON.'

# ------------------------------------------------------------------------------
def export_layer(layer, exportInfo):

	psd = exportInfo['psd']

	x1 = sys.maxint
	y1 = sys.maxint
	x2 = 0
	y2 = 0

	if isFolder(layer):
		for subLayer in layer.layers:
			if subLayer.bbox.x1 < x1:
				x1 = subLayer.bbox.x1

			if subLayer.bbox.y1 < y1:
				y1 = subLayer.bbox.y1

			if subLayer.bbox.x2 > x2:
				x2 = subLayer.bbox.x2

			if subLayer.bbox.y2 > y2:
				y2 = subLayer.bbox.y2

	width = x2 - x1
	height = y2 - y1

	x1 += math.floor(width / 2)
	y1 += math.floor(height / 2)

	x2 += math.floor(width / 2)
	y2 += math.floor(height / 2)

    # Center the image on Spine's x origin,
	x1 -= math.floor(psd.header.width / 2)
	x2 -= math.floor(psd.header.width / 2)

    # Compensate for y axis going from top to bottom, vs Spine
    # going bottom to top
	y1 = psd.header.height - y1
	y2 = psd.header.height - y2

	addAttachment(layer.name, exportInfo, x1, y1, x2, y2)

	image = layer.as_PIL()
	if image is not None:
		image.save(os.path.join(exportInfo['outputFolder'], layer.name))
		print 'Saved attachment layer image for layer ' + layer.name + '.'
	else:
		print 'Image was not exported. Layer is empty.'

# ------------------------------------------------------------------------------
def process_layer(layer, exportInfo):

	if isSkinFolder(layer):
		layerName = getLayerName(layer)
		setSkin(layerName, exportInfo)

	if isSlotFolder(layer):
		layerName = getLayerName(layer)
		addSlot(layerName, exportInfo)
		setSlot(layerName, exportInfo)

	if isPngLayer(layer):
		export_layer(layer, exportInfo)

	if isFolder(layer):
		for subLayer in layer.layers:
			process_layer(subLayer, exportInfo)

# ------------------------------------------------------------------------------
def check_layer(layer):

	if not layer.visible:
		print '!!! Layer ' + layer.name + ' is not visible and will not be exported with images.'

# ------------------------------------------------------------------------------
def process_psd(psdFilename, exportInfo):

	psd = PSDImage.load(psdFilename)

	exportInfo['psd'] = psd

	for layer in psd.layers:
		check_layer(layer)

	for layer in psd.layers:
		process_layer(layer, exportInfo)

	export_json(exportInfo)

# ------------------------------------------------------------------------------
parser = argparse.ArgumentParser(description='Creates images and JSON from a PSD for import into Spine.')

parser.add_argument('filename', help='The PSD file to process.')
parser.add_argument('outputFolder', nargs='?', default=os.getcwd(), help='The output folder for images and JSON.')

args = parser.parse_args()

if os.path.exists(args.filename):

	if not os.path.exists(args.outputFolder):
		print 'Created output folder ' + args.outputFolder + '.'
		os.makedirs(args.outputFolder)

	spineInfo = {
        'bones': [{'name': 'root'}],
        'slots': [],
        'skins': {},
        'animations': {}
    }

	exportInfo = {
        'psdFilename': args.filename,
        'outputFolder': args.outputFolder,
        'slot': '',
        'skin': '',
        'spine': spineInfo,
    }

	setSkin('default', exportInfo)

	process_psd(args.filename, exportInfo)
else:
    print args.filename + " does not exist."