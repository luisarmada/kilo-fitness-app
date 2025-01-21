import os
import sys
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# Import the OBJ loader
from objloader import OBJ

# Initialize Pygame and OpenGL
pygame.init()
viewport = (800, 600)
hx, hy = viewport[0] // 2, viewport[1] // 2
srf = pygame.display.set_mode(viewport, OPENGL | DOUBLEBUF)

# Set up lighting
glLightfv(GL_LIGHT0, GL_POSITION, (-40, 200, 100, 0.0))
glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.8, 1.0))
glEnable(GL_LIGHT0)
glEnable(GL_LIGHTING)
glEnable(GL_COLOR_MATERIAL)
glEnable(GL_DEPTH_TEST)
glShadeModel(GL_SMOOTH)

# Set up projection
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
width, height = viewport
gluPerspective(45.0, width / float(height), 1, 1000.0)
glMatrixMode(GL_MODELVIEW)

# Function to load all OBJ files in a folder
def load_objects_from_folder(folder):
    """Load all OBJ files from the specified folder."""
    obj_files = [f for f in os.listdir(folder) if f.endswith('.obj')]
    objects = []
    for obj_file in obj_files:
        path = os.path.join(folder, obj_file)
        print(f"Loading {path}...")
        objects.append(OBJ(path, swapyz=False))
    return objects

# Main program
def main(folder):
    # Load all objects from the folder
    objects = load_objects_from_folder(folder)
    if not objects:
        print("No OBJ files found in the folder!")
        sys.exit(1)

    current_obj_index = 0
    clock = pygame.time.Clock()
    rx, ry = 0, 0
    tx, ty = 0, 0
    zpos = 15
    rotate = move = False

    while True:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == K_p:  # Switch to the previous object
                    current_obj_index = (current_obj_index + 1) % len(objects)
                    print(f"Switched to: {current_obj_index + 1}/{len(objects)}")
                elif event.key == K_o:  # Switch to the next object
                    current_obj_index = (current_obj_index - 1) % len(objects)
                    print(f"Switched to: {current_obj_index + 1}/{len(objects)}")
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll up
                    zpos = max(1, zpos - 1)
                elif event.button == 5:  # Scroll down
                    zpos += 1
                elif event.button == 1:  # Left mouse button
                    rotate = True
                elif event.button == 3:  # Right mouse button
                    move = True
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    rotate = False
                elif event.button == 3:  # Right mouse button
                    move = False
            elif event.type == MOUSEMOTION:
                i, j = event.rel
                if rotate:
                    rx += i
                    # ry += j
                if move:
                    tx += i
                    ty -= j

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Apply transformations
        glTranslatef(tx / 20.0, ty / 20.0, -zpos)
        glRotatef(ry, 1, 0, 0)
        glRotatef(rx, 0, 1, 0)

        # Render the current object
        glCallList(objects[current_obj_index].gl_list)

        pygame.display.flip()

# Run the program with the folder containing OBJ files
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python obj_viewer.py <folder_path>")
        sys.exit(1)
    folder_path = sys.argv[1]
    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid directory.")
        sys.exit(1)
    main(folder_path)