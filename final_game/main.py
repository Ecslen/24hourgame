import pygame
import sys
import random
from pygame.locals import *
import sqlite3
from threading import Timer

mainClock = pygame.time.Clock()

# определение переменных для размера окна
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
pygame.mixer.init()
pygame.init()

pygame.display.set_caption('24 HOUR GAME')
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
mm = 0
high_score = 0
font_title = pygame.font.Font('19888.ttf', 72)
font = pygame.font.Font('19888.ttf', 48)

# загрузка всех музыкальных файлов
move_up_sound = pygame.mixer.Sound("Rising_putter.ogg")
move_down_sound = pygame.mixer.Sound("Falling_putter.ogg")
collision_sound = pygame.mixer.Sound("Collision.ogg")
record_score = 0
# установка громкости для звукогового сопровождения
move_up_sound.set_volume(0.3)
move_down_sound.set_volume(0.3)
collision_sound.set_volume(0.9)
lost_ticks = pygame.time.get_ticks()


# Определение класса Player используя("расширяя") pygame.sprite.Sprite
# юзаем картинку для модельки персонажа
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.image.load("jet_x.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()

    # Передвижение игрока основано на нажатиях клавиш
    def update(self, pressed_keys):
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -5)
            move_up_sound.play()
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, 5)
            move_down_sound.play()
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)

        # Закрепляем игрока на экране
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT


# Определение класса Enemy(Враг) используя("расширяя") pygame.sprite.Sprite
# используем картинку для модельки врагов
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        global mm
        mm += 1
        super(Enemy, self).__init__()
        self.surf = pygame.image.load("missile.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        # Стартовая позиция и скорость сгенерирована рандомно
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )
        self.speed = random.randint(5, 20)

    # Передвижение зависит от их скорости
    # убираем врага когда он достиг левого края
    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()


# Определение класса cloud используя pygame.sprite.Sprite
# используем картинку для отображение модельки облаков
class Cloud(pygame.sprite.Sprite):
    def __init__(self):
        super(Cloud, self).__init__()
        self.surf = pygame.image.load("cloud.png").convert()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        # The starting position is randomly generated
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )

    # Передвижени облаков зависит от скорости заданной в переменной
    # убираем облако когда оно достигло левого края
    def update(self):
        self.rect.move_ip(-5, 0)
        if self.rect.right < 0:
            self.kill()


def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, 1, color)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)


click = False


def main_menu():
    global high_score, click
    while True:

        screen.fill('light blue')
        draw_text('24 hours game', font_title, (255, 255, 255), screen, 150, 20)

        mx, my = pygame.mouse.get_pos()

        button_1 = pygame.Rect(300, 150, 200, 50)
        button_2 = pygame.Rect(300, 250, 200, 50)
        if button_1.collidepoint((mx, my)):
            if click:
                game()
        if button_2.collidepoint((mx, my)):
            if click:
                leave()

        pygame.draw.rect(screen, 'blue', button_1)
        pygame.draw.rect(screen, 'blue', button_2)
        # pygame.draw.rect(screen, 'blue', button_3)
        draw_text('Играть', font, (255, 255, 255), screen, 325, 153)
        draw_text('Выход', font, (255, 255, 255), screen, 335, 253)
        # draw_text('On/off', font, (255, 255, 255), screen, 160, 300)
        draw_text(f'Ваш рекорд: {high_score}', font, (255, 255, 255), screen, 400, 500)

        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        pygame.display.update()
        mainClock.tick(60)


