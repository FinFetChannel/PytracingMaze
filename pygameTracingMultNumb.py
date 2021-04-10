import numpy as np
import multiprocessing
import pygame as pg
from numba import njit

def main():
    size = 15 # size of the map
    posx, posy, posz = (1, np.random.randint(1, size -1), 0.5)
    rot, rot_v = (np.pi/4, 0)
    lx, ly, lz = (size/2-0.5, size/2-0.5, 1)    
    mapc, maph, mapr, exitx, exity = maze_generator(posx, posy, size)

    width = 96 # 64 96 112 192 224
    height = int(0.75*width)
    mod = width/64
    inc = 0.05/mod
    nuc = 8
    pool = multiprocessing.Pool(processes = nuc)
        
    bench = []
    running = True
    pg.init()
    font = pg.font.SysFont("Arial", 18)
    screen = pg.display.set_mode((800, 600))
    clock = pg.time.Clock()
    pg.mouse.set_visible(False)
    pg.mouse.set_pos([320, 240])
    
    while running:
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False

        param_values = []
        for j in range(height): #vertical loop 
            rot_j = rot_v + np.deg2rad(24 - j/mod)
            for i in range(width): #horizontal vision loop
                param_values.append([rot, i, j, inc, rot_j])
        tam = len(param_values)
        lista = []
        pixels=[]
        
        for i in range(nuc):
            lista.append([i, param_values[i*int(tam/nuc):(i+1)*int(tam/nuc)],
                          mapc, maph, lx, ly, lz, exitx, exity, mapr, posx, posy, posz, mod])

        retorno = pool.map(caster, lista)

        for i in range(nuc):
            pixels.append(retorno[i][1])
            
        pixels = np.reshape(pixels, (height,width,3))
        pixels = np.asarray(pixels)/np.sqrt(np.max(pixels))        
        surf = pg.surfarray.make_surface((np.rot90(pixels*255)).astype('uint8'))
        surf = pg.transform.scale(surf, (800, 600))
        screen.blit(surf, (0, 0))
        fps = font.render(str(round(clock.get_fps(),1)), 1, pg.Color("coral"))
        screen.blit(fps,(10,0))
        pg.display.update()

        # player's movement

        if (int(posx) == exitx and int(posy) == exity):
            break

        pressed_keys = pg.key.get_pressed()        
        posx, posy, rot, rot_v = movement(pressed_keys,posx, posy, rot, rot_v, maph, clock.tick()/500)
        pg.mouse.set_pos([320, 240])

    pg.quit()
    pool.close()
    
def maze_generator(x, y, size):
    mapc = np.random.uniform(0,1, (size,size,3)) 
    mapr = np.random.choice([0, 0, 0, 0, 1], (size,size))
    maph = np.random.choice([0, 0, 0, 0, 0, 0, 0, .2, .4, .6, .8], (size,size))
    maph[0,:], maph[size-1,:], maph[:,0], maph[:,size-1] = (1,1,1,1)

    mapc[x][y], maph[x][y], mapr[x][y] = (0, 0, 0)
    count = 0 
    while 1:
        testx, testy = (x, y)
        if np.random.uniform() > 0.5:
            testx = testx + np.random.choice([-1, 1])
        else:
            testy = testy + np.random.choice([-1, 1])
        if testx > 0 and testx < size -1 and testy > 0 and testy < size -1:
            if maph[testx][testy] == 0 or count > 5:
                count = 0
                x, y = (testx, testy)
                mapc[x][y], maph[x][y], mapr[x][y] = (0, 0, 0)
                if x == size-2:
                    exitx, exity = (x, y)
                    break
            else:
                count = count+1
    return mapc, maph, mapr, exitx, exity

def movement(pressed_keys,posx, posy, rot, rot_v, maph, et):
    
    x, y = (posx, posy)
    
    p_mouse = pg.mouse.get_pos()
    rot = rot + 4*np.pi*(0.5-(p_mouse[0]-320)/6400)
    rot_v = rot_v + 4*np.pi*(0.5-(p_mouse[1]-240)/9600)
    
    if pressed_keys[pg.K_UP] or pressed_keys[ord('w')]:
        x, y = (x + et*np.cos(rot), y + et*np.sin(rot))
        
    if pressed_keys[pg.K_DOWN] or pressed_keys[ord('s')]:
        x, y = (x - et*np.cos(rot), y - et*np.sin(rot))
        
    if pressed_keys[pg.K_LEFT] or pressed_keys[ord('a')]:
        x, y = (x - et*np.sin(rot), y + et*np.cos(rot))
        
    if pressed_keys[pg.K_RIGHT] or pressed_keys[ord('d')]:
        x, y = (x + et*np.sin(rot), y - et*np.cos(rot))
        
    if maph[int(x)][int(y)] == 0:
        posx, posy = (x, y)
                                                
    return posx, posy, rot, rot_v
        
       
