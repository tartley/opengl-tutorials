
from ctypes import sizeof
from os.path import join
import sys

from OpenGL.GL.shaders import compileShader, compileProgram
from OpenGL import GL as gl

import pyglet



vertex_data = [
    -1.0, -1.0,
     1.0, -1.0,
    -1.0,  1.0,
     1.0,  1.0,
]
element_data = [ 0, 1, 2, 3 ]



class Attributes(object):
    def __init__(self):
        self.position = None

    def make(self, shader):
        self.position = gl.glGetAttribLocation(shader, 'position')


class Uniforms(object):
    def __init__(self):
        self.fade_factor = None
        self.textures = None

    def make(self, shader):
        self.fade_factor = gl.glGetUniformLocation(shader, 'fade_factor')
        self.textures = [
            gl.glGetUniformLocation(shader, 'textures[0]'),
            gl.glGetUniformLocation(shader, 'textures[1]'),
        ]


class Resources(object):
    def __init__(self):
        self.vertex_buffer = None
        self.element_buffer = None
        self.textures = None
        self.vertex_shader = None
        self.fragment_shader = None
        self.shader_program = None
        self.attributes = Attributes()
        self.uniforms = Uniforms()


    def make_buffer(self, target, data, element_type):
        '''
            target: buffer type, eg.
                GL_ARRAY_BUFFER (vertices), GL_ELEMENT_ARRAY_BUFFER (indices)
            data: list of values
        '''
        buffer_id = gl.glGenBuffers(1)
        gl.glBindBuffer(target, buffer_id)
        size = len(data) * sizeof(element_type)
        array_type = (element_type * len(data))
        gl.glBufferData(target, size, array_type(*data), gl.GL_STATIC_DRAW)
        return buffer_id


    def make_texture(self, filename):
        return pyglet.image.load(filename).get_texture().id


    def make(self):
        self.vertex_buffer = self.make_buffer(
            gl.GL_ARRAY_BUFFER, vertex_data, gl.GLfloat)
        self.element_buffer = self.make_buffer(
            gl.GL_ELEMENT_ARRAY_BUFFER, element_data, gl.GLushort) 

        self.textures = [
            self.make_texture(join('data', 'gl2-hello-0.png')),
            self.make_texture(join('data', 'gl2-hello-1.png')),
        ]

        self.shader_program = make_shader_program(
            'hello-gl.v.glsl', 'hello-gl.f.glsl')

        self.uniforms.make(self.shader_program)
        self.attributes.make(self.shader_program)
        

def make_shader_program(vertex_filename, fragment_filename):

    def read_file(filename):
        with open(filename) as fp:
            return fp.readlines()

    try:
        shader_program = compileProgram(
            compileShader(read_file(vertex_filename), gl.GL_VERTEX_SHADER),
            compileShader(read_file(fragment_filename), gl.GL_FRAGMENT_SHADER)
        )
    except RuntimeError as exc:
        args = list(exc.args)
        sys.stderr.write(''.join(str(a) for a in args[:-2]))
        # sys.stderr.write(''.join(str(a) for a in args[-2]))
        # sys.stderr.write(args[-1])
        sys.exit(1)

    return shader_program


def render(window, resources):
    gl.glClearColor(0.6, 0.5, 0.7, 1.0)
    window.clear()

    gl.glUseProgram(resources.shader_program)

    gl.glUniform1f(resources.uniforms.fade_factor, 0.5)

    gl.glActiveTexture(gl.GL_TEXTURE0)
    gl.glBindTexture(gl.GL_TEXTURE_2D, resources.textures[0])
    gl.glUniform1i(resources.uniforms.textures[0], 0)

    gl.glActiveTexture(gl.GL_TEXTURE1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, resources.textures[1])
    gl.glUniform1i(resources.uniforms.textures[1], 1)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, resources.vertex_buffer)
    gl.glEnableVertexAttribArray(resources.attributes.position)
    gl.glVertexAttribPointer(
        resources.attributes.position,
        2,              # size (position has 2 components?)
        gl.GL_FLOAT,    # type
        gl.GL_FALSE,          # normalized?
        sizeof(gl.GLfloat) * 2,  # stride
        gl.GLuint(0),   # array buffer offset
    )

    #gl.glColor3ub(100, 150, 50)
    #gl.glBegin(gl.GL_TRIANGLES)
    #scale = 1.0/500
    #gl.glVertex(100.0 * scale, +100.0 * scale)
    #gl.glVertex(200.0 * scale, +300.0 * scale)
    #gl.glVertex(300.0 * scale, +100.0 * scale)
    #gl.glEnd()

    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, resources.element_buffer)

    gl.glDrawElements(
        gl.GL_TRIANGLE_STRIP,   # mode
        len(element_data),      # element count
        gl.GL_UNSIGNED_SHORT,   # type TODO, may not be bytes in future
        0                       # element array buffer offset
    )

    gl.glDisableVertexAttribArray(resources.attributes.position)

    window.invalid = False
    return pyglet.event.EVENT_HANDLED

    
def update(window, dt):
    window.invalid = True


def main():
    window = pyglet.window.Window(
        fullscreen=True,
        vsync=False,
        visible=False,
    )
    try:
        resources = Resources()
        resources.make()

        pyglet.clock.schedule(lambda dt: update(window, dt))
        window.on_draw = lambda: render(window, resources)
        window.set_visible()

        pyglet.app.run()

    finally:
        window.close()


if __name__ == '__main__':
    main()

