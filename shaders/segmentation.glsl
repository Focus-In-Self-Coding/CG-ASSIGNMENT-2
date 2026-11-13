#version 330 core
out vec4 FragColor;
uniform vec3 u_object_color;
void main() {
    // Flat, unlit color. Each object has a unique 24-bit instance ID.
    FragColor = vec4(u_object_color, 1.0);
}
