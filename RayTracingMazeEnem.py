import numpy as np
import pygame as pg
from numba import njit

def main():
    size = np.random.randint(15,40) # size of the map
    posx, posy, posz = 1.5, np.random.uniform(1, size -1), 0.5
    
    rot, rot_v = (np.pi/4, 0)
    lx, ly, lz = (size*20, size*30, 1000)
    mr, mg, mb, maph, mapr, exitx, exity, mapt, maps = maze_generator(int(posx), int(posy), size)
    enx, eny = np.random.uniform(size/2-5, size/2+5), np.random.uniform(size/2-5, size/2+5)
    seenx, seeny = enx, eny
    maph[int(enx)][int(eny)] = 0
    shoot, sx, sy, sdir = 1, -1, -1, rot

    res, res_o = 6, [96, 112, 160, 192, 224, 260, 300, 340, 400, 480, 540, 600]
    width, height, mod, inc, rr, gg, bb = adjust_resol(res_o[res])

    running = True
    pg.init()
    
    font = pg.font.SysFont("Arial", 18)
    font2 = pg.font.SysFont("Impact", 58)
    screen = pg.display.set_mode((800, 600))
    rr, gg, bb = np.linspace(0,0.8, width*height), np.linspace(0.5,.1, width*height), np.linspace(1,0.1, width*height)
    pixels = np.dstack((rr,gg,bb))
    pixels = np.reshape(pixels, (height,width,3))
    surf = pg.surfarray.make_surface((np.rot90(pixels*255)).astype('uint8'))
    surf = pg.transform.scale(surf, (800, 600))
    screen.blit(surf, (0, 0))
    endmsg = font2.render("FinFET's PyTracing Maze", 1, pg.Color("white"))
    screen.blit(endmsg,(50,100))
    endmsg = font2.render("Loading, please wait...", 1, pg.Color("black"))
    screen.blit(endmsg,(50,300))
    pg.display.update()
    
    clock = pg.time.Clock()
    pg.mouse.set_visible(False)
    et = 0.1
    mplayer = np.zeros([size, size])
    enx, eny, mplayer, et, shoot, sx, sy, sdir, seenx, seeny = agents(enx, eny, maph, posx, posy, rot, et, shoot, sx, sy, sdir, mplayer, seenx, seeny)
    sstart, timer, count, autores = None, 0, 0, 1
    pause = False
    while running:
        count += 1
##        print(maph)
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                endmsg = "It's not all fun and games..."
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == ord('p'): # pause
                    pause = not(pause)
                if event.key == ord('t'): # toggle auto resolution
                    autores = not(autores)
                if not autores:
                    if event.key == ord('q'): # manually change resolution
                        if res > 0 :
                            res = res-1
                            width, height, mod, inc, rr, gg, bb = adjust_resol(res_o[res])
                    if event.key == ord('e'):
                        if res < len(res_o)-1 :
                            res = res+1
                            width, height, mod, inc, rr, gg, bb = adjust_resol(res_o[res])
            
        
        rr, gg, bb = super_fast(width, height, mod, inc, posx, posy, posz, rot, rot_v, mr, mg, mb, lx, ly, lz, mplayer, exitx, exity, mapr, mapt, maps, rr, gg, bb, enx, eny, sx, sy)
        
        pixels = np.dstack((rr,gg,bb))

        pixels = np.reshape(pixels, (height,width,3))

        surf = pg.surfarray.make_surface((np.rot90(pixels*255)).astype('uint8'))
        surf = pg.transform.smoothscale(surf, (800, 600))

        screen.blit(surf, (0, 0))
        fpss = int(clock.get_fps())
        if autores and count > 10: #auto adjust render resolution
            if fpss < 40:
                if width > 100 :
                    width, count = width-40, 0
                    width, height, mod, inc, rr, gg, bb = adjust_resol(width)
            if fpss > 60 and not shoot:
                if width < 600:
                    width, count = width+20, 0
                    width, height, mod, inc, rr, gg, bb = adjust_resol(width)#res_o[res])
        fps = font.render(str(fpss)+' w: '+str(width), 1, pg.Color("coral"))
        screen.blit(fps,(10,0))

        # player's movement
        if (int(posx) == exitx and int(posy) == exity):
            endmsg = "You escaped safely"
            break
        
        pressed_keys = pg.key.get_pressed()
        et = clock.tick()/500
        if et > 0.5:
            et = 0.5

        if shoot:
            if sstart == None:
                if fpss < 59 and autores:
                    width, count = width-60, 0
                    width, height, mod, inc, rr, gg, bb = adjust_resol(width)
                sstart = pg.time.get_ticks()
            elif pg.time.get_ticks() - sstart > 500:
                shoot, sx, sstart = 0, -1, None
                
        if enx == 0 and np.random.uniform() > 0.999:
            screen.blit(font2.render("Respawn", 1, pg.Color("red")),(500,50))
            pg.display.update()
            while 1:
                enx, eny = np.random.uniform(size/2+5, size-2 ), np.random.uniform(1, size-2)
                if maph[int(enx)][int(eny)] == 0:
                    break
            seenx, seeny = enx, eny
        else:
            if (int(posx) == int(enx) and int(posy) == int(eny)):
                endmsg = "You died"
                break

        if not pause:
            ticks = pg.time.get_ticks()/100000
            lx = size/2 + 1000*np.cos(ticks)
            ly = size/2 + 1000*np.sin(ticks)
            posx, posy, rot, rot_v, shoot = movement(pressed_keys,posx, posy, rot, rot_v, maph, et, shoot)
            pg.mouse.set_pos([400, 300])
            mplayer = np.zeros([size, size])
            enx, eny, mplayer, et, shoot, sx, sy, sdir,seenx, seeny = agents(enx, eny, maph, posx, posy, rot, et, shoot, sx, sy, sdir, mplayer, seenx, seeny)
        else:
            screen.blit(font2.render("Paused, press P", 1, pg.Color("white")),(50,50))
        
        pg.display.update()


    end = font2.render(endmsg, 1, pg.Color("white"))
    screen.blit(end,(50,300))
    pg.display.update()
    print(endmsg)
    pg.time.wait(2000)
    pg.quit()
    
