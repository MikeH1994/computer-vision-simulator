import numpy as np
from pycvsim.sceneobjects.targets.checkerboardtarget import CheckerbordTarget
from pycvsim.rendering.panda3drenderer import Panda3DRenderer
from pycvsim.rendering.scenecamera import SceneCamera
from pycvsim.core.image_utils import overlay_points_on_image
import matplotlib.pyplot as plt

mesh = CheckerbordTarget((9, 8), (0.05, 0.05), board_thickness=0.02, color_bkg=(128, 0, 0), board_boundary=0.05)
cameras = [SceneCamera(pos=np.array([0.0, 0.0, -1.5]), res=(1600, 1024), hfov=30.0)]
renderer = Panda3DRenderer(cameras=cameras, objects=[mesh])
image_points = renderer.cameras[0].get_pixel_point_lies_in(mesh.get_boundary_region())
img_1 = renderer.render(0)
plt.imshow(img_1)
plt.show()
