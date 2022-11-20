def _WriteToGML(dst,n,fts):
	with open(f"{dst}\\{n}.gml") as f:
		f.write(fts)