import pygame
import sys
import random

#Inisialisasi
pygame.init()
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fungi Fight")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)

#Constants
PHASE_ORDER = ["morning", "afternoon", "evening", "chaos"]  
PHASES = {
    "morning": {"time": 0, "bg": "daysky.png", "drop": ("kumbang", 3)},
    "afternoon": {"time": 10000, "bg": "redsky.png", "drop": ("pinus", 5)},
    "evening": {"time": 20000, "bg": "nightsky.png", "drop": ("rock", 7)},
    "chaos": {"time": 30000, "bg": "nightsky.png", "drops": [
        ("kumbang", 3), ("pinus", 5), ("rock", (6, 9))
    ]}
}

#Assets
bg_dict = {key: pygame.transform.scale(pygame.image.load(f"assets/{val['bg']}"), (WIDTH, HEIGHT))
           for key, val in PHASES.items()}
btn_play = pygame.transform.scale(pygame.image.load("assets/play.png"), (120, 50))
btn_restart = pygame.transform.scale(pygame.image.load("assets/restart.png"), (120, 50))
mushroom_right = pygame.image.load("assets/mushroom2.png")
mushroom_left = pygame.image.load("assets/mushroom.png")
rain_imgs = {
    "kumbang": pygame.transform.scale(pygame.image.load("assets/obstacle2.png"), (35, 35)),
    "pinus": pygame.transform.scale(pygame.image.load("assets/obstacle1.png"), (35, 35)),
    "rock": pygame.transform.scale(pygame.image.load("assets/obstacle3.png"), (35, 35))
}
cover_img = pygame.transform.scale(pygame.image.load("assets/cover1.png"), (300, 200))
gameover_img = pygame.transform.scale(pygame.image.load("assets/gameover.png"), (400, 180))

class Player:
    def __init__(self):
        self.image = mushroom_right
        self.rect = self.image.get_rect(midbottom=(WIDTH // 2, HEIGHT - 50))
        self.speed = 5

    def update(self, keys):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.image = mushroom_left
            self.rect.x -= self.speed
        elif keys[pygame.K_RIGHT]:
            self.image = mushroom_right
            self.rect.x += self.speed
        self.rect.clamp_ip(screen.get_rect())

    def draw(self):
        shadow = pygame.Surface((self.rect.width, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 60), shadow.get_rect())
        screen.blit(shadow, (self.rect.x, self.rect.bottom - 5))
        screen.blit(self.image, self.rect)

class RainDrop:
    def __init__(self, image, speed):
        self.image = image
        self.rect = self.image.get_rect(midtop=(random.randint(0, WIDTH - 30), -30))
        self.speed = speed

    def move(self):
        self.rect.y += self.speed

    def draw(self):
        screen.blit(self.image, self.rect)

    def off_screen(self):
        return self.rect.top > HEIGHT

class Game:
    def __init__(self):
        self.player = Player()
        self.drops = []
        self.score = 0
        self.start_time = pygame.time.get_ticks()
        self.immune_until = self.start_time + 1000
        self.phase = "morning"
        self.fade_alpha = 0
        self.active = True
        self.current_bg = bg_dict["morning"]
        pygame.time.set_timer(pygame.USEREVENT + 1, 500)

    def get_phase(self, elapsed):
        for phase in reversed(PHASE_ORDER):
            if elapsed >= PHASES[phase]["time"]:
                return phase
        return "morning"  

    def spawn_rain(self, phase):
        if phase != "chaos":
            img_key, speed = PHASES[phase]["drop"]
            return RainDrop(rain_imgs[img_key], speed)
        else:
            img_key, speed = random.choice(PHASES["chaos"]["drops"])
            speed = random.randint(*speed) if isinstance(speed, tuple) else speed
            return RainDrop(rain_imgs[img_key], speed)

    def handle_fade(self):
        if self.fade_alpha > 0:
            overlay = self.current_bg.copy()
            overlay.set_alpha(255 - self.fade_alpha)
            screen.blit(overlay, (0, 0))
            self.fade_alpha -= 5

    def update(self, events):
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        new_phase = self.get_phase(elapsed)

        if new_phase != self.phase:
            self.phase = new_phase
            self.current_bg = bg_dict[self.phase]
            self.fade_alpha = 255

        self.player.update(None)
        for drop in self.drops:
            drop.move()
            if drop.off_screen():
                self.drops.remove(drop)
                self.score += 1
            elif drop.rect.colliderect(self.player.rect) and current_time > self.immune_until:
                self.active = False

    def draw(self, elapsed):
        screen.blit(bg_dict[self.phase], (0, 0))
        self.handle_fade()
        self.player.draw()
        for drop in self.drops:
            drop.draw()
        timer_text = font.render(f"Time: {elapsed // 1000}s", True, (255, 255, 255))
        screen.blit(timer_text, (10, 10))

    def final_score(self):
        elapsed = pygame.time.get_ticks() - self.start_time
        return self.score + (elapsed // 1000)

def show_screen(image, button, button_pos, extra_text=None):
    while True:
        screen.blit(bg_dict["morning" if image == cover_img else "evening"], (0, 0))
        screen.blit(image, (150 if image == cover_img else 100, 80))
        btn_rect = button.get_rect(center=button_pos)
        screen.blit(button, btn_rect)
        if extra_text:
            screen.blit(*extra_text)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and btn_rect.collidepoint(event.pos):
                pygame.time.delay(200)
                return

        pygame.display.update()
        clock.tick(60)

def main():
    while True:
        show_screen(cover_img, btn_play, (300, 320))
        game = Game()

        while game.active:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.USEREVENT + 1:
                    game.drops.append(game.spawn_rain(game.phase))

            game.update(events)
            game.draw(pygame.time.get_ticks() - game.start_time)
            pygame.display.update()
            clock.tick(60)

        score_text = font.render(f"Score: {game.final_score()}", True, (0, 0, 0))
        show_screen(gameover_img, btn_restart, (300, 300), (score_text, (250, 240)))

if __name__ == "__main__":
    main()