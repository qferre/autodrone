blender_install_dependencies:
	blender --background --python install_dependencies_blender.py
	# TODO REWRITE THIS USING BLENDER PATH AND THE PIP OF BLENDER

tests:
	# Tests may necessitate a Blender file to operate on
	# for test file in test directory :
	# blender scenes/scene.blend --background --python $test


