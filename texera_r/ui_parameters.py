# This file is part of texera-rudf
#
# Copyright (c) 2024 The Texera Team
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from functools import lru_cache
from importlib.resources import files

import rpy2.robjects as robjects

UI_PARAMETERS_API_VERSION = 1
UI_PARAMETERS_HEADER = "# Texera UI parameters: SDK v1\n"


@lru_cache(maxsize=1)
def _loader():
    source = files("texera_r").joinpath("ui_parameters.R").read_text(encoding="utf-8")
    return robjects.r(source)


def load_user_function(code):
    """Load legacy R scripts or compiler-generated calls into the parameter SDK."""
    code = code.replace("\r\n", "\n").replace("\r", "\n")
    if code.startswith(UI_PARAMETERS_HEADER):
        return _loader()(code)
    if code.startswith("# Texera UI parameters:"):
        raise ValueError("Unsupported Texera UI parameter SDK version.")
    return robjects.r(code)
