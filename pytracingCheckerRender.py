import numpy as np
import pygame as pg
from numba import njit

def main():
    #new map
    mr, mg, mb, maph, mapr, exitx, exity, mapt, maps, posx, posy, posz, size, rot, rot_v = new_map()

    #new game
    running, pause, fps_lock, score, maxscore = 1, 1, 60, 0, 0
    timer, autores, checker , move = 0, 1, 1, 0
    width, height, mod, rr, gg, bb, count = adjust_resol(300)
    minimap, mplayer = np.zeros((size, size, 3)), np.zeros([size, size])
        
    endmsg = ' Numba compiling, please wait... '
    rr, gg, bb = np.linspace(0,0.8, width*height), np.linspace(0.5,.1, width*height), np.linspace(1,0.1, width*height)
    drawing(rr, gg, bb, height, width, 1, endmsg, 0, 10, minimap, score, False)
    pg.time.wait(200)
    
    clock = pg.time.Clock()
    pg.mouse.set_visible(False)
    pg.mixer.set_num_channels(4)# 0 ambient, 1 - run kill respawn 2 - shoot player 3 - shoot enemy
    ambient, runfx, shotfx, killfx, respawnfx, successfx, failfx, fr, fg, fb = sfx()
    pg.mixer.Channel(0).play(ambient, -1)
    endmsg = " Numba may need more compiling... "
    pg.mixer.Channel(1).play(respawnfx)
    ticks = pg.time.get_ticks()/100000
    lx, ly, lz = size/2 + 1500*np.cos(ticks), size/2 + 1000*np.sin(ticks), 1000
    enx, eny, seenx, seeny, lock, run, shoot, sx, sy, sstart, et, count, health, sdir, sdir2, shoot2, sx2, sy2, sstart2, won, et, run, respawn = \
    new_game(width, height, mod, move, posx, posy, .99, rot, rot_v, mr, mg, mb, lx, ly, lz, maph, exitx, exity, mapr, mapt, maps,
             rr, gg, bb, 0, 0, 0, 0, 0, 0, size, checker, 0, fb, fg, fr, pause, endmsg, 0, 10, minimap, score, -.5/61)
    
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                if not pause:
                    pause = 1
                    pg.mixer.Channel(1).play(respawnfx)
                    endmsg = " Game paused. Current score: " + str(score) + ' '
                else:
                    endmsg = " Thanks for playing! Max score: " + str(maxscore) + ' '
                    pg.mixer.Channel(1).play(killfx)
                    running = False
            if sstart == None and(event.type == pg.MOUSEBUTTONDOWN or event.type == pg.MOUSEBUTTONUP):
                shoot = 1
            if event.type == pg.KEYDOWN:
                if event.key == ord('p') or (pause and event.key == pg.K_SPACE): # pause
                    if not pause:
                        pause = 1
                        pg.mixer.Channel(1).play(respawnfx)
                        endmsg = " Game paused. Current score: " + str(score)
                    elif (int(posx) != exitx or int(posy) != exity):
                        if health == 0:
                            health = 5
                        pause = 0
                        pg.mixer.Channel(1).play(respawnfx)
                if pause and event.key == ord('n'): # new game
                    pause = 0
                    mr, mg, mb, maph, mapr, exitx, exity, mapt, maps, posx, posy, posz, size, rot, rot_v = new_map()
                    enx, eny, seenx, seeny, lock, run, shoot, sx, sy, sstart, et, count, health, sdir, sdir2, shoot2, sx2, sy2, sstart2, won, et, run, respawn = \
                    new_game(width, height, mod, move, posx, posy, .99, rot, rot_v, mr, mg, mb, lx, ly, lz, maph, exitx, exity, mapr, mapt, maps,
                             rr, gg, bb, enx, eny, sx, sy, sx2, sy2, size, checker, count, fb, fg, fr, pause, endmsg, won, health, minimap, score, -.5/61)
                    mplayer, minimap = np.zeros([size, size]), np.zeros((size, size, 3))
                    pg.mixer.Channel(1).play(respawnfx)
                    
                if event.key == ord('t'): # toggle auto resolution
                    autores = not(autores)
                if event.key == ord('r'): # toggle checkerboard rendering
                    checker = not(checker)
                if event.key == ord('f'): # toggle fullscreen
                    pg.display.toggle_fullscreen()
                if event.key == ord('q'): # change resolution or fps
                    if autores:
                        fps_lock = max(20, fps_lock - 10)
                    else:
                        if width > 100 :
                            width, height, mod, rr, gg, bb, count = adjust_resol(int(width*0.8))
                if event.key == ord('e'): # change resolution or fps
                    if autores:
                        fps_lock = min(120, fps_lock + 10)
                    else:
                        width, height, mod, rr, gg, bb, count = adjust_resol(int(width*1.1))
            
        if pause:
            clock.tick(30)
            drawing(gg, gg, gg, height, width, pause, endmsg, won, health, minimap, score)

        else:
            enx, eny, mplayer, et, shoot, sx, sy, sdir, shoot2, sx2, sy2, sdir2, seenx, seeny, lock = agents(enx, eny, maph, posx, posy, rot, et, shoot,
                                                                                                             sx, sy, sdir, shoot2, sx2, sy2, sdir2, mplayer,
                                                                                                             seenx, seeny, lock, size)
