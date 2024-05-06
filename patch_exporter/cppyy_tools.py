import os
import platform
import sys
from pathlib import Path

import cppyy


def is_arm_mac():
    is_arm = platform.machine() in ("arm64", "aarch64")
    is_mac = sys.platform == "darwin"

    return is_arm and is_mac


def get_naoth_dir():
    """
    TODO add readme
    """
    return Path(os.environ["NAOTH_REPO"]).resolve()


def get_toolchain_dir():
    """
    TODO add readme
    """
    return Path(os.environ["TOOLCHAIN_REPO"]).resolve()


def setup_shared_lib(naoth_dir=None, toolchain_dir=None):
    """
    load shared lib and general + patch specific includes
    # TODO the patch specific stuff should eventually go into separate function
    """
    naoth_dir = get_naoth_dir() if not naoth_dir else Path(naoth_dir).resolve()
    toolchain_dir = (
        get_toolchain_dir() if not toolchain_dir else Path(toolchain_dir).resolve()
    )

    if is_arm_mac():
        setup_shared_lib_arm_mac(naoth_dir, toolchain_dir)
        return

    shared_lib_name = "libscriptsim.so"
    if sys.platform.startswith("win32"):
        shared_lib_name = "scriptsim.dll"
    elif sys.platform.startswith("darwin"):
        shared_lib_name = "libscriptsim.dylib"

    # fmt: off
    lib_path = Path(naoth_dir) / Path("NaoTHSoccer/dist/Native/") / shared_lib_name
    cppyy.load_library(str(lib_path))

    # add relevant include paths to allow mapping our code
    include_path = Path(naoth_dir) / Path("Framework/Commons/Source")
    cppyy.add_include_path(str(include_path))

    include_path = Path(naoth_dir) / Path("NaoTHSoccer/Source")
    cppyy.add_include_path(str(include_path))

    include_path = Path(toolchain_dir) / Path("toolchain_native/extern/include")
    cppyy.add_include_path(str(include_path))

    include_path = Path(toolchain_dir) / Path("toolchain_native/extern/include/glib-2.0")
    cppyy.add_include_path(str(include_path))

    include_path = Path(toolchain_dir) / Path("toolchain_native/extern/lib/glib-2.0/include")
    cppyy.add_include_path(str(include_path))

    # include platform
    cppyy.include(str(naoth_dir / Path("Framework/Commons/Source/PlatformInterface/Platform.h")))
    cppyy.include(str(naoth_dir / Path("Framework/Platforms/Source/DummySimulator/DummySimulator.h")))

    # make more representations available to cppyy
    cppyy.include(str(naoth_dir / Path("Framework/Commons/Source/ModuleFramework/ModuleManager.h")))
    cppyy.include(str(naoth_dir / Path("NaoTHSoccer/Source/Cognition/Cognition.h")))
    cppyy.include(str(naoth_dir / Path("NaoTHSoccer/Source/Representations/Perception/BallCandidates.h")))
    cppyy.include(str(naoth_dir / Path("NaoTHSoccer/Source/Representations/Perception/CameraMatrix.h")))

    # fmt: on


def setup_shared_lib_arm_mac(naoth_dir=None, toolchain_dir=None):
    naoth_dir = get_naoth_dir() if not naoth_dir else Path(naoth_dir).resolve()
    toolchain_dir = (
        get_toolchain_dir() if not toolchain_dir else Path(toolchain_dir).resolve()
    )

    # fmt: off
    lib_path = Path(naoth_dir) / Path("NaoTHSoccer/dist/Native/libscriptsim.dylib")
    cppyy.load_library(str(lib_path))

    # add relevant include paths to allow mapping our code
    include_path = Path(naoth_dir) / Path("Framework/Commons/Source")
    cppyy.add_include_path(str(include_path))

    include_path = Path(naoth_dir) / Path("NaoTHSoccer/Source")
    cppyy.add_include_path(str(include_path))


    include_path = Path("/opt/homebrew/opt/eigen/include/eigen3")
    cppyy.add_include_path(str(include_path))

    include_path = Path("/opt/homebrew/opt/glib/include/glib-2.0")
    cppyy.add_include_path(str(include_path))

    include_path = Path("/opt/homebrew/lib/glib-2.0/include")
    cppyy.add_include_path(str(include_path))

    include_path = Path(toolchain_dir) / Path("toolchain_native/extern/include")
    cppyy.add_include_path(str(include_path))

    # include platform
    cppyy.include(str(naoth_dir / Path("Framework/Commons/Source/PlatformInterface/Platform.h")))
    cppyy.include(str(naoth_dir / Path("Framework/Platforms/Source/DummySimulator/DummySimulator.h")))

    # make more representations available to cppyy
    cppyy.include(str(naoth_dir / Path("Framework/Commons/Source/ModuleFramework/ModuleManager.h")))
    cppyy.include(str(naoth_dir / Path("NaoTHSoccer/Source/Cognition/Cognition.h")))
    cppyy.include(str(naoth_dir / Path("NaoTHSoccer/Source/Representations/Perception/BallCandidates.h")))
    cppyy.include(str(naoth_dir / Path("NaoTHSoccer/Source/Representations/Perception/CameraMatrix.h")))

    # fmt: on
