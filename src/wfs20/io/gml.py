def _WriteToGML(reader,out):
	with open(f"{out}\\{reader.Keyword}.gml","w") as f:
		f.write(reader.gml.decode())