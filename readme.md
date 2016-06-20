# psd2spine #

Creates PNG images and JSON from a PSD for import into Spine.

Requires psd-tools and Pillow.
pip install psd-tools
pip install Pillow

# Usage #

psd2spine.py filename [outputFolder]

filename - The PSD file to process.
outputFolder - The output folder for images and JSON.

# PSD Structure #

A folder layer with the prefix 'skin:' will set the current skin to the specified name.

A folder layer with the prefix 'slot:' will set the current slot to the specified name.

A folder layer with the suffix '.png:' will be exported to a PNG file with the specified name. During export, any layers within a PNG folder layer will be merged into one output image.

e.g. the following PSD file:

+ skin:default
	+ slot:eyes
		+ default_eyes.png
			- PUPIL INK
			- PUPIL PAINT
			- EYES INK
			- EYES PAINT
	+ slot:head
		+ default_head.png
			- HEAD INK
			- HEAD PAINT

where + is a folder layer and - is a normal layer,
would generate images and Spine JSON with:
	2 slots named 'eyes' and 'head'.
	2 skin placeholders named 'eyes' and 'head' in the respective slots.
	2 attachments named 'default_eyes.png' and 'default_head.png'.