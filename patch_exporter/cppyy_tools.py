import cppyy
import os
import sys
from pathlib import Path


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


def setup_shared_lib(naoth_dir, toolchain_dir):
    """
    load shared lib and general + patch specific includes
    # TODO the patch specific stuff should eventually go into separate function
    """
    shared_lib_name = "libscriptsim.so"
    if sys.platform.startswith("win32"):
        shared_lib_name = "scriptsim.dll"
    elif sys.platform.startswith("darwin"):
        shared_lib_name = "libscriptsim.dylib"
    
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
