import pygame
import sys
import random
import math
from pygame import mixer

# Initialize pygame
pygame.init()
mixer.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
BACKGROUND_COLOR = (26, 26, 47)

# Game constants
BUBBLE_RADIUS = 20
GRID_WIDTH = 15
GRID_HEIGHT = 12
SHOOTER_ANGLE_LIMIT = 180
BUBBLE_SPEED = 17
BUBBLE_COLORS = [RED, GREEN, BLUE, YELLOW, PURPLE, CYAN]
POWERUP_COLOR = (255, 165, 0)  # Orange
POWERUP_CHANCE = 0.1  # 10% chance for powerup

class Bubble:
    def __init__(self, x, y, color, row=-1, col=-1, is_powerup=False):
        self.x = x
        self.y = y
        self.color = color
        self.radius = BUBBLE_RADIUS
        self.row = row
        self.col = col
        self.is_powerup = is_powerup
        self.visited = False
    
    def draw(self, screen):
        if self.is_powerup:
            # Draw powerup with special effect
            pygame.draw.circle(screen, POWERUP_COLOR, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius - 5)
        else:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 1)

class BubbleShooter:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Kaliya Martha - Advanced Bubble Shooter")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        self.big_font = pygame.font.SysFont('Arial', 48)
        
        # Game state
        self.bubbles = []
        self.shooter_bubble = None
        self.next_bubble = None
        self.shooting_bubble = None
        self.shooter_angle = 0
        self.score = 0
        self.level = 1
        self.game_over = False
        self.game_won = False
        self.paused = False
        
        # Sounds
        self.pop_sound = mixer.Sound('assets/pop.mp3') if pygame.mixer.get_init() else None
        self.powerup_sound = mixer.Sound('assets/powerup_sound.mp3') if pygame.mixer.get_init() else None
        self.background_music = mixer.Sound('assets/background_music.mp3') if pygame.mixer.get_init() else None
        
        # Initialize game
        self.reset_game()
    
    def reset_game(self):
        self.bubbles = []
        self.score = 0
        self.level = 1
        self.game_over = False
        self.game_won = False
        
        # Create initial bubble grid
        self.create_bubble_grid()
        
        # Create shooter and next bubble
        self.create_shooter_bubble()
        self.create_next_bubble()
        
        # Play background music
        if self.background_music:
            self.background_music.play(-1)  # Loop indefinitely
    
    def create_bubble_grid(self):
        rows = min(3 + self.level, 8)  # Increase rows with level
        
        for row in range(rows):
            for col in range(GRID_WIDTH):
                if row % 2 == 0 or col < GRID_WIDTH - 1:
                    x = col * BUBBLE_RADIUS * 2 + BUBBLE_RADIUS
                    if row % 2 != 0:
                        x += BUBBLE_RADIUS
                    y = row * BUBBLE_RADIUS * 1.8 + BUBBLE_RADIUS
                    
                    # Random chance for powerup
                    is_powerup = random.random() < POWERUP_CHANCE and row > 1
                    color = POWERUP_COLOR if is_powerup else random.choice(BUBBLE_COLORS)
                    
                    self.bubbles.append(Bubble(x, y, color, row, col, is_powerup))
    
    def create_shooter_bubble(self):
        color = self.next_bubble.color if self.next_bubble else random.choice(BUBBLE_COLORS)
        self.shooter_bubble = Bubble(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, color)
    
    def create_next_bubble(self):
        color = random.choice(BUBBLE_COLORS)
        self.next_bubble = Bubble(SCREEN_WIDTH - 50, 50, color)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_r and (self.game_over or self.game_won):
                    self.reset_game()
                if event.key == pygame.K_p:
                    self.paused = not self.paused
            
            if not self.game_over and not self.game_won and not self.paused:
                if event.type == pygame.MOUSEBUTTONDOWN and not self.shooting_bubble:
                    if event.button == 1:  # Left click
                        self.shoot_bubble()
        
        return True
    
    def update_shooter_angle(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - self.shooter_bubble.x
        dy = mouse_y - self.shooter_bubble.y
        self.shooter_angle = math.degrees(math.atan2(dy, dx))
        
        # Limit angle
        if self.shooter_angle < -SHOOTER_ANGLE_LIMIT:
            self.shooter_angle = -SHOOTER_ANGLE_LIMIT
        if self.shooter_angle > SHOOTER_ANGLE_LIMIT:
            self.shooter_angle = SHOOTER_ANGLE_LIMIT
    
    def shoot_bubble(self):
        angle_rad = math.radians(self.shooter_angle)
        self.shooting_bubble = Bubble(
            self.shooter_bubble.x,
            self.shooter_bubble.y,
            self.shooter_bubble.color
        )
        self.shooting_bubble.dx = BUBBLE_SPEED * math.cos(angle_rad)
        self.shooting_bubble.dy = BUBBLE_SPEED * math.sin(angle_rad)
        
        # Prepare next shooter bubble
        self.shooter_bubble.color = self.next_bubble.color
        self.create_next_bubble()
    
    def update_shooting_bubble(self):
        self.shooting_bubble.x += self.shooting_bubble.dx
        self.shooting_bubble.y += self.shooting_bubble.dy
        
        # Wall collision
        if (self.shooting_bubble.x - BUBBLE_RADIUS < 0 or 
            self.shooting_bubble.x + BUBBLE_RADIUS > SCREEN_WIDTH):
            self.shooting_bubble.dx = -self.shooting_bubble.dx
        
        # Ceiling collision
        if self.shooting_bubble.y - BUBBLE_RADIUS < 0:
            self.attach_bubble_to_grid()
            return
        
        # Bubble collision
        collided_bubble = self.check_bubble_collision()
        if collided_bubble:
            self.attach_bubble_to_grid(collided_bubble)
            return
    
    def check_bubble_collision(self):
        for bubble in self.bubbles:
            dx = self.shooting_bubble.x - bubble.x
            dy = self.shooting_bubble.y - bubble.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < self.shooting_bubble.radius + bubble.radius:
                return bubble
        return None
    
    def attach_bubble_to_grid(self, collided_bubble=None):
        if collided_bubble:
            # Find grid position near collided bubble
            grid_pos = self.find_grid_position(collided_bubble)
            new_bubble = Bubble(
                grid_pos['x'],
                grid_pos['y'],
                self.shooting_bubble.color,
                grid_pos['row'],
                grid_pos['col']
            )
        else:
            # Attach to top
            col = round((self.shooting_bubble.x - BUBBLE_RADIUS) / (BUBBLE_RADIUS * 2))
            col = max(0, min(GRID_WIDTH - 1, col))
            x = col * BUBBLE_RADIUS * 2 + BUBBLE_RADIUS
            y = BUBBLE_RADIUS
            new_bubble = Bubble(x, y, self.shooting_bubble.color, 0, col)
        
        self.bubbles.append(new_bubble)
        self.shooting_bubble = None
        
        # Check for matches
        self.check_for_matches(new_bubble)
        
        # Check if all bubbles are cleared
        if not self.bubbles:
            self.game_won = True
            self.level += 1
            if self.level <= 5:  # 5 levels total
                self.create_bubble_grid()
                self.game_won = False
    
    def find_grid_position(self, collided_bubble):
        # Find all possible adjacent positions
        possible_positions = []
        
        # Standard positions (left, right, top, bottom)
        possible_positions.append({'row': collided_bubble.row, 'col': collided_bubble.col - 1})
        possible_positions.append({'row': collided_bubble.row, 'col': collided_bubble.col + 1})
        possible_positions.append({'row': collided_bubble.row - 1, 'col': collided_bubble.col})
        possible_positions.append({'row': collided_bubble.row + 1, 'col': collided_bubble.col})
        
        # Diagonal positions (hexagonal grid)
        if collided_bubble.row % 2 == 0:
            possible_positions.append({'row': collided_bubble.row - 1, 'col': collided_bubble.col - 1})
            possible_positions.append({'row': collided_bubble.row + 1, 'col': collided_bubble.col - 1})
        else:
            possible_positions.append({'row': collided_bubble.row - 1, 'col': collided_bubble.col + 1})
            possible_positions.append({'row': collided_bubble.row + 1, 'col': collided_bubble.col + 1})
        
        # Find the closest empty position
        closest_pos = None
        min_distance = float('inf')
        
        for pos in possible_positions:
            if 0 <= pos['row'] < GRID_HEIGHT and 0 <= pos['col'] < GRID_WIDTH:
                # Check if position is empty
                occupied = False
                for bubble in self.bubbles:
                    if bubble.row == pos['row'] and bubble.col == pos['col']:
                        occupied = True
                        break
                
                if not occupied:
                    # Calculate position coordinates
                    x = pos['col'] * BUBBLE_RADIUS * 2 + BUBBLE_RADIUS
                    if pos['row'] % 2 != 0:
                        x += BUBBLE_RADIUS
                    y = pos['row'] * BUBBLE_RADIUS * 1.8 + BUBBLE_RADIUS
                    
                    # Calculate distance to shooting bubble
                    dx = self.shooting_bubble.x - x
                    dy = self.shooting_bubble.y - y
                    distance = dx*dx + dy*dy
                    
                    if distance < min_distance:
                        min_distance = distance
                        closest_pos = pos
                        closest_pos['x'] = x
                        closest_pos['y'] = y
        
        return closest_pos or {'x': self.shooting_bubble.x, 'y': self.shooting_bubble.y, 'row': -1, 'col': -1}
    
    def check_for_matches(self, new_bubble):
        # Reset visited flags
        for bubble in self.bubbles:
            bubble.visited = False
        
        # Find connected bubbles of the same color
        connected = []
        self.find_connected_bubbles(new_bubble, new_bubble.color, connected)
        
        if len(connected) >= 3:
            # Check for powerups in the connected bubbles
            powerup_activated = any(bubble.is_powerup for bubble in connected)
            
            # Remove connected bubbles
            self.bubbles = [bubble for bubble in self.bubbles if bubble not in connected]
            
            # Play sound
            if self.pop_sound:
                self.pop_sound.play()
            
            # Update score
            self.score += len(connected) * 10
            
            # Powerup effect
            if powerup_activated and self.powerup_sound:
                self.powerup_sound.play()
                self.activate_powerup()
            
            # Check for floating bubbles
            self.check_floating_bubbles()
    
    def find_connected_bubbles(self, bubble, color, connected):
        if bubble.visited or bubble.color != color:
            return
        
        bubble.visited = True
        connected.append(bubble)
        
        # Check adjacent bubbles
        for other in self.bubbles:
            if other != bubble and not other.visited:
                dx = bubble.x - other.x
                dy = bubble.y - other.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < BUBBLE_RADIUS * 2.1:  # Slightly more than diameter
                    self.find_connected_bubbles(other, color, connected)
    
    def check_floating_bubbles(self):
        # Reset visited flags
        for bubble in self.bubbles:
            bubble.visited = False
        
        # Mark all bubbles connected to the ceiling
        ceiling_bubbles = [bubble for bubble in self.bubbles if bubble.row == 0]
        for bubble in ceiling_bubbles:
            self.mark_connected_to_ceiling(bubble)
        
        # Any unvisited bubbles are floating
        floating_bubbles = [bubble for bubble in self.bubbles if not bubble.visited]
        
        if floating_bubbles:
            # Remove floating bubbles
            self.bubbles = [bubble for bubble in self.bubbles if bubble.visited]
            
            # Play sound
            if self.pop_sound:
                self.pop_sound.play()
            
            # Update score
            self.score += len(floating_bubbles) * 20
    
    def mark_connected_to_ceiling(self, bubble):
        if bubble.visited:
            return
        
        bubble.visited = True
        
        # Check adjacent bubbles
        for other in self.bubbles:
            if other != bubble:
                dx = bubble.x - other.x
                dy = bubble.y - other.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < BUBBLE_RADIUS * 2.1:  # Slightly more than diameter
                    self.mark_connected_to_ceiling(other)
    
    def activate_powerup(self):
        # Powerup effect: remove all bubbles of a random color
        if not self.bubbles:
            return
        
        color_to_remove = random.choice([bubble.color for bubble in self.bubbles])
        bubbles_removed = [bubble for bubble in self.bubbles if bubble.color == color_to_remove]
        self.bubbles = [bubble for bubble in self.bubbles if bubble.color != color_to_remove]
        
        # Update score
        self.score += len(bubbles_removed) * 15
    
    def check_game_over(self):
        for bubble in self.bubbles:
            if bubble.y + BUBBLE_RADIUS > SCREEN_HEIGHT - 50:
                self.game_over = True
                if self.background_music:
                    self.background_music.stop()
                break
    
    def draw(self):
        # Draw background
        self.screen.fill(BACKGROUND_COLOR)
        
        # Draw bubbles
        for bubble in self.bubbles:
            bubble.draw(self.screen)
        
        # Draw shooting bubble
        if self.shooting_bubble:
            self.shooting_bubble.draw(self.screen)
        
        # Draw shooter
        pygame.draw.circle(self.screen, GRAY, 
                          (int(self.shooter_bubble.x), int(self.shooter_bubble.y)), 
                          int(BUBBLE_RADIUS * 1.5))
        self.shooter_bubble.draw(self.screen)
        
        # Draw shooter line
        line_length = 100
        end_x = self.shooter_bubble.x + line_length * math.cos(math.radians(self.shooter_angle))
        end_y = self.shooter_bubble.y + line_length * math.sin(math.radians(self.shooter_angle))
        pygame.draw.line(self.screen, WHITE, 
                        (self.shooter_bubble.x, self.shooter_bubble.y), 
                        (end_x, end_y), 2)
        
        # Draw next bubble preview
        pygame.draw.circle(self.screen, self.next_bubble.color, 
                          (SCREEN_WIDTH - 50, 50), BUBBLE_RADIUS - 5)
        pygame.draw.circle(self.screen, WHITE, 
                          (SCREEN_WIDTH - 50, 50), BUBBLE_RADIUS - 5, 1)
        
        # Draw score and level
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        level_text = self.font.render(f"Level: {self.level}/5", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(level_text, (10, 40))
        
        # Draw game over or win message
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.big_font.render("GAME OVER", True, RED)
            score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.font.render("Press R to restart", True, WHITE)
            
            self.screen.blit(game_over_text, 
                           (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 
                            SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(score_text, 
                           (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 
                            SCREEN_HEIGHT // 2 + 10))
            self.screen.blit(restart_text, 
                           (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 
                            SCREEN_HEIGHT // 2 + 50))
        
        elif self.game_won and self.level > 5:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            win_text = self.big_font.render("YOU WIN!", True, GREEN)
            score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.font.render("Press R to play again", True, WHITE)
            
            self.screen.blit(win_text, 
                           (SCREEN_WIDTH // 2 - win_text.get_width() // 2, 
                            SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(score_text, 
                           (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 
                            SCREEN_HEIGHT // 2 + 10))
            self.screen.blit(restart_text, 
                           (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 
                            SCREEN_HEIGHT // 2 + 50))
        
        elif self.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            pause_text = self.big_font.render("PAUSED", True, WHITE)
            continue_text = self.font.render("Press P to continue", True, WHITE)
            
            self.screen.blit(pause_text, 
                           (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 
                            SCREEN_HEIGHT // 2 - 30))
            self.screen.blit(continue_text, 
                           (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, 
                            SCREEN_HEIGHT // 2 + 20))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            
            if not self.paused and not self.game_over and not self.game_won:
                self.update_shooter_angle()
                
                if self.shooting_bubble:
                    self.update_shooting_bubble()
                
                self.check_game_over()
            
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = BubbleShooter()
    game.run()