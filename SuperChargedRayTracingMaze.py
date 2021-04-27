import numpy as np
import pygame as pg
from numba import njit

def main():
    size = 25 # size of the map
    posx, posy, posz = (1.5, np.random.uniform(1, size -1), 0.5)
    rot, rot_v = (np.pi/4, 0)
    lx, ly, lz = (size/2-0.5, size/2-0.5, 1)    
    mr, mg, mb, maph, mapr, exitx, exity, mapt, maps = maze_generator(int(posx), int(posy), size)

    res, res_o = 5, [64, 96, 112, 160, 192, 224, 300, 400]
    width, height, mod, inc, rr, gg, bb = adjust_resol(res_o[res])
    
    running = True
    pg.init()
    font = pg.font.SysFont("Arial", 18)
    screen = pg.display.set_mode((800, 600)) 
        
    clock = pg.time.Clock()
    pg.mouse.set_visible(False)
    
    while running:
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
             
                if event.key == ord('q'): # change resolution
                    if res > 0 :
                        res = res-1
                        width, height, mod, inc, rr, gg, bb = adjust_resol(res_o[res])
                if event.key == ord('e'):
                    if res < len(res_o)-1 :
                        res = res+1
                        width, height, mod, inc, rr, gg, bb = adjust_resol(res_o[res])
                        
        rr, gg, bb = super_fast(width, height, mod, inc, posx, posy, posz, rot, rot_v, mr, mg, mb, lx, ly, lz, maph, exitx, exity, mapr, mapt, maps, rr, gg, bb)
        pixels = np.dstack((rr,gg,bb))


        pixels = np.reshape(pixels, (height,width,3))

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
        pg.mouse.set_pos([400, 300])
    pg.quit()
    
def maze_generator(x, y, size):
    
    mr = np.random.uniform(0,1, (size,size)) 
    mg = np.random.uniform(0,1, (size,size)) 
    mb = np.random.uniform(0,1, (size,size)) 
    mapr = np.random.choice([0, 0, 0, 0, 1], (size,size))
    maps = np.random.choice([0, 0, 0, 0, 1], (size,size))
    mapt = np.random.choice([0, 0, 0, 1, 2], (size,size))
    maph = np.random.choice([0, 0, 0, 0, 0, 0, 0, .3, .4, .7, .9], (size,size))
    maph[0,:], maph[size-1,:], maph[:,0], maph[:,size-1] = (1,1,1,1)
    maps[0,:], maps[size-1,:], maps[:,0], maps[:,size-1] = (0,0,0,0)

    maph[x][y], mapr[x][y] = (0, 0)
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
                maph[x][y], mapr[x][y] = (0, 0)
                if x == size-2:
                    exitx, exity = (x, y)
                    break
            else:
                count = count+1
    mapt[np.where(mapr == 1)] = 0
    return mr, mg, mb, maph, mapr, exitx, exity, mapt, maps

