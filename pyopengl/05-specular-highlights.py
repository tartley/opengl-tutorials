'''
This tutorial builds on earlier tutorials by adding:
    * 	specular lighting (Phong Lighting)
    * 	specular lighting (Blinn-Phong Lighting)
    * 	per-fragment lighting
    * 	Sphere geometry object (indexed rendering)
'''
import sys

from OpenGLContext import testingcontext
BaseContext = testingcontext.getInteractive()
from OpenGLContext.arrays import array
from OpenGLContext.scenegraph.basenodes import Sphere
from OpenGL import GL as gl
from OpenGL.arrays import vbo
from OpenGL.GL.shaders import compileProgram, compileShader

DLIGHT_FUNC = """
vec2 dLight( 
    in vec3 light_pos, // light position
    in vec3 half_light, // half-way vector between light and view
    in vec3 frag_normal, // geometry normal
    in float shininess
) {
    // returns vec2( ambientMult, diffuseMult )
    float n_dot_pos = max( 0.0, dot( 
        frag_normal, light_pos
    ));
    float n_dot_half = 0.0;
    if (n_dot_pos > -.05) {
        n_dot_half = pow(max(0.0,dot( 
            half_light, frag_normal
        )), shininess);
    }
    return vec2( n_dot_pos, n_dot_half);
}		
"""

VERTEX_SHADER = '''
attribute vec3 Vertex_position;
attribute vec3 Vertex_normal;
varying vec3 baseNormal;
void main() {
    gl_Position = gl_ModelViewProjectionMatrix * vec4( 
        Vertex_position, 1.0
    );
    baseNormal = gl_NormalMatrix * normalize(Vertex_normal);
}
'''

FRAGMENT_SHADER = DLIGHT_FUNC + '''
uniform vec4 Global_ambient;
uniform vec4 Light_ambient;
uniform vec4 Light_diffuse;
uniform vec4 Light_specular;
uniform vec3 Light_location;
uniform float Material_shininess;
uniform vec4 Material_specular;
uniform vec4 Material_ambient;
uniform vec4 Material_diffuse;
varying vec3 baseNormal;
void main() {
    // normalized eye-coordinate Light location
    vec3 EC_Light_location = normalize(
        gl_NormalMatrix * Light_location
    );
    // half-vector calculation 
    vec3 Light_half = normalize(
        EC_Light_location - vec3( 0,0,-1 )
    );
    vec2 weights = dLight(
        EC_Light_location,
        Light_half,
        baseNormal,
        Material_shininess
    );
    gl_FragColor = clamp( 
    (
        (Global_ambient * Material_ambient)
        + (Light_ambient * Material_ambient)
        + (Light_diffuse * Material_diffuse * weights.x)
        // material's shininess is the only change here...
        + (Light_specular * Material_specular * weights.y)
    ), 0.0, 1.0);
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

        self.coords, self.indices, self.count = Sphere(radius=1).compile()

        for uniform in (
            'Global_ambient',
            'Light_ambient',
            'Light_diffuse',
            'Light_location',
            'Light_specular',
            'Material_ambient',
            'Material_diffuse',
            'Material_shininess',
            'Material_specular',
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
            self.coords.bind()
            self.indices.bind()
            stride = self.coords.data[0].nbytes
            try:
                gl.glUniform4f( self.Global_ambient_loc, .05,.05,.05,.1 )
                gl.glUniform4f( self.Light_ambient_loc, .1,.1,.1, 1.0 )
                gl.glUniform4f( self.Light_diffuse_loc, .25,.25,.25,1 )

                gl.glUniform4f( self.Light_specular_loc, 0.0,1.0,0,1 )
                gl.glUniform3f( self.Light_location_loc, 6,2,4 )
                gl.glUniform4f( self.Material_ambient_loc, .1,.1,.1, 1.0 )
                gl.glUniform4f( self.Material_diffuse_loc, .15,.15,.15, 1 )

                gl.glUniform4f( self.Material_specular_loc, 1.0,1.0,1.0, 1.0 )
                gl.glUniform1f( self.Material_shininess_loc, .95)
                gl.glEnableVertexAttribArray( self.Vertex_position_loc )
                gl.glEnableVertexAttribArray( self.Vertex_normal_loc )
                gl.glVertexAttribPointer( 
                    self.Vertex_position_loc, 
                    3, gl.GL_FLOAT, False, stride, self.coords
                )
                gl.glVertexAttribPointer( 
                    self.Vertex_normal_loc, 
                    3, gl.GL_FLOAT, False, stride, self.coords+(5*4)
                )

                gl.glEnableVertexAttribArray( self.Vertex_position_loc )
                gl.glEnableVertexAttribArray( self.Vertex_normal_loc )
                gl.glVertexAttribPointer( 
                    self.Vertex_position_loc, 
                    3, gl.GL_FLOAT,False, stride, self.coords
                )
                gl.glVertexAttribPointer( 
                    self.Vertex_normal_loc, 
                    3, gl.GL_FLOAT,False, stride, self.coords + (5 * 4)
                )
                
                gl.glDrawElements(
                    gl.GL_TRIANGLES,
                    self.count,
                    gl.GL_UNSIGNED_SHORT,
                    self.indices
                )
            finally:
                self.coords.unbind()
                self.indices.unbind()
                gl.glDisableVertexAttribArray( self.Vertex_position_loc )
                gl.glDisableVertexAttribArray( self.Vertex_normal_loc )

        finally:
            gl.glUseProgram( 0 )


if __name__ == "__main__":
    TestContext.ContextMainLoop()