def game():
    paused = False
    if __name__ == '__main__':
        global record_score
        running = True
        # инициализация pygame
        pygame.init()

        # установа Clock для фреймрейта
        clock = pygame.time.Clock()

        # Создаем нашего игрока
        player = Player()
        # загрузка и воспроизведение музыки
        pygame.mixer.music.load("frizzyopposite176.mp3")
        pygame.mixer.music.play(loops=-1)
        # создаем группы спрайтов для отображения всех спрайтов
        # - у врагов присутствует коллизия и обновление позиции
        # - облака используются для обновления координат(позиций)
        # - все спрайты используются для рендера
        enemies = pygame.sprite.Group()
        clouds = pygame.sprite.Group()
        all_sprites = pygame.sprite.Group()
        all_sprites.add(player)
        # сохдаем кастомные события для создания врагов и облаков
        ADD_ENEMY = pygame.USEREVENT + 1
        pygame.time.set_timer(ADD_ENEMY, 250)
        ADD_CLOUD = pygame.USEREVENT + 2
        pygame.time.set_timer(ADD_CLOUD, 1000)

        # СМЕНА УРОВНЕЙ СЛОЖНОСТИ
        def lvl1():
            pygame.time.set_timer(ADD_ENEMY, 150)
            pygame.time.set_timer(ADD_CLOUD, 600)
            t1 = Timer(60.0, lvl2)
            t1.start()

        def lvl2():
            pygame.time.set_timer(ADD_ENEMY, 120)
            pygame.time.set_timer(ADD_CLOUD, 450)
            t2 = Timer(60.0, lvl3)
            t2.start()

        def lvl3():
            pygame.time.set_timer(ADD_ENEMY, 100)
            pygame.time.set_timer(ADD_CLOUD, 350)
            t3 = Timer(60.0, lvl4)
            t3.start()

        def lvl4():
            pygame.time.set_timer(ADD_ENEMY, 80)
            pygame.time.set_timer(ADD_CLOUD, 250)
            t4 = Timer(60.0, lvl5)
            t4.start()

        def lvl5():
            pygame.time.set_timer(ADD_ENEMY, 60)
            pygame.time.set_timer(ADD_CLOUD, 100)
            t5 = Timer(60.0, last_lvl)
            t5.start()

        def last_lvl():
            pygame.time.set_timer(ADD_CLOUD, 10)
            pygame.time.set_timer(ADD_ENEMY, 40)

        t = Timer(60.0, lvl1)
        t.start()

        # переменная для работы основного цикла игры
        # основной цикл игры
        while running:
            # смотрим на каждое событие в очереди
            for event in pygame.event.get():
                # нажал ли юзер на клавишу?
                if event.type == KEYDOWN:
                    # Был ли это "Escape"(Esc) клавиша? Если да, останавливаем цикл
                    if event.key == K_ESCAPE:
                        con = sqlite3.connect('NEW_BASE.db')
                        cur = con.cursor()
                        cur.execute("""UPDATE RECORDS SET RECORD = ? WHERE id = 1""", [record_score])
                        con.commit()

                        # проверка на паузу
                        if paused:
                            paused = False

                            # убираем музыку с паузы
                            pygame.mixer.music.unpause()
                        else:
                            paused = True
                            # ставив музыку на паузу
                            pygame.mixer.music.pause()

                # Закрыл ли юзер окно игры? если да, останавливаем цикл игры
                elif event.type == QUIT:
                    running = False

                # Следует ли нам добавить еще одного врага?
                elif event.type == ADD_ENEMY:
                    if not paused:
                        # Создаем врага и добавляем его в группу к спрайтам
                        new_enemy = Enemy()
                        enemies.add(new_enemy)
                        all_sprites.add(new_enemy)

                # Следует ли нам добавить новое облако?
                elif event.type == ADD_CLOUD:
                    # Создаем облако и добавляем его в группу к спрайтам
                    new_cloud = Cloud()
                    clouds.add(new_cloud)
                    all_sprites.add(new_cloud)
            # (Нажмите на набор клавиш и проверьте ввод данных пользователем???)

            if not paused:

                pressed_keys = pygame.key.get_pressed()
                player.update(pressed_keys)

                # Update the position of our enemies and clouds(Обновление координат врагов, облаков)
                enemies.update()
                clouds.update()

                # Заполнение бг чистым небом
                screen.fill((135, 206, 250))

                # рисовка всех спрайтов
                for entity in all_sprites:
                    screen.blit(entity.surf, entity.rect)
                draw_text(f'Score:{mm}', font, (255, 255, 255), screen,
                          80,
                          20)

                # проверка на столкновения с игроком
                if pygame.sprite.spritecollideany(player, enemies):
                    # если да, убираем игрока
                    bd_connect()
                    player.kill()

                    # остановка всех звуков
                    move_up_sound.stop()
                    move_down_sound.stop()
                    collision_sound.play()

                    # record_score = pygame.time.get_ticks() // 100
                    # print(record_score)
                    # отсановка игрового цикла
                    running = False
                    pygame.mixer.music.stop()
                    pygame.mixer.quit()
                    lose()

                # обновление {всего} на экране
                pygame.display.flip()

                # фпс = 30
                clock.tick(30)

        # (остановка звука в случае закрытия игры)
        pygame.mixer.music.stop()
        pygame.mixer.quit()


def leave():
    con = sqlite3.connect('NEW_BASE.db')
    cur = con.cursor()
    cur.execute("""UPDATE RECORDS SET RECORD = 0 WHERE id = 1""")
    con.commit()
    pygame.quit()


# подключение бд
def bd_connect():
    global high_score
    con = sqlite3.connect('NEW_BASE.db')
    cur = con.cursor()
    bd_record = cur.execute("""SELECT RECORD FROM RECORDS ORDER BY RECORD DESC""").fetchall()
    high_score = bd_record[0][0]


def lose():
    global mm
    running = True
    click_lose = False
    con = sqlite3.connect('NEW_BASE.db')
    cur = con.cursor()
    cur.execute("""INSERT INTO RECORDS(RECORD) VALUES(?) """, [mm])
    con.commit()
    mm = 0
    while running:
        screen.fill('light blue')
        mx, my = pygame.mouse.get_pos()
        button_menu = pygame.Rect(300, 300, 180, 50)
        pygame.draw.rect(screen, 'blue', button_menu)
        if button_menu.collidepoint((mx, my)):
            if click_lose:
                main_menu()
        pygame.draw.rect(screen, 'blue', button_menu)
        draw_text('Меню', font, (255, 255, 255), screen, 340, 300)
        draw_text('LOSE', font_title, (255, 255, 255), screen, 340, 20)

        click_lose = False

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click_lose = True

        pygame.display.update()
        mainClock.tick(60)


bd_connect()
main_menu()
