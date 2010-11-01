'''
Demonstrates use of uniform values to tween between two vertex buffers.
'''

import sys

from OpenGLContext import testingcontext
BaseContext = testingcontext.getInteractive()
from OpenGLContext.arrays import array
from OpenGLContext.events.timer import Timer
from OpenGL import GL as gl
from OpenGL.arrays import vbo
from OpenGL.GL.shaders import compileProgram, compileShader

VERTEX_SHADER = '''
uniform float tween;
attribute vec3 position;
attribute vec3 tweened;
attribute vec3 color;
varying vec4 baseColor;
void main() {
    gl_Position = gl_ModelViewProjectionMatrix * mix(
        vec4( position,1.0),
        vec4( tweened,1.0),
        tween
    );
    baseColor = vec4(color,1.0);
}
'''

FRAGMENT_SHADER = '''
varying vec4 baseColor;
void main() {
    gl_FragColor = baseColor;
}
'''

VERTEX_DATA = [
#      pos1   ,  pos2   ,  r  g  b
    [  0, 1, 0,  1, 3, 0,  0, 1, 0 ],
    [ -1,-1, 0, -1,-1, 0,  1, 1, 0 ],
    [  1,-1, 0,  1,-1, 0,  0, 1, 1 ],
    [  2,-1, 0,  2,-1, 0,  1, 0, 0 ],
    [  4,-1, 0,  4,-1, 0,  0, 1, 0 ],
    [  4, 1, 0,  4, 9, 0,  0, 0, 1 ],
    [  2,-1, 0,  2,-1, 0,  1, 0, 0 ],
    [  4, 1, 0,  1, 3, 0,  0, 0, 1 ],
    [  2, 1, 0,  1,-1, 0,  0, 1, 1 ],
]


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
            array( VERTEX_DATA, 'f' )
        )

        self.position = gl.glGetAttribLocation( self.shader, 'position' )
        self.tweened = gl.glGetAttribLocation( self.shader, 'tweened' )
        self.color = gl.glGetAttribLocation( self.shader, 'color' )
        self.tween = gl.glGetUniformLocation( self.shader, 'tween' )

        self.time = Timer( duration = 2.0, repeating = 1 )
        self.time.addEventHandler( "fraction", self.OnTimerFraction )
        self.time.register( self )
        self.time.start()


    def Render( self, mode ):
        '''
        render the scene geometry
        '''
        gl.glUseProgram( self.shader )
        try:
            # set the value of attributes passed to the vertex shader
            gl.glUniform1f( self.tween, self.tween_fraction )
            
            self.vbo.bind()
            try:
                gl.glEnableVertexAttribArray( self.position )
                gl.glEnableVertexAttribArray( self.tweened )
                gl.glEnableVertexAttribArray( self.color )

                stride = 9 * 4
                gl.glVertexAttribPointer( 
                    self.position, 
                    3, gl.GL_FLOAT, False, stride, self.vbo 
                )
                gl.glVertexAttribPointer( 
                    self.tweened, 
                    3, gl.GL_FLOAT, False, stride, self.vbo+12
                )
                gl.glVertexAttribPointer( 
                    self.color, 
                    3, gl.GL_FLOAT, False, stride, self.vbo+24
                )

                gl.glDrawArrays( gl.GL_TRIANGLES, 0, 9 )
            finally:
                self.vbo.unbind()
                gl.glDisableVertexAttribArray( self.position )
                gl.glDisableVertexAttribArray( self.tweened )
                gl.glDisableVertexAttribArray( self.color )

        finally:
            gl.glUseProgram( 0 )


    tween_fraction = 0.0

    def OnTimerFraction( self, event ):
        frac = event.fraction()
        if frac > .5:
            frac = 1.0-frac 
        frac *= 2
        self.tween_fraction =frac
        self.triggerRedraw()



if __name__ == "__main__":
    TestContext.ContextMainLoop()

