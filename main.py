#Theme: It's not a bug, It's a feature
#Credits: Me, pymunk docs, pygame docs
import pymunk
import pygame
import numpy as np

global space, player
pygame.init()
screen_size = (500,600)
screen = pygame.display.set_mode(screen_size)
clock = pygame.time.Clock()

space = pymunk.Space()
space.gravity = 0,0
player = None

boxes = []
balls = []

def munk2pygame(x,y):
    return x+screen_size[0]/2,-y+screen_size[1]/2

def list_division(list1,other, isnum=False):
    if isnum:
        new = []
        for i in range(len(list1)):
            new.append(float(list1[i]/other))
        return new
    elif len(list1) == len(other):
        new = []
        for i in range(len(list1)):
            new.append(list1[i]/other[i])
        return new
    else:
        raise ValueError("Tuples not the same length")

def create_box(x,y,w,h,mass=10,friction=0.01,class_type=pymunk.Body.DYNAMIC):
    body = pymunk.Body(body_type=class_type)
    body.position = x,y
    shape = pymunk.Poly.create_box(body, (w,h), 0)
    shape.mass = mass
    shape.friction = friction
    space.add(body,shape)
    boxes.append(shape)
    return shape

def create_ball(x,y,r,mass=10,friction=0.01,class_type=pymunk.Body.DYNAMIC):
    body = pymunk.Body(body_type=class_type)
    body.position = x,y
    shape = pymunk.Circle(body, r)
    shape.mass = mass
    shape.friction = friction
    space.add(body,shape)    
    balls.append(shape)
    return shape

def open_level(n):
    global space, player
    space = pymunk.Space()
    space.gravity = 0,0
    x=-1
    y=0
    for line in open(f"level{n}.level","r").readlines():
        if x == -1:
            x=0
            p_pos = line.strip("\n").split(",")
            print(p_pos)
            player = create_ball(float(p_pos[0])*100,float(p_pos[1])*100,20,1099999,0.1)
            print(player.body.position)
            continue
        for char in line:
            match char:
                case "#":
                    create_box(x*100,y*100,100,100,1,1,pymunk.Body.STATIC)
                case "!":
                    create_box(x*100,y*100,100,100,1,1)
                case "*":
                    create_ball(x*100,y*100,50,1,0,pymunk.Body.STATIC)
            x+=1
            
        x=0
        y+=1

open_level(1)

dt = 0.016
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    mouse_x,mouse_y =pygame.mouse.get_pos()
    theta = np.arctan2(mouse_x-screen_size[0]/2,mouse_y-screen_size[1]/2)
    player.body.rotation = theta

    player_pos = player.body.position
    player_vel = player.body.velocity
    keys = pygame.key.get_pressed()
    vec_wanted = [0,0]
    vel_add = float(0.2 - np.sqrt(player_vel[0]**2+player_vel[1]**2))/5
    if keys[pygame.K_w]:
        vec_wanted[1] -= 1    
    if keys[pygame.K_a]:
        vec_wanted[0] += 1
    if keys[pygame.K_s]:
        vec_wanted[1] += 1  
    if keys[pygame.K_d]:
        vec_wanted[0] -= 1
    vec_wanted = list_division(vec_wanted, np.sqrt(vec_wanted[0]**2+vec_wanted[1]**2)+1*(10**-10) , True) # normalize
    player.body.velocity += (float(vec_wanted[0] * vel_add), float(vec_wanted[1] * vel_add))
    screen.fill((0,0,0))
    space.step(dt)
    for shape in boxes:
        # Custom Physics
        friction = shape.friction
        shape.body.velocity *= (1-friction)
        shape.body.angular_velocity *= (1-friction)

        # Draw
        x,y = shape.body.position
        verts = shape.get_vertices()
        p=[]
        for vec in verts:
            vx,vy = vec.rotated(shape.body.angle)
            vx += player_pos[0]-x
            vy += player_pos[1]-y
            p.append(munk2pygame(vx,vy))
        pygame.draw.polygon(screen,(200,200,100),p)
    for shape in balls:
        # Custom Physics
        friction = shape.friction
        shape.body.velocity *= (1-friction)
        shape.body.angular_velocity *= (1-friction)

        # Draw'
        x,y = shape.body.position
        sx = player_pos[0]-x
        sy = player_pos[1]-y
        pygame.draw.circle(screen,(100,200,200),munk2pygame(sx,sy),shape.radius)
    pygame.display.flip()
    dt = clock.tick(60)
