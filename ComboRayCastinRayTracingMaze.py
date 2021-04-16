import numpy as np
import multiprocessing
import pygame as pg
from numba import njit

def main():
    size = 25 # size of the map
    posx, posy, posz = (1.5, np.random.uniform(1, size -1), 0.5)
    rot, rot_v = (np.pi/4, 0)
    lx, ly, lz = (size/2-0.5, size/2-0.5, 1)    
    mapc, maph, mapr, exitx, exity, mapt = maze_generator(int(posx), int(posy), size)

    res, res_o = 2, [64, 96, 112, 160, 192, 224]
    width, height, mod, inc, sky, floor = adjust_resol(res_o[res])
    
    nuc = 8
    pool = multiprocessing.Pool(processes = nuc)
        
    bench = []
    running = True
    pg.init()
    font = pg.font.SysFont("Arial", 18)
    screen = pg.display.set_mode((800, 600)) 
        
    clock = pg.time.Clock()
    pg.mouse.set_visible(False)
    pg.mouse.set_pos([400, 300])

    traceray = True
    
    while running:
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                if event.key == ord('r'): # switch ray tracing
                    traceray = not traceray
                    rot_v = 0

                    if traceray:
                        print('Ray tracing on!')
                    else:
                        print('Ray tracing off!')
                        
                if event.key == ord('q'): # change resolution
                    if res > 0 :
                        res = res-1
                        width, height, mod, inc, sky, floor = adjust_resol(res_o[res])
                if event.key == ord('e'):
                    if res < len(res_o)-1 :
                        res = res+1
                        width, height, mod, inc, sky, floor = adjust_resol(res_o[res])
                        
        if traceray:
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
                              mapc, maph, lx, ly, lz, exitx, exity, mapr, posx, posy, posz, mod, mapt])

            retorno = pool.map(caster, lista)

            for i in range(nuc):
                pixels.append(retorno[i][1])

            pixels = np.reshape(pixels, (height,width,3))
            pixels = np.asarray(pixels)/np.sqrt(np.max(pixels))

        else:
            pixels = np.ones([height, width, 3])
            for i in range(width): #vision loop
                rot_i = rot + np.deg2rad(i/mod - 30)
                pixels[0:len(sky),i] = sky*(0.5 + np.sin((rot_i-np.pi/2)/2)**2/2)
                pixels[int(height/2)+1:height-1,i] = floor[:-1]*(0.75 + np.sin((rot_i+np.pi/2)/2)**2/4)
                x, y = (posx, posy)
                sin, cos = (0.05*np.sin(rot_i)/mod, 0.05*np.cos(rot_i)/mod)
                
                n, half = 0, None
                c, h, x, y, n, half, ty, tc = ray_caster(x, y, i/mod, exitx, exity, maph, mapc, sin, cos, n, half, mod)
                if mapr[int(x)][int(y)]:
                     pixels, ty, tc = reflection_caster(x, y, i, exitx, exity, maph, mapc, sin, cos, n, c, h, half, pixels, ty, tc, height, mod)
                else:
                    pixels[int((height - h*height)/2):int((height+h*height)/2),i] = c
                    if half !=  None:
                        pixels[int(height/2):int((height+half[0]*height)/2),i] = half[1]
                if len(ty) > 0:
                    ty = (np.asarray(ty)*1*height/2+height/2).astype(int)
                    ty2, ind = np.unique(ty, return_index=True)
                    pixels[ty2,i] = (np.asarray(tc)[ind]*3 + pixels[ty2,i])/4

        
        surf = pg.surfarray.make_surface((np.rot90(pixels*255)).astype('uint8'))
        surf = pg.transform.scale(surf, (800, 600))
        screen.blit(surf, (0, 0))
        fps = font.render(str(round(clock.get_fps(),1)), 1, pg.Color("coral"))
        screen.blit(fps,(10,0))
        pg.display.flip()

        # player's movement
        if (int(posx) == exitx and int(posy) == exity):
            break
        pressed_keys = pg.key.get_pressed()        
        posx, posy, rot, rot_v = movement(pressed_keys,posx, posy, rot, rot_v, maph, clock.tick()/500)
        pg.mouse.set_pos([400, 300])
    stop_thread = True
    pg.quit()
    pool.close()
    
