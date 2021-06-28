import numpy as np
import pygame as pg
from numba import njit

def main():
    running, pause, fps_lock, score, maxscore, fullscreen = 1, 1, 59, 0, 0, 0
    timer, autores, checker, count, enhealth = 0, 1, 2, 0, 0
    renders = [' R: Standard. ', ' R: Doubled pixels. ', ' R: Checkerboard. ', ' R: Radial window. ', ' R: Squared window. ']
    endmsg = ' Numba compiling, please wait... '
    rr, gg, bb = np.linspace(0,0.8, 25*14), np.linspace(0.5,.1, 25*14), np.linspace(1,0.1, 25*14)
    drawing(rr, gg, bb, 14, 25, 1, endmsg, 0, 10, 10, np.zeros([3,3]), score, fullscreen, False)
    pg.time.wait(200)
    
    clock = pg.time.Clock()
    pg.mouse.set_visible(False)
    pg.mixer.init()
    ambient, runfx, shotfx, killfx, respawnfx, successfx, failfx, fr, fg, fb = sfx()
    ambient.set_volume(0.5)
    ambient.play(-1)
    endmsg = " Numba may need more compiling..."
    
    (mr, mg, mb, maph, mapr, exitx, exity, mapt, maps, posx, posy, posz, size, rot, rot_v, minimap,
     width, height, mod, rr, gg, bb, count, enx, eny, seenx, seeny, lock, run, shoot, sx, sy, sz, sstart,
     et, health, sdir, sdirz, sdir2, sdirz2, shoot2, sx2, sy2, sz2, sstart2, won, respawn, move) = new_game(fb, fg, fr, endmsg, score)    

    while running:
        ticks = pg.time.get_ticks()/100000
        if np.random.uniform() > 0.99:
            pg.display.set_caption(endmsg + ' Options: P or C - Pause, F - Fulscreen, Q/W - FPS lock/Res, R - Render type, T - AutoRes ')
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                if not pause:
                    pause = 1
                    respawnfx.play()
                    endmsg = " Game paused. Current score: " + str(score) + ' '
                else:
                    endmsg = " Thanks for playing! Max score: " + str(maxscore) + ' '
                    killfx.play()
                    running = False
            if sstart == None and(event.type == pg.MOUSEBUTTONDOWN or event.type == pg.MOUSEBUTTONUP):
                shoot = 1
            if event.type == pg.KEYDOWN:
                if event.key == ord('p') or event.key == ord('c'): # pause
                    if not pause:
                        pause = 1
                        respawnfx.play()
                        endmsg = " Game paused. Current score: " + str(score)
                    elif (int(posx) != exitx or int(posy) != exity):
                        if health == 0:
                            health = 5
                            animate(width, height, mod, move, posx, posy, .01, rot, rot_v, mr, mg, mb, lx, ly, lz,
                                    mplayer, exitx, exity, mapr, mapt, maps, rr, gg, bb, enx, eny, sx, sy, sx2, sy2,
                                    size, checker, count,fb, fg, fr, pause, endmsg, won, health, minimap, score, .5/61, fps)
                        pause = 0
                        respawnfx.play()
                if pause and event.key == ord('n'): # new game
                    pause = 0
                    (mr, mg, mb, maph, mapr, exitx, exity, mapt, maps, posx, posy, posz, size, rot, rot_v, minimap,
                     width, height, mod, rr, gg, bb, count, enx, eny, seenx, seeny, lock, run, shoot, sx, sy, sz, sstart,
                     et, health, sdir, sdirz, sdir2, sdirz2, shoot2, sx2, sy2, sz2, sstart2, won, respawn, move) = new_game(fb, fg, fr, endmsg, score)
                    
                    respawnfx.play()
                    
                if event.key == ord('t'): # toggle auto resolution
                    autores = not(autores)
                if event.key == ord('r'): # toggle rendering method
                    checker += 1
                    if checker > 4:
                        checker = 0
                if event.key == ord('f'): # toggle fullscreen
                    pg.display.toggle_fullscreen()
                    fullscreen =  not(fullscreen)
                if event.key == ord('q'): # change resolution or fps
                    if autores:
                        fps_lock = max(19, fps_lock - 10)
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
            drawing(rr*.7, gg*.7, bb*.7, height, width, pause, endmsg, won, health, enhealth, minimap, score, fullscreen)

        else:
            mplayer = np.zeros([size, size])
            (enx, eny, mplayer, et, shoot, sx, sy, sz, sdir, sdirz, shoot2,
             sx2, sy2, sz2, sdir2, sdirz2, seenx, seeny, lock, enhealth, health) = agents(enx, eny, maph, posx, posy, rot, rot_v, et, shoot, sx, sy, sz, sdir,
                                                                                          sdirz, shoot2, sx2, sy2, sz2, sdir2, sdirz2, mplayer,
                                                                                          seenx, seeny, lock, size, enhealth, health, score)

            lx, ly, lz = size/2 + 1500*np.cos(ticks), size/2 + 1000*np.sin(ticks), 1000
            rwr = checker
            if shoot2:
                rwr = 3
            rr, gg, bb = super_fast(width, height, mod, move, posx, posy, posz, rot, rot_v, mr, mg, mb, lx, ly, lz,
                                    mplayer, exitx, exity, mapr, mapt, maps, rr, gg, bb, enx, eny, sx, sy, sx2, sy2,
                                    size, rwr, count, fb, fg, fr, sz, sz2)
            count += 1
            if enhealth != 0 and lock:
                endmsg = 'Pytracing Maze -   Watch out!   Score:'+str(score)+' Res: '+ str(width) +'x'+str(height)+'  FPS: '+str(int(clock.get_fps()))+renders[checker]
            else:
                endmsg = 'Pytracing Maze - Find the exit! Score:'+str(score)+' Res: '+ str(width) +'x'+str(height)+'  FPS: '+str(int(clock.get_fps()))+renders[checker]

            minimap[int(posy)][int(posx)] = (50, 50, 255)
            drawing(rr, gg, bb, height, width, pause, endmsg, won, health, enhealth, minimap, score, fullscreen)
            minimap[int(posy)][int(posx)] = (100, 100, 0)
                
            fps = int(1000/(pg.time.get_ticks() - ticks*100000 +1e-16))
            if autores and count > 10: #auto adjust render resolution
                if fps < fps_lock - 10 and width > 100:
                        width, height, mod, rr, gg, bb, count = adjust_resol(int(width*0.8))
                elif fps > fps_lock + 15:
                        width, height, mod, rr, gg, bb, count = adjust_resol(int(width*1.1))        

            if (int(posx) == exitx and int(posy) == exity):
                endmsg, won = " You escaped safely! ", 1
                successfx.play()
                animate(width, height, mod, move, posx, posy, .5, rot, rot_v, mr, mg, mb, lx, ly, lz,
                        mplayer, exitx, exity, mapr, mapt, maps, rr, gg, bb, enx, eny, sx, sy, sx2, sy2,
                        size, checker, count,fb, fg, fr, pause, endmsg, won, health, minimap, score, .5/61, clock.get_fps())
                pause = 1
                score += 1
                maxscore = max(score, maxscore)         
            
            et = min(clock.tick()/500, 0.1)*(0.8+move)

            if shoot or sstart != None:
                if sstart == None:
                    shotfx.play()
                    if fps < fps_lock and autores:
                        width, height, mod, rr, gg, bb, count = adjust_resol(int(width*0.8))
                    sstart = pg.time.get_ticks()
                elif pg.time.get_ticks() - sstart > 500:
                    shoot, sx, sy, sstart = 0, -1, -1, None

            if enhealth == 0:
                if not respawn:
                    if shoot:
                        health = min(health+5, 10)
                    shoot2, sx2, sy2, run, respawn, sstart2 = 0, -1, -1, 1, 1, None
                    killfx.play()
                
            else:
                if respawn:
                    respawn = 0
                    respawnfx.play()
            if shoot2 or sy2 == 0 or sstart2 != None:
                if run:
                    run = 0
                    runfx.play()
                if sstart2 == None:
                    shotfx.play()
                    sstart2 = pg.time.get_ticks()
                elif pg.time.get_ticks() - sstart2 > 500:
                    shoot2, sx2, sy2, sstart2 = 0, -1, -1, None

            if health <= 0:
                won, pause, health = -1, 1, 0
                if score > 0:
                    score -= 1
                endmsg = " You died! Current score: " + str(score) + ' '
                failfx.play()
                animate(width, height, mod, move, posx, posy, .5, rot, rot_v, mr, mg, mb, lx, ly, lz,
                        mplayer, exitx, exity, mapr, mapt, maps, rr, gg, bb, enx, eny, sx, sy, sx2, sy2,
                        size, checker, count,fb, fg, fr, pause, endmsg, won, health, minimap, score, -.5/61, clock.get_fps())
                enx, eny, seenx, seeny, lock, won, enhealth  = 0, 0, 0, 0, 0, 0, 0


            posx, posy, rot, rot_v, shoot, move = movement(pg.key.get_pressed(),posx, posy, rot, rot_v, maph, et, shoot, sstart, move)
            pg.mouse.set_pos([640, 360])
            
            
        
        pg.display.update()

    pg.mixer.fadeout(1000)
    print(endmsg)
    posz, ani = 0.5, .5/61
    if health <= 0:
        posz, ani = 0.01, .99/61
    elif int(posx) == exitx and int(posy) == exity:
        posz, ani = 0.99, -.99/61
        
    animate(width, height, mod, move, posx, posy, posz, rot, rot_v, mr, mg, mb, size/2 + 1500, size/2 + 1000, 1000,
            maph, exitx, exity, mapr, mapt, maps, rr, gg, bb, enx, eny, sx, sy, sx2, sy2,
            size, checker, count,fb, fg, fr, pause, endmsg, won, health, minimap, score, ani, fps)
    
    pg.quit()

