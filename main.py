import pygame, sys

pygame.init()

ANCHO, ALTO = 800, 600
PISO_Y = 480

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("foxes adventure")

clock = pygame.time.Clock()

fondo = pygame.image.load("img/FondoDeTutorial.png").convert()
fondo = pygame.transform.scale(fondo, (ANCHO, ALTO))


class Jugador:
    def __init__(self):
        self.idle = pygame.image.load("img/Fox.png").convert_alpha()
        self.idle = pygame.transform.scale(self.idle, (155, 155))

        self.salto_img = pygame.image.load("img/salto1.png").convert_alpha()
        self.salto_img = pygame.transform.scale(self.salto_img, (135, 135))

        self.animaciones_correr = []
        for i in range(1, 4):
            img = pygame.image.load("img/correr2.png").convert_alpha()
            img = pygame.transform.scale(img, (135, 135))
            self.animaciones_correr.append(img)

            img = pygame.image.load("img/correr3.png").convert_alpha()
            img = pygame.transform.scale(img, (135, 135))
            self.animaciones_correr.append(img)

            img = pygame.image.load("img/correr4.png").convert_alpha()
            img = pygame.transform.scale(img, (135, 135))
            self.animaciones_correr.append(img)

            img = pygame.image.load("img/correr5.png").convert_alpha()
            img = pygame.transform.scale(img, (135, 135))
            self.animaciones_correr.append(img)

        self.image = self.idle
        self.frame = 0

        self.rect = self.image.get_rect(midbottom=(ANCHO // 2, PISO_Y))

        self.velocidad = 5
        self.vel_y = 0
        self.gravedad = 1
        self.salto = -18
        self.en_suelo = True
        self.mirando_derecha = True

        self.anim_delay = 80
        self.last_update = pygame.time.get_ticks()

    def update(self):
        keys = pygame.key.get_pressed()
        moviendo = False

        if keys[pygame.K_LEFT]:
            self.rect.x -= self.velocidad
            self.mirando_derecha = False
            moviendo = True

        if keys[pygame.K_RIGHT]:
            self.rect.x += self.velocidad
            self.mirando_derecha = True
            moviendo = True

        if keys[pygame.K_UP] and self.en_suelo:
            self.vel_y = self.salto
            self.en_suelo = False

        self.vel_y += self.gravedad
        self.rect.y += self.vel_y

        if self.rect.bottom >= PISO_Y:
            self.rect.bottom = PISO_Y
            self.vel_y = 0
            self.en_suelo = True

        ahora = pygame.time.get_ticks()

        if not self.en_suelo:
            self.image = self.salto_img

        elif moviendo:
            if ahora - self.last_update > self.anim_delay:
                self.frame = (self.frame + 1) % len(self.animaciones_correr)
                self.last_update = ahora
            self.image = self.animaciones_correr[self.frame]

        else:
            self.frame = 0
            self.image = self.idle

        if not self.mirando_derecha:
            self.image = pygame.transform.flip(self.image, True, False)

    def draw(self, pantalla):
        pantalla.blit(self.image, self.rect)


jugador = Jugador()

while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    jugador.update()

    pantalla.blit(fondo, (0, 0))
    jugador.draw(pantalla)

    pygame.display.flip()
    clock.tick(60)
