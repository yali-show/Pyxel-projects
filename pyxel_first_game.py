import pyxel


class Block:  # blocks and barier class
    def __init__(self, x, y, texture=(24, 8)):
        self.x = x
        self.y = y
        self.wh = 8
        self.texture = texture
        self.top_positions = {(x, y)
                              for x in range(self.x, self.x + 8)
                              for y in range(self.y, self.y + 1)}

        self.bottom_positions = {(x, y)
                                 for x in range(self.x, self.x + 8)
                                 for y in range(self.y + 7, self.y + 9)}
        self.sides_positions = {(x, y)
                                for x in range(self.x, self.x + 2)
                                for y in range(self.y, self.y + 8)}
        self.sides_positions.update({(x, y)
                                     for x in range(self.x + 7, self.x + 9)
                                     for y in range(self.y, self.y + 8)
                                     })
        self.inside_pos = {(x, y)
                           for x in range(self.x + 1, self.x + 7)
                           for y in range(self.y + 1, self.y + 7)}

    def draw(self):
        pyxel.blt(self.x, self.y, 0, self.texture[0], self.texture[1], 8, 8)


class Constructor:  # aggregator of blocks objects
    def __init__(self):
        self.blocks = self.__create_platform()
        self.positions = self.__col_positions()
        self.inside_positions = self.__inside_pos()

    def __create_platform(self):
        """
        fabric method of blocks objects
        :return: set of block objects
        """

        blocks = set()

        for i in range(25):
            blocks.add(Block(i * 8, 112))

        # blocks.add(Block(10 * 9, 104))

        for i in range(10):
            blocks.add(Block(i * 8, 92))

        # for i in range(13):
        #     blocks.add(Block(i * 8 + 100, 82))

        return blocks

    def __col_positions(self):
        """
            :return: tuple of 3 set obj and dict
        """

        result = (set(), set(), set(), {})
        for block in self.blocks:
            result[0].update(block.top_positions)
            result[1].update(block.sides_positions)
            result[2].update(block.bottom_positions)
            y = block.y
            if y in result[3]:
                result[3][y].append(block.x)
            else:
                result[3][y] = [block.x]
        return result

    def __inside_pos(self):
        """
        :return: set of positions inside blocks
        """
        result = set()
        for block in self.blocks:
            result.update(block.inside_pos)
        return result

    def draw(self):
        for block in self.blocks:
            block.draw()