def new_map(score):
    size = np.random.randint(20+score*5,30+score*10) # size of the map
    posx, posy, posz = np.random.randint(1, size -2)+0.5, np.random.randint(1, size -2)+0.5, 0.5
    x, y = int(posx), int(posy)
    rot, rot_v = (np.pi/4, 0)
    
    mr, mg, mb = np.random.uniform(0,1, (size,size)), np.random.uniform(0,1, (size,size)), np.random.uniform(0,1, (size,size)) 
    mapr = np.random.choice([0, 0, 0, 0, 1], (size,size))
    maps = np.random.choice([0, 0, 0, 0, 1], (size,size))
    mapt = np.random.choice([0, 0, 0, 1, 2, 3], (size,size))
    maptemp = np.random.choice([0,0, 1], (size,size))
    maph = np.random.uniform(0.25, 0.99, (size,size))
    maph[np.where(maptemp == 0)] = 0
    maph[0,:], maph[size-1,:], maph[:,0], maph[:,size-1] = (1,1,1,1) # outer walls
    maps[0,:], maps[size-1,:], maps[:,0], maps[:,size-1] = (0,0,0,0) # no spheres

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

def new_game(fb, fg, fr, endmsg, score):
    width, height, mod, rr, gg, bb, count = adjust_resol(200)
    mr, mg, mb, maph, mapr, exitx, exity, mapt, maps, posx, posy, posz, size, rot, rot_v = new_map(score)
    minimap = np.zeros((size, size, 3))
    animate(width, height, mod, 0, posx, posy, .99, rot, rot_v, mr, mg, mb, size/2 + 1500, size/2 + 1000, 1000, maph, exitx, exity, mapr, mapt, maps,
             rr, gg, bb, 0, 0, -1, -1, -1, -1, size, 2, 0, fb, fg, fr, 0, endmsg, 0, 10, minimap, score, -.5/61)
    
    return (mr, mg, mb, maph, mapr, exitx, exity, mapt, maps, posx, posy, posz, size, rot, rot_v, minimap, width, height, mod, rr, gg, bb, count,
            -1, -1, 0, 0, 0, 1, 0, -1, -1, -1, None, 0.1, 10, 0, 0, 0, 0, 0, -1, -1, -1, None, 0, 1, 0)
