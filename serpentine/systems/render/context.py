import moderngl
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class RenderContext:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RenderContext, cls).__new__(cls)
            cls._instance.ctx = None
            cls._instance.fbo = None
            cls._instance.width = 640
            cls._instance.height = 480
        return cls._instance

    def init_context(self, width: int = 640, height: int = 480):
        if self.ctx:
            return

        try:
            # Create a standalone context (headless)
            self.ctx = moderngl.create_context(standalone=True)
            logger.info("ModernGL context created (standalone).")

            self.resize(width, height)

            # Enable depth test and blending
            self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE | moderngl.BLEND)

        except Exception as e:
            logger.error(f"Failed to create ModernGL context: {e}")
            raise e

    def resize(self, width: int, height: int):
        self.width = width
        self.height = height

        if self.fbo:
            self.fbo.release()

        # Create texture and depth buffer
        self.texture = self.ctx.texture((width, height), 4)
        self.depth_attachment = self.ctx.depth_texture((width, height))

        # Create framebuffer
        self.fbo = self.ctx.framebuffer(
            color_attachments=[self.texture],
            depth_attachment=self.depth_attachment
        )
        logger.info(f"Framebuffer resized to {width}x{height}")

    def clear(self, color: Tuple[float, float, float, float] = (0.1, 0.1, 0.1, 1.0)):
        if self.fbo:
            self.fbo.clear(*color)

    def read_pixels(self) -> bytes:
        if self.fbo:
            return self.fbo.read(components=4)
        return b""

    def release(self):
        if self.fbo:
            self.fbo.release()
            self.fbo = None
        if self.ctx:
            self.ctx.release()
            self.ctx = None
        logger.info("ModernGL context released.")
