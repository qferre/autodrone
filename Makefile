blender_install_dependencies:
	# & "C:\Program Files (x86)\Steam\steamapps\common\Blender\4.1\python\bin\python.exe" -m pip install -r requirements.txt --upgrade --force-reinstall


tests:
	directory="/tests"
	for file in "$directory"/*; do
		blender scenes/basic.blend --background --python "$file"
	done

# & "C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe" scenes/basic.blend --background --python scripts/main.py -- --start_pos 0,0,2 --index_path "scenes\basic.index"