def maze_generator(x, y, size):
    
    mr = np.random.uniform(0,1, (size,size)) 
    mg = np.random.uniform(0,1, (size,size)) 
    mb = np.random.uniform(0,1, (size,size)) 
    mapr = np.random.choice([0, 0, 0, 0, 1], (size,size))
    maps = np.random.choice([0, 0, 0, 0, 1], (size,size))
    mapt = np.random.choice([0, 0, 0, 1, 2], (size,size))
    maptemp = np.random.choice([0, 1], (size,size))
    maph = np.random.uniform(0.25, 0.99, (size,size))
    maph[np.where(maptemp == 0)] = 0
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
    
    return mr, mg, mb, maph, mapr, exitx, exity, mapt, maps

def movement(pressed_keys,posx, posy, rot, rot_v, maph, et, shoot):
    
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

    if not shoot and pressed_keys[pg.K_SPACE]:
        shoot = 1
                                                
    return posx, posy, rot, rot_v, shoot
        
@njit(fastmath=True)
def super_fast(width, height, mod, inc, posx, posy, posz, rot, rot_v, mr, mg, mb, lx, ly, lz, maph, exitx, exity, mapr, mapt, maps, pr, pg, pb, enx, eny, sx, sy):
        
    texture=[[ .95,  .99,  .97, .8], # brick wall
             [ .97,  .95,  .96, .85],
             [.8, .85, .8, .8],
             [ .93, .8,  .98,  .96],
             [ .99, .8,  .97,  .95],
             [.8, .85, .8, .8]]

    idx = 0
    for j in range(height): #vertical loop 
        rot_j = rot_v + np.deg2rad(24 - j/mod)
        inv = 1
