from multiprocessing.dummy import Pool as ThreadPool
import threading
import time
import pygame, sys
from docutils.nodes import label
from pygame.locals import *
import numpy as np
from time import sleep
from random import randint

class Map(object):
    def __init__(self):
       #self.blocks = np.arange(1000000).reshape(1000,1000)
        self.height = 100
        self.width = 160
        self.tile_size = 40
        self.build_list = []
        self.visited = np.empty( (self.width,self.height), dtype=np.int32)
        #self.blocks = np.empty([self.width,self.height], dtype=np.int32)
        self.blocks = np.random.random_integers(0, 7, (self.width,self.height))
        self.tiles = np.empty( (self.width,self.height), dtype=object)
        self.wood = np.empty([self.width,self.height], dtype=np.int32)
        self.orem = np.empty([self.width,self.height], dtype=np.int32)
        self.waterm = np.empty([self.width, self.height], dtype=np.int32)
        self.fish = np.empty([self.width,self.height], dtype=np.int32)
        #self.blocks = np.random.random([1000,1000], dtype=np.int64)
        self.dirt = pygame.image.load("files/dirt.png")
        self.hide = pygame.image.load("files/hide.png")
        self.ore = pygame.image.load("files/ore.png")
        self.tree1 = pygame.image.load("files/tree1.png")
        self.tree2 = pygame.image.load("files/tree2.png")
        self.tree3 = pygame.image.load("files/tree3.png")
        self.tree4 = pygame.image.load("files/tree4.png")
        self.tree5 = pygame.image.load("files/tree5.png")
        self.water = pygame.image.load("files/water.png")
        self.test = pygame.image.load("files/person.bmp")
        #self.mini = pygame.image.load("files/mini.bmp")
        #print(pygame.image.tostring(self.mini, 'RGB'))
        self.tile_list = [self.dirt,self.ore,self.tree1,self.tree2,self.tree3,self.tree4,self.tree5,self.water]
        #self.set_tiles()
        self.spread = 0
        self.build_map('wood')
        self.build_map('ore')
        self.build_map('water')
        self.mini = b''
        self.build_mini()
        self.minimap = pygame.image.fromstring(self.mini,(self.width,self.height), 'RGBA')
        self.mini_rect = self.minimap.get_rect()
        #print(self.blocks)

    def set_tiles(self):
        for x in range(self.width):
             for y in range(self.height):
                 self.tiles[x,y] = self.tile_list[self.blocks[x,y]]

    def build_map(self, resource):
        if resource == 'wood':
            seed_min = 50
            seed_max = 70
            rand_min = 0
            rand_max = 1.24
            resource_map = self.wood
        if resource == 'ore':
            seed_min = 2
            seed_max = 4
            rand_min = 0
            rand_max = 1.2
            resource_map = self.orem
        if resource == 'water':
            seed_min = 2
            seed_max = 4
            rand_min = 0
            rand_max = 1.2
            resource_map = self.waterm
        visited = np.empty((self.width, self.height), dtype=np.int32)
        visited.fill(0)
        seed = randint(seed_min, seed_max)
        print('wood')
        print(seed)
        for i in range(1, seed):
            x = randint(0, self.width-1)
            y = randint(0, self.height-1)
            #self.wood[x,y] = 250
            resource_map[x,y] = 250
            visited[x,y] = 1
            self.build_list.append([x,y,250])

        while self.build_list:
            prev = self.build_list.pop()
            x = prev[0]
            y = prev[1]
            for xn in range(x-1, x+2):
                for yn in range(y-1, y+2):
                    if xn > 0 and xn < self.width and yn > 0 and yn < self.height:
                        if visited[xn,yn] != 1:
                            visited[xn, yn] = 1
                            resource_map[xn, yn] = randint(rand_min, int(prev[2] * rand_max))
                            if resource_map[xn,yn] > 250:
                                resource_map[xn,yn] = 250
                            if resource_map[xn,yn] > 50:
                                self.build_list.append([xn, yn, resource_map[xn,yn]])
                                #print(self.wood[xn,yn])

            #self.spread = 0
        self.tile_fill()


    def tile_fill(self):
        for x in range(0, self.width):
            for y in range(0, self.height):
                value = self.wood[x,y]
                if value == 0:
                    t = 0
                if value > 0 and value <=50:
                    t = 2
                if value > 50 and value <= 100:
                    t = 3
                if value > 100 and value <= 150:
                    t = 4
                if value > 150 and value <= 200:
                    t = 5
                if value > 200 and value <= 250:
                    t = 6
                self.tiles[x, y] = self.tile_list[t]

        for x in range(0, self.width):
            for y in range(0, self.height):
                value = self.orem[x, y]
                if value > 0:
                    self.tiles[x, y] = self.tile_list[1]

        for x in range(0, self.width):
            for y in range(0, self.height):
                value = self.waterm[x, y]
                if value > 0:
                    self.tiles[x, y] = self.tile_list[7]
        print(self.tiles)

    def build_mini(self):
        mdirt = b'\xcc\x66\x00\x66'
        mtree = b'\x00\x99\x00\x66'
        more = b'\x99\x99\x66\x99'
        mwater = b'\x00\x66\xff\x99'
        mini = b''
        for y in range(0, self.height):
            for x in range(0, self.width):
                if self.orem[x, y] > 0:
                    self.mini = self.mini + more
                elif self.waterm[x, y] > 0:
                    self.mini = self.mini + mwater
                elif self.wood[x,y] > 0:
                    self.mini = self.mini + mtree
                else:
                    self.mini = self.mini + mdirt
                print(len(self.mini))


