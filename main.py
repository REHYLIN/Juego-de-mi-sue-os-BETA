import pygame
import sys
import math

pygame.init()

# Configuración de pantalla
ANCHO, ALTO = 1200, 640
PISO_Y = 480
PISO_Y_POZO = 510
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Foxes Adventure")
clock = pygame.time.Clock()

# Cargar fondos
fondo_tutorial = pygame.image.load("img/FondoDeTutorial.png").convert()
fondo_tutorial = pygame.transform.scale(fondo_tutorial, (ANCHO, ALTO))

fondo_interior = pygame.image.load("img/FondoInterior.png").convert()
fondo_interior = pygame.transform.scale(fondo_interior, (ANCHO, ALTO))

fondo_aldea = pygame.image.load("img/AldeaPixelada.png").convert()
fondo_aldea = pygame.transform.scale(fondo_aldea, (ANCHO, ALTO))

# Variables globales
COLOR_MAGICO = (191, 94, 45)
cambiando_escena = False

# Configuración del área del pozo
POZO_CENTRO_X = 530
POZO_ANCHO = 200
POZO_X_MIN = POZO_CENTRO_X - POZO_ANCHO // 2
POZO_X_MAX = POZO_CENTRO_X + POZO_ANCHO // 2

# Sistema de música
pygame.mixer.music.set_volume(0.5)
musica_actual = None


def cargar_musica(escena):
    global musica_actual
    rutas_musica = {
        "tutorial": "music/606_full_game-kid_0144_preview.mp3",
        "interior": "music/606_full_game-kid_0144_preview.mp3",
        "aldea": "music/AldeaMusic.mp3"  # ⬅️ MÚSICA DE ALDEA CORREGIDA
    }
    
    if escena in rutas_musica and musica_actual != escena:
        try:
            pygame.mixer.music.load(rutas_musica[escena])
            pygame.mixer.music.play(-1)
            musica_actual = escena
            print(f"🎵 Reproduciendo música de: {escena}")
        except pygame.error as e:
            print(f"⚠️ No se pudo cargar la música de '{escena}': {e}")


def cambiar_volumen(incremento):
    volumen_actual = pygame.mixer.music.get_volume()
    nuevo_volumen = max(0.0, min(1.0, volumen_actual + incremento))
    pygame.mixer.music.set_volume(nuevo_volumen)
    print(f"🔊 Volumen: {int(nuevo_volumen * 100)}%")


def pausar_reanudar_musica():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
        print("⏸️ Música pausada")
    else:
        pygame.mixer.music.unpause()
        print("▶️ Música reanudada")


