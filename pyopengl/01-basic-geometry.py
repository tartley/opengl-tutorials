
from OpenGLContext import testingcontext

BaseContext = testingcontext.getInteractive()

from OpenGL import GL as gl
from OpenGL.arrays import vbo
from OpenGLContext.arrays import array
from OpenGL.GL.shaders import compileProgram, compileShader


VERTEX_SHADER = '''
void main() {
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
}
'''
FRAGMENT_SHADER = '''
void main() {
    gl_FragColor = vec4( 0, 1, 0, 1 );
}
'''

class TestContext( BaseContext ):
    '''
    creates a simple vertex shader
    '''
    def OnInit( self ):
        self.shader = compileProgram(
            compileShader( VERTEX_SHADER, gl.GL_VERTEX_SHADER ),
            compileShader( FRAGMENT_SHADER, gl.GL_FRAGMENT_SHADER )
        )
        self.vbo = vbo.VBO(
            array( [
                [  0, 1, 0 ],
                [ -1,-1, 0 ],
                [  1,-1, 0 ],
                [  2,-1, 0 ],
                [  4,-1, 0 ],
                [  4, 1, 0 ],
                [  2,-1, 0 ],
                [  4, 1, 0 ],
                [  2, 1, 0 ],

            ], 'f')
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
                gl.glVertexPointerf( self.vbo )
                gl.glDrawArrays(gl.GL_TRIANGLES, 0, 9)
            finally:
                self.vbo.unbind()
                gl.glDisableClientState( gl.GL_VERTEX_ARRAY )
        finally:
            gl.glUseProgram( 0 )


if __name__ == "__main__":
    TestContext.ContextMainLoop()

