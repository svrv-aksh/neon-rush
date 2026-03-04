import pygame
import random
import sys
import math 
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)
WIDTH, HEIGHT = screen.get_size() 
pygame.display.set_caption("Neon Rush")

font = pygame.font.SysFont(None, int(HEIGHT * 0.05))
large_font = pygame.font.SysFont(None, int(HEIGHT * 0.1))

try:
    bg_image = pygame.transform.scale(pygame.image.load("assets/bg.png"), (WIDTH, HEIGHT))
    
    raw_player = pygame.image.load("assets/player.png").convert_alpha()
    player_ratio = raw_player.get_width() / raw_player.get_height()
    
    raw_train = pygame.image.load("assets/train.png").convert_alpha()
    train_ratio = raw_train.get_width() / raw_train.get_height()
    
    raw_coin = pygame.image.load("assets/coin.png").convert_alpha()
    coin_ratio = raw_coin.get_width() / raw_coin.get_height()
    
    PLAYER_H = int(HEIGHT * 0.25)
    PLAYER_W = int(PLAYER_H * player_ratio)
    player_image = pygame.transform.scale(raw_player, (PLAYER_W, PLAYER_H))
except FileNotFoundError:
    print("CRITICAL ERROR: Make sure bg.png, player.png, train.png, and coin.png are in the 'assets' folder!")
    pygame.quit()
    sys.exit()

CENTER_X = WIDTH / 2
track_spread = WIDTH * 0.22 
lanes_center = [CENTER_X - track_spread, CENTER_X, CENTER_X + track_spread] 

base_y = HEIGHT * 0.75      
jump_power = -(HEIGHT * 0.025)  
gravity = (HEIGHT * 0.0015)       
game_speed = HEIGHT * 0.012 
HORIZON_Y = HEIGHT * 0.35  

SPAWN_TRAIN = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_TRAIN, 2000) 
SPAWN_COIN = pygame.USEREVENT + 2
pygame.time.set_timer(SPAWN_COIN, 900)

clock = pygame.time.Clock()
frame_count = 0 

def reset_game():
    global trains, coins, score, target_lane, player_x, player_y, is_jumping, y_velocity, game_state
    trains = []
    coins = []
    score = 0
    target_lane = 1               
    player_x = lanes_center[1]    
    player_y = base_y
    is_jumping = False
    y_velocity = 0
    game_state = "PLAYING"

def draw_shadow(surface, x, y, width, height, alpha=100):
    safe_alpha = max(0, min(255, int(alpha)))
    shadow = pygame.Surface((int(width), int(height)), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, safe_alpha), (0, 0, int(width), int(height)))
    surface.blit(shadow, (x - width/2, y - height/2))

reset_game()
running = True

while running:
    frame_count += 1 
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if game_state == "PLAYING":
            if event.type == SPAWN_TRAIN:
                trains.append({'y': HORIZON_Y, 'lane': random.randint(0, 2)}) 
            if event.type == SPAWN_COIN:
                coins.append({'y': HORIZON_Y, 'lane': random.randint(0, 2), 'phase': random.uniform(0, 6.28)})

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False 
                
            if game_state == "PLAYING":
                if event.key == pygame.K_LEFT and target_lane > 0:
                    target_lane -= 1
                if event.key == pygame.K_RIGHT and target_lane < 2:
                    target_lane += 1
                if event.key == pygame.K_UP and not is_jumping:
                    is_jumping = True
                    y_velocity = jump_power
                    
            elif game_state == "GAME_OVER":
                if event.key == pygame.K_r:
                    reset_game() 

    if game_state == "PLAYING":
        if is_jumping:
            player_y += y_velocity 
            y_velocity += gravity  
            if player_y >= base_y:
                player_y = base_y
                is_jumping = False

        player_x += (lanes_center[target_lane] - player_x) * 0.15 

        for t in trains: t['y'] += game_speed
        for c in coins: c['y'] += game_speed

        for c in coins[:]:
            distance = (c['y'] - HORIZON_Y) / (base_y - HORIZON_Y)
            if c['lane'] == target_lane and 0.85 <= distance <= 1.15:
                if player_y >= base_y - (PLAYER_H * 0.5): 
                    coins.remove(c)
                    score += 10
                    
        for t in trains[:]:
            distance = (t['y'] - HORIZON_Y) / (base_y - HORIZON_Y)
            if t['lane'] == target_lane and 0.85 <= distance <= 1.15:
                scale = 0.4 + (0.6 * distance)
                train_h = int((HEIGHT * 0.25) * scale)
                if player_y > base_y - (train_h * 0.6):
                    game_state = "GAME_OVER"

        trains = [t for t in trains if t['y'] < HEIGHT * 1.5]
        coins = [c for c in coins if c['y'] < HEIGHT * 1.5]

    screen.blit(bg_image, (0, 0)) 
    
    render_list = []
    for c in coins: render_list.append(('coin', c))
    for t in trains: render_list.append(('train', t))
    
    render_list.sort(key=lambda item: item[1]['y'])

    for obj_type, obj in render_list:
        distance = (obj['y'] - HORIZON_Y) / (base_y - HORIZON_Y)
        scale = max(0.01, 0.4 + (0.6 * distance)) 
        target_center_x = lanes_center[obj['lane']]
        current_center_x = CENTER_X + (target_center_x - CENTER_X) * distance
        
        if obj_type == 'coin':
            coin_h = int((HEIGHT * 0.1) * scale)
            coin_w = int(coin_h * coin_ratio)
            hover_offset = math.sin((frame_count * 0.1) + obj['phase']) * (10 * scale)
            draw_x = current_center_x - (coin_w / 2)
            
            draw_shadow(screen, current_center_x, obj['y'] + (coin_h*0.8), coin_w * 0.8, coin_h * 0.3, alpha=int(100 * scale))
            scaled_coin = pygame.transform.scale(raw_coin, (coin_w, coin_h))
            screen.blit(scaled_coin, (draw_x, obj['y'] + hover_offset))
            
        elif obj_type == 'train':
            train_h = int((HEIGHT * 0.25) * scale)
            train_w = int(train_h * train_ratio)
            draw_x = current_center_x - (train_w / 2)
            
            draw_shadow(screen, current_center_x, obj['y'] + train_h, train_w * 0.9, train_h * 0.2, alpha=int(150 * scale))
            scaled_train = pygame.transform.scale(raw_train, (train_w, train_h))
            screen.blit(scaled_train, (draw_x, obj['y']))

    if game_state == "PLAYING":
        player_draw_x = player_x - (PLAYER_W / 2)
        shadow_width = PLAYER_W * 0.6
        shadow_height = PLAYER_H * 0.15
        shadow_alpha = max(0, 150 - int((base_y - player_y) * 1.5)) 
        draw_shadow(screen, player_x, base_y + PLAYER_H * 0.9, shadow_width, shadow_height, alpha=shadow_alpha)
        screen.blit(player_image, (player_draw_x, player_y))
    
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (20, 20))

    if game_state == "GAME_OVER":
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180) 
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        go_text = large_font.render("GAME OVER", True, (255, 50, 50))
        final_score_text = large_font.render(f"FINAL SCORE: {score}", True, (255, 215, 0)) 
        restart_text = font.render("Press 'R' to Restart or 'ESC' to Quit", True, (255, 255, 255))
        
        screen.blit(go_text, (CENTER_X - go_text.get_width()//2, HEIGHT * 0.35))
        screen.blit(final_score_text, (CENTER_X - final_score_text.get_width()//2, HEIGHT * 0.45))
        screen.blit(restart_text, (CENTER_X - restart_text.get_width()//2, HEIGHT * 0.6))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