#enx, eny, seenx, seeny, lock, run, shoot, sx, sy, sz, sstart, et, health, sdir, sdirz, sdir2, sdirz2, shoot2, sx2, sy2, sz2, sstart2, won, respawn, move

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
        x, y = x - et*np.sin(rot), y + et*np.cos(rot)
        
    elif pressed_keys[pg.K_RIGHT] or pressed_keys[ord('d')]:
        et = et/(diag+1)
        x, y = x + et*np.sin(rot), y - et*np.cos(rot)

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
    move = np.clip(move, 0, 0.4)
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
def ray_caster(posx, posy, posz, sin, cos, sinz, lx, ly, lz, maph, mapr, maps, enx, eny, sx, sy, sx2, sy2, size, sz, sz2):
    x, y, z = posx, posy, posz
    modr, cx, cy, shot, mapv = 1, 1, 1, 0, 0
    dtp = np.random.uniform(0.002,0.01)
    for k in range(2000):
        
        if (mapv == 0) or (sinz > 0 and (z > mapv or (mapv > 1 and mapv < 6 and z > 0.58))): ## LoDev DDA for optimization
            x, y, z = lodev(x, y, z, cos, sin, sinz, maph, size)
        
        x += cos; y += sin; z += sinz
        if (z > 1 or z < 0): # check ceiling and floor
            break
        mapv = maph[int(x)][int(y)]
        if (mapv == 2 or mapv == 8 or mapv == 14) and modr > 0.7:
            mapv = 0
        if mapv > 1 and z < 0.58: # check agents
            if mapv == 2 or mapv == 8 or mapv == 3 or mapv == 15:
                refx, refy, sh = posx, posy, .8
                if  mapv%2 != 0:
                    refx, refy, sh =  enx, eny, .2                               
                if z> 0.45 and (x-refx)**2 + (y-refy)**2 + (z-0.5)**2 < 0.003 +abs(z-0.47)/30 :
                    break # head
                if z < 0.45 and z > 0.28 and (x-refx)**2 + (y-refy)**2  < (z/10 - 0.02):
                    break # chest
                if z < 0.28 and (x-refx)**2 + (y-refy)**2 + (z-0.15)**2 < 0.023 :
                        break #roller
        if  mapv > 5:# and z < 0.4 and z > 0.2:
            refx, refy, refz = sx, sy, sz
            if mapv < 12:
                refx, refy, refz = sx2, sy2, sz2
            if ((x-refx)**2 + (y-refy)**2 + (z-refz)**2 < dtp):
                shot = 1
                break

        if mapv > z and mapv < 2: # check walls
            if maps[int(x)][int(y)]: # check spheres
                if ((x%1-0.5)**2 + (y%1-0.5)**2 + (z%1-0.5)**2 < 0.24):
                    x, y, z = refine(x, y, z, sin, cos, sinz)
                    if (mapr[int(x)][int(y)]): # spherical mirror
                        if (modr == 1):
                            cx, cy = int(x), int(y)
                        modr = modr*0.7
                        if (modr < 0.2):
                            break
                        if (mapv - z <= abs(sinz)): ## horizontal surface
                            sinz = -sinz
                        else:
                            nx = (x%1-0.5)/0.5; ny = (y%1-0.5)/0.5; nz =(z%1-0.5)/0.5
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
    return x, y, z, modr, shot, mapv, refx, refy, refz, cx, cy, sin, cos, sinz, sh, shot

