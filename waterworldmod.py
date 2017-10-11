import pygame
# import base
import sys
import math
from .base.pygamewrapper import PyGameWrapper

# import base

from utils.vec2d import vec2d
from utils import percent_round_int
from pygame.constants import K_w, K_a, K_s, K_d
from pygame.constants import K_UP, K_LEFT, K_DOWN, K_RIGHT
from primitives import Player, Creep

class WaterWorldMod(PyGameWrapper):
    """
    Based Karpthy's WaterWorld in `REINFORCEjs`_.
    
    .. _REINFORCEjs: https://github.com/karpathy/reinforcejs 

    Parameters
    ----------
    width : int
        Screen width.

    height : int
        Screen height, recommended to be same dimension as width.

    num_creeps : int (default: 3)
        The number of creeps on the screen at once.
    """
    def __init__(self, width=48, height=48, num_creeps=3):

        self.actions = {
            "up": K_w,
            "left": K_a,
            "right": K_d,
            "down": K_s,
            "up1": K_UP,
            "left1":K_LEFT,
            "right1":K_RIGHT,
            "down1":K_DOWN
        }
 
        PyGameWrapper.__init__(self, width, height, actions=self.actions)

        self.BG_COLOR = (255, 255, 255)
        self.N_CREEPS = num_creeps
        self.CREEP_TYPES = [ "GOOD", "BAD" ]
        self.CREEP_COLORS = [ (40, 140, 40), (150, 95, 95) ]
        radius = percent_round_int(width, 0.047)
        self.CREEP_RADII = [ radius, radius ]
        self.CREEP_REWARD = [ self.rewards["positive"], self.rewards["negative"] ]
        self.CREEP_SPEED = 0.25*width 
        self.AGENT_COLOR = (60, 60, 140)
        self.AGENT_SPEED = 0.25*width 
        self.AGENT_RADIUS = radius 
        self.AGENT_INIT_POS = (self.width/2, self.height/2)
        # self.AGENT_INIT_POS_1 = (self.width/2+self.AGENT_RADIUS, self.height/2+self.AGENT_RADIUS)
        self.AGENT_INIT_POS_1 = (self.width/2, self.height/2)
        self.AGENT_SPEED_1 = 0.25*width 
        
        
        self.creep_counts = {
            "GOOD": 0,
            "BAD": 0
        }
        self.creep1_counts = {
            "GOOD": 0,
            "BAD": 0
        }

        self.dx = 0
        self.dy = 0
        self.dx1 = 0
        self.dy1 = 0
        self.player = None
        self.creeps = None
        self.player1 = None


    def _handle_player_events(self):
        self.dx = 0
        self.dy = 0
        self.dx1 = 0
        self.dy1 = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                key = event.key
                
                if key == self.actions["left"]:
                    self.dx -= self.AGENT_SPEED
                    # print "a", self.dx
                    # print "a ", self.AGENT_SPEED
                elif key == self.actions["left1"]:
                    self.dx1 -= self.AGENT_SPEED_1
                    # print "a1", self.AGENT_SPEED
                    # print "a1", self.dx1

                elif key == self.actions["right"]:
                    self.dx += self.AGENT_SPEED
                    # print "a", self.dx
                    # print "a ", self.AGENT_SPEED                    
                elif key == self.actions["right1"]:
                    self.dx1 += self.AGENT_SPEED_1
                    # print "a1", self.dx
                    # print "a1 ", self.AGENT_SPEED                    

                elif key == self.actions["up"]:
                    self.dy -= self.AGENT_SPEED
                    # print "a", self.dy
                    # print "a ", self.AGENT_SPEED                    
                elif key == self.actions["up1"]:
                    self.dy1 -= self.AGENT_SPEED_1
                    # print "a1", self.dy1
                    # print "a1 ", self.AGENT_SPEED                    

                elif key == self.actions["down"]:
                    self.dy += self.AGENT_SPEED
                    # print "a", self.dy
                    # print "a ", self.AGENT_SPEED                    
                elif key == self.actions["down1"]:
                    self.dy1 += self.AGENT_SPEED_1
                    # print "a1", self.dy1
                    # print "a1 ", self.AGENT_SPEED                    


    def _add_creep(self):
        creep_type = self.rng.choice([0, 1]) 

        creep = None
        pos = ( 0,0 )
        dist = 0.0

        while dist < 1.5:
            radius = self.CREEP_RADII[creep_type]*1.5
            pos = self.rng.uniform(radius, self.height-radius, size=2) 
            dist = math.sqrt( (self.player.pos.x - pos[0])**2 + (self.player.pos.y - pos[1])**2 )
  
        creep = Creep(
            self.CREEP_COLORS[creep_type], 
            self.CREEP_RADII[creep_type], 
            pos,
            self.rng.choice([-1,1], 2), 
            self.rng.rand()*self.CREEP_SPEED,
            self.CREEP_REWARD[creep_type],
            self.CREEP_TYPES[creep_type], 
            self.width, 
            self.height,
            self.rng.rand()
        )

        self.creeps.add(creep)

        self.creep_counts[ self.CREEP_TYPES[creep_type] ] += 1

    def getGameState(self):
        """

        Returns
        -------

        dict
            * player x position.
            * player y position.
            * player x velocity.
            * player y velocity.
            * player distance to each creep


        """

        state = {
            "player_x": self.player.pos.x,
            "player_y": self.player.pos.y,
            "player_velocity_x": self.player.vel.x,
            "player_velocity_y": self.player.vel.y,
            "creep_dist": {
                "GOOD": [],
                "BAD": []
                },
            
            "player1_x": self.player1.pos.x,
            "player1_y": self.player1.pos.y,
            "player1_velocity_x": self.player1.vel.x,
            "player1_velocity_y": self.player1.vel.y,
            "creep1_dist": {
                "GOOD": [],
                "BAD": []
            }

        }

        for c in self.creeps:
            dist = math.sqrt( (self.player.pos.x - c.pos.x)**2 + (self.player.pos.y - c.pos.y)**2 )
            state["creep_dist"][c.TYPE].append(dist)
            dist1 = math.sqrt( (self.player1.pos.x - c.pos.x)**2 + (self.player1.pos.y - c.pos.y)**2 )
            state["creep1_dist"][c.TYPE].append(dist)


        return state

    def getScore(self):
        return self.score

    def game_over(self):
        """
            Return bool if the game has 'finished'
        """
        return ( self.creep_counts['GOOD'] == 0 )
    
    def init(self):
        """
            Starts/Resets the game to its inital state
        """
        self.creep_counts = { "GOOD":0, "BAD":0 }

        if self.player is None: 
            self.player = Player(
                    self.AGENT_RADIUS, self.AGENT_COLOR, 
                    self.AGENT_SPEED, self.AGENT_INIT_POS, 
                    self.width, self.height
            ) 
            self.player1 = Player(
                    self.AGENT_RADIUS, self.AGENT_COLOR, 
                    self.AGENT_SPEED_1, self.AGENT_INIT_POS_1, 
                    self.width, self.height
            )

        else:
            self.player.pos = vec2d(self.AGENT_INIT_POS)
            self.player.vel = vec2d((0.0,0.0))

            self.player1.pos = vec2d(self.AGENT_INIT_POS_1)
            self.player1.vel = vec2d((0.0,0.0))

        if self.creeps is None: 
            self.creeps = pygame.sprite.Group()
        else:
            self.creeps.empty()

        for i in range(self.N_CREEPS):
            self._add_creep()

        self.score = 0
        self.ticks = 0
        self.lives = -1

    def step(self, dt):
        """
            Perform one step of game emulation.
        """
        dt /= 1000.0
        self.screen.fill(self.BG_COLOR)

        self.score += self.rewards["tick"]

        self._handle_player_events()
        self.player.update(self.dx, self.dy, dt)
        self.player1.update(self.dx1, self.dy1, dt)
        
        hits = pygame.sprite.spritecollide(self.player, self.creeps, True) + pygame.sprite.spritecollide(self.player1, self.creeps, True)

        for creep in hits:
            self.creep_counts[creep.TYPE] -= 1
            self.score += creep.reward
            self._add_creep()

        if self.creep_counts["GOOD"] == 0:
            self.score += self.rewards["win"] 

        self.creeps.update(dt)
        
        self.player.draw(self.screen)
        self.player1.draw(self.screen)

        self.creeps.draw(self.screen)

if __name__ == "__main__":
        import numpy as np

        pygame.init()
        game = WaterWorldMod(width=256, height=256, num_creeps=10)
        game.screen = pygame.display.set_mode( game.getScreenDims(), 0, 32)
        game.clock = pygame.time.Clock()
        game.rng = np.random.RandomState(24)
        game.init()

        while True:
            dt = game.clock.tick_busy_loop(30)
            game.step(dt)
            pygame.display.update()
