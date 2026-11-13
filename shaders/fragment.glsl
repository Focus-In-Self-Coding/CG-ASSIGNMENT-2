#version 330 core
in vec3 v_world_position;
in vec3 v_world_normal;
out vec4 FragColor;

uniform vec3 u_color;
uniform vec3 u_light_pos;
uniform vec3 u_view_pos;
uniform vec3 u_light_color;

void main() {
    vec3 normal = normalize(v_world_normal);
    vec3 light_dir = normalize(u_light_pos - v_world_position);
    vec3 view_dir = normalize(u_view_pos - v_world_position);
    vec3 reflect_dir = reflect(-light_dir, normal);

    float ambient = 0.22;
    float diffuse = max(dot(normal, light_dir), 0.0);
    float specular = pow(max(dot(view_dir, reflect_dir), 0.0), 32.0) * 0.18;
    vec3 lighting = (ambient + diffuse + specular) * u_light_color;
    FragColor = vec4(u_color * lighting, 1.0);
}
