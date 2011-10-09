def split_len(seq, length):
    return [seq[i:i+length] for i in range(0, len(seq), length)]

class MineMap():
	def __init__(self, mapfile = None):
		if mapfile:
			self.mapfile_name = mapfile
			self.loadMapString(open(mapfile, 'r').read())

	def loadMapString(self, data):
		cellMap = "0123456789abcdefghijklmnopqrstuvwxyz"
		print "// Parsing"
		layers = data.split('\n\n')
		settings = layers[0].split('\n')
		self.map = [[[cellMap.find(cell) for cell in split_len(row,1)] for row in layer.split('\n')] for layer in layers[1:]]
		self.resolution = tuple([int(x) for x in settings[0].split(',')])
	
		# removes last layer if its empty, and only then
		if len(self.map) == self.resolution[2] + 1:
			if len(self.map[::-1][0]) == 1:
				if  len(self.map[::-1][0][0]) == 0:
					self.map = self.map[:-1]
		
		print "// Validating"
		if len(self.map) == self.resolution[2]:
			for z in range(self.resolution[2]):
				if len(self.map[z]) == self.resolution[1]:
					for y in range(self.resolution[1]):
						if len(self.map[z][y]) != self.resolution[0]:
							raise Exception("Invalid column count in Layer: %d Row: %d" % (layer, row))
				else:
					raise Exception("Invalid row count in Layer: %d" % layer)
		else:
			raise Exception("Invalid layer count in map")
			
		self.quadrateMap()
		
	def quadrateMap(self):
		print "// Quadrating"
		self.quads = []
		for z in range(-1, self.resolution[2]+1):
			for y in range(-1, self.resolution[1]+1):
				for x in range(-1, self.resolution[0]+1):
					self.quads += self.quadrateCell(x, y, z)
		
	def quadrateCell(self, x, y, z):
		cc = self.getCell(x, y, z)
		if (cc < 0):
			return []
		left = self.getCell(x-1,y,z)
		right = self.getCell(x+1,y,z)
		fore = self.getCell(x,y-1,z)
		aft = self.getCell(x,y+1,z)
		down = self.getCell(x,y,z-1)
		up = self.getCell(x,y,z+1)

		#print "L", left, "R", right, ':', "F", fore, "A", aft,  ':', "U", up, "D", down
		cc = self.getCell(x, y, z)
		quads = []
		
		cube = [
			(x,   z  , y+1),
			(x+1, z  , y+1),
			(x+1, z  , y, ),
			(x,   z  , y, ),
			(x,   z+1, y+1),
			(x+1, z+1, y+1),
			(x+1, z+1, y, ),
			(x,   z+1, y, ),
		]
		
		if (left < 0):
			quads += [(cube[0] + (0.0, 0.0), cube[3] + (1.0, 0.0), cube[7] + (1.0, 1.0), cube[4] + (0.0, 1.0), cc)]
		if (right < 0):
			quads += [(cube[1] + (0.0, 0.0), cube[2] + (1.0, 0.0), cube[6] + (1.0, 1.0), cube[5] + (0.0, 1.0), cc)]

		if (fore < 0):
			quads += [(cube[2] + (0.0, 0.0), cube[3] + (1.0, 0.0), cube[7] + (1.0, 1.0), cube[6] + (0.0, 1.0), cc)]
		if (aft < 0):
			quads += [(cube[0] + (0.0, 0.0), cube[1] + (1.0, 0.0), cube[5] + (1.0, 1.0), cube[4] + (0.0, 1.0), cc)]


		if (down < 0):
			quads += [(cube[3] + (0.0, 0.0), cube[2] + (1.0, 0.0), cube[1] + (1.0, 1.0), cube[0] + (0.0, 1.0), cc)]
		if (up < 0):
			quads += [(cube[4] + (0.0, 0.0), cube[5] + (1.0, 0.0), cube[6] + (1.0, 1.0), cube[7] + (0.0, 1.0), cc)]

		return quads
					
	def getCell(self, x, y, z):
		if (x < 0) or (y < 0) or (x >= self.resolution[0]) or (y >= self.resolution[1]):
			return 0
		if (z < 0):
			return 1
		if (z >= self.resolution[2]):
			return 2
			
		cell = self.map[z][y][x]
		
		return cell
		
	def convertTriangles(self):
		result = []
		for quad in self.quads:
			result += [(quad[0], quad[1], quad[2])]
			result += [(quad[0], quad[2], quad[3])]
			
		return result
	
