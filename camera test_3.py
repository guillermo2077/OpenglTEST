import ctypes

import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import pyrr
from Camera import Camera
import numpy as np
from Dicom_reader import DicomParse

# camera creation

cam1 = Camera()
initial_width, initial_height = 1280, 720
lastX, lastY = 0, 0
first_mouse = True
moving_camera = False
rotation = pyrr.matrix44.create_from_matrix33(pyrr.matrix33.create_identity(float))


# callbacks
def mouse_button_callback(window, button, action, mods):
    global moving_camera, first_mouse
    if button == glfw.MOUSE_BUTTON_RIGHT and action == glfw.PRESS:
        first_mouse = True
        moving_camera = True
    elif button == glfw.MOUSE_BUTTON_RIGHT and action == glfw.RELEASE:
        moving_camera = False


def mouse_look_callback(window, xpos, ypos):
    global lastX, lastY, first_mouse, moving_camera

    if moving_camera:
        if first_mouse:
            lastX = xpos
            lastY = ypos
            first_mouse = False

        xoffset = xpos - lastX
        # opengl coords start from bottom to top, for that reason it is inverted
        yoffset = lastY - ypos

        lastX = xpos
        lastY = ypos

        x_rot, y_rot = cam1.mouse_movement_rotate_item(xoffset, yoffset)

        global rotation
        rotation = pyrr.matrix44.create_from_matrix33(pyrr.matrix33.multiply(x_rot, y_rot))

        print(rotation)
    else:
        pass


def window_resize(window, width, height):
    glViewport(0, 0, width, height)
    projection = pyrr.matrix44.create_perspective_projection_matrix(45, width / height, 0.1, 100)
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)


def scroll_callback(window, x_offset, y_offset):
    global cam1
    cam1.scroll(y_offset)


vertex_src = """
# version 330 core

in vec3 a_position;

uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;

void main()
{
    gl_Position = projection * view * model * vec4(a_position, 1.0);
}
"""

fragment_src = """
# version 330 core

out vec4 out_color;

void main()
{
    out_color = vec4(1.0, 0.0, 0.0, 1.0);
}
"""

# initialize library and create + verify window
if True:
    # initializing glfw library
    if not glfw.init():
        raise Exception("glfw can not be initialized!")

    # creating the window
    window = glfw.create_window(initial_width, initial_height, "My OpenGL window", None, None)

    # check if window was created
    if not window:
        glfw.terminate()
        raise Exception("glfw window can not be created!")

# Set callbacks and window pos
if True:
    glfw.set_window_pos(window, 400, 200)

    # set the callback function for window resize
    glfw.set_window_size_callback(window, window_resize)

    # camera control callbacks
    glfw.set_cursor_pos_callback(window, mouse_look_callback)
    # glfw.set_cursor_enter_callback(window, mouse_enter_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    # scroll wheel callback
    glfw.set_scroll_callback(window, scroll_callback)

# make the context current
glfw.make_context_current(window)

d1 = DicomParse("dicomFiles/ANGIO-CT")
d1.obtainThresholdImage(120, 118)
d1.centerXYZ()


vertices = d1.getPixelDataXYZ()
colors = []

vertices = np.array(vertices, dtype=np.float32)
colors = np.array(colors, dtype=np.float32)

shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))

# create buffer and connect to where gl stores vertex data
# vertices.nbyes = size in bytes of vertices, each is 32 bits so 4 bytes each
VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

# store the position of "a_position" attribute from shader in variable
position = glGetAttribLocation(shader, "a_position")
glEnableVertexAttribArray(position)
glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

glUseProgram(shader)
glClearColor(0.91, 0.84, 0.74, 1)


glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

projection = pyrr.matrix44.create_perspective_projection_matrix(45, initial_width / initial_height, 0.1, 100)
translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([0, 0, 0]))

# eye, target, up
# view = pyrr.matrix44.create_look_at(pyrr.Vector3([0, 0, 20]), pyrr.Vector3([0, 0, 0]), pyrr.Vector3([0, 1, 0]))

model_loc = glGetUniformLocation(shader, "model")
proj_loc = glGetUniformLocation(shader, "projection")
view_loc = glGetUniformLocation(shader, "view")

glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
# glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
model = translation

glPointSize(3)
# the main application loop
while not glfw.window_should_close(window):
    glfw.poll_events()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    view = cam1.get_view_matrix()
    glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

    # rot_y = pyrr.Matrix44.from_y_rotation(0.8 * glfw.get_time())
    # model = pyrr.matrix44.multiply(rot_y, fox_pos)

    glUniformMatrix4fv(model_loc, 1, GL_FALSE, pyrr.matrix44.multiply(translation, rotation))

    # count will need to be changed
    glDrawArrays(GL_POINTS, 0, int(len(vertices)/3))

    glfw.swap_buffers(window)

# terminate glfw, free up allocated resources
glfw.terminate()
