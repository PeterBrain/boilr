"""initialization"""
try:
    from ._version import version as __version__
    from ._version import version_tuple as __version_tuple__
except ImportError:
    __version__ = "unknown version"
    __version_tuple__ = (0, 0, "unknown version")

major = __version_tuple__[0]
minor = __version_tuple__[1]
dev_info = __version_tuple__[2] if len(__version_tuple__) > 2 else None
extra_info = __version_tuple__[3] if len(__version_tuple__) > 3 else None
dev_version = ".".join(map(str, __version_tuple__[:3]))
