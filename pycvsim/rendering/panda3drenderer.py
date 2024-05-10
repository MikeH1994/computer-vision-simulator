from typing import List
import cv2
import matplotlib.pyplot as plt
import time
import numpy as np
import open3d as o3d
from direct.showbase.ShowBase import ShowBase
from numpy.typing import NDArray
from pycvsim.rendering.baserenderer import BaseRenderer
from panda3d.core import LPoint3f, GraphicsBuffer, DisplayRegion, LVecBase4f
from panda3d.core import NodePath, AntialiasAttrib, FrameBufferProperties, GraphicsPipe, Texture, GraphicsOutput
from panda3d.core import WindowProperties
from pycvsim.sceneobjects.sceneobject import SceneObject
from .scenecamera import SceneCamera


class Panda3DRenderer(BaseRenderer):
    def __init__(self, cameras: List[SceneCamera] = None, objects: List[SceneObject] = None):
        self.renderer = ShowBase(windowType='offscreen')
        super().__init__(cameras, objects)

    def add_object(self, obj: SceneObject):
        self.objects.append(obj)
        obj.node_path.reparentTo(self.renderer.render)

    def set_render_camera_fov(self, hfov, vfov):
        self.renderer.camLens.setFov(hfov, vfov)

    def set_render_camera_position(self, pos):
        x, y, z = pos
        self.renderer.camera.setPos(x, y, z)

    def set_render_camera_lookpos(self, pos: NDArray, up: NDArray):
        pos = LPoint3f(pos[0], pos[1], pos[2])
        up = LPoint3f(up[0], up[1], up[2])
        self.renderer.camera.lookAt(pos, up)

    def render_image(self, camera_index, apply_distortion=True, apply_noise=True, n_samples=32,
                     antialiasing=AntialiasAttrib.MAuto, return_as_8_bit=True):
        if camera_index >= len(self.cameras):
            raise Exception("Camera index {} is out of bounds".format(camera_index))
        camera = self.cameras[camera_index]
        self.set_render_camera_fov(*camera.get_fov(include_safe_zone=apply_distortion))
        self.set_render_camera_position(camera.pos)
        self.set_render_camera_lookpos(camera.get_lookpos(), camera.get_up())
        xres, yres = camera.get_res(include_safe_zone=apply_distortion)

        dtype = np.uint8 if return_as_8_bit else np.float32
        window, bgr_tex = self.get_texture_buffer(xres, yres, n_samples, dtype=dtype)

        for obj in self.objects:
            obj.node_path.setAntialias(antialiasing)

        self.renderer.graphicsEngine.renderFrame()
        img = np.frombuffer(bgr_tex.getRamImage(), dtype=dtype)
        img.shape = (bgr_tex.getYSize(), bgr_tex.getXSize(), bgr_tex.getNumComponents())
        # flip vertically, discard the last channel and go from rgb to bgr
        img = np.copy(img[:, ::-1, 2::-1])

        if dtype == np.float32:
            img *= 255.0

        if apply_distortion:
            img = camera.distortion_model.distort_image(img)

        self.renderer.graphicsEngine.removeWindow(self.renderer.graphicsEngine.windows[1])

        if apply_noise and camera.noise_model is not None:
            img = camera.noise_model.apply(img)

        return img

    def get_texture_buffer(self, xres, yres, n_samples, dtype=np.float32,
                           background: NDArray = np.array([0.2, 0.2, 0.2])):
        assert(dtype == np.float32 or dtype == np.uint8)

        fb_prop = FrameBufferProperties()
        if dtype == np.float32:
            fb_prop.set_srgb_color(False)
            fb_prop.set_float_color(True)
            fb_prop.set_rgba_bits(32, 32, 32, 32)
            fb_prop.set_multisamples(n_samples)
            fb_prop.set_depth_bits(32)
            fb_prop.set_color_bits(32)

        else:
            fb_prop.setRgbaBits(8, 8, 8, 8)
            fb_prop.setMultisamples(n_samples)
            fb_prop.setDepthBits(24)
            fb_prop.set_color_bits(24)

        win_prop = WindowProperties.size(xres, yres)
        window: GraphicsBuffer = self.renderer.graphicsEngine.makeOutput(self.renderer.pipe, "cameraview", 0, fb_prop,
                                                                         win_prop, GraphicsPipe.BFRefuseWindow,
                                                                         self.renderer.win.getGsg(), self.renderer.win)
        disp_region: DisplayRegion = window.makeDisplayRegion()
        disp_region.setCamera(self.renderer.cam)
        bgr_tex = Texture()
        window.addRenderTexture(bgr_tex, GraphicsOutput.RTMCopyRam, GraphicsOutput.RTPColor)
        bkg = background
        window.set_clear_color(LVecBase4f(bkg[0], bkg[1], bkg[2], 1.0))

        return window, bgr_tex