class Person(object):
    def __init__(self, map, image, x, y):
        self.image = image
        self.image_rect = image.get_rect()
        self.image_rect.x = x
        self.image_rect.y = y
        self.map = map
        self.x = x
        self.y = y
        self.job = Explorer(self)
        self.dest = [x,y]
        self.dest[0] = x
        self.dest[1] = y
        self.name = "John Smith"
        self.birthday = 'May 2nd'


class Job(object):
    
    def __init__(self, person):
        self.person = person
        self.task = []

    #def do_job(self):
    #    pass

    def do_task(self):
        pass
    
    def walk(self, x,y):
        #print(x)
        #print(self.person.image_rect.x)
        try:
            #print('x1')
            if x > self.person.x:
                self.person.x = self.person.x + 10
            #print('x2')
            if x < self.person.x:
                self.person.x = self.person.x - 10
            #print('x3')
            if y > self.person.y:
                self.person.y = self.person.y + 10
            #print('x4')
            if y < self.person.y:
                self.person.y = self.person.y - 10
        except:
            print('walkbad')
            print(x)
            print(y)
        #print(self.person.image_rect.x)

    def scan(self, array):
        try:
            for x in range(int((person.x - 3) / 40), int((person.x + 4) / 40)):
                for y in range(int((person.y - 3) / 40),int((person.x + 4) / 40)):
                    if array[x,y] == 1000:
                       print('found')

        except:
            print(str(x) + ' ' + str(y))
            print(sys.exc_info()[0])
            print("error")


class Explorer(Job):
    
    def __init__(self, person):
        self.name = 'Explorer'
        self.person = person

    def do_job(self):
        #print('job')
        super(Explorer,self).walk(randint(0,400) * 10,randint(0,400) * 10)

    def scan(self):
        super(Explorer,self).scan(person.map.wood)


def do_scan(p):
    while True:
        sleep(.5)
        for person in p:
            
            person.job.scan()
            try:
                person.job.do_job()
            except:
                #print( sys.exc_info()[0])
                print('bad')
            #print('loop')



#############
window_x = 1200
window_y = 675
map = Map()
trans_x = -map.width / 2 * map.tile_size
trans_y = -map.height / 2 * map.tile_size
scale = 1.0




character = pygame.image.load("files/person.bmp")



#pool = ThreadPool(4) 
threads = []

people = []



rect = map.dirt.get_rect()
rect_reset = map.dirt.get_rect()

for z in range(100):
    person = Person(map, character,randint(0,map.width * map.tile_size),randint(0,map.height * map.tile_size))
    people.append(person)
    #print('person')

