import os
import runpy

_t100 = runpy.run_path(os.path.join(os.path.dirname(__file__), 'msg_T100_launch.py'))
generate_launch_description = _t100['generate_launch_description']