@njit(fastmath=True)
def fast_ray(x, y, z, cos, sin, sinz, maph):
    while 1:
        x, y, z = x + cos, y + sin, z + sinz
        if (z > 1 or z < 0):
            break
        if maph[int(x)][int(y)] > z:
            break        
    return x, y, z        

def view_ray(x, y, z, cos, sin, sinz, mapc, lx, ly, lz, maph, exitx, exity):

    x, y, z = fast_ray(x, y, z, cos, sin, sinz, maph)

    if z > 1: # ceiling
        if (x-lx)**2 + (y-ly)**2 < 0.1: #light source
            c = np.asarray([1,1,1])
        elif int(np.rad2deg(np.arctan((y-ly)/(x-lx)))/6)%2 ==1:
            c = np.asarray([.6,1,1])
        else:
            c = np.asarray([1,1,0.6])
    elif z < 0: # floor
        if int(x) == exitx and int(y) == exity:
            c = np.asarray([0,0,.6])
        elif int(x*2)%2 == int(y*2)%2:
            c = np.asarray([.1,.1,.1])
        else:
            c = np.asarray([.8,.8,.8])
    elif z < maph[int(x)][int(y)]:
        c = np.asarray(mapc[int(x)][int(y)])
    else:
        c = np.asarray([.5,.5,.5]) # last resort

    dtol = np.sqrt((x-lx)**2+(y-ly)**2+(lz-1)**2)
    h = 0.3 + 0.7*np.clip(1/dtol, 0, 1)
    c = c*h
    return c, x, y, z, dtol


@njit(fastmath=True)
def shadow_ray(x, y, z, lx, ly, lz, maph, c, inc, dtol):
    dx, dy, dz = inc*2*(lx-x)/dtol, inc*2*(ly-y)/dtol, inc*2*(lz-z)/dtol
    mod = 1
    while 1:
        x, y, z = (x + dx, y + dy, z + dz)
        if maph[int(x)][int(y)]!= 0 and z<= maph[int(x)][int(y)]:
            mod = mod*0.9
            if mod < 0.5:
                break
        elif z > 0.9:
            break
    return c*mod

def reflection(x, y, z, cos, sin, sinz, mapc, lx, ly, lz, maph, exitx, exity, c, posz, inc, mapr, recur):
    if abs(z-maph[int(x)][int(y)])<abs(sinz):
        sinz = -sinz
    elif maph[int(x+cos)][int(y-sin)] != 0:
        cos = -cos
    else:
        sin = -sin
    c2, x, y, z, dtol = view_ray(x, y, z, cos, sin, sinz, mapc, lx, ly, lz, maph, exitx, exity)
    if z < 1:
        c2 = shadow_ray(x, y, z, lx, ly, lz, maph, c2, inc, dtol)
    if (mapr[int(x)][int(y)] != 0 and z < 1 and z > 0 and not recur):
        c2 = reflection(x, y, z, cos, sin, sinz, mapc, lx, ly, lz, maph, exitx, exity, c2, posz, inc, mapr, recur=True)
    c = (c + c2)/2
    return c

def caster(lista):
    param_values = lista[1]
    mapc = lista[2]
    maph = lista[3]
    lx = lista[4]
    ly = lista[5]
    lz = lista[6]
    exitx = lista[7]
    exity = lista[8]
    mapr = lista[9]
    posx = lista[10]
    posy = lista[11]
    posz = lista[12]
    mod = lista[13]
    pixels = []
    
    for values in param_values:
        rot = values[0]
        i = values[1]
        j = values[2]
        inc = values[3]
        rot_j = values[4]
        rot_i = rot + np.deg2rad(i/mod - 30)
        x, y, z = (posx, posy, posz)
        sin, cos,  = (inc*np.sin(rot_i), inc*np.cos(rot_i))
        sinz = inc*np.sin(rot_j)
        c, x, y, z, dtol = view_ray(x, y, z, cos, sin, sinz, mapc, lx, ly, lz,
                                    maph, exitx, exity)
        if z < 1:
            c = shadow_ray(x, y, z, lx, ly, lz, maph, c, inc, dtol)
            if mapr[int(x)][int(y)] != 0 and z > 0:
                c = reflection(x, y, z, cos, sin, sinz, mapc, lx, ly, lz, maph,
                               exitx, exity, c, posz, inc, mapr, recur=False)
                
        pixels.append(c)
    return lista[0],pixels

if __name__ == '__main__':
    main()