##        if abs(rot_j) > np.pi/2:
##            inv = -1
        sinzo = inc*np.sin(rot_j)
        coszo = inc*np.sqrt(abs(np.cos(rot_j)))        
        for i in range(width): #horizontal vision loop
            rot_i = rot + np.deg2rad(i/mod - 30)
            x, y, z = (posx, posy, posz)
            sin, cos,  = (inv*coszo*np.sin(rot_i), inv*coszo*np.cos(rot_i))
            sinz = sinzo
            
            
            modr = 1
            cx, cy, c1r, c2r, c3r = 1, 1, 1, 1, 1
            mapv, shot, enem = 0, 0, 0
           
            while 1:
                if (mapv == 0 or (sinz > 0 and (z > mapv or (mapv==6 and (z>0.4 or z <0.2)) or(z > 0.57 and mapv > 1)))): ## LoDev DDA for optimization
                    
                    norm = np.sqrt(cos**2 + sin**2 + sinz**2)
                    rayDirX, rayDirY, rayDirZ = cos/norm + 1e-16, sin/norm + 1e-16, sinz/norm + 1e-16
                    
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

                        if (maph[mapX][mapY] != 0):
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
                mapv = maph[int(x)][int(y)]
                if mapv > 1 and z < 0.57:
                    if  mapv == 2:
                        if z> 0.45 and (x-posx)**2 + (y-posy)**2 + (z-0.5)**2 < 0.005 :
                            break
                        if z < 0.45 and z > 0.3 and (x-posx)**2 + (y-posy)**2  < (z/10 - 0.02):
                            break
                        if z < 0.3 and (x-posx)**2 + (y-posy)**2 + (z-0.15)**2 < 0.023 :
                                break
                    elif  mapv == 3 or mapv == 9:
                        enem = 1
                        if z> 0.45 and (x-enx)**2 + (y-eny)**2 + (z-0.5)**2 < 0.005 :
                            break
                        if z < 0.45 and z > 0.3 and (x-enx)**2 + (y-eny)**2  < (z/10 - 0.02):
                            break
                        if z < 0.3 and (x-enx)**2 + (y-eny)**2 + (z-0.15)**2 < 0.023 :
                            break
                    elif  z < 0.4 and z > 0.2:
                        if ((x-sx)**2 + (y-sy)**2 + (z-0.3)**2 < 0.01):
                            shot = 1
                            break

                if mapv > z and mapv < 2: # check walls
                    if maps[int(x)][int(y)]: # check spheres
                        if ((x-int(x)-0.5)**2 + (y-int(y)-0.5)**2 + (z-int(z)-0.5)**2 < 0.25):
                            if (mapr[int(x)][int(y)]): # spherical mirror
                                if (modr == 1):
                                    cx, cy = int(x), int(y)
                                modr = modr*0.7
                                if (modr < 0.2):
                                    break
                                if (mapv - z <= abs(sinz) ): ## horizontal surface
                                    sinz = -sinz
                                else:
                                    nx = (x-int(x)-0.5)/0.5; ny = (y-int(y)-0.5)/0.5; nz =(z-int(z)-0.5)/0.5
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
                deltaDistZ = (lz-z)*deltaDistZ
                x += deltaDistZ*rayDirX; y += deltaDistZ*rayDirY; z += deltaDistZ*rayDirZ
                dtol = np.sqrt((x-lx)**2+(y-ly)**2+(lz-z)**2)
                
                if dtol < 50: #light source
                    c1, c2, c3 = 1, 1, 0.5
                else:
                    angle = np.rad2deg(np.arctan((y-ly)/(x-lx)))/np.random.uniform(12,15)
                    sh = (0.8+ abs(angle - int(angle))/5)/(dtol/1000)
                    if sh > 1:
                        sh = 1
                    if int(angle)%2 == 1:
                        c1, c2, c3 = 0.8*(1-sh), 0.8*(1-sh/4), (1-sh/10)
                    else:
                        c1, c2, c3 = 0.8*(1-sh), 0.9*(1-sh/4), (1-sh/10)
                    
            elif z < 0: # floor
                
                if int(x*2)%2 == int(y*2)%2:
                    c1, c2, c3 = .8,.8,.8
                else:
                    if int(x) == exitx and int(y) == exity: #exit
                        c1, c2, c3 = 0,0,.6
                    else:
                        c1, c2, c3 = .1,.1,.1
                        
            elif mapv < 2: # walls
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
                    
                if not mapv - z <= abs(sinz) and not maps[int(x)][int(y)]:
                    if int(x-cos) != int(x):
                        x = max(int(x-cos), int(x))
                        modr = modr*0.80
                    else:
                        y = max(int(y-sin), int(y))
                        modr = modr*0.9
            else:
                if shot:
                    c1, c2, c3 = 1, 0.5 , 0 # shot
                elif z> 0.45:
                    c1, c2, c3 = 0.6, 0.3, 0.3 # Head
                elif z > 0.3:
                    c1, c2, c3 = 0.3, 0.5, 0.5 # Chest
                else:
                    if enem:
                        c1, c2, c3 = 1, 0.2, 0.2 # Roller red
                    else:
                        c1, c2, c3 = 0.2, 0.2, 1 # Roller blue

            if modr <= 0.7:
                c1r, c2r, c3r = mr[cx][cy], mg[cx][cy], mg[cx][cy]

            if not shot and z < 1:
                dtol = np.sqrt((x-lx)**2+(y-ly)**2+(z-lz)**2)
                dtp = np.sqrt((x-posx)**2+(y-posy)**2+(z-posz)**2)
                if dtp > 5:
                    modr = modr/np.sqrt(dtp-4)

                if z < 1: # shadows
                    cos, sin, sinz = .01*(lx-x)/dtol, .01*(ly-y)/dtol, .01*(lz-z)/dtol
                    x += cos; y += sin; z += sinz
                    mapv = maph[int(x)][int(y)]
                    if z < mapv and mapv < 1 and not maps[int(x)][int(y)]:
                        modr = modr*0.5
                    while modr > 0.5:
                        if (mapv == 0 or (z > mapv) or mapv == 6 or (z > 0.57 and mapv > 1)): ## LoDev DDA for optimization
                        
                            norm = np.sqrt(cos**2 + sin**2 + sinz**2)
                            rayDirX, rayDirY, rayDirZ = cos/norm + 1e-16, sin/norm + 1e-16, sinz/norm + 1e-16
                            
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

                                if (maph[mapX][mapY] != 0):
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
                        mapv = maph[int(x)][int(y)]
                        if z < 0.57 and mapv > 1:
                            if  mapv == 3 or mapv == 9:
                                if z> 0.45 and (x-enx)**2 + (y-eny)**2 + (z-0.5)**2 < 0.005 :
                                    modr = modr*0.7
                                elif z < 0.45 and z > 0.3 and (x-enx)**2 + (y-eny)**2  < (z/10 - 0.02):
                                    modr = modr*0.7
                                elif z < 0.3 and (x-enx)**2 + (y-eny)**2 + (z-0.15)**2 < 0.023 :
                                    modr = modr*0.7
                            else:
                                if z> 0.45 and (x-posx)**2 + (y-posy)**2 + (z-0.5)**2 < 0.005 :
                                    modr = modr*0.7
                                elif z < 0.45 and z > 0.3 and (x-posx)**2 + (y-posy)**2  < (z/10 - 0.02):
                                    modr = modr*0.7
                                elif z < 0.3 and (x-posx)**2 + (y-posy)**2 + (z-0.15)**2 < 0.023 :
                                    modr = modr*0.7

                                    
                        if mapv > 0 and z <= mapv and mapv < 2:      
                            if maps[int(x)][int(y)]: # check spheres
                                if ((x-int(x)-0.5)**2 + (y-int(y)-0.5)**2 + (z-int(z)-0.5)**2 < 0.25):
                                    modr = modr*0.9
                            else:    
                                modr = modr*0.9
                                
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
##    print('Resolution: ', width, height)
    return width, height, mod, inc, rr, gg, bb

