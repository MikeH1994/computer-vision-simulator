import numpy as np
import cv2
from typing import Tuple
from numpy.typing import NDArray


class DistortionModel:
    def __init__(self, camera_matrix: NDArray, distortion_coeffs: NDArray, image_size: Tuple[int, int]):
        assert(distortion_coeffs.shape == (5,))
        self.width, self.height = image_size
        self.camera_matrix = camera_matrix
        self.distortion_coeffs = distortion_coeffs
        self.undistort_map_x, self.undistort_map_y = cv2.initUndistortRectifyMap(camera_matrix, distortion_coeffs, None,
                                                                                 None, image_size, cv2.CV_32FC1)
        # self.distort_map_x, self.distort_map_y = self.invert_maps(self.undistort_map_x, self.undistort_map_y)
        self.distort_map_x, self.distort_map_y = self.compute_distortion_map(camera_matrix, distortion_coeffs,
                                                                             image_size)

    def distort_image(self, image: NDArray):
        return cv2.remap(image, self.distort_map_x, self.distort_map_y, cv2.INTER_LINEAR)

    def undistort_image(self, image: NDArray):
        #return cv2.remap(image, self.undistort_map_x, self.undistort_map_y, cv2.INTER_LINEAR)
        return cv2.undistort(image, self.camera_matrix, self.distortion_coeffs, None, None)

    @staticmethod
    def compute_distortion_map(camera_matrix, distortion_coeffs, size):
        fx = camera_matrix[0][0]
        fy = camera_matrix[1][1]
        cx = camera_matrix[0][2]
        cy = camera_matrix[1][2]
        k1, k2, p1, p2, k3 = distortion_coeffs
        width, height = size

        x, y = np.meshgrid(np.arange(width), np.arange(height))
        x = (x - cx) / fx
        y = (y - cy) / fy
        r = np.sqrt(x**2 + y**2)

        x_dist = x * (1 + k1*r**2 + k2*r**4 + k3*r**6) + (2 * p1 * x * y + p2 * (r**2 + 2 * x * x))
        y_dist = y * (1 + k1*r**2 + k2*r**4 + k3*r**6) + (p1 * (r**2 + 2 * y * y) + 2 * p2 * x * y)
        x_dist = x_dist * fx + cx
        y_dist = y_dist * fy + cy

        return x_dist.astype(np.float32), y_dist.astype(np.float32)

    def invert_maps(self, map_x, map_y):
        F = np.zeros((map_x.shape[0], map_x.shape[1], 2), dtype=np.float32)
        F[:, :, 0] = map_x
        F[:, :, 1] = map_y

        (h, w) = F.shape[:2]  # (h, w, 2), "xymap"
        I = np.zeros_like(F)
        I[:, :, 1], I[:, :, 0] = np.indices((h, w))  # identity map
        P = np.copy(I)
        for i in range(10):
            correction = I - cv2.remap(F, P, None, interpolation=cv2.INTER_LINEAR)
            P += correction * 0.5
        return P[:, :, 0], P[:, :, 1]