class ToiletEnemy:  # default toilet enemy class
    def __init__(self, x, y, blocks_pos, hero, dir_rigth=True):
        self.x = x
        self.y = y
        self.positions = blocks_pos
        self.hero_pos = hero
        self.animation = ((32, 0), (8, 0), (8, 0), (16, 0), (32, 0))
        self.flashed_animation = ((32, 0), (24, 0), (24, 0), (24, 0), (32, 0))
        self.deth_animation = ((24, 0), (24, 0), (24, 0), (32, 8), (24, 0))
        self.w = 8
        self.h = 8
        self.animation_count = 0
        self.flashed_timer = 30
        self.deth_timer = 80
        self.targeted = False
        self.alive = True
        self.flashed = False
        self.damaged = False
        self.all_positions = {(x, y)
                              for x in range(self.x, self.x + 8)
                              for y in range(self.y - 1, self.y + 9)}
        self.all_positions_flashed = self.all_positions
        self.direction_rigth = dir_rigth

    def __animate(self):
        if self.animation_count >= 20:
            self.animation_count = 0

        if self.alive:
            self.animation_count += 1
            if not self.flashed:
                pyxel.blt(self.x, self.y, 0,
                          self.animation[self.animation_count // 5][0],
                          self.animation[self.animation_count // 5][1],
                          self.w, self.h, 0)
                self.__move()
            else:
                self.targeted = False
                pyxel.blt(self.x, self.y, 0,
                          self.flashed_animation[self.animation_count // 5][0],
                          self.flashed_animation[self.animation_count // 5][1],
                          self.w, self.h, 0)
                self.__update_pos()
        else:
            self.__update_pos()
            if self.deth_timer > 0:
                pyxel.blt(self.x, self.y, 0,
                          24,
                          0,
                          self.w, self.h, 0)
            self.deth_timer -= 1

    def __update_pos(self):
        if not self.flashed and self.alive:
            self.all_positions = {(x, y)
                                  for x in range(self.x, self.x + 8)
                                  for y in range(self.y, self.y + 9)}
            self.all_positions_flashed = self.all_positions
            self.__attack()
        else:
            self.all_positions = set()

        self.__flashed_update()

    def __flashed_update(self):
        if self.flashed:
            if self.flashed_timer > 0:
                self.flashed_timer -= 0.5
            else:
                self.flashed = False
                self.flashed_timer = 30

    def __move(self):
        if self.direction_rigth:
            bottom_side_pos = (self.x + 8, self.y + 8)
            side_pos = (self.x + 8, self.y + 4)
            if bottom_side_pos in self.positions[0]\
                    and side_pos not in self.positions[1]:
                if self.targeted:
                    self.x += 2
                else:
                    self.x += 1
            else:
                self.direction_rigth = False
                self.w = -8
                self.targeted = False
        else:
            bottom_side_pos = (self.x, self.y + 8)
            side_pos = (self.x, self.y + 4)
            if bottom_side_pos in self.positions[0]\
                    and side_pos not in self.positions[1]:
                if self.targeted:
                    self.x -= 2
                else:
                    self.x -= 1
            else:
                self.direction_rigth = True
                self.w = 8
                self.targeted = False
        self.__update_pos()

    def __attack(self):  # attack user if was seen
        if self.direction_rigth is False:
            if self.x > self.hero_pos[0] and self.y == self.hero_pos[1]:
                can_target = True
                if self.y in self.positions[3]:
                    for x in self.positions[3][self.y]:
                        if self.x - self.hero_pos[0] > self.x - x:
                            can_target = False

                if can_target:
                    self.targeted = True

        elif self.direction_rigth:
            if self.x < self.hero_pos[0] and self.y == self.hero_pos[1]:
                can_target = True
                if self.y in self.positions[3]:
                    for x in self.positions[3][self.y]:
                        if self.hero_pos[0] - self.x < x - self.x:
                            can_target = False

                if can_target:
                    self.targeted = True

    def get_damaged(self, hero_dir, punch_pos):
        if self.alive:
            if not self.direction_rigth and hero_dir:
                if self.all_positions_flashed.intersection(punch_pos):
                    self.alive = False
                    pyxel.play(2, 6)

            elif not hero_dir and self.direction_rigth:
                if self.all_positions_flashed.intersection(punch_pos):
                    self.alive = False
                    pyxel.play(2, 6)

    def draw(self):
        self.__animate()


class EnemiesControl:  # aggregator of toilets/enemies
    def __init__(self, blocks, hero_pos, flash_pos, hero_direction=True):
        self.blocks = blocks
        self.hero = hero_pos
        self.light_pos = flash_pos
        self.punch_pos = set()
        self.hero_dir_right = hero_direction
        self.toilets = self.__setup_enemies()
        self.positions()

    def __setup_enemies(self):
        # toilet1 = ToiletEnemy(150, 74, self.blocks, self.hero)
        toilet2 = ToiletEnemy(150, 104, self.blocks, self.hero)
        # toilet3 = ToiletEnemy(20, 84, self.blocks, self.hero)
        result = (toilet2, )
        return result

    def draw(self):
        for toilet in self.toilets:
            toilet.draw()
            self.positions()

    def punch_control(self, punch_pos):
        if len(punch_pos):
            for toilet in self.toilets:
                toilet.get_damaged(self.hero_dir_right, punch_pos)

    @staticmethod
    def __flash_control(toilet, light_positions, right_direction):
        if len(light_positions):
            if light_positions[1] == toilet.y:
                if right_direction and not toilet.direction_rigth:
                    if light_positions[0] < toilet.x:
                        if toilet.y in toilet.positions[3]:
                            for x in toilet.positions[3][toilet.y]:
                                if light_positions[0] > x:
                                    toilet.flashed = True
                        else:
                            toilet.flashed = True

                elif not right_direction and toilet.direction_rigth:
                    if light_positions[0] > toilet.x:
                        if toilet.y in toilet.positions[3]:
                            for x in toilet.positions[3][toilet.y]:
                                if light_positions[0] > x:
                                    toilet.flashed = True
                        else:
                            toilet.flashed = True

    def positions(self):
        """
        update positions
        :return self.all_positions = set of all block`s positions:
        """
        result = set()

        light_positions = self.light_pos[0]
        if len(light_positions):
            right_direction = True if self.light_pos[1][0] > 0 else False
        else:
            right_direction = None

        for toilet in self.toilets:
            result.update(toilet.all_positions)

            self.__flash_control(toilet, light_positions, right_direction)

        self.all_positions = result


class Cameraman:  # user class
    def __init__(self, x, y, blocks_pos, inside_blocks_pos, enemies):
        # tuple of sets of coordinates of all blocks
        self.blocks_positions = blocks_pos
        self.inside_blocks_pos = inside_blocks_pos
        self.enemies = enemies

        # data of character
        self.x = x
        self.y = y
        self.health = 3
        self.onground = True
        self.in_jump = False
        self.in_move = False
        self.punch = False
        self.can_move = True
        self.camera_flash = True
        self.immortal = False
        self.alive = True
        self.immortal_timer = 50
        self.flash_timer = 150
        self.punch_timer = 0
        self.jump_count = 20
        self.animation_count = 0
        self.animation_immortal = ((40, 0), (32, 8), (40, 0), (40, 0), (40, 0))
        self.animation_punch = (0, 8)
        self.animation_stand = ((40, 0), (40, 8), (40, 8), (40, 8), (40, 8))
        self.animation_move = ((48, 8), (56, 8), (56, 8), (48, 8), (56, 8))
        self.light_pos = ([], [])
        # data of sprite
        self.w = 8
        self.h = 8

        # all coordinates of cameramen (bottom pos)

        # all coordinates of cameramen (right side pos)
        # all coordinates of cameramen (left side pos)
        self.update_positions()

    def __animate(self):
        # animations control

        if self.immortal:
            pyxel.blt(self.x, self.y, 0,
                      self.animation_immortal[self.animation_count // 5][0],
                      self.animation_immortal[self.animation_count // 5][1],
                      self.w, self.h, 0)
        else:
            if self.punch:
                side = self.w / 8

                pyxel.blt(self.x - 8 if side != 1 else self.x,
                          self.y, 0,
                          self.animation_punch[0],
                          self.animation_punch[1],
                          side * 16, self.h, 0)

            elif self.in_move:
                pyxel.blt(self.x, self.y, 0,
                          self.animation_move[self.animation_count // 5][0],
                          self.animation_move[self.animation_count // 5][1],
                          self.w, self.h, 0)

            else:
                pyxel.blt(self.x, self.y, 0,
                          self.animation_stand[self.animation_count // 5][0],
                          self.animation_stand[self.animation_count // 5][1],
                          self.w, self.h, 0)

        self.animation_count += 1
        if self.animation_count >= 20:
            self.animation_count = 0

    def __draw_extra_obj(self):  # draw battery and hearts
        count = 0
        for heart in range(self.health):

            pyxel.blt(2 + count * 10, 2, 0, 48, 0, 8, 8, 0)
            count += 1

        if self.camera_flash:
            pyxel.blt(2, 11, 0, 56, 0, 8, 8, 0)

        else:
            pyxel.blt(2, 11, 0, 64, 0, 8, 8, 0)

        if not self.camera_flash:
            self.__flash()

    def __flash(self):  # flashlight setups

        if self.onground:
            if self.camera_flash:
                self.camera_flash = False
                pyxel.play(2, 3)
                self.light_pos = ((self.x, self.y), (self.w, ))

        if not self.camera_flash:
            if self.flash_timer != 0:
                self.flash_timer -= 0.5
                if self.flash_timer < 100:
                    self.light_pos = ((), ())
            else:
                self.camera_flash = True
                self.flash_timer = 150

    def __events_control(self):  # control of controls (buttons)
        if self.alive:
            self.__falling_check()
            self.__get_damaged()

            if not self.bottom_positions.intersection(self.blocks_positions[0]):
                self.onground = False
                if self.bottom_positions.intersection(self.inside_blocks_pos):
                    if self.w > 0:
                        self.x -= 2
                    else:
                        self.x += 2
                    self.y -= 5

            else:
                self.onground = True
                self.jump_count = 20
                if not self.in_jump:
                    self.y = list(self.bottom_positions.intersection(
                        self.blocks_positions[0]))[0][1] - 8
                self.in_jump = False

            if self.can_move:
                if pyxel.btn(pyxel.KEY_RIGHT):
                    if self.x < 192:
                        if not self.sides_positions_right.intersection(self.blocks_positions[1]):
                            self.in_move = True
                            self.w = 8
                            if self.onground:
                                self.x += 1
                                self.update_positions()

                            else:
                                if self.in_jump:
                                    if self.x + 2 >= 184:
                                        self.x += 1
                                    else:
                                        self.x += 2
                                else:
                                    self.x += 1

                            self.update_positions()

                        else:
                            self.x = list(self.sides_positions_right.intersection(self.blocks_positions[1]))[0][0] - 8
                            self.update_positions()

                elif pyxel.btn(pyxel.KEY_LEFT):
                    if self.x > 0:
                        if not self.sides_positions_left.intersection(self.blocks_positions[1]):
                            self.in_move = True
                            self.w = -8
                            if self.onground:
                                self.x -= 1

                            else:
                                if self.in_jump:
                                    if self.x - 2 > 0:
                                        self.x -= 2
                                    else:
                                        self.x -= 1

                                else:
                                    self.x -= 1

                            self.update_positions()

                        else:

                            self.x = list(self.sides_positions_left.intersection(self.blocks_positions[1]))[0][0]

                else:
                    self.in_move = False

            if pyxel.btn(pyxel.KEY_UP):

                if self.onground:
                    pyxel.play(3, 5)
                    self.onground = False
                    self.in_jump = True

            # if pyxel.btn(pyxel.KEY_DOWN):
            #     self.y = 0
            #     self.x = 0
            #     self.update_positions()

            if pyxel.btn(pyxel.KEY_SPACE):
                if not self.punch:
                    pyxel.play(3, 7)
                    self.punch = True

                if self.punch_timer <= 0:
                    self.can_move = False
                    self.punch_timer = 50
                else:
                    self.punch_timer -= 1.5

            else:
                if self.punch_timer > 0:
                    self.punch_timer -= 1.5

                self.punch = False
                self.can_move = True

            if pyxel.btn(pyxel.KEY_X):
                if self.camera_flash:

                    self.__flash()

    def __falling_check(self):  # falling control
        if not self.onground:
            self.jump_count -= 0.9
            if self.in_jump:
                if self.jump_count >= 10:
                    if not self.top_positions.intersection(self.blocks_positions[2]):
                        self.y -= 2

                    else:
                        self.jump_count = 9
                        self.in_jump = False

                    self.update_positions()

            if self.jump_count <= 10:
                self.y += 2
                self.update_positions()

    def __get_damaged(self):  # check if user was damaged
        if not self.immortal:
            if self.bottom_positions.intersection(self.enemies.all_positions):

                self.health -= 1
                if self.health == 0:
                    self.alive = False
                    pyxel.stop()
                    pyxel.play(2, 8)

                else:
                    pyxel.play(2, 4)
                if self.onground:
                    self.x -= self.w // 8 * 10
                    self.y -= 10
                else:
                    self.x -= self.w // 8 * 20
                    self.y -= 10

                self.immortal = True
                self.immortal_timer = 50

                # print(self.health)
        else:
            if self.immortal_timer > 0:
                self.immortal_timer -= 0.5

            else:
                self.immortal_timer = 50
                self.immortal = False

    def get_punch_positions(self):
        if self.punch:
            if self.w > 0:
                result = {(x, self.y + 4) for x in range(self.x + 8, self.x + 16)}
            else:
                result = {(x, self.y + 4) for x in range(self.x - 8, self.x)}
        else:
            result = set()

        return result

    def update_positions(self):
        self.bottom_positions = {(x, self.y + 8)
                                 for x in range(self.x, self.x + 8)}

        self.top_positions = {(x, self.y) for x in range(self.x, self.x + 8)}

        self.sides_positions_left = {(self.x, y)
                                     for y in range(self.y - 1, self.y + 8)}

        self.sides_positions_right = {(self.x + 8, y)
                                      for y in range(self.y - 1, self.y + 8)}

    def draw(self):

        # change coordinates (move obj)
        self.__events_control()

        # draw obj with new coordinates

        self.__animate()
        # hearts sprites draw
        self.__draw_extra_obj()


class Button:  # buttons class (with mouse)
    def __init__(self, x, y, w, h, animation, animation_targeted, action):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.x_anim = animation[0]
        self.y_anim = animation[1]
        self.x_anim_targ = animation_targeted[0]
        self.y_anim_targ = animation_targeted[1]
        self.targeted = False
        self.function = action

    def draw(self):
        if not self.targeted:
            pyxel.blt(self.x, self.y, 0, self.x_anim, self.y_anim, self.w, self.h, 0)
        else:
            pyxel.blt(self.x, self.y, 0, self.x_anim_targ, self.y_anim_targ, self.w,
                      self.h, 0)

    # def is_clicked(self, x, y):  # check if was clicked
    #     if self.x <= x <= self.x + self.w and self.y <= y <= self.y + self.h:
    #         self.function()

    def event(self):
        self.function()


class Level:  # level class
    def __init__(self, hero: Cameraman, hero_pos: tuple,
                 enemies_controll: EnemiesControl,
                 contructor: Constructor, background, musik):
        self.blocks = contructor
        self.enemies = enemies_controll
        self.hero = hero
        self.hero.x, self.hero.y = hero_pos

    def draw(self):
        ...


class App:  # game class
    def __init__(self):
        pyxel.init(200, 120, title='Skibidi battle', fps=120)
        # pyxel.mouse(True)
        pyxel.load('assets/resources.pyxres')
        # pyxel.playm(0, loop=True)
        self.blocks_controler = Constructor()
        self.hero_positions = [8, 104]
        self.flash_pos = [[], [None, ]]  # ((x, y), (direction))
        self.punch_pos = set()

        self.enemies = EnemiesControl(self.blocks_controler.positions,
                                       self.hero_positions, self.flash_pos)

        self.hero = Cameraman(8, 84, self.blocks_controler.positions,
                              self.blocks_controler.inside_positions,
                              self.enemies)
        self.start_menu = True
        self.in_game = False
        self.in_pause = False
        self.dead = False
        self.music = True

        self.counter_choose = -1

        self.start_button = Button(67, 30, 67, 16, (0, 32), (0, 48),  self.play)

        # TODO add continue button in pause
        # TODO change action argument to self.back_to_main
        self.back_to_main_menu_button = Button(67, 30, 67, 16, (0, 128), (0, 144),
                                               self.play)
        self.exit_button = Button(67, 48, 67, 16, (0, 64), (0, 80), self.exit)
        self.reset_button = Button(67, 66, 67, 16, (0, 96), (0, 112), self.reset)
        self.start_buttons = (self.start_button, self.exit_button)
        self.in_pause_buttons = (self.back_to_main_menu_button, self.exit_button, self.reset_button)

        pyxel.run(self.update, self.draw)

    def button_update(self, buttons):
        for button in buttons:
            button.targeted = False

        buttons[self.counter_choose].targeted = True

    def update(self):
        if self.in_pause or self.start_menu:
            if pyxel.btnp(pyxel.KEY_RETURN):
                if self.in_pause:
                    self.in_pause_buttons[self.counter_choose].event()

                else:
                    self.start_buttons[self.counter_choose].event()
                self.counter_choose = -1

            if pyxel.btnp(pyxel.KEY_UP):
                pyxel.play(2, 9)
                if self.start_menu:

                    if len(self.start_buttons) * -1 > self.counter_choose - 1:
                        self.counter_choose = 1
                    else:
                        self.counter_choose -= 1

                    self.button_update(self.start_buttons)
                else:
                    if len(self.in_pause_buttons) * -1 > self.counter_choose - 1:
                        self.counter_choose = 1
                    else:
                        self.counter_choose -= 1

                    self.button_update(self.in_pause_buttons)

            elif pyxel.btnp(pyxel.KEY_DOWN):
                pyxel.play(2, 9)
                if self.start_menu:
                    if len(self.start_buttons) - 1 < self.counter_choose + 1:
                        self.counter_choose = 0
                    else:
                        self.counter_choose += 1
                    self.button_update(self.start_buttons)
                else:
                    if len(self.in_pause_buttons) - 1 < self.counter_choose + 1:
                        self.counter_choose = 0
                    else:
                        self.counter_choose += 1
                    self.button_update(self.in_pause_buttons)

        # if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
        #
        #     mx = pyxel.mouse_x
        #     my = pyxel.mouse_y
        #
        #     if self.start_menu:
        #         self.start_button.is_clicked(mx, my)
        #
        #     elif self.in_pause:
        #         self.start_button.is_clicked(mx, my)
        #         self.reset_button.is_clicked(mx, my)

        if pyxel.btnp(pyxel.KEY_M):
            if self.music:
                self.music = False
                pyxel.stop()
            else:
                self.music = True
                pyxel.playm(0, loop=True)

        if pyxel.btnp(pyxel.KEY_N):

            if not self.start_menu:
                if self.in_pause:
                    self.in_pause = False
                    self.in_game = True

                else:
                    self.in_game = False
                    self.in_pause = True

        self.hero_positions[0] = self.hero.x
        self.hero_positions[1] = self.hero.y
        self.flash_pos[0] = self.hero.light_pos[0]
        self.flash_pos[1] = self.hero.light_pos[1]
        self.__enemies_updates()

    def __enemies_updates(self):
        self.enemies.hero_dir_right = False if self.hero.w > 0 else True
        self.enemies.punch_control(self.hero.get_punch_positions())
        self.enemies.positions()

    def exit(self):
        ...

    def back_to_menu(self):
        ...

    def play(self):
        self.in_game = True
        self.in_pause = False
        self.start_menu = False

    def reset(self):
        print(111)

    def draw_in_game(self):
        self.hero.draw()
        self.blocks_controler.draw()
        self.enemies.draw()

    def draw_pause(self):
        self.back_to_main_menu_button.draw()
        self.exit_button.draw()
        self.reset_button.draw()

    def draw_start_menu(self):
        self.start_button.draw()
        self.exit_button.draw()

    def draw(self):

        if self.in_game:
            pyxel.bltm(0, 0, 0, 0, 0, 200, 120)
            self.draw_in_game()

        elif self.start_menu:
            pyxel.bltm(0, 0, 1, 0, 0, 200, 120)
            self.draw_start_menu()

        elif self.in_pause:
            pyxel.bltm(0, 0, 1, 0, 0, 200, 120)
            self.draw_pause()


App()
