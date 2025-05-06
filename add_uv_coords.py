import math
import re

def add_spherical_uv_to_egg(file_path, output_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    vertex_pattern = re.compile(r'<Vertex> (\d+) {')
    vertex_pos_pattern = re.compile(r'(\-?\d+\.?\d*) (\-?\d+\.?\d*) (\-?\d+\.?\d*)')

    # Parse all vertices
    vertices = []
    for line in lines:
        match = vertex_pos_pattern.search(line)
        if match:
            x, y, z = map(float, match.groups())
            vertices.append((x, y, z))

    if not vertices:
        raise ValueError("No vertices found in the .egg file.")

    modified_lines = []
    vertex_index = -1
    uv_inserted = False

    for i, line in enumerate(lines):
        modified_lines.append(line)

        if '<Vertex>' in line:
            match = vertex_pattern.search(line)
            if match:
                vertex_index = int(match.group(1))
                uv_inserted = False

        if vertex_index != -1 and not uv_inserted:
            match = vertex_pos_pattern.search(line)
            if match:
                x, y, z = map(float, match.groups())

                # Normalize to unit sphere (optional, assuming sphere already centered)
                length = math.sqrt(x**2 + y**2 + z**2)
                if length == 0:
                    u = v = 0.5  # Default value at center
                else:
                    nx, ny, nz = x / length, y / length, z / length

                    u = 0.5 + (math.atan2(ny, nx) / (2 * math.pi))   # Longitude
                    v = 0.5 - (math.asin(nz) / math.pi)              # Latitude

                uv_line = f'  <UV> {{ {u:.6f} {v:.6f} }}\n'
                modified_lines.append(uv_line)
                uv_inserted = True
                vertex_index = -1

    with open(output_path, 'w') as out_file:
        out_file.writelines(modified_lines)


if __name__ == "__main__":
    input_file = 'assets/models/planet_sphere.egg'
    output_file = 'assets/models/planet_sphere_with_uv.egg'
    add_spherical_uv_to_egg(input_file, output_file)