@njit(cache=True)
def refine(x, y, z, sin, cos, sinz):
    x -= .9*cos; y -= .9*sin; z -= .9*sinz
    while ((x%1-0.5)**2 + (y%1-0.5)**2 + (z%1-0.5)**2 - 0.24 > 0):
        x += 0.1*cos; y += 0.1*sin; z += 0.1*sinz
    return x, y, z

@njit(cache=True)
def shadow_ray(x, y, z, cos, sin, sinz, modr, shot, maps, enx, eny, posx, posy, posz, size, maph, limodr, refz):
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
            if mapv > 5 or (sinz > 0 and z > refz) or (sinz < 0 and z < refz) or modr < limodr:
                break
        elif z >1 or modr < limodr:
            break
        if z < 0.58 and mapv > 1 and (mapv == 3 or mapv == 2 or mapv == 15 or mapv == 8):
            refx, refy, sh = enx, eny, .2
            if  mapv%2 == 0:
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
    return modr

@njit(cache=True)
def get_color(x, y, z, modr, shot, mapv, refx, refy, refz, cx, cy, sin, cos, sinz, sh, mapt, maps, exitx, exity,
              mr, mg, mb, fr, fg, fb, lx, ly, lz, size):
    if z > 1: # ceiling
        norm = np.sqrt(cos**2 + sin**2 + sinz**2)
        rayDirX, rayDirY, rayDirZ = cos/norm + 1e-16, sin/norm + 1e-16, sinz/norm + 1e-16    
        deltaDistZ = (lz-z)/rayDirZ
        x += deltaDistZ*rayDirX; y += deltaDistZ*rayDirY; z = lz
        dtol = np.sqrt((x-lx)**2+(y-ly)**2)

        if dtol < 50: #light source
            c1, c2, c3, shot = 1, 1, 0.5, 1
        else:
            angle = np.rad2deg(np.arctan((y-ly)/(x-lx)))/np.random.uniform(12,15)
            sh = min((0.8+ abs(angle - int(angle))/5)/(dtol/1000), 1)
            if int(angle)%2 == 1:
                c1, c2, c3 = 0.82*(1-sh), 0.86*(1-sh/4), (1-sh/10)
            else:
                c1, c2, c3 = 0.8*(1-sh), 0.9*(1-sh/4), (1-sh/10)*0.9
            
    elif z < 0: # floor
        xx, sh = int(3*x%1*100) + int(3*y%1*100)*100, 0.3 + (x+y)/(3*size)
        c1, c2, c3, z = .85*(1-sh/2)*fg[xx], sh*fg[xx], 0.85*sh*fb[xx], 0
        if int(x) == exitx and int(y) == exity: #exit
            c3 = np.random.uniform(0.5, 1)
                
    elif mapv < 2: # walls
        c1, c2, c3 = mr[int(x)][int(y)], mg[int(x)][int(y)], mb[int(x)][int(y)]
        mapvt = mapt[int(x)][int(y)]
        if mapv - z <= abs(sinz): # round coordinates and pre shade
            z = mapv
        elif not maps[int(x)][int(y)]:
            if int(x-cos) != int(x):
                x = max(int(x-cos), int(x))
                modr = modr*0.80
            else:
                y = max(int(y-sin), int(y))
                modr = modr*0.9
                
        if mapvt > 1: # textured walls
            if z == mapv:
                xx = int(3*x%1*100) + 100*int(3*y%1*100)
            elif x%1 == 0:
                xx = int(3*z%1*100) + 100*int(3*y%1*100)
            else:
                xx = int(3*z%1*100) + 100*int(3*x%1*100)
            xx = fr[xx]
            c1, c2, c3 = c1*xx, c2*xx, c3*xx
            if mapvt%2 == 1: # gradient walls
                c1, c2, c3 = c1*(2+z)/3, c2*(3-z)/3, c3*(2+z**2)/3
                    
    else: # agents
        if shot: # fireball
            sh = ((x-refx)**2 + (y-refy)**2 + (z-refz)**2)/0.012
            c1, c2, c3 = 1, 0.6*sh+0.2 , 0.2*sh+0.1 
        elif z> 0.45: # Head
            c1, c2, c3 = (1-z)*(1-sh), (1-z)*sh, z*sh 
        elif z > 0.28: # Chest
            c1, c2, c3 = (z-0.28), (z-0.28)*(1-sh), (z-0.28)*sh 
        else: # Roller
            c1, c2, c3 = refx%1*z*(1-sh), refy%1*0.2*sh, refy%1*z*sh

    return c1, c2, c3, modr, x, y, z, shot

        
