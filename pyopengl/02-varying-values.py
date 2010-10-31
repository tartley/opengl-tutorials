'''
This shader just passes gl_Color from an input array to 
the fragment shader, which interpolates the values across the 
face (via a "varying" data type).
'''

import sys

from OpenGLContext import testingcontext
BaseContext = testingcontext.getInteractive()
from OpenGLContext.arrays import array
from OpenGL import GL as gl
from OpenGL.arrays import vbo
from OpenGL.GL.shaders import compileProgram, compileShader

VERTEX_SHADER = '''
varying vec4 vertex_color;
void main() {
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
    vertex_color = gl_Color;
}
'''
FRAGMENT_SHADER = '''
varying vec4 vertex_color;
void main() {
    gl_FragColor = vertex_color;
}
'''

class TestContext( BaseContext ):
    '''
    creates a simple vertex shader
    '''
    def OnInit( self ):
        try:
            self.shader = compileProgram(
                compileShader( VERTEX_SHADER, gl.GL_VERTEX_SHADER ),
                compileShader( FRAGMENT_SHADER, gl.GL_FRAGMENT_SHADER )
            )
        except RuntimeError, err:
            sys.stderr.write( err.args[0] )
            sys.exit( 1 )

        self.vbo = vbo.VBO(
            array( [
                [  0, 1, 0,  0,1,0 ],
                [ -1,-1, 0,  1,1,0 ],
                [  1,-1, 0,  0,1,1 ],
                [  2,-1, 0,  1,0,0 ],
                [  4,-1, 0,  0,1,0 ],
                [  4, 1, 0,  0,0,1 ],
                [  2,-1, 0,  1,0,0 ],
                [  4, 1, 0,  0,0,1 ],
                [  2, 1, 0,  0,1,1 ],
            ], 'f' )
        )

    def Render( self, mode ):
        '''
        render the scene geometry
        '''
        gl.glUseProgram( self.shader )
        try:
            self.vbo.bind()
            try:
                gl.glEnableClientState( gl.GL_VERTEX_ARRAY )
                gl.glEnableClientState( gl.GL_COLOR_ARRAY)

                gl.glVertexPointer( 3, gl.GL_FLOAT, 24, self.vbo )
                gl.glColorPointer( 3, gl.GL_FLOAT, 24, self.vbo + 12 )

                gl.glDrawArrays( gl.GL_TRIANGLES, 0, 9 )
            finally:
                self.vbo.unbind()
                gl.glDisableClientState( gl.GL_VERTEX_ARRAY )
                gl.glDisableClientState( gl.GL_COLOR_ARRAY )

        finally:
            gl.glUseProgram( 0 )


if __name__ == "__main__":
    TestContext.ContextMainLoop()

