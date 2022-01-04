import pygame


class Sprite(pygame.sprite.Sprite):
    def __init__(self, target):
        pygame.sprite.Sprite.__init__(self)
        self.target_surface = target
        self.image = None
        self.master_image = None
        self.rect = None
        self.top_left = 0, 0
        self.frame = 0
        self.old_frame = -1
        self.frame_width = 1
        self.frame_height = 1
        self.first_frame = 0
        self.last_frame = 0
        self.columns = 1
        self.last_time = 0
        self.pos_x = 0
        self.pos_y = 0

    def load(self, filename, pos_x, pos_y, width, height, columns):
        self.master_image = pygame.image.load(filename).convert_alpha()
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.frame_width = width
        self.frame_height = height
        self.rect = pos_x, pos_y, width, height
        self.columns = columns
        rect = self.master_image.get_rect()
        self.last_frame = (rect.width // width) * (rect.height // height) - 1

    def update(self, current_time, rate=60):
        if current_time > self.last_time + rate:
            self.frame += 1
            if self.frame > self.last_frame:
                self.frame = self.first_frame
            self.last_time = current_time

        if self.frame != self.old_frame:
            frame_x = (self.frame % self.columns) * self.frame_width
            frame_y = (self.frame // self.columns) * self.frame_height
            rect = (frame_x, frame_y, self.frame_width, self.frame_height)
            self.image = self.master_image.subsurface(rect)
            self.old_frame = self.frame


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600), 0, 32)
    pygame.display.set_caption("deamon")
    font = pygame.font.Font(None, 18)
    frame_rate = pygame.time.Clock()

    cat = Sprite(screen)
    cat.load("assets/img/demon.png", 300, 300, 100, 100, 4)
    group = pygame.sprite.Group()
    group.add(cat)

    while True:
        frame_rate.tick(60)
        ticks = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        key = pygame.key.get_pressed()
        if key[pygame.K_ESCAPE]:
            exit()

        screen.fill((0, 0, 100))

        group.update(ticks)
        group.draw(screen)
        pygame.display.update()


if __name__ == "__main__":
    main()