def maze_generator(x, y, size):
    
    mapc = np.random.uniform(0,1, (size,size,3)) 
    mapr = np.random.choice([0, 0, 0, 0, 1], (size,size))
    mapt = np.random.choice([0, 0, 0, 1, 2], (size,size))
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
    mapt[np.where(mapr == 1)] = 0
    return mapc, maph, mapr, exitx, exity, mapt

def movement(pressed_keys,posx, posy, rot, rot_v, maph, et):
    
    x, y = (posx, posy)
    
    p_mouse = pg.mouse.get_pos()
    rot = rot + 4*np.pi*(0.5-(p_mouse[0]-400)/8000)
    rot_v = rot_v + 4*np.pi*(0.5-(p_mouse[1]-300)/9600)
    
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
def fast_ray(x, y, z, cos, sin, sinz, maph, mapr, mapc, lx, ly, lz):
    modr = 1
    cx, cy = 1, 1
    while 1:
        x += cos
        y += sin
        z += sinz
        if (z > 1 or z < 0): # check ceiling and floor
            break
        if maph[int(x)][int(y)] > z: # check walls
            if mapr[int(x)][int(y)]: # check reflections
                if modr == 1:
                    cx, cy = int(x), int(y)
                modr  = modr*0.7
                if modr < 0.1:
                    break
                if abs(z-maph[int(x)][int(y)])<abs(sinz):
                    sinz = -sinz
                elif maph[int(x+cos)][int(y-sin)] != 0:
                    cos = -cos
                else:
                    sin = -sin
                cos, sin, sinz = cos, sin, sinz
            else:
                break
            
    dtol = np.sqrt((x-lx)**2+(y-ly)**2+(lz-1)**2)
    dx, dy, dz = .1*(lx-x)/dtol, .1*(ly-y)/dtol, .1*(lz-z)/dtol
    x2, y2, z2, mod = x, y, z, 1
    
    while 1:
        x2 += dx
        y2 += dy
        z2 += dz
        if maph[int(x2)][int(y2)]!= 0 and z2<= maph[int(x2)][int(y2)]:
            mod = mod*0.9
            if mod < 0.5:
                break
        elif z2 > 1:
            break
    return x, y, z, modr, cx, cy, mod, dtol

def view_ray(x, y, z, cos, sin, sinz, mapc, lx, ly, lz, maph, exitx, exity, mapr, mapt):
    
    x, y, z, modr, cx, cy, mod, dtol = fast_ray(x, y, z, cos, sin, sinz, maph, mapr, mapc, lx, ly, lz)

    if z > 1: # ceiling
        if (x-lx)**2 + (y-ly)**2 < 0.1: #light source
            c = np.asarray([1,1,1])
        elif int(np.rad2deg(np.arctan((y-ly)/(x-lx)))/6)%2 ==1:
            c = np.asarray([0.3,0.7,1])*(abs(np.sin(y+ly)+np.sin(x+lx))+2)/5
            c = (c + 1 - max(c))*0.8
        else:
            c = np.asarray([.2,.6,1])*(abs(np.sin(y+ly)+np.sin(x+lx))+2)/5
            c = (c + 1 - max(c))*0.8
    elif z < 0: # floor
        if int(x) == exitx and int(y) == exity:
            c = np.asarray([0,0,.6])
        elif int(x*2)%2 == int(y*2)%2:
            c = np.asarray([.1,.1,.1])
        else:
            c = np.asarray([.8,.8,.8])
    elif z < maph[int(x)][int(y)]: #walls
        c = np.asarray(mapc[int(x)][int(y)])
        c = c*check_texture(x, y, z, mapt[int(x),int(y)])
    else:
        c = np.asarray([.5,.5,.5]) # if all fails

    h = 0.3 + 0.7/(dtol+0.001)
    if h > 1:
        h = 1
    if modr < 1:
        c = modr * (np.asarray(mapc[cx][cy]) + c)/2
    c = c*h*mod
    return c, x, y, z, dtol

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
    mapt = lista[14]
    
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
                                    maph, exitx, exity, mapr, mapt)                   
        pixels.append(c)

    return lista[0], pixels


