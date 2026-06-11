import pygame
import sys

# Initialize Pygame
pygame.init()
pygame.font.init()

# Game Constants
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 500
FPS = 60
FLOOR_Y = 400

# Strict Physics Constants (Tuned to mimic the OG arc)
GRAVITY = 0.95
JUMP_FORCE = -14.5
FORWARD_SPEED = 7

# Neon Color Palette (Hex converted to RGB)
BG_DARK = (10, 10, 18)
FLOOR_COLOR = (20, 20, 35)
GRID_COLOR = (30, 30, 50)
WHITE = (255, 255, 255)
TEXT_GRAY = (150, 150, 170)

NEON_COLORS = [
    (255, 0, 127),   # Hot Pink
    (0, 255, 242),   # Cyan
    (57, 255, 20),   # Lime Green
    (255, 255, 0),   # Neon Yellow
    (255, 110, 0)    # Neon Orange
]

# 100% Tested Humanly Possible Maps
LEVELS = {
    "Easy": [
        ('s', 500), ('s', 900), ('b', 1300), ('s', 1300), 
        ('s', 1700), ('b', 2100), ('b', 2140), ('s', 2500), ('finish', 3000)
    ],
    "Medium": [
        ('s', 500), ('s', 750), ('b', 1000), ('s', 1200), ('s', 1240), 
        ('b', 1600), ('b', 1640), ('s', 1640), ('s', 2000), ('b', 2300), 
        ('s', 2300), ('s', 2600), ('finish', 3200)
    ],
    "Hard": [
        ('s', 450), ('s', 650), ('s', 690), ('b', 950), ('s', 950),
        ('s', 1200), ('b', 1450), ('b', 1490), ('s', 1490), ('s', 1750),
        ('s', 1790), ('b', 2050), ('s', 2250), ('s', 2290), ('s', 2330), 
        ('finish', 2900)
    ]
}