##            print( ' agents ok ')
            ticks = pg.time.get_ticks()/100000
            lx, ly, lz = size/2 + 1500*np.cos(ticks), size/2 + 1000*np.sin(ticks), 1000
            
            rr, gg, bb = super_fast(width, height, mod, move, posx, posy, posz, rot, rot_v, mr, mg, mb, lx, ly, lz,
                                    mplayer, exitx, exity, mapr, mapt, maps, rr, gg, bb, enx, eny, sx, sy, sx2, sy2,
                                    size, checker, count,fb, fg, fr)
##            print(' render ok')
            count += 1
            if enx != 0 and lock:
                endmsg = 'Pytracing Maze -   Watch out!      Score:'
            else:
                endmsg = 'Pytracing Maze - Find the exit!    Score:'
            endmsg = endmsg + str(score)+' Res: '+ str(width) +'x' + str(height) + '  FPS: '+ str(int(clock.get_fps()))
            minimap[int(posy)][int(posx)] = (50, 50, 255)
            drawing(rr, gg, bb, height, width, pause, endmsg, won, health, minimap, score)
            minimap[int(posy)][int(posx)] = (100, 100, 0)
                
            fpss = int(1000/(pg.time.get_ticks() - ticks*100000 +1e-16))

            if autores and count > 10: #auto adjust render resolution
                if fpss < fps_lock - 10 and width > 100:
                        width, height, mod, rr, gg, bb, count = adjust_resol(int(width*0.8))
                elif fpss > fps_lock + 15:
                        width, height, mod, rr, gg, bb, count = adjust_resol(int(width*1.1))        

            if (int(posx) == exitx and int(posy) == exity):
                endmsg, won = " You escaped safely! ", 1
                pg.mixer.Channel(1).play(successfx)
                animate(width, height, mod, move, posx, posy, .5, rot, rot_v, mr, mg, mb, lx, ly, lz,
                        mplayer, exitx, exity, mapr, mapt, maps, rr, gg, bb, enx, eny, sx, sy, sx2, sy2,
                        size, checker, count,fb, fg, fr, pause, endmsg, won, health, minimap, score, .5/61)
                pause = 1
                score += 1
                maxscore = max(score, maxscore)         
            
            et = min(clock.tick()/500, 0.1)*(0.8+move)

            if shoot or sstart != None:
                if sstart == None:
                    pg.mixer.Channel(2).play(shotfx)
                    if fpss < fps_lock and autores:
                        width, height, mod, rr, gg, bb, count = adjust_resol(int(width*0.8))
                    sstart = pg.time.get_ticks()
                elif pg.time.get_ticks() - sstart > 500:
                    shoot, sx, sy, sstart = 0, -1, -1, None

            if enx == 0:
                if not respawn:
                    if shoot:
                        health = min(health+2, 20)
                    shoot2, sx2, sy2 = 0, -1, -1
                    pg.mixer.Channel(1).play(killfx)
                    run = 1
                    respawn = 1
                    
                
            else:
                if respawn:
                    respawn = 0
                    pg.mixer.Channel(1).play(respawnfx)    
                if shoot2 or sstart2 != None:
                    if run:
                        run = 0
                        pg.mixer.Channel(1).play(runfx)
                    if sstart2 == None:
                        pg.mixer.Channel(3).play(shotfx)
                        sstart2 = pg.time.get_ticks()
                    elif pg.time.get_ticks() - sstart2 > 500:
                        shoot2, sx2, sy2, sstart2 = 0, -1, -1, None
                        
                    if (sx2 - posx)**2 + (sy2 - posy)**2 < 0.01:
                        health -= 1 + score/2
                        if health <= 0:
                            won, pause, health = -1, 1, 0
                            if score > 0:
                                score -= 1
                            endmsg = " You died! Current score: " + str(score) + ' '
                            pg.mixer.Channel(1).play(failfx)
                            animate(width, height, mod, move, posx, posy, .5, rot, rot_v, mr, mg, mb, lx, ly, lz,
                                    mplayer, exitx, exity, mapr, mapt, maps, rr, gg, bb, enx, eny, sx, sy, sx2, sy2,
                                    size, checker, count,fb, fg, fr, pause, endmsg, won, health, minimap, score, -.5/61)
                            pg.time.wait(500)    
                            enx, eny, seenx, seeny, lock, won  = 0, 0, 0, 0, 0, 0

                dtp = (enx-posx)**2 + (eny-posy)**2
                if dtp > 150 and not shoot2:
                    run = 1
                if dtp > 300:
                    enx, eny, seenx, seeny, lock, run  = 0, 0, 0, 0, 0, 0

            posx, posy, rot, rot_v, shoot, move = movement(pg.key.get_pressed(),posx, posy, rot, rot_v, maph, et, shoot, sstart, move)
            pg.mouse.set_pos([640, 360])
            mplayer = np.zeros([size, size])
            
        
        pg.display.update()

    pg.mixer.fadeout(600)
    print(endmsg)
    if health > 0 and (int(posx) != exitx or int(posy) != exity):
        animate(width, height, mod, move, posx, posy, .5, rot, rot_v, mr, mg, mb, lx, ly, lz,
                maph, exitx, exity, mapr, mapt, maps, rr, gg, bb, enx, eny, sx, sy, sx2, sy2,
                size, checker, count,fb, fg, fr, pause, endmsg, won, health, minimap, score, +.5/61)
    else:
        pg.time.wait(500)
    pg.quit()