def ray_caster(x, y, i, ex, ey, maph, mapc, sin, cos, n, half, mod):
    zz= 0.5
    if half == None:
        zz = 0.1
    x, y, n, tc, ty = fast_ray_caster(x, y, zz, cos, sin, maph, n, i, ex, ey, mod)
    h , c = shader(n, maph, mapc, sin, cos, x, y, i, mod)
    if maph[int(x)][int(y)] < 0.5 and half == None:
        half = [h, c, n]
        x, y, n, tc2, ty2 = fast_ray_caster(x, y, 0.5, cos, sin, maph, n, i, ex, ey, mod)
        ty, tc = ty + ty2, tc + tc2
        h , c = shader(n, maph, mapc, sin, cos, x, y, i, mod)
    return(c, h, x, y, n, half, ty, tc)


@njit(fastmath=True)
def fast_ray_caster(x, y, z, cos, sin, maph, n, i, ex, ey, mod):
    ty, tc = [], []
    while 1:
        n = n+1
        x, y = x + cos, y + sin
        if z < 0.5 and int(x*2)%2 == int(y*2)%2:
                th = 1/(0.05/mod * n)#*np.cos(np.deg2rad(i/mod - 30)))
                if th < 1  and th >= 0:
                    ty.append(th)
                    if int(x) == ex and int(y) == ey:
                        tc.append(np.asarray([0,0,1]))
                    else:
                        tc.append(np.asarray([0,0,0]))
        if maph[int(x)][int(y)] > z:
            break        
    return x, y, n, tc, ty

def shader(n, maph, mapc, sin, cos, x, y, i, mod):
    
    h = np.clip(1/(0.05/mod * n), 0, 1)#*np.cos(np.deg2rad(i/mod-30))), 0, 1)
    c = np.asarray(mapc[int(x)][int(y)])*(0.4 + 0.6 * h)
    
    if x%1 < abs(cos) or x%1 > 1 -abs(cos):
        c = 0.75*c
    elif y%1 > 1 - abs(sin):
        c = 0.5*c
            
    return h, c

def reflection_caster(x, y, i, ex, ey, maph, mapc, sin, cos, n, c, h, half, pixels, ty, tc, height, mod):
    hor = int(height/2)
    hh = int((h*height)/2)
    pixels[hor-hh:hor+hh,i] = np.add(pixels[hor-hh:hor+hh,i], np.asarray([c]*(hh*2)))/2
    
    if maph[int(x+cos)][int(y-sin)] > 0.5:
        cos = -cos
        
    else:
        sin = -sin
        
    c2, h2, x, y, n2, half2, ty2, tc2 = ray_caster(x, y, i, ex, ey, maph, mapc, sin, cos, n, half, mod)
        
    ty, tc = ty + ty2, tc + tc2
    hh = int((h2*height)/2)
    pixels[hor-hh:hor+hh,i] = (c + c2)/2
    
    if half2 != None and half == None:
        hh = int((half2[0]*height)/2)
        pixels[hor:hor+hh,i] = (c + half2[1])/2
        
    if half != None:
        hh = int((half[0]*height)/2)
        pixels[hor:hor+hh,i] = half[1]
           
    return pixels, ty, tc     

def adjust_resol(width):
    height = int(0.75*width)
    mod = width/64
    inc = 0.05/mod
    gradient = np.linspace(0,1,int(height/2-1))
    sky = np.asarray([gradient/3,gradient/2+0.25,gradient/3+0.5]).T
    floor = np.asarray([gradient,gradient,gradient]).T
    print('Resolution: ', width, height)
    return width, height, mod, inc, sky, floor

def check_texture(x, y, z, tt):
    if tt == 0:
        return 1
    elif tt == 1:
        np.random.seed(int(x*2+y*147))
        texture = np.random.uniform(0.7,1, [6,4])
    else:
        texture=[[ .95,  .99,  .97, .8],
                 [ .97,  .95,  .96, .8],
                 [.8, .8, .8, .8],
                 [ .93, .8,  .98,  .96],
                 [ .99, .8,  .97,  .95],
                 [.8, .8, .8, .8]]
    
    if y%1 < 0.05 or y%1 > 0.95:
        ww = int((x*3)%1*4)
    else:
        ww = int((y*3)%1*4)
    if x%1 < 0.95 and x%1 > 0.05 and y%1 < 0.95 and y%1 > 0.05:
        zz = int(x*5%1*6)
    else:
        zz = int(z*5%1*6)
    return texture[zz][ww]

if __name__ == '__main__':
    main()
