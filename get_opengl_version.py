import glfw
import logging

def get_opengl_version_glfw():
    if not glfw.init():
        return None, "GLFW initialization failed"

    try:
        # Create invisible window (no UI)
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 1)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 0)

        window = glfw.create_window(1, 1, "GL Check", None, None)
        if not window:
            return None, "Failed to create GLFW window"

        glfw.make_context_current(window)

        from OpenGL.GL import glGetString, GL_VERSION

        version_bytes = glGetString(GL_VERSION)
        version = version_bytes.decode() if version_bytes else None

        glfw.destroy_window(window)
        return version, None

    except Exception as e:
        return None, str(e)

    finally:
        glfw.terminate()


def validate_opengl(min_major, min_minor, logger: logging.Logger):
    version_str, error = get_opengl_version_glfw()

    if error or not version_str:
        logger.error(f"⚠ OpenGL Detection Failed: {error or 'Unknown error'}")
        return False

    logger.info(f"Detected OpenGL: {version_str}")

    try:
        # Parse version safely (handles vendor strings)
        ver_num = version_str.split(' ')[0]
        parts = ver_num.split('.')

        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0

        if major > min_major or (major == min_major and minor >= min_minor):
            logger.info(f"  ✓ Pass: OpenGL {major}.{minor} >= {min_major}.{min_minor}")
            return True

        logger.error(f"  ✗ Fail: OpenGL {major}.{minor} < {min_major}.{min_minor}")
        return False

    except Exception as e:
        logger.error(f"⚠ Version parsing failed: {e}")
        return False


# Example usage
#if __name__ == "__main__":
#    logging.basicConfig(level=logging.INFO)
#    validate_opengl(3, 3, logging.getLogger("GLCheck"))