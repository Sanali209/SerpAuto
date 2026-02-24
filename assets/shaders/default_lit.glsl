#version 330

#if defined VERTEX_SHADER

in vec3 in_position;
in vec3 in_normal;
in vec2 in_texcoord_0;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

out vec3 v_vert;
out vec3 v_norm;
out vec2 v_text;

void main() {
    mat4 m_view_model = m_view * m_model;
    vec4 p = m_view_model * vec4(in_position, 1.0);
    gl_Position = m_proj * p;
    v_vert = p.xyz;
    v_norm = mat3(m_view_model) * in_normal;
    v_text = in_texcoord_0;
}

#elif defined FRAGMENT_SHADER

in vec3 v_vert;
in vec3 v_norm;
in vec2 v_text;

uniform vec4 diffuse_color;
uniform vec3 light_pos; // In view space

out vec4 f_color;

void main() {
    float ambient = 0.2;
    vec3 n = normalize(v_norm);
    vec3 l = normalize(light_pos - v_vert);
    float diff = max(dot(n, l), 0.0);
    
    // Simple specular
    vec3 v = normalize(-v_vert);
    vec3 h = normalize(l + v);
    float spec = pow(max(dot(n, h), 0.0), 32.0) * 0.5;

    vec3 color = diffuse_color.rgb * (diff + ambient) + spec;
    f_color = vec4(color, diffuse_color.a);
}

#endif
