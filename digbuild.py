#!/usr/bin/env python

# prozacgod's minecraft clone... shitty!
# walk with arrow keys, and leave with esc!

#TODO: if you walk at a very perfect 45 towards a corner, you can enter a block!
import time
import os, random
from math import sin, cos, trunc
from pyglet.gl import *
from pyglet import window
from pyglet import image
from pyglet.window import key
import pyglet.clock

from minemap import MineMap

piover180 = 0.0174532925

class MineWindow:
  def __init__(self):
    # Create a window with specified OpenGL configuration
    config = pyglet.gl.Config(double_buffer=True, alpha_size=8)
    self.window = pyglet.window.Window(config=config)

    self.label = pyglet.text.Label('',
      font_name='Times New Roman',
      font_size=36,
      x=10, y=10,
      anchor_x='left', anchor_y='top')

    self.coordLabel = pyglet.text.Label('Coord:',
      font_name='Times New Roman',
      font_size=36,
      x=10, y=10,
      anchor_x='left', anchor_y='top')

    self.blocklabel = pyglet.text.Label('Block:',
      font_name='Times New Roman',
      font_size=36,
      x=10, y=10,
      anchor_x='left', anchor_y='top')


    self.textures = []
    self.filter = 0
    self.quad = []

    self.yrot = 270.0
    self.xpos = 2
    self.zpos = 2
    self.ypos = 0

    self.lookupdown = 0.5
    self.gravity = -9.8
    self.velocity_y = 0

    self.LightAmbient  = (GLfloat*4)(0.5, 0.5, 0.5, 1.0)
    self.LightDiffuse  = (GLfloat*4)(1.0, 1.0, 1.0, 1.0)
    self.LightPosition = (GLfloat*4)(0.0, 0.0, 2.0, 1.0)		
    
    self.window = pyglet.window.Window(caption="Digbuild", visible=False, resizable=True, vsync=False, fullscreen=True)
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
    glLightfv( GL_LIGHT1, GL_AMBIENT, self.LightAmbient)
    glLightfv( GL_LIGHT1, GL_DIFFUSE, self.LightDiffuse)
    glLightfv( GL_LIGHT1, GL_POSITION, self.LightPosition)
    glEnable(GL_LIGHT1)
    glColor4f( 1.0, 1.0, 1.0, 0.5)		
  
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
      texturefile = os.path.join('data', str(i) + '.png')
      print("Loading:", texturefile)
      texture = pyglet.image.load(texturefile).get_texture()
      glBindTexture(GL_TEXTURE_2D, texture.id)
      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

      self.textures += [texture]

  def worldInit(self):
    self.mine_map = MineMap('minemap.txt')
    print(len(self.mine_map.quads))
      
  def eventInit(self):
    self.window.on_resize = self.on_resize
    self.window.on_key_press = self.on_key_press
    self.window.on_key_release = self.on_key_release
    self.window.on_mouse_motion = self.on_mouse_motion

  def setup_3d(self):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, float(self.window.width)/self.window.height, 0.02, 100.0)
    glMatrixMode(GL_MODELVIEW)

  def setup_2d(self):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, self.window.width, 0, self.window.height)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

  def on_resize(self, width, height):
    if height==0:
      height = 1.0
    glViewport(0, 0, width, height)
    
  def on_key_press(self, sym, mod):
    self.key_state[sym] = True
    
  def on_key_release(self, sym, mod):
    self.key_state[sym] = False
    
    if sym == key.ESCAPE:
      self.window.has_exit = True
    elif sym == key.F:
      self.filter +=1
      if self.filter == 3:
        self.filter = 0

  def getKeyState(self, sym, mod=0):
    if sym in self.key_state:
      return self.key_state[sym]
    return False

  def on_mouse_motion(self, x, y, dx, dy):
    self.yrot -= dx *.1;
    self.lookupdown -= dy*.1
    pass

  def updateFrame(self, dt):
    global piover180

    xpos = self.xpos
    ypos = -self.ypos
    zpos = self.zpos

    bxpos = trunc(xpos)
    bypos = trunc(zpos)
    bzpos = trunc(ypos)

    ibzpos = ypos - bzpos

    self.velocity_y += self.gravity * dt

    ypos += self.velocity_y * dt

    self.coordLabel.text = f'Coord: ({xpos:.2f}, {ypos:.2f}, {zpos:.2f}) :: ({bxpos}, {bypos}, {bzpos}) :: {ibzpos}'

    currentCell = self.mine_map.getCell(bxpos, bypos, bzpos)
    belowCell = self.mine_map.getCell(bxpos, bypos, bzpos - 1)

    footCell = self.mine_map.getCell(trunc(xpos), trunc(zpos), trunc(ypos-0.01))

    self.blocklabel.text = f'Block {currentCell}, {belowCell}'

    if ypos < 0:
      ypos = 0
      self.velocity_y = 0
      
    if footCell >= 0:
      ypos = -self.ypos
      self.velocity_y = 0

    if self.getKeyState(key.W):
      xpos -= dt * sin(self.yrot * piover180)*2
      zpos -= dt * cos(self.yrot * piover180)*2
      
    if self.getKeyState(key.S):
      xpos += dt * sin(self.yrot * piover180)*2
      zpos += dt * cos(self.yrot * piover180)*2
      
    if self.getKeyState(key.D):
      xpos += dt * sin((self.yrot+90) * piover180)*2
      zpos += dt * cos((self.yrot+90) * piover180)*2
      
    if self.getKeyState(key.A):
      xpos += dt * sin((self.yrot-90) * piover180)*2
      zpos += dt * cos((self.yrot-90) * piover180)*2

    if self.getKeyState(key.SPACE):
      self.velocity_y = 10
      print('jump')

    bxpos = trunc(xpos)
    bypos = trunc(zpos)
    bzpos = trunc(ypos)
        
    ibxpos = xpos - bxpos
    ibypos = zpos - bypos
    ibzpos = ypos - bzpos
        
    left = self.mine_map.getCell(bxpos - 1, bypos, bzpos)
    right = self.mine_map.getCell(bxpos + 1, bypos, bzpos)
    fore = self.mine_map.getCell(bxpos, bypos-1, bzpos)
    aft = self.mine_map.getCell(bxpos, bypos+1, bzpos)

    below = self.mine_map.getCell(bxpos, bypos, bzpos-1)
    
    if (ibxpos < .10) and (left >= 0):
      xpos = bxpos + .10
      
    if (ibxpos > .90) and (right >= 0):
      xpos = bxpos + .90
    
    if (ibypos < .10) and (fore >= 0):
      zpos = bypos + .10
      
    if (ibypos > .90) and (aft >= 0):
      zpos = bypos + .90
    
    self.xpos = xpos
    self.ypos = -ypos
    self.zpos = zpos
    

  def draw(self):
    xtrans = -self.xpos
    ztrans = -self.zpos
    ytrans = self.ypos - 1.5
    sceneroty = 360.0 - self.yrot

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glRotatef(self.lookupdown, 1.0, 0.0 , 0.0)
    glRotatef(sceneroty, 0.0, 1.0 , 0.0)
    glTranslatef(xtrans, ytrans, ztrans)
    glCallList(1);
  
  def update_fps(self, clock):
    self.label.text = f'FPS: {clock.get_fps():.2f}'

  def run(self):
    self.label.text = 'asdfas'

    self.window.set_visible()
    self.window.set_mouse_visible(False)
    self.window.set_exclusive_mouse(True)

    clock = pyglet.clock.Clock()
    frame = 0
    while not self.window.has_exit:
      frame = (frame + 1) % 10
      if (frame == 0):
        self.update_fps(clock)

      dt = clock.tick()

      self.window.dispatch_events()
      self.updateFrame(dt)
      self.setup_3d()
      self.draw()
      self.setup_2d()
      self.label.y = self.window.height - 10
      self.label.draw()

      self.coordLabel.y = self.window.height - 56
      self.coordLabel.draw()

      self.blocklabel.y = self.window.height - 102
      self.blocklabel.draw()
      self.window.flip()

    print("fps:  %d" % clock.get_fps())


def main():
  mw = MineWindow()
  mw.run()

if __name__ == "__main__":
  main()
