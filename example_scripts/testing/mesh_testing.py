import numpy as np
from pycvsim.sceneobjects.sceneobject import SceneObject
from pycvsim.rendering.panda3drenderer import Panda3DRenderer
from pycvsim.camera.basecamera import BaseCamera
import matplotlib.pyplot as plt

cameras = [
    BaseCamera.create_camera_from_euler_angles(pos=np.array([0.0, 0.0, -3.0]),
                                               euler_angles=np.array([0, 0, 0]),
                                               res=(640, 512), hfov=30.0),
]

obj_mesh = SceneObject.load_armadillo()
renderer = Panda3DRenderer(cameras=cameras)
renderer.add_object(obj_mesh)

fig = plt.figure()
ax_1 = fig.add_subplot(111)
im_1 = ax_1.imshow(np.zeros((640, 512, 3), dtype=np.float32))

#plt.ion()

while True:
    for theta in np.linspace(-180, 180, 20):
        angles = np.array([0.0, theta, 0.0])
        obj_mesh.set_euler_angles(angles)
        img_1 = renderer.render(0)
        plt.imshow(img_1)
        plt.show()
        """
        im_1.set_data(img_1)
        fig.canvas.draw()
        fig.canvas.flush_events()
        plt.pause(0.05)
        """