def new_map():
    size = np.random.randint(30,80) # size of the map
    posx, posy, posz = np.random.randint(1, size -2)+0.5, np.random.randint(1, size -2)+0.5, 0.5
    x, y = int(posx), int(posy)
    rot, rot_v = (np.pi/4, 0)
    
    mr = np.random.uniform(0,1, (size,size)) 
    mg = np.random.uniform(0,1, (size,size)) 
    mb = np.random.uniform(0,1, (size,size)) 
    mapr = np.random.choice([0, 0, 0, 0, 1], (size,size))
    maps = np.random.choice([0, 0, 0, 0, 1], (size,size))
    mapt = np.random.choice([0, 0, 0, 1, 2, 3], (size,size))
    maptemp = np.random.choice([0,0, 1], (size,size))
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
                dtx = np.sqrt((x-posx)**2 + (y-posy)**2)
                if (dtx > size*.6 and np.random.uniform() > .99) or np.random.uniform() > .99999:
                    exitx, exity = (x, y)
                    break
            else:
                count = count+1
    
    return mr, mg, mb, maph, mapr, exitx, exity, mapt, maps, posx, posy, posz, size, rot, rot_v

def new_game(width, height, mod, move, posx, posy, posz, rot, rot_v, mr, mg, mb, lx, ly, lz, maph, exitx, exity, mapr, mapt, maps,
             rr, gg, bb, enx, eny, sx, sy, sx2, sy2, size, checker, count, fb, fg, fr, pause, endmsg, won, health, minimap, score, ani):

    animate(width, height, mod, move, posx, posy, posz, rot, rot_v, mr, mg, mb, lx, ly, lz, maph, exitx, exity, mapr, mapt, maps,
             rr, gg, bb, enx, eny, sx, sy, sx2, sy2, size, checker, count, fb, fg, fr, pause, endmsg, won, health, minimap, score, ani)
#enx, eny, seenx, seeny, lock, run, shoot, sx, sy, sstart, et, count, health, sdir, sdir2, shoot2, sx2, sy2, sstart2, won, et, run, respawn
    return 0, 0, 0, 0, 0, 1, 0, -1, -1, None, 0.1, 0, 10, 0, 0, 0, -1, -1, None, 0, 0.1, 1, 1

def movement(pressed_keys,posx, posy, rot, rot_v, maph, et, shoot, sstart, move):
    x, y = (posx, posy)
    p_mouse = pg.mouse.get_pos()
    rot, rot_v = rot - np.clip((p_mouse[0]-640)/200, -0.2, .2), rot_v -(p_mouse[1]-360)/400
    rot_v = np.clip(rot_v, -1, 1)
    diag = 0

    if pressed_keys[pg.K_UP] or pressed_keys[ord('w')]:
        diag = 0.5
        x, y, move, diag = x + et*np.cos(rot), y + et*np.sin(rot), move + et/4, 1

    elif pressed_keys[pg.K_DOWN] or pressed_keys[ord('s')]:
        x, y, move, diag = x - et*np.cos(rot), y - et*np.sin(rot), move - et/2, 1
        
    if pressed_keys[pg.K_LEFT] or pressed_keys[ord('a')]:
        et = et/(diag+1)
        x, y, move = x - et*np.sin(rot), y + et*np.cos(rot), move - et/2
        
    elif pressed_keys[pg.K_RIGHT] or pressed_keys[ord('d')]:
        et = et/(diag+1)
        x, y, move = x + et*np.sin(rot), y - et*np.cos(rot), move - et/2

    if x == posx and y == posy:
        move = move - et/2

    if maph[int(x-0.05)][int(y)] == 0 and maph[int(x+0.05)][int(y)] == 0 and maph[int(x)][int(y+0.05)] == 0:
        posx, posy = x, y 
    elif maph[int(posx-0.05)][int(y)] == 0 and maph[int(posx+0.05)][int(y)] == 0 and maph[int(posx)][int(y+0.05)] == 0:
        posy = y
    elif maph[int(x-0.05)][int(posy)] == 0 and maph[int(x+0.05)][int(posy)] == 0 and maph[int(x)][int(posy+0.05)] == 0:
        posx = x
    else:
        move = move - et/2
        
    if not shoot and sstart == None and pressed_keys[pg.K_SPACE]:
        shoot = 1
    move = np.clip(move, 0, 0.3)
    return posx, posy, rot, rot_v, shoot, move

