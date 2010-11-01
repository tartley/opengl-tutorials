'''
This tutorial builds on earlier tutorials by adding:
    * 	ambient lighting 
    * 	diffuse lighting 
    * 	directional lights (e.g. the Sun)
    * 	normals, the normal matrix
'''
import sys

from OpenGLContext import testingcontext
BaseContext = testingcontext.getInteractive()
from OpenGLContext.arrays import array
from OpenGL import GL as gl
from OpenGL.arrays import vbo
from OpenGL.GL.shaders import compileProgram, compileShader

DLIGHT_FUNC = """
float dLight( 
    in vec3 light_pos, // normalised light position
    in vec3 frag_normal // normalised geometry normal
) {
    // returns vec2( ambientMult, diffuseMult )
    float n_dot_pos = max( 0.0, dot( 
        frag_normal, light_pos
    ));
    return n_dot_pos;
}		
"""

VERTEX_SHADER = DLIGHT_FUNC + '''
uniform vec4 Global_ambient;
uniform vec4 Light_ambient;
uniform vec4 Light_diffuse;
uniform vec3 Light_location;
uniform vec4 Material_ambient;
uniform vec4 Material_diffuse;
attribute vec3 Vertex_position;
attribute vec3 Vertex_normal;
varying vec4 baseColor;
void main() {
    gl_Position = gl_ModelViewProjectionMatrix * vec4( 
        Vertex_position, 1.0
    );
    vec3 EC_Light_location = gl_NormalMatrix * Light_location;
    float diffuse_weight = dLight(
        normalize(EC_Light_location),
        normalize(gl_NormalMatrix * Vertex_normal)
    );
    baseColor = clamp( 
    (
        // global component 
        (Global_ambient * Material_ambient)
        // material's interaction with light's contribution 
        // to the ambient lighting...
        + (Light_ambient * Material_ambient)
        // material's interaction with the direct light from 
        // the light.
        + (Light_diffuse * Material_diffuse * diffuse_weight)
    ), 0.0, 1.0);
}
'''

FRAGMENT_SHADER = '''
varying vec4 baseColor;
void main() {
    gl_FragColor = baseColor;
}
'''

VERTEX_DATA = [
#      x  y  z,  r  g  b
    [ -1, 0, 0, -1, 0, 1],
    [  0, 0, 1, -1, 0, 2],
    [  0, 1, 1, -1, 0, 2],
    [ -1, 0, 0, -1, 0, 1],
    [  0, 1, 1, -1, 0, 2],
    [ -1, 1, 0, -1, 0, 1],
    [  0, 0, 1, -1, 0, 2],
    [  1, 0, 1,  1, 0, 2],
    [  1, 1, 1,  1, 0, 2],
    [  0, 0, 1, -1, 0, 2],
    [  1, 1, 1,  1, 0, 2],
    [  0, 1, 1, -1, 0, 2],
    [  1, 0, 1,  1, 0, 2],
    [  2, 0, 0,  1, 0, 1],
    [  2, 1, 0,  1, 0, 1],
    [  1, 0, 1,  1, 0, 2],
    [  2, 1, 0,  1, 0, 1],
    [  1, 1, 1,  1, 0, 2],
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

        for uniform in (
            'Global_ambient',
            'Light_ambient',
            'Light_diffuse',
            'Light_location',
            'Material_ambient',
            'Material_diffuse',
        ):
            location = gl.glGetUniformLocation( self.shader, uniform )
            if location in ( None, -1 ):
                print 'Warning, no uniform: %s'%( uniform )
            setattr( self, uniform+ '_loc', location )

        for attribute in (
            'Vertex_position',
            'Vertex_normal',
        ):
            location = gl.glGetAttribLocation( self.shader, attribute )
            if location in ( None, -1 ):
                print 'Warning, no attribute: %s'%( attribute )
            setattr( self, attribute + '_loc', location )
        

    def Render( self, mode ):
        '''
        render the scene geometry
        '''
        gl.glUseProgram( self.shader )
        try:
            self.vbo.bind()
            try:
                gl.glUniform4f( self.Global_ambient_loc, .9,.05,.05,.1 )
                gl.glUniform4f( self.Light_ambient_loc, .2,.2,.2, 1.0 )
                gl.glUniform4f( self.Light_diffuse_loc, 1,1,1,1 )
                gl.glUniform3f( self.Light_location_loc, 2,2,10 )
                gl.glUniform4f( self.Material_ambient_loc, .2,.2,.2, 1.0 )
                gl.glUniform4f( self.Material_diffuse_loc, 1,1,1, 1 )

                stride = 6*4
                gl.glEnableVertexAttribArray( self.Vertex_position_loc )
                gl.glEnableVertexAttribArray( self.Vertex_normal_loc )
                gl.glVertexAttribPointer( 
                    self.Vertex_position_loc, 
                    3, gl.GL_FLOAT,False, stride, self.vbo 
                )
                gl.glVertexAttribPointer( 
                    self.Vertex_normal_loc, 
                    3, gl.GL_FLOAT,False, stride, self.vbo+12
                )
                
                gl.glDrawArrays( gl.GL_TRIANGLES, 0, 18 )
            finally:
                self.vbo.unbind()
                gl.glDisableVertexAttribArray( self.Vertex_position_loc )
                gl.glDisableVertexAttribArray( self.Vertex_normal_loc )

        finally:
            gl.glUseProgram( 0 )


if __name__ == "__main__":
    TestContext.ContextMainLoop()

