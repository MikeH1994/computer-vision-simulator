import numpy as np
from pycvsim.sceneobjects.calibrationtargets.checkerboardtarget import CheckerbordTarget
from pycvsim.sceneobjects.sceneobject import SceneObject
from pycvsim.rendering.scenerenderer import SceneRenderer
from pycvsim.rendering.scenecamera import SceneCamera
from pycvsim.core.image_utils import overlay_points_on_image
import matplotlib.pyplot as plt
import cv2

obj = CheckerbordTarget((7, 6), (0.05, 0.05), board_thickness=0.02,
                        color_1=(255, 255, 255), color_2=(0, 0, 0),
                        color_bkg=(128, 0, 0), board_boundary=0.05, name="checkerboard")
cameras = [SceneCamera(pos=np.array([0.0, 0.0, -1.5]), res=(720, 720), hfov=30.0, safe_zone=0)]
renderer = SceneRenderer(cameras=cameras, objects=[obj])
obj.set_euler_angles(np.array([0, 0, 20.0]))
object_points = obj.get_object_points()
image_points = renderer.cameras[0].calc_pixel_point_lies_in(object_points)

img_render = renderer.render_image(0, apply_distortion=True)
img_overlayed = overlay_points_on_image(img_render, image_points)
plt.imshow(img_overlayed)
plt.show()
