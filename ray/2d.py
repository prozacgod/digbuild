#!/usr/bin/env python
import math, os, sys, random
from time import sleep

import pygame
from pygame import *
pygame.init()

cell_size = 16

def bresenhamLine(x0, y0, x1, y1):
	dx = abs(x1-x0)
	dy = abs(y1-y0) 
	
	sx = 1 if x0 < x1 else -1
	sy = 1 if y0 < y1 else -1

	err = dx - dy
	result = []
	while True:
		result += [(x0,y0)]
	 	if (x0 == x1) and (y0 == y1):
	 		break
	 		
		e2 = 2*err
		if e2 > -dy: 
			err = err - dy
			x0 = x0 + sx
		if e2 < dx:
			err = err + dx
			y0 = y0 + sy 
			
	return result
	
class bresenhamRay:
	"""bresenhamRay(x0, y0, x1, y1) generates an infinite number of points starting at x0, y0 and going through x1, y1"""
	
	def __init__(self, x0, y0, x1, y1):
		self.x0 = x0
		self.y0 = y0
		self.x1 = x1
		self.y1 = y1
		
		self.x = x0
		self.y = y0
		self.i = 0
			
		self.dx = abs(x1-x0)
		self.dy = abs(y1-y0)
	
		self.sx = 1 if x0 < x1 else -1
		self.sy = 1 if y0 < y1 else -1

		self.err = self.dx - self.dy
		self.complete = False
		
	def __iter__(self):
		return self
	
	def next(self):
		result = (self.i, self.x, self.y)
		
		if (self.x == self.x1) and (self.y == self.y1):
			self.complete = True
			
	 	self.i +=1
	 	
		e2 = 2*self.err
		if e2 > -self.dy: 
			self.err = self.err - self.dy
			self.x = self.x + self.sx
		if e2 < self.dx:
			self.err = self.err + self.dx
			self.y = self.y + self.sy 
			
		return result
	   
		
def traceScene(trace_width, trace_fov, player_map, cell_size, player_x, player_y, angle):
	trace_fov = math.radians(trace_fov)
	angleRad = math.radians(angle)
	
	cell_x = math.floor(float(player_x) / cell_size)
	cell_y = math.floor(float(player_y) / cell_size)

	cell_xofs = player_x - (cell_x * cell_size)
	cell_yofs = player_y - (cell_y * cell_size)
	
	result = []   # trace distances
	
	start_angleRad = angleRad - (trace_fov / 2)
	
	for ray in range(trace_width):
		cast_angleRad = start_angleRad + (ray * trace_fov / trace_width)
		
		w_x1 = math.sin(cast_angleRad) * 100 + player_x
		w_y1 = math.cos(cast_angleRad) * 100 + player_y
		
		cell_x1 = math.sin(cast_angleRad) * 100 + cell_x
		cell_y1 = math.cos(cast_angleRad) * 100 + cell_y
		
		caster = bresenhamRay(int(cell_x), int(cell_y), int(cell_x1), int(cell_y1))
		last_point = (0, int(cell_x), int(cell_y))
		for point in caster:
			if point[0] > 500:
				break
				
			px = point[1]
			py = point[2]
			
			if (px < 0) or (py < 0) or (py > len(player_map)) or (px > len(player_map[0])):
				break;
				
			if player_map[point[2]][point[1]] >= 0:
				break
				
			last_point = point
		
		world_x = point[1] * cell_size
		world_y = point[2] * cell_size
		# point found, now we have to figure out its world_x, world_y
		# that depends on its direction		"""
		if caster.sx < 0:  # more east
			world_x += cell_size

		if caster.sy < 0:  # more north
			world_y += cell_size
		
		slope = math.cos(cast_angleRad) / max(.000000000000001, math.sin(cast_angleRad))



		# now we have to find the cell surface offset, need to know what side I hit first
		
		#wx = world_x - player_x
		#wy = world_y - player_y
		
		#if caster.dx > caster.dy:
		#	 if I move more in my x than my x, then I'm moving east to west so world_x is fixed
		#	wy = slope * wx + wy
		#else:
		#	#slope = math.cos(cast_angleRad) / math.sin(cast_angleRad)
		#	world_x = slope
		
		#world_y = player_y + wy	
			
		xdist = player_x - world_x
		ydist = player_y - world_y
		dist = math.sqrt(xdist*xdist + ydist*ydist)
			
		result += [(player_x, player_y, world_x, world_y, dist)]
	return result	
		
def cosineDeconvolute(self, trace_distances):
	"""cosineDeconvolute, removes circular distortions from the ray trace based on current FOV"""
	return trace_distances


playerMap = [
	"00000000000000000000",
	"0                  0",
	"0                  0",
	"0          00      0",
	"0           0      0",
	"0                  0",
	"0     000    0     0",
	"0                  0",
	"0                  0",
	"0                  0",
	"0                  0",
	"0                  0",
	"0                  0",
	"0                  0",
	"0                  0",
	"00000000000000000000"
]	

# convert textual map into 2d integer array
playerMap = [["0123456789".find(cell) for cell in line] for line in playerMap]

def main(playerMap):
	global cell_size
	
	screen = pygame.display.set_mode((640,480))
	pygame.display.set_caption('2d voxel ray tracing')

	running = True
	
	mapColors = [
		(0, 255, 0)
	]

	frame = 0
	
	player_x = 3*cell_size 
	player_y = 3*cell_size

	mapOfsX = 0
	mapOfsY = 0
	displayOfsX = 100
	displayOfsY = 100
	displayWidth = 320
	displayHeight = 200

	
	while running:
		for event in pygame.event.get():
			if event.type == QUIT:
				running = False
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				running = False

		pressed = pygame.key.get_pressed()

		screen.fill((0,0,0))
		
		
		for y in range(len(playerMap)):
			for x in range(len(playerMap[0])):
				cell = playerMap[y][x]
				if cell >= 0:
					rr = (mapOfsX + x * cell_size, mapOfsY + y * cell_size, cell_size, cell_size)
					screen.fill(mapColors[cell], rr)
					pygame.draw.rect(screen, (255,0,0), rr, 1)


		rays = traceScene(displayWidth, 60, playerMap, cell_size, player_x, player_x,  frame % 360)
	
		for i in range(len(rays)):
			ray = rays[i]
			
			pygame.draw.line(screen, (255,255,255), (ray[0], ray[1]), (ray[2], ray[3]))
			"""
			d = ray[4] * 10
			
			c = 255 - d
			if c < 0:
				c = 0;
				
			h = min(displayHeight, displayHeight-d)
			y = displayOfsY + displayHeight/2 - h/2
			pygame.draw.line(screen, (c,c,c),
				(displayOfsX + i, y),
				(displayOfsX + i, y+h)
			 )
			"""

		
		pygame.display.flip()
		frame += 1

main(playerMap)