@njit(cache=True)
def super_fast(width, height, mod, move, posx, posy, posz, rot, rot_v, mr, mg, mb, lx, ly, lz,
               maph, exitx, exity, mapr, mapt, maps, pr, pg, pb, enx, eny, sx, sy, sx2, sy2,
               size, checker, count, fb, fg, fr, sz=0, sz2=0):
    
    inv, inv2, garbage, idx = (count%2), -(int(count/2)%2), not(count), 0
    if checker == 0:
        garbage = 0
    for j in range(height): #vertical loop 
        rot_j = rot_v + (1+move**1.5)*np.deg2rad(24 - j/mod)
        sinzo = (0.04/mod)*np.sin(rot_j) 
        coszo = (0.04/mod)*np.sqrt(abs(np.cos(rot_j)))        
        for i in range(width): #horizontal vision loop
            if (checker == 1 or garbage) and idx%2 == 1:
                pr[idx], pg[idx], pb[idx] = pr[idx-1], pg[idx-1], pb[idx-1]
            else:
                if checker == 3: # radial
                    rad = np.sqrt((i-width/2)**2 + (j-height/2)**2)
                elif checker == 4: # square
                    rad = max(abs(i-width/2)*1, abs(j-height/2))
                
                if (checker < 2 or garbage or # standard and doubled pixels, first frame after res adjust
                    (checker == 2 and ((inv and i%2 == j%2) or (not(inv) and i%2 != j%2))) or # checkerboard
                    (checker > 2 and ((rad < height/2.9 and ((inv and i%2 == j%2) or (not(inv) and i%2 != j%2))) or # radial and square
                                      (rad > height/2.9 and rad < height/1.9 and (((i+2*inv)%3 == 0 and  (j+2*inv2)%3 == 0))) or
                                      (rad > height/1.9 and (((i+3*inv)%5 == 0 and  (j+3*inv2)%5 == 0)))))):
                    
                    rot_i = rot + (1+move**1.5)*np.deg2rad(i/mod - 30)
                    si = 1
                    if checker > 2:
                        si = 2
                        if rad > height/1.9:
                            si = 3

                    sin, cos, sinz = coszo*np.sin(rot_i), coszo*np.cos(rot_i), sinzo
                    modr, cx, cy, c1r, c2r, c3r, shot, mapv = 1, 1, 1, 1, 1, 1, 0, 0
                    
                    x, y, z, modr, shot, mapv, refx, refy, refz, cx, cy, sin, cos, sinz, sh, shot = ray_caster(posx, posy, posz, sin, cos, sinz, lx, ly, lz, maph, mapr, maps,
                                                                                                         enx, eny, sx, sy, sx2, sy2, size, sz, sz2)

                    c1, c2, c3, modr, x, y, z, shot = get_color(x, y, z, modr, shot, mapv, refx, refy, refz, cx, cy, sin, cos, sinz, sh, mapt, maps, exitx, exity,
                                                                mr, mg, mb, fr, fg, fb, lx, ly, lz, size)

                    if modr <= 0.7 and not shot: # tinted mirrors
                        c1r, c2r, c3r = mr[cx][cy], mg[cx][cy], mg[cx][cy]

                    if not shot and z < 1: # shadows
                        limodr, refx, refy, refz = 0.4, lx, ly, lz
                        dtp = np.sqrt((x-posx)**2+(y-posy)**2+(z-posz)**2)
                        if dtp > 7:
                            modr = modr/np.log((dtp-6)/4+np.e)
                        if sx != -1 or sx2 != -1: # fireball
                            refx, refy, refz, shot, c3 = sx2, sy2, sz2, 1, c3*0.9
                            if sx != -1:
                                refx, refy, refz = sx, sy, sz
                        dtol = np.sqrt((x-refx)**2+(y-refy)**2+(z-refz)**2)
                        cos, sin, sinz = .01*(refx-x)/dtol, .01*(refy-y)/dtol, .01*(refz-z)/dtol
                        modr = shadow_ray(x, y, z, cos, sin, sinz, modr, shot, maps, enx, eny, posx, posy, posz, size, maph, limodr, refz)
                            
                    c1, c2, c3 =  modr*np.sqrt(c1*c1r), modr*np.sqrt(c2*c2r), modr*np.sqrt(c3*c3r)                                                            


                    
                    if checker == 0 or garbage:
                        pr[idx], pg[idx], pb[idx] = c1, c2, c3
                        
                    elif checker > 2 and rad > height/2.9 -1 :
                        imin, imax, jmin, jmax = max(i-si, 0), min(i+si, width-1), max(j-si, 0), min(j+si, height-1)
                        for jj in range(jmin, jmax):
                            for ii in range(imin, imax):
                                idx2 = ii + jj*width
                                pr[idx2], pg[idx2], pb[idx2] = (3*c1 + pr[idx2])/4, (3*c2 + pg[idx2])/4, (3*c3 + pb[idx2])/4
                                
                    else:
                        pr[idx], pg[idx], pb[idx] = (3*c1 + pr[idx])/4, (3*c2 + pg[idx])/4, (3*c3 + pb[idx])/4                        
            idx += 1

    if checker != 0: # fill gaps and smoothing
        idx = 0
        for j in range(height): #vertical loop        
            for i in range(width): #horizontal vision loop
                if (i > 0 and i < width -1 and j > 0 and j < height -1 and ((inv and i%2 != j%2) or (not(inv) and i%2 == j%2))):
                    if abs(pr[idx-1] - pr[idx+1]) < 0.05 and abs(pg[idx-1] - pg[idx+1]) < 0.05 and abs(pb[idx-1] - pb[idx+1]) < 0.05 :
                        pr[idx], pg[idx], pb[idx]  = (pr[idx-1] + pr[idx+1])/2, (pg[idx-1] + pg[idx+1])/2, (pb[idx-1] + pb[idx+1])/2
                    elif abs(pr[idx-width] - pr[idx+width]) < 0.05 and abs(pg[idx-width] - pg[idx+width]) < 0.05 and abs(pb[idx-width] - pb[idx+width]) < 0.05 :
                        pr[idx], pg[idx], pb[idx] = (pr[idx-width] + pr[idx+width])/2, (pg[idx-width] + pg[idx+width])/2, (pb[idx-width] + pb[idx+width])/2
                    else:
                        pr[idx] = (pr[idx] + pr[idx-1] + pr[idx-width] + pr[idx+width] + pr[idx+1])/5
                        pg[idx] = (pg[idx] + pg[idx-1] + pg[idx-width] + pg[idx+width] + pg[idx+1])/5
                        pb[idx] = (pb[idx] + pb[idx-1] + pb[idx-width] + pb[idx+width] + pb[idx+1])/5
                idx += 1
                
    return pr, pg, pb

