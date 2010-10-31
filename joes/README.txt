
OpenGL tutorial from:
http://duriansoftware.com/joe/An-intro-to-modern-OpenGL.-Chapter-1:-The-Graphics-Pipeline.htm

Uses:
    OpenGL 2.0
        jlappy-xp supports 2.1
        jlappy-ubuntu supports ?
        sushik supports 2.1
    Glut (I'll be substituting pyglet window management)
    GLEW (extension wrangler - hopefully accessible via pyglet gl bindings)

I've converted this tutorial from C to Python, but somewhere in amongst my
changes is something that stops it from working. It runs, but I just have
a blank screen. I added some immediate mode glVertex calls as a sanity check,
and they do generate a visible triangle. So I'm not sure what's up.

