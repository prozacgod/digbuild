#!/usr/bin/env python
#import cProfile

# prozacgod's minecraft clone... shitty!
# walk with arrow keys, and leave with esc!

#TODO: if you walk at a very perfect 45 towards a corner, you can enter a block!

import os, random
from string import split
from math import sin, cos, trunc
from pyglet.gl import *
from pyglet import window
from pyglet import image
from pyglet.window import key
import pyglet.clock

from minemap import MineMap

piover180 = 0.0174532925

class MineWindow(object):
	def __init__(self):
		platform = pyglet.window.get_platform()
		display = platform.get_default_display()
		screen = display.get_default_screen()

		template = pyglet.gl.Config(alpha_size=8)
		config = screen.get_best_config(template)
		context = config.create_context(None)
		
		self.textures = []
		self.filter = 0
		self.quad = []

		self.yrot = 270.0
		self.xpos = 2
		self.zpos = 2
		self.ypos = 1.5

		self.lookupdown = 0.5

		self.LightAmbient  = (GLfloat*4)(0.5, 0.5, 0.5, 1.0)
		self.LightDiffuse  = (GLfloat*4)(1.0, 1.0, 1.0, 1.0)
		self.LightPosition = (GLfloat*4)(0.0, 0.0, 2.0, 1.0)		
		
		self.window = pyglet.window.Window(caption="Minecrack", visible=False, resizable=True, vsync=False, fullscreen=True)
		self.w_width = 2560
		self.w_height = 1440
		self.glInit()
		self.worldInit()
		
		self.createMapDisplayList()

		self.eventInit()
		
		self.key_state = {}
		
	def glInit(self):
		glEnable(GL_TEXTURE_2D)
		self.loadTextures()
		glShadeModel(GL_SMOOTH)
		glClearColor(0.0, 0.0, 0.0, 0.0)
		glClearDepth(1.0)
		glEnable(GL_DEPTH_TEST)
		glDepthFunc(GL_LEQUAL)
		glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
		#glLightfv( GL_LIGHT1, GL_AMBIENT, self.LightAmbient)
		#glLightfv( GL_LIGHT1, GL_DIFFUSE, self.LightDiffuse)
		#glLightfv( GL_LIGHT1, GL_POSITION, self.LightPosition)
		#glEnable(GL_LIGHT1)
		#glColor4f( 1.0, 1.0, 1.0, 0.5)		
	
	def drawMap(self):
		by_texture = {}
		for quad in self.mine_map.quads:
			if (not quad[4] in by_texture):
				by_texture[quad[4]] = [quad]
			else:
				by_texture[quad[4]] += [quad]

		for texture_i in by_texture:
			quads = by_texture[texture_i]
			
			glBindTexture(GL_TEXTURE_2D, self.textures[texture_i].id)
			glBegin(GL_QUADS)
			for quad in quads:
				glNormal3f(0.0, 0.0, 1.0)
				glTexCoord2f(0.0, 0.0)
				glVertex3f(quad[0][0], quad[0][1], quad[0][2])

				glTexCoord2f(1.0, 0.0)
				glVertex3f(quad[1][0], quad[1][1], quad[1][2])

				glTexCoord2f(1.0, 1.0)
				glVertex3f(quad[2][0], quad[2][1], quad[2][2])

				glTexCoord2f(0.0, 1.0)
				glVertex3f(quad[3][0], quad[3][1], quad[3][2])
			glEnd()    
		
	def createMapDisplayList(self):
		glNewList(1, GL_COMPILE)
		self.drawMap()
		glEndList();
	
		
	def loadTextures(self):
		for i in range(6):
			texturefile = os.path.join('data', str(i) + '.jpg')
			textureSurface = image.load(texturefile)
		
			gl_texture = textureSurface.mipmapped_texture
			glBindTexture(GL_TEXTURE_2D, gl_texture.id)
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

			self.textures += [gl_texture]

	def worldInit(self):
		self.mine_map = MineMap('minemap.txt')
		print len(self.mine_map.quads)
			
	def eventInit(self):
		self.window.on_resize = self.on_resize
		self.window.on_key_press = self.on_key_press
		self.window.on_key_release = self.on_key_release
		self.window.on_mouse_motion = self.on_mouse_motion

	def on_resize(self, width, height):
		if height==0:
			height=1.0
		glViewport(0, 0, width, height)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(60, float(width)/height, 0.02, 100.0)
		glMatrixMode(GL_MODELVIEW)
		
	def on_key_press(self, sym, mod):
		self.key_state[(sym,mod)] = True
		
	def on_key_release(self, sym, mod):
		self.key_state[(sym,mod)] = False
		
		if sym == key.ESCAPE:
			self.window.has_exit = True
		elif sym == key.F:
			self.filter +=1
			if self.filter == 3:
				self.filter = 0

	def getKeyState(self, sym, mod=0):
		if (sym, mod) in self.key_state:
			return self.key_state[(sym,mod)]
		return False

	def on_mouse_motion(self, x, y, dx, dy):
		self.yrot -= dx;
		self.lookupdown -= dy
		pass

	def updateFrame(self):
		global piover180
		xpos = self.xpos
		ypos = self.ypos
		zpos = self.zpos

		currentCell = self.mine_map.getCell(trunc(xpos), trunc(zpos), trunc(xpos))
		
		#if self.getKeyState(key.RIGHT):
		#	self.yrot -= 2.5
			
		#if self.getKeyState(key.LEFT):
		#	self.yrot += 2.5
			
		if self.getKeyState(key.W):
			xpos -= sin(self.yrot * piover180) * 0.025
			zpos -= cos(self.yrot * piover180) * 0.025
			
		if self.getKeyState(key.S):
			xpos += sin(self.yrot * piover180) * 0.025
			zpos += cos(self.yrot * piover180) * 0.025
			
		if self.getKeyState(key.D):
			xpos += sin((self.yrot+90) * piover180) * 0.025
			zpos += cos((self.yrot+90) * piover180) * 0.025
			
		if self.getKeyState(key.A):
			xpos += sin((self.yrot-90) * piover180) * 0.025
			zpos += cos((self.yrot-90) * piover180) * 0.025

		cellX = trunc(xpos)
		cellY = trunc(ypos)
		cellZ = trunc(zpos)
		
		icellX = xpos - cellX
		icellY = ypos - cellY
		icellZ = zpos - cellZ
				
		left = self.mine_map.getCell(cellX - 1, cellZ, cellY)
		right = self.mine_map.getCell(cellX + 1, cellZ, cellY)
		fore = self.mine_map.getCell(cellX, cellZ-1, cellY)
		aft = self.mine_map.getCell(cellX, cellZ+1, cellY)
		
		down = self.mine_map.getCell(cellX, cellZ, cellY-1)
		below = self.mine_map.getCell(cellX, cellZ, cellY-1)
		
		if (icellX < .10) and (left > 0):
			xpos = cellX + .10
			
		if (icellX > .90) and (right > 0):
			xpos = cellX + .90
		
		if (icellZ < .10) and (fore > 0):
			zpos = cellZ + .10
			
		if (icellZ > .90) and (aft > 0):
			zpos = cellZ + .90

		#if (icellY 
		
		self.xpos = xpos
		self.ypos = ypos
		self.zpos = zpos
		

	def draw(self):
		xtrans = -self.xpos
		ztrans = -self.zpos
		ytrans = -self.ypos
		sceneroty = 360.0 - self.yrot

		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glLoadIdentity()
		glRotatef(self.lookupdown, 1.0, 0.0 , 0.0)
		glRotatef(sceneroty, 0.0, 1.0 , 0.0)
		glTranslatef(xtrans, ytrans, ztrans)
			
		glCallList(1);
		#self.drawMap();

	def run(self):
		self.window.set_visible()
		self.window.set_mouse_visible(False)
		self.window.set_exclusive_mouse(True)

		clock = pyglet.clock.Clock()
		fps_display = pyglet.clock.ClockDisplay()
		while not self.window.has_exit:
			self.window.dispatch_events()
			self.updateFrame()
			fps_display.draw()
			self.draw()
			self.window.flip()
			
			dt = clock.tick()

		print "fps:  %d" % clock.get_fps()


def main():
	mw = MineWindow()
	mw.run()

if __name__ == "__main__":
	main()