@njit(cache=True)
def lodev(x, y, z, cos, sin, sinz, maph, size):
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
            if mapX < 2 or mapX > size-2:
                break
        else:
            sideDistY += deltaDistY; mapY += stepY
            dist = sideDistY; side = 1
            if mapY < 2 or mapY > size-2:
                break
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
    return x, y, z
        
@njit(cache=True)
def super_fast(width, height, mod, move, posx, posy, posz, rot, rot_v, mr, mg, mb, lx, ly, lz,
               maph, exitx, exity, mapr, mapt, maps, pr, pg, pb, enx, eny, sx, sy, sx2, sy2,
               size, checker, count, fb, fg, fr):
    inverse = count%2
    garbage = not(count)
    idx = 0
    for j in range(height): #vertical loop 
        rot_j = rot_v + (1+move**1.5)*np.deg2rad(24 - j/mod)
        sinzo = (0.02/mod)*np.sin(rot_j) 
        coszo = (0.02/mod)*np.sqrt(abs(np.cos(rot_j)))        
        for i in range(width): #horizontal vision loop
            if (not(checker) or i == 0 or i == width -1 or j == 0 or j == height -1 or (inverse and i%2 == j%2) or (not(inverse) and i%2 != j%2)):
                rot_i = rot + (1+move**1.5)*np.deg2rad(i/mod - 30)
                x, y, z = (posx, posy, posz)
                sin, cos, sinz = coszo*np.sin(rot_i), coszo*np.cos(rot_i), sinzo
                   
                modr = 1
                cx, cy, c1r, c2r, c3r = 1, 1, 1, 1, 1
                shot, enem, mapv = 0, 0, 0
                dtp = np.random.uniform(0.002,0.01)
                for k in range(2000):
                    if (mapv == 0 or (sinz > 0 and (z > mapv or (mapv==6 and (z>0.4 or z <0.2)) or(z > 0.57 and mapv > 1)))): ## LoDev DDA for optimization
                        x, y, z = lodev(x, y, z, cos, sin, sinz, maph, size)
                    
                    x += cos; y += sin; z += sinz
                    if (z > 1 or z < 0): # check ceiling and floor
                        break
                    mapv = maph[int(x)][int(y)]
                    if mapv > 1 and z < 0.58:
                        if mapv == 2 or mapv == 8 or mapv == 3 or mapv == 9:
                            refx, refy, sh = enx, eny, .2
                            if  mapv == 2 or mapv == 8:
                                refx, refy, sh = posx, posy, .8                                
                            if z> 0.45 and (x-refx)**2 + (y-refy)**2 + (z-0.5)**2 < 0.003 +abs(z-0.47)/30 :
                                break # head
                            if z < 0.45 and z > 0.28 and (x-refx)**2 + (y-refy)**2  < (z/10 - 0.02):
                                break # chest
                            if z < 0.28 and (x-refx)**2 + (y-refy)**2 + (z-0.15)**2 < 0.023 :
                                    break #roller
                        if  mapv > 5 and z < 0.4 and z > 0.2:
                            if mapv < 12:
                                refx = sx2; refy = sy2
                            else:
                                refx = sx; refy = sy
                            if ((x-refx)**2 + (y-refy)**2 + (z-0.3)**2 < dtp):
                                shot = 1
                                break

                    if mapv > z and mapv < 2: # check walls
                        if maps[int(x)][int(y)]: # check spheres
                            if ((x-int(x)-0.5)**2 + (y-int(y)-0.5)**2 + (z-int(z)-0.5)**2 < 0.24):
                                if (mapr[int(x)][int(y)]): # spherical mirror
                                    if (modr == 1):
                                        cx, cy = int(x), int(y)
                                    modr = modr*0.7
                                    if (modr < 0.2):
                                        break
                                    if (mapv - z <= abs(sinz)): ## horizontal surface
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
                    norm = np.sqrt(cos**2 + sin**2 + sinz**2)
                    rayDirX, rayDirY, rayDirZ = cos/norm + 1e-16, sin/norm + 1e-16, sinz/norm + 1e-16    
                    deltaDistX, deltaDistY, deltaDistZ= abs(1/rayDirX), abs(1/rayDirY), abs(1/rayDirZ)
                    deltaDistZ = (lz-z)*deltaDistZ
                    x += deltaDistZ*rayDirX; y += deltaDistZ*rayDirY; z = lz
                    dtol = np.sqrt((x-lx)**2+(y-ly)**2)

                    if dtol < 50: #light source
                        shot = 1
                        c1, c2, c3 = 1, 1, 0.5
                    else:
                        angle = np.rad2deg(np.arctan((y-ly)/(x-lx)))/np.random.uniform(12,15)
                        sh = (0.8+ abs(angle - int(angle))/5)/(dtol/1000)
                        if sh > 1:
                            sh = 1
                        if int(angle)%2 == 1:
                            c1, c2, c3 = 0.8*(1-sh), 0.86*(1-sh/4), (1-sh/10)
                        else:
                            c1, c2, c3 = 0.8*(1-sh), 0.9*(1-sh/4), (1-sh/10)
                    if sx != -1:
                        c1, c2, c3 = 0.7*c1, 0.7*c2, 0.7*c3
                        
                elif z < 0: # floor
                    z= 0
                    xx = int(3*x%1*100) + int(3*y%1*100)*100
                    if int(x) == exitx and int(y) == exity: #exit
                        c1, c2, c3 = fr[xx]/655, fr[xx]/555, fr[xx]/256
                    else:
                        sh = 0.3 + (x+y)/(3*size)
                        c1, c2, c3 = (1-sh/2)*fg[xx]/300, sh*fg[xx]/256, sh*fb[xx]/300
                            
                elif mapv < 2: # walls
                    c1, c2, c3 = mr[int(x)][int(y)], mg[int(x)][int(y)], mg[int(x)][int(y)]
                    if mapt[int(x)][int(y)] > 1: # textured walls
                        if y%1 < 0.01 or y%1 > 0.99:
                            ww = int(3*x%1*100)
                        else:
                            ww = int(3*y%1*100)
                        if x%1 < 0.99 and x%1 > 0.01 and y%1 < 0.99 and y%1 > 0.01:
                            zz = int(3*x%1*100)
                        else:
                            zz = int(3*z%1*100)
                        xx = zz + ww*100
                        
                        if maps[int(x)][int(y)]: # spheres get funky textures
                            c1, c2, c3 = c1*fr[xx+1]/455, c2*fg[xx-1]/455, c3*fb[xx]/755
                        else:
                            xx = fr[xx]/255
                            c1, c2, c3 = c1*xx, c2*xx, c3*xx
                    if mapt[int(x)][int(y)]%2 == 1: # gradient walls
                        c1, c2, c3 = c1*(2+z)/3, c2*(3-z)/3, c3*(2+z**2)/3
                        
                    if mapv - z <= abs(sinz): # round coordinates
                        z = mapv
                    elif not maps[int(x)][int(y)]:
                        if int(x-cos) != int(x):
                            x = max(int(x-cos), int(x))
                            modr = modr*0.80
                        else:
                            y = max(int(y-sin), int(y))
                            modr = modr*0.9
                else: # agents
                    if shot: # fireball
                        sh = ((x-refx)**2 + (y-refy)**2 + (z-0.3)**2)/0.012
                        c1, c2, c3 = 1, 0.6*sh+0.2 , 0.2*sh+0.1 
                    elif z> 0.45: # Head
                        c1, c2, c3 = (1-z)*(1-sh), (1-z)*sh, z*sh 
                    elif z > 0.28: # Chest
                        c1, c2, c3 = 2*(z-0.28), (z-0.28)*(1-sh), (z-0.28)*sh 
                    else: # Roller
                        c1, c2, c3 = refx%1*z*(1-sh), refy%1*0.2*sh, refy%1*z*sh 

                if modr <= 0.7 and not shot: # tinted mirrors
                    c1r, c2r, c3r = mr[cx][cy], mg[cx][cy], mg[cx][cy]

                if not shot and z < 1: # shadows
                    dtp = np.sqrt((x-posx)**2+(y-posy)**2+(z-posz)**2)
                    if dtp > 7:
                        modr = modr/np.log((dtp-6)/4+np.e)
                    if sx != -1 and maph[int(sx)][int(sy)] > 1: # fireball
                        shot, c3, limodr = 1, c3 * 0.9, 0.6
                        dtol = np.sqrt((x-sx)**2+(y-sy)**2+(z-0.35)**2)
                        cos, sin, sinz = .01*(sx-x)/dtol, .01*(sy-y)/dtol, .01*(0.35-z)/dtol
                    elif sx2 != -1 and maph[int(sx2)][int(sy2)] > 1: # fireball enemy
                        shot, c3, limodr = 1, c3 * 0.9, 0.6
                        dtol = np.sqrt((x-sx2)**2+(y-sy2)**2+(z-0.35)**2)
                        cos, sin, sinz = .01*(sx2-x)/dtol, .01*(sy2-y)/dtol, .01*(0.35-z)/dtol
                    else:  # sun
                        limodr = 0.4
                        dtol = np.sqrt((x-lx)**2+(y-ly)**2+(z-lz)**2)
                        cos, sin, sinz = .01*(lx-x)/dtol, .01*(ly-y)/dtol, .01*(lz-z)/dtol

                    x += cos; y += sin; z += sinz # advance one step
                    mapv = maph[int(x)][int(y)]
                    if z < mapv and mapv < 1:# if already hit something apply dark shade
                        if maps[int(x)][int(y)]:
                            if ((x-int(x)-0.5)**2 + (y-int(y)-0.5)**2 + (z-int(z)-0.5)**2 < 0.24):
                                modr = modr*0.39
                        else:
                            modr = modr*0.39
                    for k in range(1000):
                        if (mapv == 0) or not shot and ((z > mapv) or (z > 0.57 and mapv > 1)): ## LoDev DDA for optimization
                            x, y, z = lodev(x, y, z, cos, sin, sinz, maph, size)
                        x += cos; y += sin; z += sinz
                        mapv = maph[int(x)][int(y)]
                        if shot:
                            if mapv > 5 or (sinz > 0 and z > 0.35) or (sinz < 0 and z < 0.35) or modr < limodr:
                                break
                        elif z >1 or modr < limodr:
                            break
                        if z < 0.58 and mapv > 1 and (mapv == 2 or mapv == 8 or mapv == 3 or mapv == 9):
                            refx, refy, sh = enx, eny, .2
                            if  mapv == 2 or mapv == 8:
                                refx, refy, sh = posx, posy, .8
                            if z> 0.45 and (x-refx)**2 + (y-refy)**2 + (z-0.5)**2 < 0.003 +abs(z-0.47)/30:
                                modr = modr*0.67 # head
                            if z < 0.45 and z > 0.28 and (x-refx)**2 + (y-refy)**2  < (z/10 - 0.02):
                                modr = modr*0.67 # chest
                            if z < 0.28 and (x-refx)**2 + (y-refy)**2 + (z-0.15)**2 < 0.023 :
                                modr = modr*0.67 #roller
                                    
                        if mapv > 0 and z <= mapv and mapv < 2:      
                            if maps[int(x)][int(y)]: # check spheres
                                if ((x-int(x)-0.5)**2 + (y-int(y)-0.5)**2 + (z-int(z)-0.5)**2 < 0.25):
                                    modr = modr*0.9
                            else:    
                                modr = modr*0.9                    
                    
                pr[idx] = (3*modr*np.sqrt(c1*c1r) + (1-garbage)*pr[idx])/(4-garbage)
                pg[idx] = (3*modr*np.sqrt(c2*c2r) + (1-garbage)*pg[idx])/(4-garbage)
                pb[idx] = (3*modr*np.sqrt(c3*c3r) + (1-garbage)*pb[idx])/(4-garbage)
            idx += 1
    if checker: # fill gaps
        idx = 0
        for j in range(height): #vertical loop        
            for i in range(width): #horizontal vision loop
                if (i > 0 and i < width -1 and j > 0 and j < height -1 and ((inverse and i%2 != j%2) or (not(inverse) and i%2 == j%2))):
                    if abs(pr[idx-1] - pr[idx+1]) < 0.05 and abs(pg[idx-1] - pg[idx+1]) < 0.05 and abs(pb[idx-1] - pb[idx+1]) < 0.05 :
                        pr[idx], pg[idx], pb[idx]  = (pr[idx-1] + pr[idx+1])/2, (pg[idx-1] + pg[idx+1])/2, (pb[idx-1] + pb[idx+1])/2
                    elif abs(pr[idx-width] - pr[idx+width]) < 0.05 and abs(pg[idx-width] - pg[idx+width]) < 0.05 and abs(pb[idx-width] - pb[idx+width]) < 0.05 :
                        pr[idx], pg[idx], pb[idx] = (pr[idx-width] + pr[idx+width])/2, (pg[idx-width] + pg[idx+width])/2, (pb[idx-width] + pb[idx+width])/2
                    else:
                        pr[idx] = ((1-garbage)*pr[idx] + pr[idx-1] + pr[idx-width] + pr[idx+width] + pr[idx+1])/(5-garbage)
                        pg[idx] = ((1-garbage)*pg[idx] + pg[idx-1] + pg[idx-width] + pg[idx+width] + pg[idx+1])/(5-garbage)
                        pb[idx] = ((1-garbage)*pb[idx] + pb[idx-1] + pb[idx-width] + pb[idx+width] + pb[idx+1])/(5-garbage)
                idx += 1
    return pr, pg, pb