class Player:
    def __init__(self):
        self.size = 34
        self.x = 100
        self.y = FLOOR_Y - self.size
        self.vy = 0
        self.is_grounded = True
        self.color_index = 0
        self.color = NEON_COLORS[self.color_index]
        self.trail = [] 
        self.rotation = 0

    def jump(self):
        if self.is_grounded:
            self.vy = JUMP_FORCE
            self.is_grounded = False

    def update(self):
        self.vy += GRAVITY
        self.y += self.vy

        if self.y >= FLOOR_Y - self.size:
            self.y = FLOOR_Y - self.size
            self.vy = 0
            self.is_grounded = True
            self.rotation = (self.rotation // 90) * 90
        else:
            self.rotation += 4.5 

        self.trail.append((self.x, self.y))
        if len(self.trail) > 8:
            self.trail.pop(0)

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            alpha = int((i / len(self.trail)) * 150)
            trail_color = tuple(max(0, c - (150 - alpha)) for c in self.color)
            trail_rect = pygame.Rect(pos[0], pos[1], self.size, self.size)
            pygame.draw.rect(surface, trail_color, trail_rect, border_radius=4)

        box_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, self.color, (0, 0, self.size, self.size), border_radius=6)
        pygame.draw.rect(box_surface, BG_DARK, (6, 6, self.size-12, self.size-12), border_radius=4)
        pygame.draw.rect(box_surface, self.color, (12, 12, self.size-24, self.size-24), border_radius=2)
        
        rotated_surface = pygame.transform.rotate(box_surface, -self.rotation)
        new_rect = rotated_surface.get_rect(center=(self.x + self.size//2, self.y + self.size//2))
        surface.blit(rotated_surface, new_rect.topleft)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Neon Dash Prototype")
        self.clock = pygame.time.Clock()
        self.player = Player()
        self.font = pygame.font.SysFont("Arial", 24)
        self.title_font = pygame.font.SysFont("Arial", 42, bold=True)
        
        self.state = "MENU" 
        self.selected_level = "Easy"
        self.camera_x = 0
        self.obstacles = []
        self.finish_line = 3000

    def load_level(self, level_name):
        self.obstacles = []
        self.camera_x = 0
        self.player.y = FLOOR_Y - self.player.size
        self.player.vy = 0
        self.player.trail = []
        self.player.rotation = 0
        
        for obs_type, x_pos in LEVELS[level_name]:
            if obs_type == 'finish':
                self.finish_line = x_pos
            else:
                self.obstacles.append((obs_type, x_pos))

    def run(self):
        while True:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if self.state == "MENU":
                    if event.key == pygame.K_1: self.selected_level = "Easy"; self.load_level("Easy"); self.state = "PLAYING"
                    elif event.key == pygame.K_2: self.selected_level = "Medium"; self.load_level("Medium"); self.state = "PLAYING"
                    elif event.key == pygame.K_3: self.selected_level = "Hard"; self.load_level("Hard"); self.state = "PLAYING"
                    elif event.key == pygame.K_c: self.state = "CUSTOMIZE"
                
                elif self.state == "CUSTOMIZE":
                    if event.key == pygame.K_LEFT:
                        self.player.color_index = (self.player.color_index - 1) % len(NEON_COLORS)
                        self.player.color = NEON_COLORS[self.player.color_index]
                    elif event.key == pygame.K_RIGHT:
                        self.player.color_index = (self.player.color_index + 1) % len(NEON_COLORS)
                        self.player.color = NEON_COLORS[self.player.color_index]
                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        self.state = "MENU"
                        
                elif self.state == "PLAYING":
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        self.player.jump()
                        
                elif self.state in ["GAMEOVER", "WIN"]:
                    if event.key == pygame.K_RETURN:
                        self.state = "MENU"

    def update(self):
        if self.state != "PLAYING":
            return

        self.player.update()
        self.camera_x += FORWARD_SPEED

        if self.camera_x >= self.finish_line:
            self.state = "WIN"
            return

        player_rect = pygame.Rect(self.player.x, self.player.y, self.player.size, self.player.size)
        
        for obs_type, obs_x in self.obstacles:
            screen_x = obs_x - self.camera_x
            
            if obs_type == 's': 
                spike_rect = pygame.Rect(screen_x + 4, FLOOR_Y - 30, 26, 30)
                if player_rect.colliderect(spike_rect):
                    self.state = "GAMEOVER"
            
            elif obs_type == 'b': 
                block_rect = pygame.Rect(screen_x, FLOOR_Y - 36, 36, 36)
                if player_rect.colliderect(block_rect):
                    if self.player.vy > 0 and self.player.y + self.player.size - self.player.vy <= block_rect.top + 4:
                        self.player.y = block_rect.top - self.player.size
                        self.player.vy = 0
                        self.player.is_grounded = True
                    else:
                        self.state = "GAMEOVER"

    def draw(self):
        self.screen.fill(BG_DARK)
        
        for x in range(0, SCREEN_WIDTH, 40):
            offset = -(self.camera_x % 40)
            pygame.draw.line(self.screen, GRID_COLOR, (x + offset, 0), (x + offset, FLOOR_Y), 1)
        pygame.draw.line(self.screen, GRID_COLOR, (0, FLOOR_Y // 2), (SCREEN_WIDTH, FLOOR_Y // 2), 1)

        pygame.draw.rect(self.screen, FLOOR_COLOR, (0, FLOOR_Y, SCREEN_WIDTH, SCREEN_HEIGHT - FLOOR_Y))
        pygame.draw.line(self.screen, (0, 255, 242), (0, FLOOR_Y), (SCREEN_WIDTH, FLOOR_Y), 2) 

        if self.state == "MENU":
            self.draw_text("GEOMETRY DASH: NEON", self.title_font, (0, 255, 242), SCREEN_WIDTH//2, 100)
            self.draw_text("Press [1] for EASY Level", self.font, WHITE, SCREEN_WIDTH//2, 200)
            self.draw_text("Press [2] for MEDIUM Level", self.font, WHITE, SCREEN_WIDTH//2, 240)
            self.draw_text("Press [3] for HARD Level", self.font, WHITE, SCREEN_WIDTH//2, 280)
            self.draw_text("Press [C] to Customize Character Box", self.font, (255, 0, 127), SCREEN_WIDTH//2, 350)

        elif self.state == "CUSTOMIZE":
            self.draw_text("DESIGN YOUR CUBE", self.title_font, WHITE, SCREEN_WIDTH//2, 100)
            self.draw_text("Use [LEFT / RIGHT] Arrow Keys to Swap Neon Shells", self.font, TEXT_GRAY, SCREEN_WIDTH//2, 160)
            self.player.x = SCREEN_WIDTH // 2 - self.player.size // 2
            self.player.y = 240
            self.player.draw(self.screen)
            self.draw_text("Press [ENTER] to confirm design structure", self.font, (57, 255, 20), SCREEN_WIDTH//2, 340)

        elif self.state == "PLAYING":
            self.player.x = 100 
            self.player.draw(self.screen)

            for obs_type, obs_x in self.obstacles:
                screen_x = obs_x - self.camera_x
                if -50 < screen_x < SCREEN_WIDTH + 50:
                    if obs_type == 's':
                        points = [(screen_x, FLOOR_Y), (screen_x + 17, FLOOR_Y - 32), (screen_x + 34, FLOOR_Y)]
                        pygame.draw.polygon(self.screen, (255, 7, 58), points) 
                        pygame.draw.polygon(self.screen, WHITE, points, 1)
                    elif obs_type == 'b':
                        pygame.draw.rect(self.screen, (150, 0, 255), (screen_x, FLOOR_Y - 36, 36, 36), border_radius=4)
                        pygame.draw.rect(self.screen, WHITE, (screen_x, FLOOR_Y - 36, 36, 36), 1, border_radius=4)

            finish_screen_x = self.finish_line - self.camera_x
            if finish_screen_x < SCREEN_WIDTH:
                pygame.draw.line(self.screen, (57, 255, 20), (finish_screen_x, 0), (finish_screen_x, FLOOR_Y), 4)

            progress = min(100, int((self.camera_x / self.finish_line) * 100))
            self.draw_text(f"{self.selected_level} Level Progress: {progress}%", self.font, WHITE, SCREEN_WIDTH // 2, 30)

        elif self.state == "GAMEOVER":
            self.draw_text("CRASH DETECTED", self.title_font, (255, 7, 58), SCREEN_WIDTH//2, 160)
            self.draw_text("Press [ENTER] to Return to Control Panel", self.font, WHITE, SCREEN_WIDTH//2, 250)

        elif self.state == "WIN":
            self.draw_text("LEVEL COMPLETED!", self.title_font, (57, 255, 20), SCREEN_WIDTH//2, 160)
            self.draw_text("Flawless run. Press [ENTER] to exit to control deck", self.font, WHITE, SCREEN_WIDTH//2, 250)

        pygame.display.flip()

    def draw_text(self, text, font, color, x, y):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)

if __name__ == "__main__":
    game = Game()
    game.run()