import pygame
from OpenGL.GL import *


def MTL(filename):
    contents = {}
    mtl = None
    for line in open(filename, "r"):
        if line.startswith('#'):
            continue
        values = line.split()
        if not values:
            continue
        if values[0] == 'newmtl':
            mtl = contents[values[1]] = {}
        elif mtl is None:
            raise ValueError("MTL file doesn't start with 'newmtl' statement")
        elif values[0] == 'map_Kd':
            # Load the texture referred to by this declaration
            mtl[values[0]] = values[1]
            try:
                surf = pygame.image.load(mtl['map_Kd'])
                image = pygame.image.tostring(surf, 'RGBA', 1)
                ix, iy = surf.get_rect().size
                texid = mtl['texture_Kd'] = glGenTextures(1)
                glBindTexture(GL_TEXTURE_2D, texid)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
            except pygame.error as e:
                print(f"Error loading texture {mtl['map_Kd']}: {e}")
        else:
            try:
                mtl[values[0]] = list(map(float, values[1:]))
            except ValueError:
                pass
    return contents


class OBJ:
    def __init__(self, filename, swapyz=False):
        """Loads a Wavefront OBJ file with minimal data (v and f)."""
        self.vertices = []
        self.normals = []
        self.faces = []

        scale_factor = 10.0
        for line in open(filename, "r"):
            if line.startswith('#'):
                continue
            values = line.split()
            if not values:
                continue
            if values[0] == 'v':  # Vertex data
                v = list(map(float, values[1:4]))
                if swapyz:
                    v = [v[0], v[2], v[1]]
                v = [coord * scale_factor for coord in v]
                self.vertices.append(v)
            elif values[0] == 'f':  # Face data
                face = []
                for v in values[1:]:
                    w = v.split('/')
                    face.append(int(w[0]) - 1)  # Use only vertex indices
                self.faces.append(face)
        
        self.recenter()
        if not self.normals:  # If normals are missing, compute them
            self.compute_normals()

        self.gl_list = glGenLists(1)
        glNewList(self.gl_list, GL_COMPILE)
        glEnable(GL_LIGHTING)
        glBegin(GL_TRIANGLES)
        for face in self.faces:
            for vertex_idx in face:
                # Pass the normal to OpenGL
                if self.normals:
                    glNormal3fv(self.normals[vertex_idx])
                glVertex3fv(self.vertices[vertex_idx])
        glEnd()
        glDisable(GL_LIGHTING)
        glEndList()
    
    def recenter(self):
        """Recenter the object at the origin."""
        # Calculate the geometric center of the vertices
        center = [sum(coord[i] for coord in self.vertices) / len(self.vertices) for i in range(3)]

        # Translate all vertices to recenter the object
        self.vertices = [[v[i] - center[i] for i in range(3)] for v in self.vertices]

    def compute_normals(self):
        """Compute face and vertex normals if not provided."""
        face_normals = []
        vertex_normals = [[] for _ in range(len(self.vertices))]

        for face in self.faces:
            v0, v1, v2 = [self.vertices[idx] for idx in face]
            # Calculate vectors
            vec1 = [v1[i] - v0[i] for i in range(3)]
            vec2 = [v2[i] - v0[i] for i in range(3)]
            # Compute the cross product (face normal)
            normal = [
                vec1[1] * vec2[2] - vec1[2] * vec2[1],
                vec1[2] * vec2[0] - vec1[0] * vec2[2],
                vec1[0] * vec2[1] - vec1[1] * vec2[0],
            ]
            # Normalize the normal vector
            length = sum(n ** 2 for n in normal) ** 0.5
            normal = [n / length for n in normal]
            face_normals.append(normal)

            # Add this face normal to each vertex in the face
            for idx in face:
                vertex_normals[idx].append(normal)

        # Average the vertex normals
        self.normals = []
        for normals in vertex_normals:
            if normals:
                avg_normal = [sum(n[i] for n in normals) / len(normals) for i in range(3)]
                # Normalize the averaged normal
                length = sum(n ** 2 for n in avg_normal) ** 0.5
                avg_normal = [n / length for n in avg_normal]
                self.normals.append(avg_normal)
            else:
                self.normals.append([0, 0, 1])  # Default normal
