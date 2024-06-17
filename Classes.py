import os
import sys
import random
from collections import deque
import pygame as pg
from Settings import X_FIELDS, Y_FIELDS, WIDTH, HEIGHT, GAME_BOARD_POSITIONS,\
                     GRAPHICS_PATH, SOUNDS_PATH, HIGHSCORE_PATH, FALLBACK_HIGHSCORE_PATH, \
                    HIGHSCORE_PATH_EXPERT, FALLBACK_HIGHSCORE_PATH_EXPERT


class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()
        self.clock.tick(60)
        self.options = Options(self)
        self.start_screen = StartScreen(self)
        self.snake = Snake(self)
        self.ghost = Ghost(self)
        self.start_screen.mainloop()
        self.apple = Apple(self)
        self.background = Background(self)
        self.highscore = Highscore(self)
        self.menu = GameMenu(self)
        self.in_progress = False
        self.SNAKE_UPDATE = pg.USEREVENT+0
        self.GHOST_TIMER = pg.USEREVENT+1
        self.GHOST_UPDATE = pg.USEREVENT+2
        self.GHOST_MOVES = False
        self.direction_update_allowed = True
        self.run()

    

    
    
    def new_game(self) -> True:
        self.snake.initialize()
        self.ghost.initialize()
        self.apple.generate(self.snake)
        
        active_menu = 1
        
        snake_image = pg.image.load(f"{GRAPHICS_PATH}\\menu\\menu_snake.png").convert_alpha()
        bg_color = pg.Color('chartreuse3')
        font_color = pg.Color('brown2')
        outline_color = pg.Color('white')
        surface = pg.Surface((WIDTH,HEIGHT))
        headline = pg.font.SysFont('chiller', 150, bold = True).render('Optionen', True, pg.Color('gray20'))
        headline_outline = pg.font.SysFont('chiller', 150, bold = True).render('Optionen', True, outline_color)
        info = pg.font.SysFont('Arial', 20, bold = True).render('Auswahl mit Pfeiltasten - Bestätigen mit Enter oder Leertaste. Zurück mit ESC.', True, font_color)
        info_outline = pg.font.SysFont('Arial', 20, bold = True).render('Auswahl mit Pfeiltasten - Bestätigen mit Enter oder Leertaste. Zurück mit ESC.', True, outline_color)
        
        normal_label = pg.font.SysFont('chiller', 90, bold = True).render('Normales Spiel', True, font_color)
        normal_label_outline = pg.font.SysFont('chiller', 90, bold = True).render('Normales Spiel', True, outline_color)
        normal_info_label = pg.font.SysFont('Arial', 20, bold = True).render('Der Klassiker.\nEine Schlange, viel futtern und dabei wachsen,\nnicht in die Wände oder dich selbst knallen', True, font_color)
        normal_info_label_outline = pg.font.SysFont('Arial', 20, bold = True).render('Der Klassiker.\nEine Schlange, viel futtern und dabei wachsen,\nnicht in die Wände oder dich selbst knallen', True, outline_color)
        expert_label = pg.font.SysFont('chiller', 90, bold = True).render('Expertenmodus', True, font_color)
        expert_label_outline = pg.font.SysFont('chiller', 90, bold = True).render('Expertenmodus', True, outline_color)
        expert_info_label = pg.font.SysFont('Arial', 20, bold = True).render('Wie der Klassiker,\naber zusätzlich wirst du vom Geist der Vergangenheit eingeholt.\nAuch in den solltest du besser nicht knallen.', True, font_color)
        expert_info_label_outline = pg.font.SysFont('Arial', 20, bold = True).render('Wie der Klassiker,\naber zusätzlich wirst du vom Geist der Vergangenheit eingeholt.\nAuch in den solltest du besser nicht knallen.', True, outline_color)

        
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN or event.key == pg.K_SPACE:
                        if active_menu == 1:
                            self.EXPERT_MODE = False
                            running = False
                        elif active_menu == 2:
                            self.EXPERT_MODE = True
                            running = False
    	                        
                    elif event.key == pg.K_DOWN:
                        if active_menu < 2:
                            active_menu += 1
                    elif event.key == pg.K_UP:
                        if active_menu > 1:
                            active_menu -= 1
            surface.fill(bg_color)
            surface.blit(snake_image, (0,HEIGHT - snake_image.get_height()))
        
            self.outline(surface, headline_outline, (WIDTH - headline_outline.get_width())//2, 0)
            surface.blit(headline, ((WIDTH - headline.get_width())//2, 0))
            self.outline(surface, info_outline, (WIDTH - info.get_width())//2, 170, 2)
            surface.blit(info, ((WIDTH - info.get_width())//2, 170))

            if active_menu == 1:
                game_info_label = normal_info_label
                game_info_label_outline = normal_info_label_outline
            elif active_menu == 2:
                game_info_label = expert_info_label
                game_info_label_outline = expert_info_label_outline

            self.outline(surface, game_info_label_outline, (WIDTH - game_info_label_outline.get_width())//2,220, 2)
            surface.blit(game_info_label, ((WIDTH - game_info_label.get_width())//2,220))
            

            rect = normal_label.get_rect(right = 1000).x
            self.outline(surface, normal_label_outline, rect, 350)
            normal_placed = surface.blit(normal_label, (rect, 350))

            rect = expert_label.get_rect(right = 1000).x
            self.outline(surface, expert_label_outline, rect, 450)
            expert_placed = surface.blit(expert_label, (rect, 450))
            
            selected_menu = ['_', normal_placed, expert_placed][active_menu]
            x, y, width, height = selected_menu
            pg.draw.rect(surface, outline_color, (x-5, y, width+10, height), 3)

            self.screen.blit(surface, (0,0))
            pg.display.flip()

        
        
        pg.time.set_timer(self.SNAKE_UPDATE, 150) # creates a timer with 150 ms for updatimng the snake
        pg.time.set_timer(self.GHOST_TIMER, 5_000) # delay for the Ghost
        pg.time.set_timer(self.GHOST_UPDATE, 150) # timer for upadating the ghost
        self.ghost.wait = 0
        self.GHOST_MOVES = False
        self.direction_update_allowed = True
        return True


    def outline(self, screen:pg.Surface, label, x, y, outline_distance = 3):
        screen.blit(label, (x-outline_distance, y-outline_distance))
        screen.blit(label, (x+outline_distance, y-outline_distance))
        screen.blit(label, (x-outline_distance, y+outline_distance))
        screen.blit(label, (x+outline_distance, y+outline_distance))


    def run(self):
        
        running = True
        while running:
            if self.menu.is_active:
                self.snake.status = 'paused'
                action = self.menu.show()
                if action == 'reset':
                    self.menu.is_active = False
                    # self.in_progress = self.new_game(self.snake, self.ghost, self.apple, self.highscore, self.SNAKE_UPDATE, self.GHOST_TIMER)
                    self.in_progress = self.new_game()
                    
                    
            self.background.draw()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.KEYDOWN: 
                    if event.key == pg.K_LEFT and self.snake.direction != 'right' and self.direction_update_allowed:
                        self.snake.direction = 'left'
                        self.direction_update_allowed = False   
                    elif event.key == pg.K_RIGHT and self.snake.direction != 'left' and self.direction_update_allowed:
                        self.snake.direction = 'right'
                        self.direction_update_allowed = False  
                    elif event.key == pg.K_UP and self.snake.direction != 'down' and self.direction_update_allowed:
                        self.snake.direction = 'up'
                        self.direction_update_allowed = False  
                    elif event.key == pg.K_DOWN and self.snake.direction != 'up' and self.direction_update_allowed:
                        self.snake.direction = 'down'
                        self.direction_update_allowed = False  
                    elif event.key == pg.K_ESCAPE:
                        self.menu.is_active = True
                    elif event.key == pg.K_SPACE and self.snake.status == 'paused':
                        self.snake.status = 'active'
                
                if not self.GHOST_MOVES and event.type == self.GHOST_TIMER:
                    self.GHOST_MOVES = True

                if event.type == self.GHOST_UPDATE and self.EXPERT_MODE and not self.snake.status == 'paused':
                    self.ghost.select()

                if event.type == self.SNAKE_UPDATE and not self.menu.is_active:
                    result = self.snake.update(self.apple, self.ghost, self.EXPERT_MODE, self.SNAKE_UPDATE)
                    if self.EXPERT_MODE:
                        self.ghost.update(self.apple, self.snake, self.GHOST_MOVES)
                    if result == 'dead':
                        self.in_progress = False
                        self.snake.game_over(self.screen, self.background, self.apple)
                        self.highscore.load_highscore()
                        if ((not self.EXPERT_MODE and self.snake.score > self.highscore.highscore[-1][0]) 
                            or (self.EXPERT_MODE and self.snake.score > self.highscore.highscore_expert[-1][0])):
                            self.highscore.new_highscore(self.screen, self.background, self.snake, self.apple, self.EXPERT_MODE)
                            self.highscore.show_highscore(self.screen, self.EXPERT_MODE)
                        self.menu.is_active = True

            self.apple.draw()
            self.snake.draw()
            if self.EXPERT_MODE:
                self.ghost.draw(self.apple, self.GHOST_MOVES)
            label = pg.font.SysFont('Arial', 40, bold = True).render(f'Snacks: {self.snake.score}',True,pg.Color('black'))
            self.screen.blit(label,(10,10))
            pg.display.flip()
        pg.quit()


class Options:
    def __init__(self, game:Game):
        self.game = game
        self.active_menu = 1
        self.sfx = 1
        self.music = 1
        self.off = pg.image.load(f"{GRAPHICS_PATH}\\menu\\selection_off.png")
        self.on = pg.image.load(f"{GRAPHICS_PATH}\\menu\\selection_on.png")
    	# create entries
        # self.bg = pg.image.load(f"{GRAPHICS_PATH}\\gears.png")
        self.snake_image = pg.image.load(f"{GRAPHICS_PATH}\\menu\\menu_snake.png").convert_alpha()
        self.bg_color = pg.Color('chartreuse3')
        self.font_color = pg.Color('brown2')
        self.outline_color = pg.Color('white')
        self.surface = pg.Surface((WIDTH,HEIGHT))
        self.headline = pg.font.SysFont('chiller', 150, bold = True).render('Optionen', True, pg.Color('gray20'))
        self.headline_outline = pg.font.SysFont('chiller', 150, bold = True).render('Optionen', True, self.outline_color)
        self.info = pg.font.SysFont('Arial', 20, bold = True).render('Auswahl mit Pfeiltasten - Bestätigen mit Enter oder Leertaste. Zurück mit ESC.', True, self.font_color)
        self.info_outline = pg.font.SysFont('Arial', 20, bold = True).render('Auswahl mit Pfeiltasten - Bestätigen mit Enter oder Leertaste. Zurück mit ESC.', True, self.outline_color)
        
        self.sfx_label = pg.font.SysFont('chiller', 90, bold = True).render('Soundeffekte:', True, self.font_color)
        self.sfx_label_outline = pg.font.SysFont('chiller', 90, bold = True).render('Soundeffekte:', True, self.outline_color)
        self.music_label = pg.font.SysFont('chiller', 90, bold = True).render('Hintergrundmusik:', True, self.font_color)
        self.music_label_outline = pg.font.SysFont('chiller', 90, bold = True).render('Hintergrundmusik:', True, self.outline_color)
        

    def show(self): # , screen:pg.Surface, snake, game_is_active
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    
                    if event.key == pg.K_RETURN or event.key == pg.K_SPACE:
                        if self.active_menu == 1:
                            self.music = not self.music
                            self.game.snake.update_sound_volume(self)
                        elif self.active_menu == 2:
                            self.sfx = not self.sfx
                            self.game.snake.update_sound_volume(self)
                        
    	                        
                    elif event.key == pg.K_ESCAPE:
                        running = False
                    elif event.key == pg.K_DOWN:
                        if self.active_menu < 2:
                            self.active_menu += 1
                    elif event.key == pg.K_UP:
                        if self.active_menu > 1:
                            self.active_menu -= 1
            self.surface.fill(self.bg_color)
            self.surface.blit(self.snake_image, (0,HEIGHT - self.snake_image.get_height()))
        
            self.outline(self.surface, self.headline_outline, (WIDTH - self.headline_outline.get_width())//2, 0)
            self.surface.blit(self.headline, ((WIDTH - self.headline.get_width())//2, 0))
            self.outline(self.surface, self.info_outline, (WIDTH - self.info.get_width())//2, 170, 2)
            self.surface.blit(self.info, ((WIDTH - self.info.get_width())//2, 170))

            rect = self.music_label.get_rect(right = 1000).x
            self.outline(self.surface, self.music_label_outline, rect, 250)
            music_placed = self.surface.blit(self.music_label, (rect, 250))
            checkbox_music = self.on if self.music else self.off
            checkbox_rect = pg.Rect(1150 - checkbox_music.get_width(), music_placed.y, music_placed.h, music_placed.h)
            self.surface.blit(checkbox_music, checkbox_rect)


            rect = self.sfx_label.get_rect(right = 1000).x
            self.outline(self.surface, self.sfx_label_outline, rect, 350)
            sfx_placed = self.surface.blit(self.sfx_label, (rect, 350))
            checkbox_sfx = self.on if self.sfx else self.off
            checkbox_rect = pg.Rect(1150 - checkbox_sfx.get_width(), sfx_placed.y, sfx_placed.h, sfx_placed.h)
            self.surface.blit(checkbox_sfx, checkbox_rect)


            selected_menu = ['_', music_placed, sfx_placed][self.active_menu]
            x, y, width, height = selected_menu
            pg.draw.rect(self.surface, self.outline_color, (x-5, y, width+10, height), 3)

            self.game.screen.blit(self.surface, (0,0))
            pg.display.flip()


    def outline(self, screen:pg.Surface, label, x, y, outline_distance = 3):
        screen.blit(label, (x-outline_distance, y-outline_distance))
        screen.blit(label, (x+outline_distance, y-outline_distance))
        screen.blit(label, (x-outline_distance, y+outline_distance))
        screen.blit(label, (x+outline_distance, y+outline_distance))


class Background:
    def __init__(self, game):
        self.screen = game.screen
        
        #background_surface = pg.image.load(f"{GRAPHICS_PATH}\\background\\background.jpg").convert_alpha()
        #background_surface = pg.transform.scale(background_surface, (WIDTH, HEIGHT) )
        
        background_surface = pg.Surface((WIDTH, HEIGHT))
        x_size = WIDTH // X_FIELDS
        y_size = HEIGHT // Y_FIELDS
        
        color_1 = (114,174,74) # 169, 208, 142
        color_2 = (131,185,91) # 255,228,173
        color_3 = (166,213,121)
        color_4 = (145,190,107)

        color_list =[color_1, color_2, color_3, color_4]
        
        # for y in range(Y_FIELDS):    
        #     for x in range(X_FIELDS):
        #         if y % 2 == 0:
        #             if x % 2 == 0:
        #                 pg.draw.rect(background_surface, color_1, (x*x_size, y*y_size, x_size, y_size))
        #                 pg.draw.rect(background_surface, pg.Color('black'), (x*x_size, y*y_size, x_size, y_size),1)
        #             else:
        #                 pg.draw.rect(background_surface, color_2, (x*x_size, y*y_size, x_size, y_size))
        #                 pg.draw.rect(background_surface, pg.Color('black'), (x*x_size, y*y_size, x_size, y_size),1)
        #         else:
        #             if x % 2 == 0:
        #                 pg.draw.rect(background_surface, color_3, (x*x_size, y*y_size, x_size, y_size))
        #                 pg.draw.rect(background_surface, pg.Color('black'), (x*x_size, y*y_size, x_size, y_size),1)
        #             else:
        #                 pg.draw.rect(background_surface, color_4, (x*x_size, y*y_size, x_size, y_size))
        #                 pg.draw.rect(background_surface, pg.Color('black'), (x*x_size, y*y_size, x_size, y_size),1)

        for y in range(Y_FIELDS):    
            for x in range(X_FIELDS):
                pg.draw.rect(background_surface, random.choice(color_list), (x*x_size, y*y_size, x_size, y_size))
                

        self.background = background_surface


    def draw(self):
        self.screen.blit(self.background,(0,0))


class Apple:
    def __init__(self, game):
        self.screen = game.screen
        symbol_list = []
        picture = pg.image.load(f"{GRAPHICS_PATH}\\items\\apple.png").convert_alpha()
        picture = pg.transform.scale(picture, (WIDTH // X_FIELDS, HEIGHT // Y_FIELDS))
        symbol_list.append(picture)
        picture = pg.image.load(f"{GRAPHICS_PATH}\\items\\rat.png").convert_alpha()
        picture = pg.transform.scale(picture, (WIDTH // X_FIELDS, HEIGHT // Y_FIELDS))
        symbol_list.append(picture)
        self.symbol = symbol_list
        
    
    def generate(self, snake):
        snake_fields = {pos for pos,_ in snake.snake_body}
        free_cells = list(GAME_BOARD_POSITIONS - snake_fields)
        self.position = random.choice(free_cells)
        self.item = random.choice(self.symbol)


    def draw(self):
        x, y = self.position
        upper_left_corner_x = WIDTH // X_FIELDS 
        upper_left_corner_y = HEIGHT // Y_FIELDS
        self.screen.blit(self.item, (x* upper_left_corner_x, y* upper_left_corner_y))


class Snake: 
    def __init__(self, game:Game):
        self.screen = game.screen
        self.game = game
        # head graphics
        directions = ['up', 'down', 'left', 'right']
        head_graphics = {}
        for direction in directions:
            picture = pg.image.load(f"{GRAPHICS_PATH}\\snake\\head_{direction}.png").convert_alpha()
            picture = pg.transform.scale(picture, (WIDTH // X_FIELDS, HEIGHT // Y_FIELDS))
            head_graphics[direction] = picture
        for direction in directions:
            picture = pg.image.load(f"{GRAPHICS_PATH}\\snake\\head_{direction}_2.png").convert_alpha()
            picture = pg.transform.scale(picture, (WIDTH // X_FIELDS, HEIGHT // Y_FIELDS))
            head_graphics[f"{direction}_2"] = picture
        self.head_graphics = head_graphics
        # tail graphics
        tail_graphics = {}
        for direction in directions:
            picture = pg.image.load(f"{GRAPHICS_PATH}\\snake\\tail_{direction}.png").convert_alpha()
            picture = pg.transform.scale(picture, (WIDTH // X_FIELDS, HEIGHT // Y_FIELDS))
            tail_graphics[direction] = picture
        self.tail_graphics = tail_graphics
        # body_graphics    
        body_graphics = {}
        directions = ['vertical', 'horizontal', 'topleft', 'topright', 'bottomleft', 'bottomright']
        for direction in directions:    
            picture = pg.image.load(f"{GRAPHICS_PATH}\\snake\\body_{direction}.png").convert_alpha()
            picture = pg.transform.scale(picture, (WIDTH // X_FIELDS, HEIGHT // Y_FIELDS))
            body_graphics[direction] = picture    
        self.body_graphics = body_graphics
        # sounds
        self.eating_sound = pg.mixer.Sound(f"{SOUNDS_PATH}\\eating.mp3")
        self.rat_eating = pg.mixer.Sound(f"{SOUNDS_PATH}\\ratdeath.mp3")
        self.moving_sound = pg.mixer.Sound(f"{SOUNDS_PATH}\\move.mp3")
        self.bg_music = pg.mixer.Sound(f"{SOUNDS_PATH}\\bg_music.mp3")
        self.update_sound_volume(game.options)
        self.bg_music.play(loops = -1)

        
    def update_sound_volume(self, options):
        self.eating_sound.set_volume(1 * options.sfx)
        self.rat_eating.set_volume(1 * options.sfx)
        self.moving_sound.set_volume(0.1 * options.sfx)
        self.bg_music.set_volume(0.5 * options.music)


    def initialize(self):
        self.snake_body = deque([((X_FIELDS - 3,Y_FIELDS // 2), 'left'), ((X_FIELDS - 2, Y_FIELDS // 2),'left'), ((X_FIELDS - 1, Y_FIELDS // 2), 'left')])
        self.direction = 'left' # 'left'
        self.speed = 150
        self.score = 0
        self.moves = 0
        self.status = 'active'

    
    def draw(self):
        length_of_snake = len(self.snake_body)
        eyes_closed = '_2' if self.moves % 30 == 0 else '' # every 30 moves the snake closes his eyes
        for idx, (coords, direction) in enumerate(self.snake_body):
            x, y = coords
            x = x * WIDTH // X_FIELDS
            y = y * HEIGHT // Y_FIELDS
            if idx == 0: # head
                graphic = self.head_graphics[f"{direction}{eyes_closed}"]
            elif idx == length_of_snake - 1: # tail
                graphic = self.tail_graphics[self.snake_body[idx-1][1]] # direction of the last segment before the tail  
            else:
                if self.snake_body[idx-1][1] == self.snake_body[idx][1]:
                    if direction in ('right', 'left'):
                        tile = 'horizontal'
                    else:
                        tile = 'vertical'
                
                if (self.snake_body[idx][1] == 'right' and self.snake_body[idx-1][1] == 'up') or (self.snake_body[idx][1] == 'down' and self.snake_body[idx-1][1] == 'left'):
                    tile = 'topleft'
                elif (self.snake_body[idx][1] == 'right' and self.snake_body[idx-1][1] == 'down') or (self.snake_body[idx][1] == 'up' and self.snake_body[idx-1][1] == 'left'):
                    tile = 'bottomleft'
                elif (self.snake_body[idx][1] == 'left' and self.snake_body[idx-1][1] == 'up') or (self.snake_body[idx][1] == 'down' and self.snake_body[idx-1][1] == 'right'):
                    tile = 'topright'
                elif (self.snake_body[idx][1] == 'left' and self.snake_body[idx-1][1] == 'down') or (self.snake_body[idx][1] == 'up' and self.snake_body[idx-1][1] == 'right'):
                    tile = 'bottomright'
                graphic = self.body_graphics[tile]
            
            self.screen.blit(graphic, (x,y))
            if self.status == 'paused':
                label = pg.font.SysFont('Arial', 40, bold = True).render('Zum Weiterspielen Leertaste drücken.', True, pg.Color('brown2'))
                self.screen.blit(label, ((WIDTH - label.get_width())//2, 600))

    
    def update(self, apple:Apple, ghost, EXPERT_MODE, SNAKE_UPDATE:pg.USEREVENT):
        if self.status == 'paused':
            return
        self.game.direction_update_allowed = True
        self.moves += 1
        if self.moves > 1_000_000_000:
            self.moves = 0
        head_x, head_y = self.snake_body[0][0]
        if self.direction == 'left':
            x = head_x - 1
            y = head_y  
        elif self.direction == 'right':
            x = head_x + 1
            y = head_y
        elif self.direction == 'up':    
            x = head_x
            y = head_y - 1
        elif self.direction == 'down':
            x = head_x
            y = head_y + 1

        new_head = (x,y)
        
        # check if snake leaves the board or bites itself
        if X_FIELDS-1 < x or x < 0 or Y_FIELDS-1 < y or y < 0 or any((x,y) == coords for coords, _ in self.snake_body):
            return 'dead'   
        if EXPERT_MODE and any((x,y) == coords for coords, _ in ghost.actual_body):
            return 'dead'
        
        # check if snake eats the apple
        self.moving_sound.play()
        if new_head == apple.position:
            if apple.item == apple.symbol[0]:
                self.eating_sound.play()
            else:
                self.rat_eating.play()
            if self.game.EXPERT_MODE:
                self.game.ghost.wait += self.speed
            apple.generate(self)
            self.snake_body.appendleft((new_head, self.direction)) # type: ignore
             
            self.score += 1
            if self.score % 10 == 0 and self.score > 0:
                if self.speed > 100:
                    self.speed -= 10
                    if self.game.EXPERT_MODE:
                        self.game.ghost.ghost_speed -= 10
                        pg.time.set_timer(self.game.GHOST_UPDATE, self.game.ghost.ghost_speed)
                    pg.time.set_timer(self.game.SNAKE_UPDATE, self.speed) # each 10 apples the speed will raise
        else:
            self.snake_body.appendleft((new_head, self.direction)) # type: ignore
            self.snake_body.pop()


    def game_over(self, screen:pg.Surface, background:Background, apple:Apple):
        running = True
        outline_distance = 3
        text_color = pg.Color('blue')
        outline_color = pg.Color('white')
        game_over_label = pg.font.SysFont('chiller', 180, bold = True).render("GAME OVER", True, text_color)
        game_over_label_outlined = pg.font.SysFont('chiller', 180, bold = True).render("GAME OVER", True, outline_color)
        space_label = pg.font.SysFont('chiller', 60, bold = True).render('Leertaste drücken',True,pg.Color('red'))
        space_label_outlined = pg.font.SysFont('chiller', 60, bold = True).render('Leertaste drücken',True,pg.Color('white'))
        point_string = 'Punkt' if self.score == 1 else 'Punkte'
        score_label =  pg.font.SysFont('chiller', 90, bold = True).render(f'Du hast {self.score} {point_string} erzielt.',True, text_color)
        score_label_outlined =  pg.font.SysFont('chiller', 90, bold = True).render(f'Du hast {self.score} {point_string} erzielt.',True, outline_color)
        game_label_x_position = (WIDTH - game_over_label.get_width()) // 2
        space_label_x_position = (WIDTH - space_label.get_width()) // 2
        score_label_x_position =  (WIDTH - score_label.get_width()) // 2
        color_list = ['red', 'orange', 'yellow', 'darkgreen', 'blue', 'indigo', 'violet']
        index = 0
        color_change = pg.USEREVENT
        pg.time.set_timer(color_change, 500)
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                    pg.quit
                    sys.exit()
                elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                    running = False
                if event.type == color_change:
                    index += 1
                    if index > len(color_list) -1:
                        index = 0
                    space_label = pg.font.SysFont('chiller', 60, bold = True).render('Leertaste drücken',True,color_list[index])
            background.draw()
            apple.draw()
            self.draw()
            # render Game over with outline
            screen.blit(game_over_label_outlined, (game_label_x_position - outline_distance, HEIGHT // 10 - outline_distance))
            screen.blit(game_over_label_outlined, (game_label_x_position + outline_distance, HEIGHT // 10 - outline_distance))
            screen.blit(game_over_label_outlined, (game_label_x_position - outline_distance, HEIGHT // 10 + outline_distance))
            screen.blit(game_over_label_outlined, (game_label_x_position + outline_distance, HEIGHT // 10 + outline_distance))
            screen.blit(game_over_label, (game_label_x_position, HEIGHT // 10))
            # render the score and outline
            screen.blit(score_label_outlined, (score_label_x_position - outline_distance, HEIGHT // 2 - outline_distance))
            screen.blit(score_label_outlined, (score_label_x_position + outline_distance, HEIGHT // 2 - outline_distance))
            screen.blit(score_label_outlined, (score_label_x_position - outline_distance, HEIGHT // 2 + outline_distance))
            screen.blit(score_label_outlined, (score_label_x_position + outline_distance, HEIGHT // 2 + outline_distance))
            screen.blit(score_label, (score_label_x_position, HEIGHT // 2))
            # render  spacelabel and outline
            screen.blit(space_label_outlined, (space_label_x_position - outline_distance, HEIGHT // 2 + 300 - outline_distance))
            screen.blit(space_label_outlined, (space_label_x_position + outline_distance, HEIGHT // 2 + 300 - outline_distance))
            screen.blit(space_label_outlined, (space_label_x_position - outline_distance, HEIGHT // 2 + 300 + outline_distance))
            screen.blit(space_label_outlined, (space_label_x_position + outline_distance, HEIGHT // 2 + 300 + outline_distance))
            screen.blit(space_label, (space_label_x_position, HEIGHT // 2 + 300))
            pg.display.flip()
        

class Ghost(Snake):
    def __init__(self, game):
        self.screen = game.screen
        self.game = game
        self.moves = 0
        self.wait = 0
        self.ghost_speed = 150
        # head graphics
        directions = ['up', 'down', 'left', 'right']
        head_graphics = {}
        for direction in directions:
            picture = pg.image.load(f"{GRAPHICS_PATH}\\ghost\\head_{direction}.png").convert_alpha()
            picture = pg.transform.scale(picture, (WIDTH // X_FIELDS, HEIGHT // Y_FIELDS))
            head_graphics[direction] = picture
        for direction in directions:
            picture = pg.image.load(f"{GRAPHICS_PATH}\\ghost\\head_{direction}_2.png").convert_alpha()
            picture = pg.transform.scale(picture, (WIDTH // X_FIELDS, HEIGHT // Y_FIELDS))
            head_graphics[f"{direction}_2"] = picture
        self.head_graphics = head_graphics
        # tail graphics
        tail_graphics = {}
        for direction in directions:
            picture = pg.image.load(f"{GRAPHICS_PATH}\\ghost\\tail_{direction}.png").convert_alpha()
            picture = pg.transform.scale(picture, (WIDTH // X_FIELDS, HEIGHT // Y_FIELDS))
            tail_graphics[direction] = picture
        self.tail_graphics = tail_graphics
        # body_graphics    
        body_graphics = {}
        directions = ['vertical', 'horizontal', 'topleft', 'topright', 'bottomleft', 'bottomright']
        for direction in directions:    
            picture = pg.image.load(f"{GRAPHICS_PATH}\\ghost\\body_{direction}.png").convert_alpha()
            picture = pg.transform.scale(picture, (WIDTH // X_FIELDS, HEIGHT // Y_FIELDS))
            body_graphics[direction] = picture    
        self.body_graphics = body_graphics
        # apple, rat
        apple_image = pg.image.load(f"{GRAPHICS_PATH}\\ghost\\apple.png").convert_alpha()
        apple_image = pg.transform.scale(apple_image, (WIDTH // X_FIELDS, HEIGHT // Y_FIELDS))
        self.apple_image = apple_image
        rat_image = pg.image.load(f"{GRAPHICS_PATH}\\ghost\\rat.png").convert_alpha()
        rat_image = pg.transform.scale(rat_image, (WIDTH // X_FIELDS, HEIGHT // Y_FIELDS))
        self.rat_image = rat_image
        

    
    def initialize(self):
        self.body_list = deque()
        self.body_list.append([((X_FIELDS - 3,Y_FIELDS // 2), 'left'), ((X_FIELDS - 2, Y_FIELDS // 2),'left'), ((X_FIELDS - 1, Y_FIELDS // 2), 'left')])
        self.fruit_list = deque()
        self.actual_body = self.body_list[0]
        self.actual_fruit = None
    
    
    def update(self, apple:Apple, snake:Snake, GHOST_MOVES:bool):
        if self.game.snake.status == 'paused':
            return
        self.body_list.append(list(snake.snake_body))
        if apple.item == apple.symbol[0]:
            self.fruit_list.append([self.apple_image, apple.position])
        else:
            self.fruit_list.append([self.rat_image, apple.position])
        
        
    def select(self):    
        # print(f"{self.game.snake.speed=} {self.ghost_speed=}")
        if self.wait > 0 and self.ghost_speed == self.game.snake.speed:
            self.ghost_speed = self.game.snake.speed + self.game.snake.speed // 4
            pg.time.set_timer(self.game.GHOST_UPDATE, self.ghost_speed)
            self.wait -= self.game.snake.speed // 4
        elif self.wait < 0:
            self.wait = 0
            self.ghost_speed = self.game.snake.speed
            pg.time.set_timer(self.game.GHOST_UPDATE, self.ghost_speed)
        elif self.wait == 0 and self.ghost_speed != self.game.snake.speed:
            self.ghost_speed = self.game.snake.speed
            pg.time.set_timer(self.game.GHOST_UPDATE, self.ghost_speed)

        if self.wait >0:
            self.wait -= self.game.snake.speed // 4
            

        if not self.game.GHOST_MOVES:
            self.actual_body = self.body_list[0]
            self.actual_fruit = []
        elif self.game.GHOST_MOVES:
            self.actual_body = self.body_list.popleft()
            if len(self.fruit_list) > 0:
                self.actual_fruit = self.fruit_list.popleft()
            self.moves += 1

    
    def draw(self, apple:Apple, GHOST_MOVES:bool):
        length_of_snake = len(self.actual_body)
        eyes_closed = '_2' if self.moves % 30 == 0 else '' # every 30 moves the snake closes his eyes
        
        # draw ghost fruit
        if GHOST_MOVES and self.actual_fruit:
            fruit, position = self.actual_fruit
            x, y = position
            if position != apple.position:
                upper_left_corner_x = WIDTH // X_FIELDS 
                upper_left_corner_y = HEIGHT // Y_FIELDS
                self.screen.blit(fruit, (x* upper_left_corner_x, y* upper_left_corner_y))  
        
        # draw ghost snake
        for idx, (coords, direction) in enumerate(self.actual_body):
            
            x, y = coords
            x = x * WIDTH // X_FIELDS
            y = y * HEIGHT // Y_FIELDS
            if idx == 0: # head
                graphic = self.head_graphics[f"{direction}{eyes_closed}"]
            elif idx == length_of_snake - 1: # tail
                graphic = self.tail_graphics[self.actual_body[idx-1][1]] # direction of the last segment before the tail  
            else:
                if self.actual_body[idx-1][1] == self.actual_body[idx][1]:
                    if direction in ('right', 'left'):
                        tile = 'horizontal'
                    else:
                        tile = 'vertical'
                
                if (self.actual_body[idx][1] == 'right' and self.actual_body[idx-1][1] == 'up') or (self.actual_body[idx][1] == 'down' and self.actual_body[idx-1][1] == 'left'):
                    tile = 'topleft'
                elif (self.actual_body[idx][1] == 'right' and self.actual_body[idx-1][1] == 'down') or (self.actual_body[idx][1] == 'up' and self.actual_body[idx-1][1] == 'left'):
                    tile = 'bottomleft'
                elif (self.actual_body[idx][1] == 'left' and self.actual_body[idx-1][1] == 'up') or (self.actual_body[idx][1] == 'down' and self.actual_body[idx-1][1] == 'right'):
                    tile = 'topright'
                elif (self.actual_body[idx][1] == 'left' and self.actual_body[idx-1][1] == 'down') or (self.actual_body[idx][1] == 'up' and self.actual_body[idx-1][1] == 'right'):
                    tile = 'bottomright'
                
                graphic = self.body_graphics[tile]
            self.screen.blit(graphic, (x,y))


class StartScreen:
    def __init__(self, game:Game):
        self.game = game
        picture = pg.image.load(f"{GRAPHICS_PATH}\\start_screen\\start_screen.png").convert_alpha()
        picture = pg.transform.scale(picture, (WIDTH, HEIGHT))
        self.picture = picture
        self.event = pg.USEREVENT
        pg.time.set_timer(self.event, 500)
    
    
    def mainloop(self):
        my_surface = pg.Surface((WIDTH, HEIGHT))
        label = pg.font.SysFont('chiller', 60, bold = True).render('Leertaste drücken zum Spielen',True,pg.Color('red'))
        label_outlined = pg.font.SysFont('chiller', 60, bold = True).render('Leertaste drücken zum Spielen',True,pg.Color('white'))
        outline_distance = 3
        label_x_position = (WIDTH - label.get_width()) // 2
        color_list = ['red', 'orange', 'yellow', 'darkgreen', 'blue', 'indigo', 'violet']
        index = 0
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                    pg.quit
                    sys.exit()
                elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                    running = False
                if event.type == self.event:
                    index += 1
                    if index > len(color_list) -1:
                        index = 0
                    label = pg.font.SysFont('chiller', 60, bold = True).render('Leertaste drücken zum Spielen',True,color_list[index])
            my_surface.blit(self.picture, (0,0))
            my_surface.blit(label_outlined, (label_x_position - outline_distance, 700 - outline_distance))
            my_surface.blit(label_outlined, (label_x_position + outline_distance, 700 - outline_distance))
            my_surface.blit(label_outlined, (label_x_position - outline_distance, 700 + outline_distance))
            my_surface.blit(label_outlined, (label_x_position + outline_distance, 700 + outline_distance))
            my_surface.blit(label,(label_x_position,700))
            self.game.screen.blit(my_surface, (0,0))
            pg.display.flip()


class Highscore:
    def __init__(self, game:Game):
        if not os.path.exists(HIGHSCORE_PATH):
            self.highscore_path = FALLBACK_HIGHSCORE_PATH
            self.highscore_path_expert = FALLBACK_HIGHSCORE_PATH_EXPERT
        else:
            self.highscore_path = HIGHSCORE_PATH
            self.highscore_path_expert = HIGHSCORE_PATH_EXPERT

        self.event = pg.USEREVENT
        pg.time.set_timer(self.event, 500)
        self.game = game
    
    def load_highscore(self):
        with open(self.highscore_path, 'r') as file:
            lines = [x.strip() for x in file.readlines()]
        highscore_list = []
        for line in lines:
            k , v = line.split(':')
            highscore_list.append((int(k), v))
        self.highscore = highscore_list

        with open(self.highscore_path_expert, 'r') as file:
            lines = [x.strip() for x in file.readlines()]
        highscore_list_expert = []
        for line in lines:
            k , v = line.split(':')
            highscore_list_expert.append((int(k), v))
        self.highscore_expert = highscore_list_expert
    
    
    def save_highscore(self, EXPERT_MODE):
        if not EXPERT_MODE:
            new_string = ''
            for k, v in self.highscore:
                new_string += f"{k}:{v}\n"
            with open(self.highscore_path, 'w') as file:
                file.write(new_string)
        else:
            new_string = ''
            for k, v in self.highscore_expert:
                new_string += f"{k}:{v}\n"
            with open(self.highscore_path_expert, 'w') as file:
                file.write(new_string)

    def sort_highscore(self):
        self.highscore = sorted(self.highscore, reverse = True)[:10]
        self.highscore_expert = sorted(self.highscore_expert, reverse = True)[:10]

    def new_highscore(self, screen:pg.Surface, background:pg.Surface, snake:Snake, apple:Apple, EXPERT_MODE):
        highscore_surface = pg.Surface((WIDTH, HEIGHT))
        font_color = pg.Color('brown2')
        outline_color = pg.Color('white')
        trophy = pg.image.load(f"{GRAPHICS_PATH}\\highscore\\Trophy.png")
        trophy = pg.transform.scale(trophy, (800,800))
        input_box = InputBox(300, 350, 600,100, color = 'brown2')
        running = True
        while running:
            highscore_surface.fill('chartreuse3')
            highscore_surface.blit(trophy, ((WIDTH - trophy.get_width())//2, 0))
            for event in pg.event.get():
                player_name = input_box.handle_input(event)
                if player_name:
                    running = False
                    self.load_highscore()
                    if EXPERT_MODE:
                        self.highscore_expert.append((snake.score, player_name))
                    else:
                        self.highscore.append((snake.score, player_name))
            
            input_box.draw(highscore_surface)
            highscore_headline_1 =  pg.font.SysFont('Arial', 90, bold = True).render('Herzlichen Glückwunsch.', True, font_color)
            highscore_headline_1_outline =  pg.font.SysFont('Arial', 90, bold = True).render('Herzlichen Glückwunsch.', True, outline_color)
            highscore_headline_2 =  pg.font.SysFont('Arial', 40, bold = True).render('Du hast dich für die Highscoreliste qualifiziert.', True, font_color)
            highscore_headline_2_outline =  pg.font.SysFont('Arial', 40, bold = True).render('Du hast dich für die Highscoreliste qualifiziert.', True, outline_color)
            highscore_headline_3 =  pg.font.SysFont('Arial', 40, bold = True).render('Bitte gib deinen Namen ein. (max. 20 Zeichen)', True, font_color)
            highscore_headline_3_outline =  pg.font.SysFont('Arial', 40, bold = True).render('Bitte gib deinen Namen ein. (max. 20 Zeichen)', True, outline_color)
            
            self.outline(highscore_surface, highscore_headline_1_outline, (WIDTH - highscore_headline_1.get_width())//2, 50)
            highscore_surface.blit(highscore_headline_1, ((WIDTH - highscore_headline_1.get_width())//2, 50))
            self.outline(highscore_surface, highscore_headline_2_outline, (WIDTH - highscore_headline_2.get_width())//2, 150)
            highscore_surface.blit(highscore_headline_2, ((WIDTH - highscore_headline_2.get_width())//2, 150))
            self.outline(highscore_surface, highscore_headline_3_outline, (WIDTH - highscore_headline_3.get_width())//2, 250)
            highscore_surface.blit(highscore_headline_3, ((WIDTH - highscore_headline_3.get_width())//2, 250))
            screen.blit(highscore_surface, (0,0))
            pg.display.flip()    
        
        self.sort_highscore()
        self.save_highscore(EXPERT_MODE)

    def show_highscore(self, screen:pg.Surface, EXPERT_MODE = False):
        self.load_highscore()
        
        if EXPERT_MODE:
            headline_text = 'Highscores Expertenmodus'
            highscore_liste = self.highscore_expert
        else:
            headline_text = 'Highscores normaler Modus'
            highscore_liste = self.highscore
        
        # highscore_surf = pg.Surface((WIDTH,HEIGHT))
        highscore_surf = pg.image.load(f"{GRAPHICS_PATH}\\highscore\\Highscore wide.png").convert_alpha()
        text_color = pg.Color('black')
        outline_color = pg.Color('white')
        highscore_headline = pg.font.SysFont('chiller', 100, bold = True).render(headline_text, True, text_color)
        highscore_headline_outlined = pg.font.SysFont('chiller', 100, bold = True).render(headline_text, True, outline_color)
        
        highscore_names = [pg.font.SysFont('Arial', 40, bold = True).render(name, True, text_color) for _ , name in highscore_liste]
        highscore_names_outlined = [pg.font.SysFont('Arial', 40, bold = True).render(name, True, outline_color) for _ , name in highscore_liste]
        symbol_label =  pg.font.SysFont('Arial', 40, bold = True).render("-", True, text_color)
        symbol_label_outlined =  pg.font.SysFont('Arial', 40, bold = True).render("-", True, outline_color)
        highscore_score = [pg.font.SysFont('Arial', 40, bold = True).render(f"{score} Punkte", True, text_color) for score, _ in highscore_liste]
        highscore_score_outlined = [pg.font.SysFont('Arial', 40, bold = True).render(f"{score} Punkte", True, outline_color) for score, _ in highscore_liste]
        
        space_label = pg.font.SysFont('chiller', 60, bold = True).render('Leertaste drücken',True,pg.Color('red'))
        space_label_outlined = pg.font.SysFont('chiller', 60, bold = True).render('Leertaste drücken',True,pg.Color('white'))
        color_list = ['red', 'orange', 'yellow', 'darkgreen', 'blue', 'indigo', 'violet']
        
        index = 0
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit
                    sys.exit()
                elif event.type == pg.KEYDOWN: 
                    if event.key == pg.K_SPACE or event.key == pg.K_ESCAPE:
                        running = False
                if event.type == self.event:
                    index += 1
                    if index > len(color_list) -1:
                        index = 0
                    space_label = pg.font.SysFont('chiller', 60, bold = True).render('Leertaste drücken',True,color_list[index])
            # render the headline with letters outlined         
            self.outline(highscore_surf, highscore_headline_outlined, ((WIDTH - highscore_headline.get_width()) // 2), 50)
            highscore_surf.blit(highscore_headline, ((WIDTH - highscore_headline.get_width()) // 2, 50))
            # render player names
            for idx, (label, outline_label) in enumerate(zip(highscore_names, highscore_names_outlined)):
                text_rect = label.get_rect(right = 550).x
                self.outline(highscore_surf, outline_label, text_rect, (idx+1) * 40 + 240 )
                highscore_surf.blit(label, (text_rect, (idx+1) * 40 + 240))
            # render the minus symbol between players and score
            for idx in range(1, 11):
                text_rect = symbol_label.get_rect(center = (WIDTH // 2, HEIGHT // 2 )).x
                self.outline(highscore_surf, symbol_label_outlined, text_rect, idx * 40 + 240)
                highscore_surf.blit(symbol_label, (text_rect, idx * 40 + 240))
            # render the score
            longest_label = max(label.get_width() for label in highscore_score)
            for idx, (label, label_outlined) in enumerate(zip(highscore_score, highscore_score_outlined)):
                text_rect = label.get_rect(right = 625 + longest_label).x
                self.outline(highscore_surf, label_outlined, text_rect, (idx+1) * 40 + 240)
                highscore_surf.blit(label, (text_rect, (idx+1) * 40 + 240))
            # render "press space bar" 
            self.outline(highscore_surf, space_label_outlined, (WIDTH - space_label.get_width())//2, 700)
            highscore_surf.blit(space_label, ((WIDTH - space_label.get_width())//2, 700))
            screen.blit(highscore_surf, (0,0))
            pg.display.flip()

    
    def outline(self, screen:pg.Surface, label, x, y):
        outline_distance = 3
        screen.blit(label, (x-outline_distance, y-outline_distance))
        screen.blit(label, (x+outline_distance, y-outline_distance))
        screen.blit(label, (x-outline_distance, y+outline_distance))
        screen.blit(label, (x+outline_distance, y+outline_distance))


class InputBox:
    def __init__(self, x:int, y:int, width:int, height:int, text:str = '|', color:str = 'white'):
        self.rect = pg.Rect(x,y,width,height)
        self.text = text
        self.color = pg.Color(color)
        self.text_surface = pg.font.SysFont('Arial', 60, bold = True).render(self.text, True, self.color)
        self.text_surface_outline = pg.font.SysFont('Arial', 60, bold = True).render(self.text, True, pg.Color('white'))

    def handle_input(self, event:pg.Event):
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN:
                return self.text[:-1]
            elif event.key == pg.K_BACKSPACE:
                self.text = f"{self.text[:-2]}|"
            else:
                if len(self.text) < 21:
                    self.text = f"{self.text[:-1]}{event.unicode}|"
            self.text_surface = pg.font.SysFont('Arial', 60, bold = True).render(self.text, True, self.color)
            self.text_surface_outline = pg.font.SysFont('Arial', 60, bold = True).render(self.text, True, pg.Color('white'))

    def draw(self, highscore_screen:pg.Surface):
        # highscore_screen.fill(pg.Color('black'))
        self.outline(highscore_screen, self.text_surface_outline, self.rect.x +5, self.rect.y +5)
        highscore_screen.blit(self.text_surface, (self.rect.x +5, self.rect.y +5))
        x,y,w,h = self.rect
        pg.draw.rect(highscore_screen, pg.Color('white'), (x-3, y-3,w,h), 3)
        pg.draw.rect(highscore_screen, pg.Color('white'), (x+3, y-3,w,h), 3)
        pg.draw.rect(highscore_screen, pg.Color('white'), (x-3, y+3,w,h), 3)
        pg.draw.rect(highscore_screen, pg.Color('white'), (x+3, y+3,w,h), 3)
        pg.draw.rect(highscore_screen, self.color, self.rect, 3)

    def outline(self, screen:pg.Surface, label, x, y):
        outline_distance = 3
        screen.blit(label, (x-outline_distance, y-outline_distance))
        screen.blit(label, (x+outline_distance, y-outline_distance))
        screen.blit(label, (x-outline_distance, y+outline_distance))
        screen.blit(label, (x+outline_distance, y+outline_distance))


class GameMenu:
    def __init__(self, game:Game):
        self.game = game
        self.menu_surface = pg.Surface((WIDTH,HEIGHT))
        self.is_active = True
        
        
    def show(self):
        
        running = True
        snake_image = pg.image.load(f"{GRAPHICS_PATH}\\menu\\menu_snake.png").convert_alpha()
        font_color = pg.Color('brown2')
        outline_color = pg.Color('white')
        # snake_image = pg.transform.scale(snake_image, ())
        self.active_menu = 1 if self.game.in_progress else 2
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    
                    if event.key == pg.K_RETURN or event.key == pg.K_SPACE:
                        if self.active_menu == 1:
                            running = False
                            self.is_active = False
                        elif self.active_menu == 2:
                            return 'reset'
                        
                        elif self.active_menu == 3:
                            self.game.highscore.show_highscore(self.game.screen)
                            self.game.highscore.show_highscore(self.game.screen, True) # True  =Expertmode
                        
                        elif self.active_menu == 4:
                            # self.game.options.show(self.screen, self.game.snake, self.game.in_progress)
                            self.game.options.show()
                        elif self.active_menu == 5:
                            pg.quit()
                            sys.exit()
                    
                    elif event.key == pg.K_ESCAPE and self.game.in_progress:
                        running = False
                        self.is_active = False
                    elif event.key == pg.K_DOWN:
                        if self.active_menu < 5:
                            self.active_menu += 1
                    elif event.key == pg.K_UP:
                        if (self.active_menu > 1 and self.game.in_progress) or (self.active_menu > 2 and not self.game.in_progress):
                            self.active_menu -= 1

            
            
            # backgroundcolor for the menu
            self.menu_surface.fill('chartreuse3')
            
            # menu_graphic = pg.image.load(f"{GRAPHICS_PATH}\\menu\\background.jpg")
            # pg.transform.scale(menu_graphic, (WIDTH,HEIGHT))
            # self.menu_surface.blit(menu_graphic, (0,0))
            
            
            self.menu_surface.blit(snake_image, (0,HEIGHT - snake_image.get_height()))
            
            # build the menu
            menu_headline = pg.font.SysFont('chiller', 150, bold = True).render('Spielmenü', True, pg.Color('gray20'))
            menu_headline_outline = pg.font.SysFont('chiller', 150, bold = True).render('Spielmenü', True, outline_color)
            info = pg.font.SysFont('Arial', 20, bold = True).render('Auswahl mit Pfeiltasten - Bestätigen mit Enter oder Leertaste', True, font_color)
            info_outline = pg.font.SysFont('Arial', 20, bold = True).render('Auswahl mit Pfeiltasten - Bestätigen mit Enter oder Leertaste', True, outline_color)
            resume = pg.font.SysFont('chiller', 90, bold = True).render('Spiel fortsetzen', True, font_color)
            resume_outline = pg.font.SysFont('chiller', 90, bold = True).render('Spiel fortsetzen', True, outline_color)
            new_game = pg.font.SysFont('chiller', 90, bold = True).render('Neues Spiel starten', True, font_color)
            new_game_outline = pg.font.SysFont('chiller', 90, bold = True).render('Neues Spiel starten', True, outline_color)
            highscore_label = pg.font.SysFont('chiller', 90, bold = True).render('Highscoreliste', True, font_color)
            highscore_label_outline = pg.font.SysFont('chiller', 90, bold = True).render('Highscoreliste', True, outline_color)
            options_label = pg.font.SysFont('chiller', 90, bold = True).render('Optionen', True, font_color)
            options_outline = pg.font.SysFont('chiller', 90, bold = True).render('Optionen', True, outline_color)
            exit_game = pg.font.SysFont('chiller', 90, bold = True).render('Spiel verlassen', True, font_color)
            exit_game_outline = pg.font.SysFont('chiller', 90, bold = True).render('Spiel verlassen', True, outline_color)
            
            
            # blit the menu fields
            self.outline(self.menu_surface, menu_headline_outline, (WIDTH - menu_headline.get_width())//2, 0)
            self.menu_surface.blit(menu_headline, ((WIDTH - menu_headline.get_width())//2, 0))
            
            self.outline(self.menu_surface, info_outline, (WIDTH - info.get_width())//2, 170, 2)
            self.menu_surface.blit(info, ((WIDTH - info.get_width())//2, 170))
            
            resume_placed = pg.Rect(0,0,0,0)
            if self.game.in_progress:
                rect = resume.get_rect(right = 1150).x
                self.outline(self.menu_surface, resume_outline, rect, 250)
                resume_placed = self.menu_surface.blit(resume, (rect, 250))                      
            rect = new_game.get_rect(right = 1150).x
            self.outline(self.menu_surface, new_game_outline, rect, 350)
            new_game_placed = self.menu_surface.blit(new_game, (rect, 350))
            
            rect = highscore_label.get_rect(right = 1150).x
            self.outline(self.menu_surface, highscore_label_outline, rect, 450)
            highscore_placed = self.menu_surface.blit(highscore_label, (rect, 450))
            
            rect = options_label.get_rect(right = 1150).x
            self.outline(self.menu_surface, options_outline, rect, 550)
            options_placed = self.menu_surface.blit(options_label, (rect, 550))
            
            rect = exit_game.get_rect(right = 1150).x
            self.outline(self.menu_surface, exit_game_outline, rect, 650)
            exit_game_placed = self.menu_surface.blit(exit_game, (rect, 650))
            
            selected_menu = ['_', resume_placed, new_game_placed, highscore_placed, options_placed, exit_game_placed][self.active_menu]
            if self.active_menu != 1 or (self.active_menu == 1 and self.game.in_progress):
                x, y, width, height = selected_menu
                pg.draw.rect(self.menu_surface, outline_color, (x-5, y, width+10, height), 3)
            
            
            self.game.screen.blit(self.menu_surface, (0,0))
            pg.display.flip()

    def outline(self, screen:pg.Surface, label, x, y, outline_distance = 3):
        screen.blit(label, (x-outline_distance, y-outline_distance))
        screen.blit(label, (x+outline_distance, y-outline_distance))
        screen.blit(label, (x-outline_distance, y+outline_distance))
        screen.blit(label, (x+outline_distance, y+outline_distance))