def adjust_resol(width):
    height = int(0.6*width)
    mod = width/64
    rr = np.random.uniform(0,1,width * height)
    gg = np.random.uniform(0,1,width * height)
    bb = np.random.uniform(0,1,width * height)
    return width, height, mod, rr, gg, bb, 0

@njit(cache=True)
def agents(enx, eny, maph, posx, posy, rot, et, shoot, sx, sy, sdir, shoot2, sx2, sy2, sdir2, mplayer, seenx, seeny, lock, size):
    # respawn
    if enx == 0 and np.random.uniform(0,1) > 0.995:
        x, y = np.random.normal(posx, 5), np.random.normal(posy, 5)
        dtp = (x-posx)**2 + (y-posy)**2
        if x > 0 and x < size-1 and y > 0 and y < size-1:
            if maph[int(x)][int(y)] == 0 and dtp > 25 and dtp < 64:
                enx, eny, seenx, seeny, lock = x, y, x, y, 0
    else:
        # look for player
        if not lock or  np.random.uniform(0,1) > 0.99:
            dtp = np.sqrt((enx-posx)**2 + (eny-posy)**2)
            cos, sin = (posx-enx)/dtp, (posy-eny)/dtp
            x, y = enx, eny
            for i in range(300):
                x += 0.04*cos; y += 0.04*sin
                if (maph[int(x+.05)][int(y+.05)] != 0 or maph[int(x-.05)][int(y-.05)] != 0 or
                    maph[int(x-.05)][int(y+.05)] != 0 or maph[int(x+.05)][int(y-.05)] != 0):
                    lock = 0
                    break
                if(int(x) == int(posx) and int(y) == int(posy)):
                    seenx, seeny, lock = posx, posy, 1
                    break

        if int(enx) == int(seenx) and int(eny) == int(seeny):
            if not lock:
                if shoot: #if the player is shooting go towards him
                    seenx, seeny = np.random.uniform(enx, posx), np.random.uniform(eny, posy)
                else:
                    seenx, seeny = np.random.normal(enx, 2), np.random.normal(eny, 2) 
            else:
                seenx, seeny = np.random.normal(posx, 2), np.random.normal(posy, 2)
            
        dtp = np.sqrt((enx-seenx)**2 + (eny-seeny)**2)    
        cos, sin = (seenx-enx)/dtp, (seeny-eny)/dtp    
        x, y = enx + et*cos, eny + et*sin

        if maph[int(x)][int(y)] == 0:
            enx, eny = x, y
        else:
            if np.random.uniform(0,1) > 0.5:
                x, y = enx - et*sin, eny + et*cos
            else:
                x, y = enx + et*sin, eny - et*cos
            if maph[int(x)][int(y)] == 0:
                enx, eny = x, y
            else:
                seenx, seeny = enx+np.random.normal(0,3), eny+np.random.normal(0,3)
                lock = 0
                
        mplayer[int(enx)][int(eny)] = 3
        if (maph[int(enx+.1)][int(eny+.1)] == 0 and maph[int(enx-.1)][int(y-.1)] == 0 and
            maph[int(enx-.1)][int(eny+.1)] == 0 and maph[int(enx+.1)][int(y-.1)] == 0):
            mplayer[int(enx+0.1)][int(eny+0.1)], mplayer[int(enx+0.1)][int(eny-0.1)] = 3, 3
            mplayer[int(enx-0.1)][int(eny+0.1)], mplayer[int(enx-0.1)][int(eny-0.1)] = 3, 3

        
    mplayer[int(posx)][int(posy)] = 2
    if lock and not shoot2:
        shoot2 = 1
        sdir2 = np.arctan((posy-eny)/(posx-enx)) + np.random.uniform(-.1,.1)
        if abs(enx+np.cos(sdir2)-posx) > abs(enx-posx):
            sdir2 = sdir2 - np.pi
        
    if shoot2:
        if sx2 == -1:
            sx2, sy2 = enx + .5*np.cos(sdir2), eny + .5*np.sin(sdir2)
        sx2, sy2 = sx2 + 5*et*np.cos(sdir2), sy2 + 5*et*np.sin(sdir2)
        if sx2 > 0 and sx2 < size-1 and sy2 > 0 and sy2 < size-1:
            if (maph[int(sx2+.05)][int(sy2+.05)] != 0 or maph[int(sx2-.05)][int(sy2-.05)] != 0 or
                maph[int(sx2-.05)][int(sy2+.05)] != 0 or maph[int(sx2+.05)][int(sy2-.05)] != 0):
                shoot2, sx2, sy2 = 0, -1, -1
            else:    
                mplayer[int(sx2)][int(sy2)] += 6
        else:
            shoot2, sx2, sy2 = 0, -1, -1
    if shoot:
        if sx == -1:
            sdir = rot+np.random.uniform(-.1,.1)
            sx, sy = posx + .5*np.cos(sdir), posy + .5*np.sin(sdir)
        sx, sy = sx + 5*et*np.cos(sdir), sy + 5*et*np.sin(sdir)
        if sx > 0 and sy < size-1 and sy > 0 and sy < size-1:
            if enx != 0 and (sx - enx)**2 + (sy - eny)**2 < 0.02:
                enx, eny, seenx, seeny = 0, 0, 0, 0
            if (maph[int(sx+.05)][int(sy+.05)] != 0 or maph[int(sx-.05)][int(sy-.05)] != 0 or
                maph[int(sx-.05)][int(sy+.05)] != 0 or maph[int(sx+.05)][int(sy-.05)] != 0):
                shoot, sx, sy = 0, -1, -1
            else:    
                mplayer[int(sx)][int(sy)] += 12
        else:
            shoot, sx, sy = 0, -1, -1
        
    
    mplayer = maph + mplayer
    return(enx, eny, mplayer, et, shoot, sx, sy, sdir, shoot2, sx2, sy2, sdir2, seenx, seeny, lock)