@njit(fastmath=True)
def agents(enx, eny, maph, posx, posy, rot, et, shoot, sx, sy, sdir, mplayer, seenx, seeny):
    
    if enx != 0:
        dtp = np.sqrt((enx-posx)**2 + (eny-posy)**2)
        cos, sin = (posx-enx)/dtp, (posy-eny)/dtp
        x, y = enx, eny

        if int(seenx) == int(enx) or int(seeny) == int(eny) or np.random.uniform(0,1) > 0.95:
            for i in range(2000):
                x += 0.05*cos; y += 0.05*sin
                if maph[int(x)][int(y)] != 0:
                    break
                elif int(x) == int(posx) and int(y) == int(posy):
                    seenx, seeny = posx, posy
                    break
            
        if int(seenx) != int(enx) or int(seeny) != int(eny):
            cos, sin = (seenx-enx)/dtp, (seeny-eny)/np.sqrt((enx-seenx)**2 + (eny-seeny)**2)
            
            x, y = enx + et*(.9*cos+np.random.normal(0,.5)), eny + et*(.9*sin+np.random.normal(0,.5))

        if maph[int(x)][int(y)] == 0:
            enx, eny = x, y
            
        mplayer[int(enx)][int(eny)] = 3
        
        
    if shoot:
        if (sx - enx)**2 + (sy - eny)**2 < 0.1:
                shoot, sx, enx = 0, -1, 0
        if sx == -1:
            sx, sy, sdir = posx + np.cos(rot)/3, posy + np.sin(rot)/3, rot+np.random.normal(0,.05)
        sx, sy = sx + 4*et*np.cos(sdir), sy + 4*et*np.sin(sdir)
        if maph[int(sx)][int(sy)] != 0:
            shoot, sx, sy = 0, -1, -1
        else:    
            mplayer[int(sx)][int(sy)] += 6    

    if maph[int(sx)][int(sy)] != 0:
        shoot, sx, sy = 0, -1, -1
        
    mplayer[int(posx)][int(posy)] =2
    mplayer = maph + mplayer
    return(enx, eny, mplayer, et, shoot, sx, sy, sdir, seenx, seeny)

if __name__ == '__main__':
    main()