@njit(cache=True)
def agents(enx, eny, maph, posx, posy, rot, rot_v, et, shoot, sx, sy, sz, sdir,
           sdirz, shoot2, sx2, sy2, sz2, sdir2, sdirz2, mplayer,
           seenx, seeny, lock, size, enhealth, health, score):

    mplayer[int(posx)][int(posy)] = 2 # player = 2, npc = 3, npc fireball >=6, player fireball >=12
    if (maph[int(posx+.1)][int(posy+.1)] == 0 and maph[int(posx-.1)][int(posy-.1)] == 0 and
        maph[int(posx-.1)][int(posy+.1)] == 0 and maph[int(posx+.1)][int(posy-.1)] == 0):
        mplayer[int(posx+0.1)][int(posy+0.1)], mplayer[int(posx+0.1)][int(posy-0.1)] = 2, 2
        mplayer[int(posx-0.1)][int(posy+0.1)], mplayer[int(posx-0.1)][int(posy-0.1)] = 2, 2
    
    # teleport or respawn npc
    if (enhealth == 0 and np.random.uniform(0,1) > 0.995) or (enhealth > 0 and (enx-posx)**2 + (eny-posy)**2 > 300) :
        x, y = np.random.normal(posx, 5), np.random.normal(posy, 5)
        dtp = (x-posx)**2 + (y-posy)**2
        if x > 0 and x < size-1 and y > 0 and y < size-1:
            if maph[int(x)][int(y)] == 0 and dtp > 49 :
                if enhealth == 0:
                    enx, eny, seenx, seeny, lock, enhealth = x, y, x, y, 0, 10
                else:
                    enx, eny, seenx, seeny, lock = x, y, x, y, 0
    if enhealth > 0: # look for player
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
                if(int(x) == int(posx) and int(y) == int(posy)): # lock on player position
                    seenx, seeny, lock = posx, posy, 1
                    break

        if int(enx) == int(seenx) and int(eny) == int(seeny): # reached target
            if not lock:
                if shoot or np.random.uniform(0,1) > 0.7: #if the player is shooting, go towards him
                    seenx, seeny = np.random.uniform(enx, posx), np.random.uniform(eny, posy)
                else: # just keep mooving
                    seenx, seeny = np.random.normal(enx, 2), np.random.normal(eny, 2) 
            else: # go near the player if locked
                seenx, seeny = np.random.normal(posx, 2), np.random.normal(posy, 2)
            
        dtp = np.sqrt((enx-seenx)**2 + (eny-seeny)**2)    
        cos, sin = (seenx-enx)/dtp, (seeny-eny)/dtp    
        x, y = enx + et*cos, eny + et*sin # set new npc position
        if maph[int(x)][int(y)] == 0: # check if position is valid
            enx, eny = x, y
        else: # if not, try to move sideways
            if np.random.uniform(0,1) > 0.5:
                x, y = enx - et*sin, eny + et*cos
            else:
                x, y = enx + et*sin, eny - et*cos
            if maph[int(x)][int(y)] == 0: # try again
                enx, eny = x, y
            elif np.random.uniform(0,1) > 0.5: # update target
                if lock and np.random.uniform(0,1) > 0.5:
                    seenx, seeny = np.random.normal(posx, 2), np.random.normal(posy, 2)
                    if np.random.uniform(0,1) > 0.99: # release lock if stuck
                        lock = 0
                else:
                    seenx, seeny = enx+np.random.normal(0,3), eny+np.random.normal(0,3)
                
        mplayer[int(enx)][int(eny)] = 3 # mark npc position and adjacent positions 
        if (maph[int(enx+.1)][int(eny+.1)] == 0 and maph[int(enx-.1)][int(eny-.1)] == 0 and
            maph[int(enx-.1)][int(eny+.1)] == 0 and maph[int(enx+.1)][int(eny-.1)] == 0):
            mplayer[int(enx+0.1)][int(eny+0.1)], mplayer[int(enx+0.1)][int(eny-0.1)] = 3, 3
            mplayer[int(enx-0.1)][int(eny+0.1)], mplayer[int(enx-0.1)][int(eny-0.1)] = 3, 3
    
    if lock and not shoot2: # npc fireball initiate
        shoot2, sdirz2  = 1, np.sin(np.random.uniform(0,.2))
        sdir2 = np.arctan((posy-eny)/(posx-enx)) + np.random.uniform(-.1,.1)
        if abs(enx+np.cos(sdir2)-posx) > abs(enx-posx):
            sdir2 = sdir2 - np.pi
        
    if shoot2 and sy2 != 0: # npc fireball
        if sx2 == -1:
            sx2, sy2, sz2 = enx + .5*np.cos(sdir2), eny + .5*np.sin(sdir2), 0.35 + .5*sdirz2
        sx2, sy2, sz2  = sx2 + 5*et*np.cos(sdir2), sy2 + 5*et*np.sin(sdir2), sz2 + 5*et*sdirz2
        sdirz2 = sdirz2 - et/5
        if sx2 > 0 and sx2 < size-1 and sy2 > 0 and sy2 < size-1 and sz2 > 0 and sz2 < 1:
            if (maph[int(sx2+.05)][int(sy2+.05)] != 0 or maph[int(sx2-.05)][int(sy2-.05)] != 0 or
                maph[int(sx2-.05)][int(sy2+.05)] != 0 or maph[int(sx2+.05)][int(sy2-.05)] != 0):
                shoot2, sx2, sy2 = 0, -1, -1
            else:
                if (sx2 - posx)**2 + (sy2 - posy)**2 < 0.01:
                    shoot2, sx2, sy2 = 0, -1, 0
                    health -= min(1 + score/4, 5)
                else:
                    mplayer[int(sx2)][int(sy2)] += 6
        else:
            shoot2, sx2, sy2 = 0, -1, 0
            
    if shoot: # player fireball
        if sx == -1:
            sdir, sdirz = rot+np.random.uniform(-.05,.05), np.sin(min(rot_v , 0)+np.random.uniform(.1,.2))
            sx, sy, sz = posx + .5*np.cos(sdir), posy + .5*np.sin(sdir), 0.35 + .5*sdirz
        sx, sy, sz = sx + 5*et*np.cos(sdir), sy + 5*et*np.sin(sdir), sz + 5*et*sdirz
        sdirz = sdirz - et/5
        if (sx > 0 and sy < size-1 and sy > 0 and sy < size-1 and sz > 0 and sz < 1 and
            maph[int(sx+.05)][int(sy+.05)] == 0 and maph[int(sx-.05)][int(sy-.05)] == 0 and
            maph[int(sx-.05)][int(sy+.05)] == 0 and maph[int(sx+.05)][int(sy-.05)] == 0):
            if enhealth > 0 and (sx - enx)**2 + (sy - eny)**2 < 0.02:
                shoot, sx, sy = 0, -1, -1
                enhealth -= max(5 -score/4, 1)
                if enhealth <= 0:
                    enx, eny, seenx, seeny, enhealth = 0, 0, 0, 0, 0
            else:
                mplayer[int(sx)][int(sy)] += 12
        else:
            shoot, sx, sy = 0, -1, -1
            
    mplayer = maph + mplayer
    return(enx, eny, mplayer, et, shoot, sx, sy, sz, sdir, sdirz, shoot2,
           sx2, sy2, sz2, sdir2, sdirz2, seenx, seeny, lock, enhealth, health)

