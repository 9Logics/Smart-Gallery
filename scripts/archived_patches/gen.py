import math

def generate_shape(cx, cy, r_inner, r_outer, points, offset_angle=0):
    path = []
    angle_step = math.pi / points
    
    for i in range(points * 2):
        angle = i * angle_step + offset_angle
        r = r_outer if i % 2 == 0 else r_inner
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        
        if i == 0:
            path.append(f'M {x:.1f} {y:.1f}')
        else:
            # We can use Q or L. For smooth morphs, let's use C or just L if we want jagged.
            # Actually, standard M3 shapes use cubic beziers for smoothness.
            # Let's generate a polygon first and see if it looks good.
            path.append(f'L {x:.1f} {y:.1f}')
    
    path.append('Z')
    return ' '.join(path)

# Star (sharp inner radius)
star = generate_shape(50, 50, 30, 50, 10)
# Scallop (rounded/shallow inner radius)
scallop = generate_shape(50, 50, 45, 50, 10)
# Circle
circle = generate_shape(50, 50, 50, 50, 10)

print("Star:", star)
print("Scallop:", scallop)
print("Circle:", circle)
