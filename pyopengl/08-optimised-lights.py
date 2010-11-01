'''
This tutorial builds on earlier tutorials by adding:
 # Optimizing the directional-lights, doing pre-calcs in the Vertex shader
 # Using constant/common declaration blocks
'''
import sys

from OpenGLContext import testingcontext
BaseContext = testingcontext.getInteractive()
from OpenGLContext.scenegraph.basenodes import Sphere
from OpenGL import GL as gl
from OpenGL.GL.shaders import compileProgram, compileShader

# EC for 'eye-space coords'

LIGHT_CONST = '''
uniform vec4 light0_pos;
uniform vec4 light0_amb;
uniform vec4 light0_diff;
uniform vec4 light0_spec;

uniform vec4 light1_pos;
uniform vec4 light1_amb;
uniform vec4 light1_diff;
uniform vec4 light1_spec;

uniform vec4 light2_pos;
uniform vec4 light2_amb;
uniform vec4 light2_diff;
uniform vec4 light2_spec;

// precalc these values in vertex shader (which is quicker, since it is
// excuted once per vertex, not once per fragment) and use the results
// in the fragment shader
varying vec3 light0_ec_location;
varying vec3 light0_ec_half;
varying vec3 light1_ec_location;
varying vec3 light1_ec_half;
varying vec3 light2_ec_location;
varying vec3 light2_ec_half;

varying vec3 baseNormal;
'''

DLIGHT_FUNC = '''
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
        n_dot_half = pow(
            max(
                0.0,
                dot(half_light, frag_normal)
            ),
            shininess);
    }
    return vec2( n_dot_pos, n_dot_half);
}		
'''

VERTEX_SHADER = LIGHT_CONST + '''
attribute vec3 Vertex_position;
attribute vec3 Vertex_normal;
void main() {
    gl_Position = gl_ModelViewProjectionMatrix * vec4( Vertex_position, 1.0);
    baseNormal = gl_NormalMatrix * normalize(Vertex_normal);

    // half-vector calculation 
    light0_ec_location = normalize(gl_NormalMatrix * light0_pos.xyz);
    light0_ec_half = normalize( light0_ec_location - vec3( 0,0,-1 ));

    light1_ec_location = normalize(gl_NormalMatrix * light1_pos.xyz);
    light1_ec_half = normalize( light1_ec_location - vec3( 0,0,-1 ));

    light2_ec_location = normalize(gl_NormalMatrix * light2_pos.xyz);
    light2_ec_half = normalize( light2_ec_location - vec3( 0,0,-1 ));
}
'''

FRAGMENT_SHADER = LIGHT_CONST + DLIGHT_FUNC + '''
struct Material {
    vec4 ambient;
    vec4 diffuse;
    vec4 specular;
    float shininess;
};
uniform Material material;
uniform vec4 Global_ambient;

vec4 lightContrib(
    vec4 pos,
    vec4 amb,
    vec4 diff,
    vec4 spec,
    vec3 ec_location,
    vec3 ec_half_angle
) {
    vec2 weights = dLight(
        ec_location,
        ec_half_angle,
        baseNormal,
        material.shininess
    );
    return 
        (amb * material.ambient) + 
        (diff * material.diffuse * weights.x) +
        (spec * material.specular * weights.y);
}


void main() {
    vec4 fragColor = Global_ambient * material.ambient;

    fragColor = fragColor + lightContrib(
        light0_pos, light0_amb, light0_diff, light0_spec,
        light0_ec_location, light0_ec_half);
    fragColor = fragColor + lightContrib(
        light1_pos, light1_amb, light1_diff, light1_spec,
        light1_ec_location, light1_ec_half);
    fragColor = fragColor + lightContrib(
        light2_pos, light2_amb, light2_diff, light2_spec,
        light2_ec_location, light2_ec_half);

    gl_FragColor = fragColor;
}
'''

ATTRIBUTES = [
    'Vertex_position',
    'Vertex_normal',
]
UNIFORM_VALUES = {
    'Global_ambient': (0.1, 0.1, 0.1, 1.0),

    'material.ambient':  (0.2, 0.2, 0.2, 1.0),
    'material.diffuse':  (0.7, 0.7, 0.7, 1.0),
    'material.specular': (0.7, 0.7, 0.7, 1.0),
    'material.shininess': (50,),

    'light0_pos':  (0.0, 8.0, 0.0, 0.0),
    'light0_amb':  (0.5, 0.5, 0.5, 1.0),
    'light0_diff': (0.5, 0.5, 0.5, 1.0),
    'light0_spec': (0.5, 0.5, 0.5, 1.0),

    'light1_pos':  (2.0, 4.0, 8.0, 0.0),
    'light1_amb':  (0.2, 0.5, 0.1, 1.0),
    'light1_diff': (0.2, 0.5, 0.1, 1.0),
    'light1_spec': (0.2, 0.5, 0.1, 1.0),

    'light2_pos':  (8.0, 4.0, 2.0, 0.0),
    'light2_amb':  (0.1, 0.2, 0.5, 1.0),
    'light2_diff': (0.1, 0.2, 0.5, 1.0),
    'light2_spec': (0.1, 0.2, 0.5, 1.0),
}

class TestContext( BaseContext ):
    '''
    creates a simple shader
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

        self.uniforms = {}
        for name in UNIFORM_VALUES:
            location = gl.glGetUniformLocation( self.shader, name )
            if location in (None,-1):
                print 'Warning, no uniform: %s'%( name )
            self.uniforms[name] = location

        for name in ATTRIBUTES:
			location = gl.glGetAttribLocation( self.shader, name )
			if location in (None,-1):
				print 'Warning, no attribute: %s'%( name )
			setattr( self, name + '_loc', location )


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
                for uniform, value in UNIFORM_VALUES.items():
                    location = self.uniforms.get( uniform )
                    if location not in (None,-1):
                        if len(value) == 4:
                            gl.glUniform4f( location, *value )
                        elif len(value) == 3:
                            gl.glUniform3f( location, *value )
                        elif len(value) == 1:
                            gl.glUniform1f( location, *value )

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

