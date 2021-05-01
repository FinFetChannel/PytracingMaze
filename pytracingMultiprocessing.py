import numpy as np
from matplotlib import pyplot as plt
from pynput import keyboard, mouse
import multiprocessing
from numba import njit

def main():
    global key
    key = None
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    size = 15 # size of the map
    posx, posy, posz = (1, np.random.randint(1, size -1), 0.5)
    rot, rot_v = (np.pi/4, 0)
    lx, ly, lz = (size/2-0.5, size/2-0.5, 1)    
    mapc, maph, mapr, exitx, exity = maze_generator(posx, posy, size)

    mod = 2# resolution modifier
    inc = 0.05/mod # ray increment
    height, width = (int(45*mod), int(56*mod))
    nuc = 4
    pool = multiprocessing.Pool(processes = nuc)
        
    ax = plt.figure().gca()
    img = ax.imshow(np.random.rand(height, width, 3))
    plt.axis('off'); plt.tight_layout()
    
    while 1: #main game loop
        rot, rot_v = rotation(rot, rot_v)
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
        img.set_array(pixels); plt.draw(); plt.pause(0.0001)

        posx, posy, rot, rot_v, keyout = movement(posx, posy, rot, rot_v, maph)

        if (int(posx) == exitx and int(posy) == exity) or keyout == 'esc':
            break        
    plt.close()
    listener.stop()
    pool.close()
    
def maze_generator(x, y, size):
    mapc = np.random.uniform(0,1, (size,size,3)) 
    mapr = np.random.choice([0, 0, 0, 0, 1], (size,size))
    maph = np.random.choice([0, 0, 0, 0, 0, 0, 0, .3, .4, .7, .9], (size,size))
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

def rotation(rot, rot_v):
    with mouse.Controller() as check:
        position = check.position
        if abs(960-position[0]) > 200:
            dx = (960 - position[0])/4800# 1080p
            rot = np.real(rot - dx)
        if abs(540 - position[1]) > 200:
            dy = (540 - position[1])/2700# 1080p screen
            rot_v = np.real(rot_v + dy)
    return(rot, rot_v)

def on_press(key_new):
    global key
    key = key_new
    
def movement(posx, posy, rot, rot_v, maph):
    global key
    x, y = (posx, posy)
    keyout = None
    if key is not None:
        if key == keyboard.Key.up:
            x, y = (x + 0.3*np.cos(rot), y + 0.3*np.sin(rot))
        elif key == keyboard.Key.down:
            x, y = (x - 0.3*np.cos(rot), y - 0.3*np.sin(rot))
        elif key == keyboard.Key.left:
            rot = rot - np.pi/8
        elif key == keyboard.Key.right:
            rot = rot + np.pi/8
        elif key == keyboard.Key.end:
            rot_v = rot_v - np.pi/16
        elif key == keyboard.Key.home:
            rot_v = rot_v + np.pi/16
        elif key == keyboard.Key.esc:
            keyout = 'esc'
    key = None        
    if (maph[int(x+ 0.05*np.cos(rot+np.pi/4))][int(y+ 0.3*np.sin(rot+np.pi/4))] == 0 and
        maph[int(x+ 0.05*np.cos(rot-np.pi/4))][int(y+ 0.3*np.sin(rot-np.pi/4))] == 0):
        posx, posy = (x, y)
        
    return posx, posy, rot, rot_v, keyout

       
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
    dx, dy, dz = [(lx-x)/dtol, (ly-y)/dtol, (lz-z)/dtol]
    mod = 1
    while 1:
        x, y, z = (x + .1*dx, y + .1*dy, z + .1*dz)
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
    elif maph[int(x+cos)][int(y-sin)] == maph[int(x)][int(y)]:
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
