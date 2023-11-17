import pygame
import random
from itertools import chain
pygame.init()

WIDTH, HEIGHT = 1000, 700
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
FPS = 60
CLICK_DELAY = 150

COLS, ROWS = 16, 14
MAX_TURNS = COLS*ROWS*2
TILE_W, TILE_H = WIDTH//(COLS+4), HEIGHT//ROWS
SCALE = 4
UI_RECT = pygame.rect.Rect(0,0,TILE_W*4,HEIGHT)
MM_RECT = pygame.rect.Rect(0,HEIGHT//2,WIDTH//SCALE - TILE_W//SCALE*4,HEIGHT//SCALE)

stat_font = pygame.font.Font("freesansbold.ttf", TILE_H//2)
stat_font2 = pygame.font.Font("freesansbold.ttf", TILE_H//4)

ocean_color = (20,50,80)
boat_color = (200,200,200)
hit_color = (200,0,0)
miss_color = (100,130,160)


class Tile:
    def __init__(self, xy, hits):
        self.xy = xy
        self.hits = hits
        self.rect = pygame.rect.Rect(xy[0],xy[1],TILE_W,TILE_H)
        self.mini_rect = pygame.rect.Rect(xy[0]//SCALE - TILE_W,HEIGHT//2 + xy[1]//SCALE,TILE_W//SCALE,TILE_H//SCALE)
        self.color = ocean_color
        self.clicked = False
        self.populated = False
        self.populated2 = False
    def check_click(self):
        mousepos = pygame.mouse.get_pos()
        left_click = pygame.mouse.get_pressed()[0]
        if not self.clicked and self.rect.collidepoint(mousepos) and left_click:
            self.clicked = True 
            if self.populated2:
                self.hits[0] += 1
                self.hits.append(self.xy)
    def draw(self):
        if not self.populated:
            self.color = ocean_color
        if self.populated:
            self.color = boat_color
        if self.clicked and self.populated2:
            self.color = hit_color
        elif self.clicked and not self.populated2:
            self.color = miss_color
        pygame.draw.rect(WIN,self.color,self.rect)
        pygame.draw.rect(WIN,(0,0,0),self.rect,1)

hits = [0]
sunk = [0]
tiles = [[] for _ in range(ROWS)]
for r in range(ROWS):
    for c in range(COLS):
        tiles[r].append(Tile((TILE_W*4 + TILE_W*c,TILE_H*r),hits))


# BUILD BOATS
NUM_OF_BOATS = 5
boats = []
def build_boats():
    boats.clear()
    boat = []
    for i in range(NUM_OF_BOATS):
        done = False
        while not done:
            #random x,y origin and direction
            x = random.randrange(4,COLS)
            y = random.randrange(0,ROWS)
            direction = random.randrange(0,4)
            #first boat is (0) + 2....then each new boat will be one longer than the last
            for j in range(i + 2):
                #up/down
                if direction % 2 == 0:
                    dx = x
                    dy = y - j if direction == 0 else y + j
                #left/right
                if direction % 2 != 0:
                    dx = x - j if direction == 1 else x + j
                    dy = y
                #if within bounds and not colliding with already existing ship's location...
                if 3 < dx < COLS and 0 < dy < ROWS and [dx, dy] not in list(chain(*boats)): #turns 2d boats list into a 1d list to itterate through
                    boat.append([dx,dy])
                    if j == i + 1:
                        boats.append(boat.copy())
                        boat.clear()
                        done = True
                else:
                    boat.clear()
                    break
    for i in range(NUM_OF_BOATS):
        for x,y in boats[i]:
            tiles[y][x].populated2 = True
    
            
mini_tiles = [[] for _ in range(ROWS)]
def selection_menu():
    clock = pygame.time.Clock()
    then = pygame.time.get_ticks()
    text = stat_font.render("SELECT BOAT",True,(255,255,255))
    selection = 0
    build_boats()
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        mousepos = pygame.mouse.get_pos()
        left_click = pygame.mouse.get_pressed()[0]
        tilex = (mousepos[0]//TILE_W - 4) % COLS
        tiley = (mousepos[1]//TILE_H) % ROWS
        if tiles[tiley][tilex].populated and left_click:
            for boat in boats:
                if [tilex,tiley] in boat:
                    selection = boats.index(boat)
        
        now = pygame.time.get_ticks()
        user_input = pygame.key.get_pressed()
        dx = 0
        dy = 0
        if (now - then) >= 100:
            if user_input[pygame.K_UP]:
                dy = -1
                then = now
            if user_input[pygame.K_DOWN]:
                dy = 1
                then = now
            if user_input[pygame.K_LEFT]:
                dx = -1
                then = now
            if user_input[pygame.K_RIGHT]:
                dx = 1
                then = now

        #UPDATE TILES
        for r in range(ROWS):
            for c in range(COLS):
                tiles[r][c].draw()
                tiles[r][c].populated = False
                tiles[r][c].populated2 = False
        for i in range(NUM_OF_BOATS):
            for x,y in boats[i]:
                tiles[y%ROWS][x%COLS].populated = True
        for xy in boats[selection]:
            xy[0] += dx
            xy[1] += dy
            pygame.draw.rect(WIN,(255,255,255),tiles[xy[1]%ROWS][xy[0]%COLS].rect,3)
    
        pygame.draw.rect(WIN,(0,0,0),UI_RECT)
        WIN.blit(text,(TILE_W//3,HEIGHT//3))
        pygame.display.update()

    for r in range(ROWS):
        for c in range(COLS):
            mini_tiles[r].append([tiles[r][c].mini_rect, (tiles[r][c].color[0]//2,tiles[r][c].color[1]//1.4,tiles[r][c].color[2]//1.6), tiles[r][c].populated])
            tiles[r][c].populated = False



def mainloop():
    clock = pygame.time.Clock()
    then = pygame.time.get_ticks()
    turn = [0]
    usedxy = [[False for _ in range(COLS)] for _ in range(ROWS)]
    center = []
    valid_neighbors = []
    enemy_hits = 0
    yaxis = False 
    xaxis = False

    selection_menu()
    player_boats = []  
    player_boats.extend(boats)
    build_boats()

    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        # PLAYER TURN
        now = pygame.time.get_ticks()
        if (now - then) >= CLICK_DELAY and pygame.mouse.get_pressed()[0]:
            mousepos = pygame.mouse.get_pos()
            tilex = (mousepos[0]//TILE_W - 4) % COLS
            tiley = (mousepos[1]//TILE_H) % ROWS
            if not tiles[tiley][tilex].clicked:
                tiles[tiley][tilex].check_click()
                turn[0] += 1
                then = now
        # COMPUTER TURN
        if turn[0] % 2 != 0:
            if not valid_neighbors:   
                if center:
                    valid_neighbors.clear()
                    valid_neighbors.extend([[x,y] for x,y in set([(center[0]+1 if not yaxis else center[0],center[1]),(center[0]-1 if not yaxis else center[0],center[1]),
                                                                  (center[0],center[1]+1 if not xaxis else center[1]),(center[0],center[1]-1 if not xaxis else center[1])]) 
                                                                  if 0 <= x < COLS and 0 <= y < ROWS and not usedxy[y][x]])
                    if not valid_neighbors:
                        yaxis = False 
                        xaxis = False
                        valid_neighbors.extend([[x,y] for x,y in set([(center[0]+1 if not yaxis else center[0],center[1]),(center[0]-1 if not yaxis else center[0],center[1]),
                                                                      (center[0],center[1]+1 if not xaxis else center[1]),(center[0],center[1]-1 if not xaxis else center[1])]) 
                                                                      if 0 <= x < COLS and 0 <= y < ROWS and not usedxy[y][x]])
                    center.clear()
                else:
                    x = random.randrange(COLS)
                    y = random.randrange(ROWS)
                    while usedxy[y][x]:
                        x = random.randrange(COLS)
                        y = random.randrange(ROWS)  
                        if turn[0] > MAX_TURNS:
                            run = False
                            break
            if valid_neighbors: #cant be else or it will skip turn...
                x,y = random.choice(valid_neighbors)
                valid_neighbors.remove([x,y])
            usedxy[y][x] = True
            if mini_tiles[y][x][2]:         #if hit
                if center:                  #calc axis
                    if center[0] - x == 0:
                        yaxis = True
                    if center[1] - y == 0:
                        xaxis = True
                else:
                    center.extend([x,y])
                color = hit_color
                enemy_hits += 1
                valid_neighbors.clear()
                valid_neighbors.extend([[x,y] for x,y in set([(x+1 if not yaxis else x,y),(x-1 if not yaxis else x,y),
                                                              (x,y+1 if not xaxis else y),(x,y-1 if not xaxis else y)]) 
                                                              if 0 <= x < COLS and 0 <= y < ROWS and not usedxy[y][x]])
                if not valid_neighbors:     #no more valid along axis....
                    yaxis = False 
                    xaxis = False
                    valid_neighbors.extend([[x,y] for x,y in set([(x+1 if not yaxis else x,y),(x-1 if not yaxis else x,y),
                                                                  (x,y+1 if not xaxis else y),(x,y-1 if not xaxis else y)]) 
                                                                  if 0 <= x < COLS and 0 <= y < ROWS and not usedxy[y][x]])
                # COMPUTER SUNK LOGIC
                for boat in player_boats:  
                    if [x,y] in boat:
                        boat.remove([x,y])
                        if not boat:
                            yaxis = False 
                            xaxis = False
                            player_boats.remove(boat)
                            valid_neighbors.clear()
                            center.clear()
                        break
            else:
                color = miss_color
            mini_tiles[y][x][1] = (color[0]//2,color[1]//1.4,color[2]//1.6)
            turn[0] += 1
        # PLAYER SUNK LOGIC
        for xy in hits[1:]:
            for boat in boats:
                if [xy[0]//TILE_W-4,xy[1]//TILE_H] in boat:
                    boat.remove([xy[0]//TILE_W-4,xy[1]//TILE_H])
                    hits.remove(xy)
                    if not boat:
                        boats.remove(boat)
                    break
        # MINI MAP
        pygame.draw.rect(WIN,(0,0,0),UI_RECT)
        for r in range(ROWS):
            for c in range(COLS):
                tiles[r][c].draw()
                pygame.draw.rect(WIN,mini_tiles[r][c][1],mini_tiles[r][c][0])
                pygame.draw.rect(WIN,(0,0,0),mini_tiles[r][c][0],1)
        pygame.draw.rect(WIN,(200,200,200),MM_RECT,2)
        WIN.blit(stat_font2.render("SCORE",True,(0,255,0)),(TILE_W//2,TILE_H//4))
        WIN.blit(stat_font.render("HITS: " + str(hits[0]),True,(255,255,255)),(TILE_W//2,TILE_H//2))
        WIN.blit(stat_font.render("SUNK: " + str(NUM_OF_BOATS-len(boats)),True,(255,255,255)),(TILE_W//2,TILE_H))
        # ENEMY
        WIN.blit(stat_font2.render("ENEMY",True,(255,0,0)),(TILE_W//2,HEIGHT//2.74))
        WIN.blit(stat_font.render("HITS: " + str(enemy_hits),True,(255,255,255)),(TILE_W//2,HEIGHT//2.6))
        WIN.blit(stat_font2.render("ENEMY",True,(255,0,0)),(TILE_W//2,HEIGHT//2.3))
        WIN.blit(stat_font.render("SUNK: " + str(NUM_OF_BOATS-len(player_boats)),True,(255,255,255)),(TILE_W//2,HEIGHT//2.2))

        pygame.display.update()
    pygame.quit()


if __name__ == "__main__":
    mainloop()
        