def adjust_resol(width):
    height = int(0.6*width)
    mod = width/64
    rr, gg, bb = np.ones(width * height)/2, np.ones(width * height)/2, np.ones(width * height)/2
    return width, height, mod, rr, gg, bb, 0

def drawing(rr, gg, bb, height, width, pause, endmsg, won, health, enhealth, minimap, score, fullscreen, nosplash=True):
    global font, font2, screen, surfbg

    surfbg.fill(pg.Color("darkgrey"))
    pg.draw.rect(surfbg, (200-int(health*20), 50+int(health*20), 50+int(health*10)),(1205,int(700-62*health),30,int(63*health)))
    pg.draw.rect(surfbg, (enhealth*25, 200-enhealth*10, 50),(1245,700-62*enhealth,30,63*enhealth))
    
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
    screen.blit(surf, (0, 0))
    
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
                screen.blit(font2.render(" Press P or C to continue ", 0, pg.Color("grey"), (80, 34, 80)),(50,490))
    else:
        size = len(minimap)
        surfmap = pg.surfarray.make_surface(np.flip(minimap).astype('uint8'))
        surfmap = pg.transform.scale(surfmap, (size*4, size*4))
        screen.blit(surfmap,(1280-size*4 - 85, 5), special_flags=pg.BLEND_ADD)
        if fullscreen:
            fps = font.render(endmsg, 0, pg.Color("coral"))
            screen.blit(fps,(100,1))
    screen.blit(font2.render(str(score), 0, pg.Color("white")),(1210, 10))
        
    pg.display.update()

