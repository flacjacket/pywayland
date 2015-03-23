# Copyright 2015 Sean Vig
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This provides a way to run pywayland.pywayland-scanner.py without installing
# pywayland by adding ../ to sys.path and running the script.
# This is only intended for use when development on the git version, the entry
# point should be setup when pywayland is installed.

import sys
import os

this_dir = os.path.split(os.path.abspath(__file__))[0]
root_dir = os.path.split(this_dir)[0]
sys.path.append(root_dir)

if __name__ == '__main__':
    from pywayland.pywayland_scanner import main
    main()
