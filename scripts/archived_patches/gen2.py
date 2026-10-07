import math

def smooth_star(cx, cy, r_inner, r_outer, points, smoothing=0.3):
    path = []
    angle_step = math.pi / points
    
    # We will generate control points for cubic beziers
    # For a point at angle A, the tangent is A + pi/2
    # Control points will extend along the tangent by distance smoothing * distance_to_next_point
    
    pts = []
    for i in range(points * 2):
        angle = i * angle_step
        r = r_outer if i % 2 == 0 else r_inner
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        # tangent vector
        tx = math.cos(angle + math.pi/2)
        ty = math.sin(angle + math.pi/2)
        pts.append((x, y, tx, ty, r))
        
    for i in range(len(pts)):
        p0 = pts[i]
        p1 = pts[(i + 1) % len(pts)]
        
        # dist approx
        dist = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        cp_len = dist * smoothing
        
        cp1x = p0[0] + p0[2] * cp_len
        cp1y = p0[1] + p0[3] * cp_len
        
        cp2x = p1[0] - p1[2] * cp_len
        cp2y = p1[1] - p1[3] * cp_len
        
        if i == 0:
            path.append(f'M {p0[0]:.1f} {p0[1]:.1f}')
        
        path.append(f'C {cp1x:.1f} {cp1y:.1f}, {cp2x:.1f} {cp2y:.1f}, {p1[0]:.1f} {p1[1]:.1f}')
        
    path.append('Z')
    return ' '.join(path)

s1 = smooth_star(50, 50, 35, 50, 10, 0.2) # spiky star
s2 = smooth_star(50, 50, 46, 50, 10, 0.4) # smooth scallop
s3 = smooth_star(50, 50, 50, 50, 10, 0.3) # almost circle

print("S1:", s1)
print("S2:", s2)
print("S3:", s3)
