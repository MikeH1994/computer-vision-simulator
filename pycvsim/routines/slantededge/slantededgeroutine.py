import numpy as np
from numpy.typing import NDArray
from pycvsim.rendering.scenecamera import SceneCamera
from pycvsim.rendering.open3drenderer import Open3DRenderer
from pycvsim.targets.slantededgetarget import SlantedEdgeTarget
from pycvsim.algorithms.esf.edge import Edge
from pycvsim.algorithms.esf.esf import ESF
from pycvsim.algorithms.esf.gaussianesf import GaussianESF
import cv2
import scipy.ndimage
import matplotlib.pyplot as plt


class SlantedEdgeRoutine:
    camera: SceneCamera
    angle: float

    def __init__(self, camera: SceneCamera, angle: float = 5.0):
        self.camera = camera
        self.angle = angle
        self.target = SlantedEdgeTarget(5.0, angle=angle)
        self.renderer = Open3DRenderer(cameras=[self.camera], objects=[self.target])

    def generate_image(self):
        # compute the edge points
        edge_object_points = self.target.get_edge_points()
        edge_image_points = self.camera.get_pixel_point_lies_in(edge_object_points)
        p0 = edge_image_points[0]
        p1 = edge_image_points[1]
        # compute a mask that correlates to the line
        mask = np.zeros((self.camera.yres, self.camera.xres), dtype=np.uint8)
        cv2.line(mask, (int(p0[0]), int(p0[1])), (int(p1[0]), int(p1[1])), 1, thickness=6)

        image = self.renderer.render(camera_index=0, n_samples=1, return_as_8_bit=False)
        image[mask > 0] = self.renderer.render(camera_index=0, n_samples=100 ** 2, mask=mask, return_as_8_bit=False)[mask > 0]

        return image, p0, p1

    def run(self, normalize=True,  convert_to_8_bit=False, apply_gaussian=False):
        image, p0, p1 = self.generate_image()
        image = np.mean(image, axis=-1)

        if convert_to_8_bit:
            image = image.astype(np.uint8)

        if apply_gaussian:
            image = cv2.GaussianBlur(image, (9, 9), 0)  # scipy.ndimage.gaussian_filter(image, 0.2)

        edge = Edge(p0, p1)
        esf = GaussianESF(image, edge, boundary_region=50, search_region=30)
        lsf = GaussianLSF()
        esf_x, esf_f = esf.esf_x, esf.esf_f
        return esf_x, esf_f, image