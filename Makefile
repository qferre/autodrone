blender_install_dependencies:
	blender --background --python install_dependencies_blender.py
	# TODO REWRITE THIS USING BLENDER PATH AND THE PIP OF BLENDER

tests:
	directory="/tests"
	for file in "$directory"/*; do
		blender scenes/scene.blend --background --python "$file"
	done


