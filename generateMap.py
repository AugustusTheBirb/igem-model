from PIL import Image
import math
from tqdm import tqdm
import numpy as np
from fastbarnes import interpolation
  

input_data = np.loadtxt("./map model/testData.csv", delimiter=",")

lon_lat_data = input_data[:, 0:2]
qff_values = input_data[:, 2]


input_image = Image.open("./map model/lietuva_high_res.png")
width, height = input_image.size
print(width,height)
pixel_map = input_image.load()
# (0-255,0-255,0-255,0-255,) RGBA format

def viridis(t):
    """
    Viridis colormap function that maps input [0,1] to RGB tuple [0,255].
    
    Args:
        t (float): Input value between 0 and 1
        
    Returns:
        tuple: RGB values as integers between 0 and 255
    """
    # Clamp input to [0, 1]
    t = max(0, min(1, t))
    
    # Viridis control points (normalized RGB values)
    colors = [
        (0.267004, 0.004874, 0.329415),  # Dark purple
        (0.282623, 0.140926, 0.457517),  # Purple
        (0.253935, 0.265254, 0.529983),  # Blue-purple
        (0.206756, 0.371758, 0.553117),  # Blue
        (0.163625, 0.471133, 0.558148),  # Blue-teal
        (0.127568, 0.566949, 0.550556),  # Teal
        (0.134692, 0.658636, 0.517649),  # Green-teal
        (0.266941, 0.748751, 0.440573),  # Green
        (0.477504, 0.821444, 0.318195),  # Yellow-green
        (0.741388, 0.873449, 0.149561),  # Yellow
        (0.993248, 0.906157, 0.143936)   # Light yellow
    ]
    
    # Find the appropriate segment
    n_colors = len(colors) - 1
    segment = t * n_colors
    i = int(segment)
    
    # Handle edge case where t = 1.0
    if i >= n_colors:
        i = n_colors - 1
        local_t = 1.0
    else:
        local_t = segment - i
    
    # Linear interpolation between two control points
    r1, g1, b1 = colors[i]
    r2, g2, b2 = colors[i + 1]
    
    r = r1 + (r2 - r1) * local_t
    g = g1 + (g2 - g1) * local_t
    b = b1 + (b2 - b1) * local_t
    
    # Convert to 0-255 range and return as integers
    return (int(r * 255), int(g * 255), int(b * 255))

def cmap(z):
    c1 = (102,155,188,255)
    c2 = (193,33,38,255)
    return tuple(int(z*c1[i] + (1-z)*c2[i]) for i in range(4))

def euclidean_distance(x1,y1,x2,y2):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)

def nearest_neighbor(x,y,points):
    min_dist = math.inf 
    min_point = 0
    for point in points:
        dist = euclidean_distance(x,y,point[0],point[1])
        if min_dist > dist: 
            min_dist = dist
            min_point = point[2]
    return min_point, min_dist

resolution = 32.0
#step = np.asarray([1,height/width], dtype=np.float64)
step=1
x0 = np.asarray([0,0], dtype=np.float64)
size = (width, height)
sigma = 80
field = interpolation.barnes(lon_lat_data, qff_values, sigma, x0, step, size)
with open("new.txt", "w") as f:
    for i in range(field.shape[0]):
        f.write("\n")
        for j in range(field.shape[1]):
            f.write(str(field[i][j])+",")
print("done")
print(field.shape)
for i in tqdm(range(width)):
    for j in range(height):
        if pixel_map[i,j][3] != 0 and pixel_map[i,j][3] != 255: pixel_map[i,j] = (0,0,0,255) 
        elif pixel_map[i,j][3] == 0:
            temp = field[j,i]
            if temp == np.nan: pixel_map[i,j] = (0,0,255,255) 
            else: pixel_map[i,j] = viridis(field[j][i])
print("done")
input_image.save("./map model/finished_map.png",format="png")
 