def drawing(rr, gg, bb, height, width, pause, endmsg, won, health, minimap, score, nosplash=True):
    global font, font2, screen, surfbg
    
    surfbg.fill(pg.Color("darkgrey"))
    pg.draw.rect(surfbg, (200-int(health*10), 50+int(health*10), 0),(10,int(360-36*(10-health/2)),1260,int(72*(10-health/2))))
        
    pixels = np.dstack((rr,gg,bb))
    pixels = np.reshape(pixels, (height,width,3))
    surf = pg.surfarray.make_surface((np.rot90(pixels*255)).astype('uint8'))
    surf = pg.transform.scale(surf, (1200, 720))
    if not nosplash or pause:
        px, py = 1100, 360
        if nosplash:
            px, py = pg.mouse.get_pos()
        for i in range(3):
            pg.draw.circle(surf, (50, 70+i*20, 160+i*40), [px+i*10,py-i*10], 50-i*15)
            pg.draw.circle(surf, (60+i*10, 100+i*20, 100+i*10), [px+i*10,py+280-i*1], 90-i*15)
            pg.draw.polygon(surf, (150+i*30, 34+i*10, 60+i*10), [[px-100+i*20,py+40+i*15],[px+100-i*20,py+40+i*15],[px+50-i*15,py+205-i*15],[px-50+i*15,py+205-i*15]])
    screen.blit(surfbg, (0, 0))
    screen.blit(surf, (40, 0))
    
    if pause:        
        screen.blit(font2.render(" PyTracing Maze by FinFET ", 0, pg.Color("red")),(45,45))
        screen.blit(font2.render(" PyTracing Maze by FinFET ", 0, pg.Color("blue")),(55,55))
        screen.blit(font2.render(" PyTracing Maze by FinFET ", 0, pg.Color("white")),(50,50))
        screen.blit(font2.render(endmsg, 0, pg.Color("salmon"), (100, 34, 60)),(50,420))
        if nosplash:
            screen.blit(font2.render(" Press N for a new game ", 0, pg.Color("grey"), (45, 34, 100)),(50,560))
            screen.blit(font2.render(" Press ESC to leave ", 0, pg.Color("grey"), (13, 34, 139)),(50,630))
            if won == 1:
                screen.blit(font2.render(" Your current score is "+str(score) + ' ', 0, pg.Color("grey"), (80, 34, 80)),(50,490))
            if won == 0:
                screen.blit(font2.render(" Press P or Space to continue ", 0, pg.Color("grey"), (80, 34, 80)),(50,490))
    else:
        size = len(minimap)
        surfmap = pg.surfarray.make_surface(np.flip(minimap).astype('uint8'))
        surfmap = pg.transform.scale(surfmap, (size*4, size*4))
        screen.blit(surfmap,(1280-size*4 - 65, 25), special_flags=pg.BLEND_ADD)
        fps = font.render(endmsg, 0, pg.Color("coral"))
        screen.blit(fps,(100,1))
        
    pg.display.update()