class DialogoBox:
    def __init__(self):
        self.activo = False
        self.texto = ""
        self.nombre = ""
        self.fuente_nombre = pygame.font.Font(None, 28)
        self.fuente_texto = pygame.font.Font(None, 24)
        self.ancho_box = 800
        self.alto_box = 150
        self.x = (ANCHO - self.ancho_box) // 2
        self.y = ALTO - self.alto_box - 20
        self.padding = 20
        self.tiempo_mostrar = 0
        self.alpha = 0
        self.max_alpha = 240
        
    def mostrar(self, nombre, texto):
        self.activo = True
        self.nombre = nombre
        self.texto = texto
        self.tiempo_mostrar = pygame.time.get_ticks()
        self.alpha = 0
        
    def cerrar(self):
        self.activo = False
        self.alpha = 0
        
    def update(self):
        if self.activo and self.alpha < self.max_alpha:
            self.alpha = min(self.alpha + 15, self.max_alpha)
        elif not self.activo and self.alpha > 0:
            self.alpha = max(self.alpha - 15, 0)
    
    def draw(self, pantalla):
        if self.alpha > 0:
            box_surface = pygame.Surface((self.ancho_box, self.alto_box), pygame.SRCALPHA)
            
            pygame.draw.rect(box_surface, (20, 20, 40, self.alpha), 
                           (0, 0, self.ancho_box, self.alto_box), border_radius=10)
            pygame.draw.rect(box_surface, (255, 215, 100, self.alpha), 
                           (0, 0, self.ancho_box, self.alto_box), 3, border_radius=10)
            
            pygame.draw.rect(box_surface, (255, 200, 50, self.alpha), 
                           (0, 0, self.ancho_box, 40), border_radius=10)
            
            texto_nombre = self.fuente_nombre.render(self.nombre, True, (50, 30, 70))
            texto_nombre.set_alpha(self.alpha)
            box_surface.blit(texto_nombre, (self.padding, 8))
            
            y_offset = 50
            max_ancho = self.ancho_box - (self.padding * 2)
            palabras = self.texto.split(' ')
            linea_actual = ""
            
            for palabra in palabras:
                prueba_linea = linea_actual + palabra + " "
                if self.fuente_texto.size(prueba_linea)[0] <= max_ancho:
                    linea_actual = prueba_linea
                else:
                    if linea_actual:
                        texto_linea = self.fuente_texto.render(linea_actual, True, (255, 255, 255))
                        texto_linea.set_alpha(self.alpha)
                        box_surface.blit(texto_linea, (self.padding, y_offset))
                        y_offset += 30
                    linea_actual = palabra + " "
            
            if linea_actual:
                texto_linea = self.fuente_texto.render(linea_actual, True, (255, 255, 255))
                texto_linea.set_alpha(self.alpha)
                box_surface.blit(texto_linea, (self.padding, y_offset))
            
            if self.activo:
                texto_cerrar = self.fuente_texto.render("[W] Cerrar", True, (255, 215, 100))
                texto_cerrar.set_alpha(int(self.alpha * 0.8))
                box_surface.blit(texto_cerrar, 
                               (self.ancho_box - 120, self.alto_box - 35))
            
            pantalla.blit(box_surface, (self.x, self.y))


