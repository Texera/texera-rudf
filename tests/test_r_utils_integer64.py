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

import pytest
import rpy2.robjects as r

from texera_r.r_utils import convert_r_to_py


@pytest.mark.parametrize(
    "text", ["0", "42", "-42", "9223372036854775807", "-9223372036854775807"]
)
def test_integer64_scalar_preserves_precision(text):
    value = r.r["eval"](r.r["parse"](text=f'bit64::as.integer64("{text}")'))
    assert convert_r_to_py(value) == int(text)


def test_missing_integer64_becomes_none():
    assert convert_r_to_py(r.r("bit64::as.integer64(NA)")) is None


def test_ordinary_double_conversion_is_unchanged():
    assert convert_r_to_py(r.r("2.5")) == 2.5