def animate(width, height, mod, move, posx, posy, posz, rot, rot_v, mr, mg, mb, lx, ly, lz,
            maph, exitx, exity, mapr, mapt, maps, pr, pg, pb, enx, eny, sx, sy, sx2, sy2,
            size, checker, count, fb, fg, fr, pause, endmsg, won, health, minimap, score, ani):
    for i in range(60):
        rr, gg, bb = super_fast(width, height, mod, move, posx, posy, posz+ani*i, rot, rot_v, mr, mg, mb, lx, ly, lz,
                                maph, exitx, exity, mapr, mapt, maps, pr, pg, pb, enx, eny, sx, sy, sx2, sy2,
                                size, checker, count, fb, fg, fr)
        count += 1
        
        drawing(rr, gg, bb, height, width, pause, endmsg, won, health, minimap, score)
        
def sfx():      
    ambient = pg.mixer.Sound('soundfx/HauntSilentPartner.mp3')
    ambient.set_volume(0.5)
    runfx = pg.mixer.Sound('soundfx/run.mp3')
    shotfx = pg.mixer.Sound('soundfx/slap.mp3')
    killfx = pg.mixer.Sound('soundfx/shutdown.mp3')
    respawnfx = pg.mixer.Sound('soundfx/respawn.mp3')
    successfx = pg.mixer.Sound('soundfx/success.mp3')
    failfx = pg.mixer.Sound('soundfx/fail.mp3')
    floor = pg.surfarray.array3d(pg.image.load('soundfx/textures.jpg'))
    fr, fg, fb = np.dsplit(floor,floor.shape[-1])
    fr, fg, fb = fr.flatten(), fg.flatten(), fb.flatten()

    return ambient, runfx, shotfx, killfx, respawnfx, successfx, failfx, fr, fg, fb

if __name__ == '__main__':
    pg.init()
    font = pg.font.SysFont("Arial", 18)
    font2 = pg.font.SysFont("Impact", 48)
    screen = pg.display.set_mode((1280, 720))
    surfbg = pg.Surface((1280,720))
    main()
