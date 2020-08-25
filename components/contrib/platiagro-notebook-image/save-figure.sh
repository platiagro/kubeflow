#!/bin/bash
cat << EOF > save_figure.py
#!/opt/conda/bin/python
from json import loads
from platiagro import save_figure


with open("output.ipynb", "rb") as notebook_file:
	notebook = loads(notebook_file.read())
	cells = notebook['cells']
	for cell in cells:
		if 'outputs' in cell:
			outputs = cell['outputs']
			for output in outputs:
				if 'data' in output:
					data = output['data']
					keys = data.keys()
					for key in keys:
						if 'image' in key:
							save_figure(figure=data[key], extension=key.split('/')[1])

EOF

chmod 755 save_figure.py
./save_figure.py
