import pygame
import random

# Initialize Pygame
pygame.init()
start_time = pygame.time.get_ticks()  # Get the current time at the start
color_change_frequency = 250
last_color_change = pygame.time.get_ticks()

# Set up the display
width, height = 1280, 720
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Mini Hole.io")

# Colors and Functions
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GREY = (50, 50, 50)

def random_color():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

# Game Variables
hole_size = 20
hole_pos = [width // 2, height // 2]  # Logical position in the game world
camera_offset = [0, 0]
objects = [[random.randrange(width), random.randrange(height), random.randint(5, 20), random_color()] for _ in range(50)]
score = 0
max_obj_size = 20  # Maximum size of new objects
direction = [0, 0]  # Direction of movement
growth_points = 0
growth_threshold = 100  # Points required to grow the hole, adjust as needed
growth_increment = 10   # How much the hole grows, adjust as needed
outer_ring_color = random_color()  # Initial color of the outer ring


# Set up font for score display
font = pygame.font.Font(None, 36)

def update_camera():
    camera_offset[0] = hole_pos[0] - width // 2
    camera_offset[1] = hole_pos[1] - height // 2

#def draw_object(obj):
 #   pygame.draw.circle(window, obj[3], (obj[0] - camera_offset[0], obj[1] - camera_offset[1]), obj[2])


def draw_object(obj):
    if obj[4] == 'circle':
        pygame.draw.circle(window, obj[3], (obj[0] - camera_offset[0], obj[1] - camera_offset[1]), obj[2])
    elif obj[4] == 'rectangle':
        pygame.draw.rect(window, obj[3], (obj[0] - camera_offset[0] - obj[2]//2, obj[1] - camera_offset[1] - obj[2]//2, obj[2], obj[2]))



def generate_new_objects():
    global max_obj_size
    num_new_objects = 20  # Adjust this for desired density of objects
    for _ in range(num_new_objects):
        if len(objects) >= 150:  # Adjust maximum number of objects if needed
            break
        max_obj_size = min(100, max_obj_size + 0.01)  # Adjust maximum size of new objects
        new_size = random.randint(5, int(max_obj_size))
        # Generate objects around the current position of the player
        offset_x = random.randint(-1500, 1500)
        offset_y = random.randint(-1500, 1500)
        new_x = int(hole_pos[0]) + offset_x
        new_y = int(hole_pos[1]) + offset_y
        new_shape = random.choice(['circle', 'rectangle'])
        new_mass = new_size  # Assign mass based on size
        new_object = [new_x, new_y, new_size, random_color(), new_shape, new_mass]
        if not is_overlapping(new_object):
            objects.append(new_object)




def despawn_far_objects():
    # Define the maximum allowed distance from the player
    max_distance = 1500  # You can adjust this value

    # Use list comprehension to keep objects within the max distance
    global objects
    objects = [obj for obj in objects if (obj[0] - hole_pos[0])**2 + (obj[1] - hole_pos[1])**2 < max_distance**2]


def is_overlapping(new_obj):
    for obj in objects:
        if pygame.Rect(obj[0], obj[1], obj[2], obj[2]).colliderect(pygame.Rect(new_obj[0], new_obj[1], new_obj[2], new_obj[2])):
            return True
    return False


def bounce_objects(obj1, obj2):
    movement = 30  # Increased movement distance
    # Determine direction of movement
    direction_x = 1 if obj1[0] < obj2[0] else -1
    direction_y = 1 if obj1[1] < obj2[1] else -1

    # Apply movement based on mass and direction
    if obj1[5] >= obj2[5]:  # obj1 is bigger or equal to obj2
        obj2[0] += movement * direction_x
        obj2[1] += movement * direction_y
    else:
        obj1[0] += movement * direction_x
        obj1[1] += movement * direction_y


objects = []
while len(objects) < 50:  
    new_obj = [random.randrange(width), random.randrange(height), random.randint(5, 20), random_color(), random.choice(['circle', 'rectangle']), random.randint(5, 20)]
    if not is_overlapping(new_obj):
        objects.append(new_obj)







# Game Loop
running = True
while running:
    bounced_pairs = set()
    objects_to_remove = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    # Timer for survival time
    current_time = pygame.time.get_ticks()
    survival_time = (current_time - start_time) // 1000
    survival_text = font.render(f"Time: {survival_time} seconds", True, WHITE)
    
    # Timer for color change
    if current_time - last_color_change > color_change_frequency:
        outer_ring_color = random_color()
        last_color_change = current_time


    # Change direction based on key presses
    keys = pygame.key.get_pressed()
    direction = [0, 0]
    if keys[pygame.K_LEFT]:
        direction[0] -= 1
    if keys[pygame.K_RIGHT]:
        direction[0] += 1
    if keys[pygame.K_UP]:
        direction[1] -= 1
    if keys[pygame.K_DOWN]:
        direction[1] += 1

    # Normalize the direction to maintain consistent speed
    length = (direction[0]**2 + direction[1]**2)**0.5
    if length != 0:
        direction = [d / length for d in direction]

    # Move the hole continuously in the set direction
    hole_pos[0] += direction[0] * 7
    hole_pos[1] += direction[1] * 7

    update_camera()
    despawn_far_objects()
    generate_new_objects()

# Check if the hole collides with an object and can swallow it
    hole_rect = pygame.Rect(hole_pos[0] - hole_size, hole_pos[1] - hole_size, 2 * hole_size, 2 * hole_size)
    for obj in objects[:]:
        obj_rect = pygame.Rect(obj[0] - obj[2], obj[1] - obj[2], 2 * obj[2], 2 * obj[2])
        if hole_rect.colliderect(obj_rect) and hole_size > obj[2]:
            objects_to_remove.append(obj)
            score += obj[2]
            growth_points += obj[2]
            # Check if growth threshold is reached
            if growth_points >= growth_threshold:
                hole_size += growth_increment  # Increase hole size
                growth_points -= growth_threshold  # Reset points
                growth_threshold *= 1.1  # Optionally increase the threshold for the next growth stage

    # Remove the marked objects from the objects list
    for obj in objects_to_remove:
        if obj in objects:
            objects.remove(obj)

    # Collision detection with bouncing logic for non-player objects
    for i, obj1 in enumerate(objects):
        for j, obj2 in enumerate(objects):
            if i != j and (i, j) not in bounced_pairs and (j, i) not in bounced_pairs:
                if pygame.Rect(obj1[0], obj1[1], obj1[2], obj1[2]).colliderect(pygame.Rect(obj2[0], obj2[1], obj2[2], obj2[2])):
                    bounce_objects(obj1, obj2)
                    bounced_pairs.add((i, j))  # Track that these objects have bounced




    # Remove the marked objects from the objects list
    for obj in objects_to_remove:
        if obj in objects:
            objects.remove(obj)  # Accumulate growth points

    # Check if growth threshold is reached
        if growth_points >= growth_threshold:
            hole_size += growth_increment  # Increase hole size
            growth_points -= growth_threshold  # Reset points

        # Optionally increase the threshold for the next growth stage
            growth_threshold *= 1.1  # Adjust this factor as needed

    # Draw everything
    window.fill(DARK_GREY)
    for obj in objects:
        draw_object(obj)

    # Draw the player (hole) with a color-changing outer ring
    pygame.draw.circle(window, outer_ring_color, (width // 2, height // 2), hole_size + 5)  # Outer ring
    pygame.draw.circle(window, BLACK, (width // 2, height // 2), hole_size)  # Player hole


    # Display survival time
    window.blit(survival_text, (10, 50))


    # Display score
    score_text = font.render(f"Score: {score}", True, WHITE)
    window.blit(score_text, (10, 10))

    # Calculate elapsed time
    current_time = pygame.time.get_ticks()
    survival_time = (current_time - start_time) // 1000  # Convert milliseconds to seconds

    # Render the survival time and display it
    survival_text = font.render(f"Time: {survival_time} seconds", True, WHITE)
    window.blit(survival_text, (10, 50))  # Adjust position as needed




    # Update the display
    pygame.display.flip()
    pygame.time.delay(30)

pygame.quit()