class HadaCompanera:
    """Hada luminosa minúscula que sigue al jugador"""
    def __init__(self):
        try:
            img_idle_original = pygame.image.load("img/Hada_luminosa_en_la_oscuridad-removebg-preview.png").convert_alpha()
            self.imagen_idle = pygame.transform.smoothscale(img_idle_original, (80, 80))
            
            img_vuelo_original = pygame.image.load("img/Hada_brillante_en_vuelo_pixelado-removebg-preview.png").convert_alpha()
            self.imagen_vuelo = pygame.transform.smoothscale(img_vuelo_original, (80, 80))
            
            print("✨ Hada cargada correctamente")
        except:
            print("⚠️ No se encontraron las imágenes del hada, usando placeholder")
            self.imagen_idle = pygame.Surface((80, 80), pygame.SRCALPHA)
            pygame.draw.circle(self.imagen_idle, (255, 255, 150), (40, 40), 30)
            pygame.draw.circle(self.imagen_idle, (255, 255, 200), (40, 40), 20)
            self.imagen_vuelo = self.imagen_idle.copy()
        
        self.imagen_actual = self.imagen_idle
        self.rect = self.imagen_actual.get_rect()
        
        self.offset_x = -100
        self.offset_y = -120
        self.velocidad = 4.5
        self.esta_volando = False
        
        self.tiempo_flotacion = 0
        self.amplitud_flotacion = 10
        self.velocidad_flotacion = 0.12
        
        self.puede_interactuar = True
        self.primera_interaccion = True
        self.area_interaccion = 90
        
        self.tiempo_brillo = 0
        self.intensidad_brillo = 0
        
        self.fuente = pygame.font.Font(None, 16)
        
        # ⬅️ NUEVA VARIABLE: controla si el hada está activa
        self.activa = False
        
    def activar(self, jugador_pos):
        """Activa el hada en la aldea con animación de aparición"""
        self.activa = True
        self.rect.centerx = jugador_pos[0] + self.offset_x
        self.rect.centery = jugador_pos[1] + self.offset_y
        print("✨ ¡El hada ha aparecido en la aldea!")
        
    def update(self, jugador_pos):
        if not self.activa:
            return
            
        self.tiempo_flotacion += self.velocidad_flotacion
        flotacion_y = math.sin(self.tiempo_flotacion) * self.amplitud_flotacion
        
        self.tiempo_brillo += 0.1
        self.intensidad_brillo = abs(math.sin(self.tiempo_brillo)) * 100 + 155
        
        target_x = jugador_pos[0] + self.offset_x
        target_y = jugador_pos[1] + self.offset_y + flotacion_y
        
        dx = target_x - self.rect.centerx
        dy = target_y - self.rect.centery
        distancia = math.sqrt(dx**2 + dy**2)
        
        self.esta_volando = distancia > 5
        
        if self.esta_volando:
            self.imagen_actual = self.imagen_vuelo
        else:
            self.imagen_actual = self.imagen_idle
        
        if distancia > 3:
            if distancia > 0:
                dx = (dx / distancia) * self.velocidad
                dy = (dy / distancia) * self.velocidad
                
                self.rect.x += dx
                self.rect.y += dy
        else:
            self.rect.centerx = target_x
            self.rect.centery = target_y
    
    def verificar_interaccion(self, jugador_rect):
        if not self.activa:
            return False
        area = self.rect.inflate(self.area_interaccion, self.area_interaccion)
        return area.colliderect(jugador_rect)
    
    def interactuar(self, dialogo_box):
        if self.primera_interaccion:
            dialogo_box.mostrar(
                "✨ Hada Luminosa",
                "¡Hola valiente aventurero! Soy un hada guardiana de estos Lugares.No eres de por aqui verdad?,Lose. Te acompañaré en tu travesía iluminando tu camino y protegiéndote de los peligros ocultos. " \
                "Y recuerda que no todo sera facil asique te ayudare poco a poco en tu aventura."
            )
            self.primera_interaccion = False
        else:
            dialogos = [
                "¿Sientes la magia en el aire?",
                "Esta luz te protegerá de la oscuridad.",
                "Hay secretos antiguos por descubrir...",
                "Mi brillo te guiará siempre, no temas.",
                "¡Este lugar es hermoso! Sigamos explorando.",
                "Puedo sentir energías mágicas cerca.",
                "Juntos somos invencibles, aventurero."
            ]
            import random
            dialogo_box.mostrar("✨ Hada Luminosa", random.choice(dialogos))
    
    def draw(self, pantalla, jugador_cerca=False):
        if not self.activa:
            return
            
        brillo_size = self.rect.width + 40
        brillo_surface = pygame.Surface((brillo_size, brillo_size), pygame.SRCALPHA)
        
        for i in range(3):
            radio = brillo_size // 2 - (i * 8)
            alpha = int((self.intensidad_brillo * 0.2) / (i + 1))
            pygame.draw.circle(brillo_surface, (255, 240, 180, alpha), 
                             (brillo_size // 2, brillo_size // 2), radio)
        
        pygame.draw.circle(brillo_surface, (255, 255, 220, int(self.intensidad_brillo * 0.4)), 
                         (brillo_size // 2, brillo_size // 2), brillo_size // 3)
        
        brillo_pos = (self.rect.centerx - brillo_size // 2, self.rect.centery - brillo_size // 2)
        pantalla.blit(brillo_surface, brillo_pos)
        
        pantalla.blit(self.imagen_actual, self.rect)
        
        if jugador_cerca:
            alpha = int(self.intensidad_brillo)
            
            texto = self.fuente.render("HABLAR [W]", True, (255, 255, 200))
            texto.set_alpha(alpha)
            texto_rect = texto.get_rect(center=(self.rect.centerx, self.rect.top - 18))
            
            fondo = pygame.Surface((texto_rect.width + 8, texto_rect.height + 3), pygame.SRCALPHA)
            pygame.draw.rect(fondo, (50, 30, 70, 200), fondo.get_rect(), border_radius=4)
            pantalla.blit(fondo, (texto_rect.x - 4, texto_rect.y - 1))
            
            pantalla.blit(texto, texto_rect)


class Puerta:
    def __init__(self, x, y, ancho=60, alto=80, tipo="entrada"):
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.rect = pygame.Rect(x - ancho // 2, y - alto, ancho, alto)
        self.tipo = tipo
        self.tiempo = 0
        self.animando = False
        self.pulsacion = 0
        self.ultimo_uso = 0
        self.cooldown = 500
        self.fuente_pequena = pygame.font.Font(None, 18)
        self.fuente_normal = pygame.font.Font(None, 20)
        
    def update(self):
        self.tiempo += 0.15
        self.pulsacion = abs(math.sin(self.tiempo)) * 0.4 + 0.6
        
    def verificar_colision(self, jugador_rect):
        area_interaccion = self.rect.inflate(60, 60)
        return area_interaccion.colliderect(jugador_rect)
    
    def activar(self):
        ahora = pygame.time.get_ticks()
        if ahora - self.ultimo_uso >= self.cooldown:
            self.ultimo_uso = ahora
            self.animando = True
            return True
        return False
    
    def draw_invisible(self, pantalla):
        pass
    
    def draw_indicator(self, pantalla, jugador_cerca=False):
        if jugador_cerca:
            alpha_indicador = int(150 * self.pulsacion) + 80
            
            if self.tipo == "entrada":
                texto_accion = "ENTRAR [E]"
                simbolo = "↑"
            else:
                texto_accion = "SALIR [E]"
                simbolo = "←"
            
            texto_flecha = self.fuente_normal.render(simbolo, True, (255, 255, 255))
            texto_flecha.set_alpha(alpha_indicador)
            flecha_rect = texto_flecha.get_rect(center=(self.x, self.rect.y - 12))
            
            texto_entrar = self.fuente_pequena.render(texto_accion, True, (255, 255, 255))
            texto_entrar.set_alpha(alpha_indicador)
            texto_rect = texto_entrar.get_rect(center=(self.x, self.rect.y - 28))
            
            fondo_texto = pygame.Surface((texto_rect.width + 8, texto_rect.height + 3), pygame.SRCALPHA)
            pygame.draw.rect(fondo_texto, (0, 0, 0, 150), fondo_texto.get_rect(), border_radius=4)
            pantalla.blit(fondo_texto, (texto_rect.x - 4, texto_rect.y - 1))
            
            pantalla.blit(texto_entrar, texto_rect)
            pantalla.blit(texto_flecha, flecha_rect)


class Jugador:
    def __init__(self):
        # Cargar sprite inmóvil (referencia de diseño)
        self.idle = pygame.image.load("img/Fox.png").convert_alpha()
        self.idle = pygame.transform.scale(self.idle, (155, 155))

        # Cargar sprite de salto
        self.salto_img = pygame.image.load("img/salto1.png").convert_alpha()
        self.salto_img = pygame.transform.scale(self.salto_img, (155, 155))  # Mismo tamaño que idle

        # Cargar animaciones de correr con procesamiento mejorado
        self.animaciones_correr = []
        imagenes_correr = ["img/correr1.png", "img/correr2.png", "img/correr3.png", "img/correr4.png",
                           "img/correr5.png"]
        for ruta in imagenes_correr:
            img = pygame.image.load(ruta).convert_alpha()
            # Escalar al mismo tamaño que idle para mantener coherencia
            img = pygame.transform.scale(img, (135, 135))
            
            # Aplicar smoothscale para suavizar las animaciones
            img = pygame.transform.smoothscale(img, (135, 135))
            
            self.animaciones_correr.append(img)

        self.image = self.idle
        self.frame = 0
        self.rect = self.image.get_rect(midbottom=(ANCHO // 2, PISO_Y))
        self.velocidad = 4
        self.vel_y = 0
        self.gravedad = 1
        self.salto = -18
        self.en_suelo = True
        self.mirando_derecha = True
        
        # Animación más lenta para que se vean mejor las piernas
        self.anim_delay = 100  # Aumentado de 80 a 100ms
        self.last_update = pygame.time.get_ticks()
        
        # Efecto de suavizado entre frames
        self.frame_anterior = 0
        self.transicion_frame = 0

    def verificar_color_suelo(self, fondo):
        try:
            pos_x = self.rect.centerx
            pos_y = self.rect.bottom
            
            if 0 <= pos_x < ANCHO and 0 <= pos_y < ALTO:
                color = fondo.get_at((pos_x, pos_y))
                return color
        except:
            pass
        return None

    def esta_en_area_pozo(self, escena):
        if escena == "aldea":
            return POZO_X_MIN <= self.rect.centerx <= POZO_X_MAX
        return False
    
    def calcular_profundidad_pozo(self, escena):
        if not self.esta_en_area_pozo(escena):
            return PISO_Y
        
        pos_relativa = (self.rect.centerx - POZO_X_MIN) / (POZO_X_MAX - POZO_X_MIN)
        profundidad = math.sin(pos_relativa * math.pi)
        diferencia = PISO_Y_POZO - PISO_Y
        piso_calculado = PISO_Y + (diferencia * profundidad)
        
        return int(piso_calculado)

    def update(self, escena_actual):
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

        piso_actual = self.calcular_profundidad_pozo(escena_actual)

        if self.rect.bottom >= piso_actual:
            self.rect.bottom = piso_actual
            self.vel_y = 0
            self.en_suelo = True

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > ANCHO:
            self.rect.right = ANCHO

        ahora = pygame.time.get_ticks()

        # Seleccionar sprite según estado
        if not self.en_suelo:
            self.image = self.salto_img
        elif moviendo:
            if ahora - self.last_update > self.anim_delay:
                self.frame_anterior = self.frame
                self.frame = (self.frame + 1) % len(self.animaciones_correr)
                self.last_update = ahora
                self.transicion_frame = 0
            
            # Incrementar transición para suavizado
            self.transicion_frame = min(self.transicion_frame + 0.2, 1.0)
            self.image = self.animaciones_correr[self.frame]
        else:
            self.frame = 0
            self.image = self.idle

        # Aplicar flip si mira a la izquierda
        if not self.mirando_derecha:
            self.image = pygame.transform.flip(self.image, True, False)

    def draw(self, pantalla):
        pantalla.blit(self.image, self.rect)


# crear objetos del juego
jugador = Jugador()
fondo_actual = fondo_tutorial
hada = HadaCompanera()
dialogo_box = DialogoBox()

puerta_entrada = Puerta(x=947, y=375, ancho=45, alto=65, tipo="entrada")
puerta_salida = Puerta(x=200, y=350, ancho=50, alto=70, tipo="salida")

escena_actual = "tutorial"
historial_escenas = []

cargar_musica(escena_actual)

transicionando = False
direccion_transicion = "entrando"
alpha_transicion = 0
velocidad_transicion = 8

cooldown_borde = 0
tiempo_cooldown_borde = 1000

# Bucle principal
running = True
while running:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            running = False
        
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_w and not transicionando:
                if dialogo_box.activo:
                    dialogo_box.cerrar()
                    continue
                
                # Solo interactuar con el hada si está activa
                if hada.activa:
                    jugador_cerca_hada = hada.verificar_interaccion(jugador.rect)
                    if jugador_cerca_hada:
                        hada.interactuar(dialogo_box)
                        continue
            
            if evento.key == pygame.K_e and not transicionando:
                if escena_actual == "tutorial":
                    jugador_cerca = puerta_entrada.verificar_colision(jugador.rect)
                    if jugador_cerca and puerta_entrada.activar():
                        print("¡Entrando a la casa! 🚪")
                        historial_escenas.append(("tutorial", jugador.rect.midbottom))
                        transicionando = True
                        direccion_transicion = "entrando"
                
                elif escena_actual == "interior":
                    jugador_cerca = puerta_salida.verificar_colision(jugador.rect)
                    if jugador_cerca and puerta_salida.activar():
                        print("¡Saliendo de la casa! 🚪")
                        historial_escenas.append(("interior", jugador.rect.midbottom))
                        transicionando = True
                        direccion_transicion = "saliendo"
            
            if evento.key == pygame.K_r and not transicionando and len(historial_escenas) > 0:
                print("⬅️ Volviendo al mapa anterior...")
                transicionando = True
                direccion_transicion = "retroceder"
            
            if evento.key == pygame.K_m:
                pausar_reanudar_musica()
            
            if evento.key == pygame.K_PLUS or evento.key == pygame.K_EQUALS:
                cambiar_volumen(0.1)
            
            if evento.key == pygame.K_MINUS:
                cambiar_volumen(-0.1)

    jugador.update(escena_actual)
    hada.update(jugador.rect.midbottom)
    dialogo_box.update()
    
    tiempo_actual = pygame.time.get_ticks()
    if escena_actual == "tutorial" and jugador.rect.right >= ANCHO and not transicionando:
        if tiempo_actual - cooldown_borde >= tiempo_cooldown_borde:
            print("¡Llegaste al borde derecho! Cambiando a AldeaPixelada 🏘️")
            historial_escenas.append(("tutorial", jugador.rect.midbottom))
            transicionando = True
            direccion_transicion = "a_aldea"
            cooldown_borde = tiempo_actual
    
    if escena_actual == "tutorial":
        puerta_entrada.update()
    elif escena_actual == "interior":
        puerta_salida.update()

    if transicionando:
        alpha_transicion += velocidad_transicion
        if alpha_transicion >= 255:
            if direccion_transicion == "entrando":
                escena_actual = "interior"
                fondo_actual = fondo_interior
                jugador.rect.midbottom = (250, PISO_Y)
                cargar_musica(escena_actual)
                
            elif direccion_transicion == "saliendo":
                escena_actual = "tutorial"
                fondo_actual = fondo_tutorial
                jugador.rect.midbottom = (900, PISO_Y)
                cargar_musica(escena_actual)
                
            elif direccion_transicion == "a_aldea":
                escena_actual = "aldea"
                fondo_actual = fondo_aldea
                jugador.rect.midbottom = (100, PISO_Y)
                cargar_musica(escena_actual)
                # ACTIVAR EL HADA SOLO AL ENTRAR A LA ALDEA
                if not hada.activa:
                    hada.activar(jugador.rect.midbottom)
                
            elif direccion_transicion == "retroceder":
                escena_anterior, posicion_anterior = historial_escenas.pop()
                escena_actual = escena_anterior
                
                if escena_actual == "tutorial":
                    fondo_actual = fondo_tutorial
                elif escena_actual == "interior":
                    fondo_actual = fondo_interior
                elif escena_actual == "aldea":
                    fondo_actual = fondo_aldea
                
                jugador.rect.midbottom = posicion_anterior
                cargar_musica(escena_actual)
                print(f"✅ Volviste a: {escena_actual}")
            
            transicionando = False
            alpha_transicion = 0

    if escena_actual == "tutorial":
        puerta_entrada.draw_invisible(pantalla)
    elif escena_actual == "interior":
        puerta_salida.draw_invisible(pantalla)
    
    pantalla.blit(fondo_actual, (0, 0))
    
    jugador.draw(pantalla)
    
    # Solo dibujar el hada si está activa
    if hada.activa:
        jugador_cerca_hada = hada.verificar_interaccion(jugador.rect)
        hada.draw(pantalla, jugador_cerca_hada)
    
    if escena_actual == "tutorial":
        jugador_cerca = puerta_entrada.verificar_colision(jugador.rect)
        puerta_entrada.draw_indicator(pantalla, jugador_cerca)
    elif escena_actual == "interior":
        jugador_cerca = puerta_salida.verificar_colision(jugador.rect)
        puerta_salida.draw_indicator(pantalla, jugador_cerca)
    
    dialogo_box.draw(pantalla)
    
    if transicionando or alpha_transicion > 0:
        overlay = pygame.Surface((ANCHO, ALTO))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(alpha_transicion)
        pantalla.blit(overlay, (0, 0))
        
        if not transicionando and alpha_transicion > 0:
            alpha_transicion -= velocidad_transicion
            if alpha_transicion < 0:
                alpha_transicion = 0

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()