def movement(pressed_keys,posx, posy, rot, rot_v, maph, et):
    
    x, y = (posx, posy)
    p_mouse = pg.mouse.get_pos()
    rot, rot_v = rot - (p_mouse[0]-400)/200, rot_v -(p_mouse[1]-300)/400
    rot_v = np.clip(rot_v, -1, 1)

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
def super_fast(width, height, mod, inc, posx, posy, posz, rot, rot_v, mr, mg, mb, lx, ly, lz, maph, exitx, exity, mapr, mapt, maps, pr, pg, pb):

    texture=[[ .95,  .99,  .97, .8], # brick wall
             [ .97,  .95,  .96, .85],
             [.8, .85, .8, .8],
             [ .93, .8,  .98,  .96],
             [ .99, .8,  .97,  .95],
             [.8, .85, .8, .8]]
    idx = 0
    for j in range(height): #vertical loop 
        rot_j = rot_v + np.deg2rad(24 - j/mod)
        for i in range(width): #horizontal vision loop
            rot_i = rot + np.deg2rad(i/mod - 30)
            x, y, z = (posx, posy, posz)
            sin, cos,  = (inc*np.sin(rot_i), inc*np.cos(rot_i))
            sinz = inc*np.sin(rot_j)
            
            modr = 1
            cx, cy, c1r, c2r, c3r = 1, 1, 1, 1, 1
            while 1:
                if (maph[int(x)][int(y)] == 0 or (sinz > 0 and not maps[int(x)][int(y)])): ## LoDev DDA for optimization
                    
                    norm = np.sqrt(cos**2 + sin**2 + sinz**2)
                    rayDirX, rayDirY, rayDirZ = cos/norm, sin/norm, sinz/norm
                    
                    mapX, mapY = int(x), int(y)

                    deltaDistX, deltaDistY, deltaDistZ= abs(1/rayDirX), abs(1/rayDirY), abs(1/rayDirZ)

                    if (rayDirX < 0):
                        stepX, sideDistX = -1, (x - mapX) * deltaDistX
                    else:
                        stepX, sideDistX = 1, (mapX + 1.0 - x) * deltaDistX
                        
                    if (rayDirY < 0):
                        stepY, sideDistY = -1, (y - mapY) * deltaDistY
                    else:
                        stepY, sideDistY = 1, (mapY + 1 - y) * deltaDistY

                    if (rayDirZ < 0):
                        sideDistZ = z*deltaDistZ;
                    else:
                        sideDistZ = (1-z)*deltaDistZ

                    while (1):
                        if (sideDistX < sideDistY):
                            sideDistX += deltaDistX; mapX += stepX
                            dist = sideDistX; side = 0
                        else:
                            sideDistY += deltaDistY; mapY += stepY
                            dist = sideDistY; side = 1

                        if (maph[mapX][mapY] > 0):
                            break
                            
                    if (side):
                        dist = dist - deltaDistY
                    else:
                        dist = dist - deltaDistX
                        
                    if (dist > sideDistZ):
                        dist = sideDistZ

                    x = x + rayDirX*dist - cos/2
                    y = y + rayDirY*dist - sin/2
                    z = z + rayDirZ*dist - sinz/2
                    
                    ## end of LoDev DDA
                
                x += cos; y += sin; z += sinz
                if (z > 1 or z < 0): # check ceiling and floor
                    break
                if maph[int(x)][int(y)] > z: # check walls
                    if maps[int(x)][int(y)]: # check spheres
                        if ((x-int(x)-0.5)**2 + (y-int(y)-0.5)**2 + (z-int(z)-0.5)**2 < 0.25):
                            if (mapr[int(x)][int(y)]): # spherical mirror
                                if (modr == 1):
                                    cx, cy = int(x), int(y)
                                modr = modr*0.7
                                if (modr < 0.2):
                                    break
                                if (abs(maph[int(x)][int(y)] - z) <= abs(sinz)): ## horizontal surface
                                    sinz = -sinz
                                else:
                                    nx = (x-int(x)-0.5)/0.5; ny = (y-int(y)-0.5)/0.5; nz =(z-0.5)/0.5
                                    dot = 2*(cos*nx + sin*ny + sinz*nz)
                                    cos = (cos - nx*dot); sin = (sin - ny*dot); sinz = (sinz - nz*dot)
                
                                    x += cos; y += sin; z += sinz
                            else:
                                break
                                    
                                
                    elif mapr[int(x)][int(y)]: # check reflections
                        if modr == 1:
                            cx, cy = int(x), int(y)
                        modr  = modr*0.7
                        if modr < 0.2:
                            break
                        if abs(z-maph[int(x)][int(y)]) < abs(sinz):
                            sinz = -sinz
                        elif maph[int(x+cos)][int(y-sin)] == maph[int(x)][int(y)]:
                            cos = -cos
                        else:
                            sin = -sin
                    else:
                        break

                
            if z > 1: # ceiling
                sh =(abs(np.sin(y+ly)+np.sin(x+lx))+6)/8
                if (x-lx)**2 + (y-ly)**2 < 0.1: #light source
                    c1, c2, c3 = 1, 1, 1
                elif int(np.rad2deg(np.arctan((y-ly)/(x-lx)))/6)%2 ==1:
                    c1, c2, c3 = 0.3*sh, 0.7*sh, 1*sh
                else:
                    c1, c2, c3 = .2*sh, .6*sh, 1*sh
                    
            elif z < 0: # floor
                
                if int(x*2)%2 == int(y*2)%2:
                    c1, c2, c3 = .8,.8,.8
                else:
                    if int(x) == exitx and int(y) == exity: #exit
                        c1, c2, c3 = 0,0,.6
                    else:
                        c1, c2, c3 = .1,.1,.1
                        
            elif maph[int(x)][int(y)] > 0: # walls
                c1, c2, c3 = mr[int(x)][int(y)], mg[int(x)][int(y)], mg[int(x)][int(y)]
                if mapt[int(x)][int(y)]: # textured walls
                    if y%1 < 0.05 or y%1 > 0.95:
                        ww = int((x*3)%1*4)
                    else:
                        ww = int((y*3)%1*4)
                    if x%1 < 0.95 and x%1 > 0.05 and y%1 < 0.95 and y%1 > 0.05:
                        zz = int(x*5%1*6)
                    else:
                        zz = int(z*5%1*6)
                    text = texture[zz][ww]
                    c1, c2, c3 = c1*text, c2*text, c3*text
            else:
                 c1, c2, c3 = .5,.5,.5 # if all fails


            if modr < 1:
                c1r, c2r, c3r = mr[cx][cy], mg[cx][cy], mg[cx][cy]

            dtol = np.sqrt((x-lx)**2+(y-ly)**2+(lz-1)**2)
            modr = modr*(0.6 + 0.4/(dtol+0.001))
            if modr > 1:
                modr = 1
            if z < 1: # shadows
                cos, sin, sinz = .05*(lx-x)/dtol, .05*(ly-y)/dtol, .05*(lz-z)/dtol
                while 1:
                    if maph[int(x)][int(y)] < z and not maps[int(x)][int(y)]: ## LoDev DDA for optimization
                        
                        norm = np.sqrt(cos**2 + sin**2 + sinz**2)
                        rayDirX, rayDirY, rayDirZ = cos/norm, sin/norm, sinz/norm
                        
                        mapX, mapY = int(x), int(y)

                        deltaDistX, deltaDistY, deltaDistZ= abs(1/rayDirX), abs(1/rayDirY), abs(1/rayDirZ)

                        if (rayDirX < 0):
                            stepX, sideDistX = -1, (x - mapX) * deltaDistX
                        else:
                            stepX, sideDistX = 1, (mapX + 1.0 - x) * deltaDistX
                            
                        if (rayDirY < 0):
                            stepY, sideDistY = -1, (y - mapY) * deltaDistY
                        else:
                            stepY, sideDistY = 1, (mapY + 1 - y) * deltaDistY

                        if (rayDirZ < 0):
                            sideDistZ = z*deltaDistZ;
                        else:
                            sideDistZ = (1-z)*deltaDistZ

                        while (1):
                            if (sideDistX < sideDistY):
                                sideDistX += deltaDistX; mapX += stepX
                                dist = sideDistX; side = 0
                            else:
                                sideDistY += deltaDistY; mapY += stepY
                                dist = sideDistY; side = 1

                            if (maph[mapX][mapY] > 0):
                                break
                                
                        if (side):
                            dist = dist - deltaDistY
                        else:
                            dist = dist - deltaDistX
                            
                        if (dist > sideDistZ):
                            dist = sideDistZ

                        x = x + rayDirX*dist - cos/2
                        y = y + rayDirY*dist - sin/2
                        z = z + rayDirZ*dist - sinz/2
                        
                        ## end of LoDev DDA
                        
                    x += cos; y += sin; z += sinz
                    if maph[int(x)][int(y)]!= 0 and z<= maph[int(x)][int(y)]:
                        if maps[int(x)][int(y)]: # check spheres
                            if ((x-int(x)-0.5)**2 + (y-int(y)-0.5)**2 + (z-int(z)-0.5)**2 < 0.25):
                                modr = modr*0.9
                        else:    
                            modr = modr*0.9
                        if modr < 0.3:
                            break
                    if z > 1:
                        break
                    
            pr[idx] = modr*np.sqrt(c1*c1r)
            pg[idx] = modr*np.sqrt(c2*c2r)
            pb[idx] = modr*np.sqrt(c3*c3r)
            idx += 1

    return pr, pg, pb

def adjust_resol(width):
    height = int(0.75*width)
    mod = width/64
    inc = 0.02/mod
    rr = np.random.uniform(0,1,width * height)
    gg = np.random.uniform(0,1,width * height)
    bb = np.random.uniform(0,1,width * height)
    print('Resolution: ', width, height)
    return width, height, mod, inc, rr, gg, bb


if __name__ == '__main__':
    main()