for element in map.blocks.flat:
    if element == 10000:
        print('found')

pygame.init()
pygame.mixer.quit()

#blocks = []
#for i in range(10000000):
 #   blocks.append(Block())
    #print(i)

# set up the window
DISPLAYSURF = pygame.display.set_mode((window_x, window_y), 0, 32)
pygame.display.set_caption('Drawing')

# set up the colors
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)

# draw on the surface object
DISPLAYSURF.fill(WHITE)
#pygame.draw.polygon(DISPLAYSURF, GREEN, ((146, 0), (291, 106), (236, 277), (56, 277), (0, 106)))
#pygame.draw.line(DISPLAYSURF, BLUE, (60, 60), (120, 60), 4)
#pygame.draw.circle(DISPLAYSURF, BLUE, (300, 50), 20, 0)

#pixObj = pygame.PixelArray(DISPLAYSURF)
#pixObj[380][280] = BLACK
#pixObj[382][282] = BLACK
#pixObj[384][284] = BLACK
#pixObj[386][286] = BLACK
#pixObj[388][288] = BLACK
#del pixObj

i = 0
n = 0

clock = pygame.time.Clock()
# run the game loop

t = threading.Thread(target=do_scan, args=(people,),daemon=True)
t.start()

while True:
    clock.tick(30)

#    for z in people:
#        z.scan()
#    pool.map(do_scan,people)
#    thread.start_new_thread( do_scan, (people, ) )
    rect = rect_reset.move([trans_x,trans_y])

    moverx = [map.tile_size,0]
    movery = [0,map.tile_size]
    for i in range(int(trans_y / map.tile_size), map.height * map.tile_size, map.tile_size):
        if i + trans_y > window_y:
            #print('break2')
            break
        for x in range(int(trans_x / map.tile_size),map.width * map.tile_size,map.tile_size):
            if x + trans_x > window_x:
                #print('break1')
                break
            DISPLAYSURF.blit(map.tiles[int(x / map.tile_size), int(i / map.tile_size)], rect)
            rect.move_ip(moverx)
        
        rect.x = trans_x
        rect = rect.move(movery)
    
    rect.move_ip(movery)
    for persons in people:
        persons.image_rect.x = persons.x + trans_x
        persons.image_rect.y = persons.y + trans_y
        DISPLAYSURF.blit(character, persons.image_rect)

    #DISPLAYSURF.blit(map.minimap,map.mini_rect)
    #pixObj = pygame.PixelArray(DISPLAYSURF)
    #mdirt = b'/xcc/x66/x00'
    #mtree = b'/x00/x99/x00'
    #more = b'/x99/x99/x66'
    #mwater = b'/x00/x66/xff'

    #for y in range(0, map.height):
    #    for x in range(0, map.width):
    #        if map.wood[x,y] > 0:
    #            pixObj[x,y] = 0x009900
    #        else:
    #            pixObj[x,y] = 0xCC6600
    #del pixObj

    DISPLAYSURF.blit(map.minimap, map.mini_rect)
    pygame.draw.rect(DISPLAYSURF,(255,0,0),(-trans_x / map.tile_size, -trans_y / map.tile_size,window_x / map.tile_size,window_y / map.tile_size),1)
    pygame.display.flip()
    #print('flip')
    
    for event in pygame.event.get():
        print(event)
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            tile_x = int((-trans_x + event.pos[0]) / 40)
            tile_y = int((-trans_y + event.pos[1]) / 40)
            print(str(tile_x) + " " + str(tile_y))
            print(map.wood[tile_x,tile_y])

        if event.type == pygame.MOUSEMOTION:
            if event.buttons[0] == 1:
                trans_x = trans_x + event.rel[0]
                if trans_x > 0:
                    trans_x = 0
                if trans_x < (-map.width * map.tile_size) + window_x:
                    trans_x = (-map.width * map.tile_size) + window_x
                print(trans_x)
                trans_y = trans_y + event.rel[1]
                if trans_y > 0:
                    trans_y = 0
                if trans_y < (-map.height * map.tile_size) + window_y:
                    trans_y = (-map.height * map.tile_size) + window_y
    pygame.display.update()