def animate(width, height, mod, move, posx, posy, posz, rot, rot_v, mr, mg, mb, lx, ly, lz, #simple up and down animation
            maph, exitx, exity, mapr, mapt, maps, pr, pg, pb, enx, eny, sx, sy, sx2, sy2,
            size, checker, count, fb, fg, fr, pause, endmsg, won, health, minimap, score, ani, fps=60):
    ani = ani*60/fps
    for i in range(int(fps)):
        rr, gg, bb = super_fast(width, height, mod, move, posx, posy, posz+ani*i, rot, rot_v, mr, mg, mb, lx, ly, lz,
                                maph, exitx, exity, mapr, mapt, maps, pr, pg, pb, enx, eny, sx, sy, sx2, sy2,
                                size, checker, count, fb, fg, fr)
        count += 1
        
        drawing(rr, gg, bb, height, width, pause, endmsg, won, health, 0, minimap, score, 0)
        
def sfx():  #load sounds and textures
    try:
        ambient = pg.mixer.Sound('soundfx/HauntSilentPartner.mp3') 
        runfx = pg.mixer.Sound('soundfx/run.mp3')
        shotfx = pg.mixer.Sound('soundfx/slap.mp3')
        killfx = pg.mixer.Sound('soundfx/shutdown.mp3')
        respawnfx = pg.mixer.Sound('soundfx/respawn.mp3')
        successfx = pg.mixer.Sound('soundfx/success.mp3')
        failfx = pg.mixer.Sound('soundfx/fail.mp3')
    except:
        print("Sounds missing! Generating replacements...")
        ambient = generate_sounds(75, 10000, 300)
        runfx = generate_sounds(200, 800, 150)
        shotfx = generate_sounds(200, 200, 250)
        killfx = generate_sounds(1620, 241, 230)
        respawnfx = generate_sounds(230, 350, 80)
        successfx = generate_sounds(300, 900, 100)
        failfx = generate_sounds(700, 200, 350)
    try:        
        floor = pg.surfarray.array3d(pg.image.load('soundfx/textures.jpg'))
        fr, fg, fb = np.dsplit(floor,floor.shape[-1])
        fr, fg, fb = fr.flatten()/255, fg.flatten()/255, fb.flatten()/255
    except:
        print("Textures missing! Generating replacements...")
        fr, fg, fb = generate_textures()
        

    return ambient, runfx, shotfx, killfx, respawnfx, successfx, failfx, fr, fg, fb

def generate_sounds(freq = 60, var = 500, n = 10):
    sound1, sound2, sound3, freq0, dir2 = [], [], [], freq, 1
    for i in range(n):
        freq = freq+20*dir2
        if freq > freq0*3 or freq < freq0/3+10:
            dir2 = -1*dir2
            freq = freq+20*dir2
        var2 = np.random.randint(int(var/2),var*2)
        samples1 = synth(np.random.randint(int(var),var*3), np.random.randint(freq,2*freq))
        samples2 = synth(np.random.randint(int(var/2),var*2), np.random.randint(int(freq/2),freq))
        samples3 = synth(np.random.randint(int(var/4),int(var/2)), np.random.randint(int(freq/3),3*freq))
        sound1 = sound1 + list(samples1/3)
        sound2 = sound2 + list(samples2/3)
        sound3 = sound3 + list(samples3/3)

    lens = min(len(sound1), len(sound2), len(sound3))
    sound = np.asarray(sound1[:lens]) + np.asarray(sound2[:lens]) + np.asarray(sound3[:lens])
    sound = np.asarray([sound,sound]).T.astype(np.int16)
    sound = pg.sndarray.make_sound(sound.copy())
    return sound

def synth(frames, freq):
    def frame(i):
        return 0.2 * 32767 * np.sin(2.0 * np.pi * freq * i / 44100)
    arr = np.array([frame(x) for x in range(0, frames)]).astype(np.int16)
    return arr

def generate_textures():
    fr, fg, fb = [], [], []
    for i in range(100):
        for j in range(100):
            ref1, ref2 = .2, 0.2
            if i < 50 and j < 50 or i > 50 and j > 50:
                ref1 = 1
            if (i-50)**2 + (j-50)**2 < 2000:
                ref2 = 1
            fr.append(3.5-abs(np.sin(i/5)+np.cos(j/5))*ref2*np.random.uniform(i/100,j/100)+0.3+ref1)
            fg.append(ref1+np.random.uniform(i/100,ref2*ref1)/3+0.1)
            fb.append(ref1+np.random.uniform(j/100,ref2*ref1)/3+0.1)
    fr, fg, fb = np.asarray(fr)/max(fr), np.asarray(fg)/3, np.asarray(fb)/3
    return fr, fg, fb

if __name__ == '__main__':
    pg.init()
    pg.display.set_caption("Welcome to Pytracing maze! Stutters may occur on first run while Numba is compiling")
    font = pg.font.SysFont("Arial", 18)
    font2 = pg.font.SysFont("Impact", 48)
    screen = pg.display.set_mode((1280, 720))
    surfbg = pg.Surface((1280,720))
    main()
