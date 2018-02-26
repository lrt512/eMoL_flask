import sys

version = sys.version_info
if version.major < 3:
    sys.exit(-1)
elif version.minor < 6:
    sys.exit(-1)
else:
    sys.exit(0)