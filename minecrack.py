#!/usr/bin/env python

import os, random
from string import split
from math import sin, cos
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
		self.tris = []

		self.yrot = 90.0
		self.xpos = .45
		self.zpos = .50

		self.lookupdown = 0.0

		self.LightAmbient  = (GLfloat*4)(0.5, 0.5, 0.5, 1.0)
		self.LightDiffuse  = (GLfloat*4)(1.0, 1.0, 1.0, 1.0)
		self.LightPosition = (GLfloat*4)(0.0, 0.0, 2.0, 1.0)		
		
		self.window = pyglet.window.Window(width=1024, height=768, caption="Minecrack", visible=False)
		self.glInit()
		self.worldInit()
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
		glLightfv( GL_LIGHT1, GL_AMBIENT, self.LightAmbient)
		glLightfv( GL_LIGHT1, GL_DIFFUSE, self.LightDiffuse)
		glLightfv( GL_LIGHT1, GL_POSITION, self.LightPosition)
		glEnable(GL_LIGHT1)
		self.lookupdown    = 0.0
		glColor4f( 1.0, 1.0, 1.0, 0.5)
		
	def loadTextures(self):
		texturefile = os.path.join('data','0.jpg')
		textureSurface = image.load(texturefile)

		t1=textureSurface.image_data.create_texture(image.Texture)
		glBindTexture(GL_TEXTURE_2D, t1.id)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
	
		t2=textureSurface.image_data.create_texture(image.Texture)
		glBindTexture(GL_TEXTURE_2D, t2.id)
		glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR )
		glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )

		t3=textureSurface.mipmapped_texture
		glBindTexture( GL_TEXTURE_2D, t3.id)
		glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_NEAREST )
		glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )

		self.textures = [t1,t2,t3]

	def worldInit(self):
		self.tris = []
		verts = 0
		tri = []
		#for line in open(os.path.join("data", "world.txt")):
	
		for line in open("world2.txt"):
			vals = split(line)
			if len(vals) != 5:
				continue
			if vals[0] == '//':
				continue
		
			vertex = []
			for val in vals:
				vertex.append(float(val))
			tri.append(vertex)
			if (len(tri) == 3):
				self.tris.append(tri)
				tri = []
				
	def eventInit(self):
		self.window.on_resize = self.on_resize
		self.window.on_key_press = self.on_key_press
		self.window.on_key_release = self.on_key_release

	def on_resize(self, width, height):
		if height==0:
			height=1.0
		glViewport(0, 0, width, height)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(60, float(width)/height, 0.01, 100.0)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		
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

	def updateFrame(self):
		global piover180
		
		if self.getKeyState(key.RIGHT):
			self.yrot -= 2.5
			
		if self.getKeyState(key.LEFT):
			self.yrot += 2.5
			
		if self.getKeyState(key.UP):
			self.xpos -= sin(self.yrot * piover180) * 0.025
			self.zpos -= cos(self.yrot * piover180) * 0.025
			
		if self.getKeyState(key.DOWN):
			self.xpos += sin(self.yrot * piover180) * 0.025
			self.zpos += cos(self.yrot * piover180) * 0.025

	def draw(self):
		xtrans = -self.xpos
		ztrans = -self.zpos
		ytrans = -.20
		sceneroty = 360.0 - self.yrot

		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glLoadIdentity()
		glRotatef(self.lookupdown, 1.0, 0.0 , 0.0)
		glRotatef(sceneroty, 0.0, 1.0 , 0.0)
		glTranslatef(xtrans, ytrans, ztrans)

		glBindTexture(GL_TEXTURE_2D, self.textures[self.filter].id)

		for tri in self.tris:
			glBegin(GL_TRIANGLES)
			glNormal3f( 0.0, 0.0, 1.0)
		
			glTexCoord2f(tri[0][3], tri[0][4])
			glVertex3f(tri[0][0]/10.0, tri[0][1]/10.0, tri[0][2]/10.0)

			glTexCoord2f(tri[1][3], tri[1][4])
			glVertex3f(tri[1][0]/10.0, tri[1][1]/10.0, tri[1][2]/10.0)

			glTexCoord2f(tri[2][3], tri[2][4])
			glVertex3f(tri[2][0]/10.0, tri[2][1]/10.0, tri[2][2]/10.0)

			glEnd()

	def run(self):
		self.window.set_visible()
		clock = pyglet.clock.Clock()

		while not self.window.has_exit:
			self.window.dispatch_events()
			self.updateFrame()
			self.draw()
			self.window.flip()
			
			dt = clock.tick()

		print "fps:  %d" % clock.get_fps()


def main():
	mw = MineWindow()
	mw.run()

if __name__ == "__main__":
	main()
