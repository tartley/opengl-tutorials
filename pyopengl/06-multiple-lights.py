'''
This tutorial builds on earlier tutorials by adding:
 * Multiple Lights
 * GLSL Structures (for defining a Material)
 * GLSL Arrays/Looping (for processing multiple lights)
'''
import sys

from OpenGLContext import testingcontext
BaseContext = testingcontext.getInteractive()
from OpenGLContext.scenegraph.basenodes import Sphere
from OpenGL import GL as gl
from OpenGL.GL.shaders import compileProgram, compileShader


MATERIAL_STRUCT = '''
struct Material {
    vec4 ambient;
    vec4 diffuse;
    vec4 specular;
    float shininess;
};
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
        n_dot_half = pow(max(0.0,dot( 
            half_light, frag_normal
        )), shininess);
    }
    return vec2( n_dot_pos, n_dot_half);
}		
'''

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

FRAGMENT_SHADER = DLIGHT_FUNC + MATERIAL_STRUCT + '''
uniform Material material;
uniform vec4 Global_ambient;

// I got a link error: Fragment shader not supported by HW. Assuming it's
// because of this array of uniforms, which I've reimplimented as a series
// of 12 scalars, and unrolled the for loop which used to operate on the array
//uniform vec4 lights[ 12 ]; // 3 possible lights 4 vec4's each 

uniform vec4 light0_amb;
uniform vec4 light0_diff;
uniform vec4 light0_spec;
uniform vec4 light0_pos;

uniform vec4 light1_amb;
uniform vec4 light1_diff;
uniform vec4 light1_spec;
uniform vec4 light1_pos;

uniform vec4 light2_amb;
uniform vec4 light2_diff;
uniform vec4 light2_spec;
uniform vec4 light2_pos;

varying vec3 baseNormal;


vec4 lightContrib(vec4 pos, vec4 amb, vec4 diff, vec4 spec) {
    // normalized eye-coordinate Light location
    vec3 EC_Light_location = normalize(
        gl_NormalMatrix * pos.xyz
    );
    // half-vector calculation 
    vec3 Light_half = normalize(
        EC_Light_location - vec3( 0,0,-1 )
    );
    vec2 weights = dLight(
        EC_Light_location,
        Light_half,
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
    int AMBIENT = 0;
    int DIFFUSE = 1;
    int SPECULAR = 2;
    int POSITION = 3;

    fragColor = fragColor + lightContrib(
        light0_pos, light0_amb, light0_diff, light0_spec);
    fragColor = fragColor + lightContrib(
        light1_pos, light1_amb, light1_diff, light1_spec);
    fragColor = fragColor + lightContrib(
        light2_pos, light2_amb, light2_diff, light2_spec);

    gl_FragColor = fragColor;
}
'''

ATTRIBUTES = [
    'Vertex_position',
    'Vertex_normal',
]
UNIFORM_VALUES = {
    'Global_ambient': (.05,.05,.05,1.0),

    'material.ambient': (.2,.2,.2,1.0),
    'material.diffuse': (.5,.5,.5,1.0),
    'material.specular': (.9,.9,.9,1.0),
    'material.shininess': (.995,),

    'light0_pos':  (4.0,2.0,10.0,0.0),
    'light0_amb':  (.05,.05,.05,1.0),
    'light0_diff': (.3,.3,.3,1.0),
    'light0_spec': (1.0,0.0,0.0,1.0),

    'light1_pos':  (-4.0,2.0,10.0,0.0),
    'light1_amb':  (.05,.05,.05,1.0),
    'light1_diff': (.3,.3,.3,1.0),
    'light1_spec': (1.0,1.0,1.0,1.0),

    'light2_pos':  (-4.0,2.0,-10.0,0.0),
    'light2_amb':  (.05,.05,.05,1.0),
    'light2_diff': (.3,.3,.3,1.0),
    'light2_spec': (0.0,0.0,1.0,1.0),
}

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

