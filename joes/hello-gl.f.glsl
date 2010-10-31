#version 110

uniform float fade_factor;
uniform sampler2D textures[2];

varying vec2 texcoord;

void main()
{
    //gl_FragColor = mix(
    //    texture2D(textures[0], texcoord),
    //    texture2D(textures[1], texcoord),
    //    fade_factor
    //);

    // gl_FragColor = texture2D(textures[0], texcoord);

    gl_FragColor = vec4(0.1, 0.6, 0.5, 1.0);
}

