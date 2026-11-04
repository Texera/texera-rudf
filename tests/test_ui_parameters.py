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
from rpy2.rinterface_lib.embedded import RRuntimeError

from texera_r.ui_parameters import load_user_function, UI_PARAMETERS_HEADER


def script(value, name="count"):
    return (
        UI_PARAMETERS_HEADER
        + f'''texera_ui_parameters({{
      count <- UiParameter("{name}", AttributeType$INT)$value
      function() count
    }}, parameters=list(count=list(type="integer", value="{value}", inputType="")),
    attribute_types=list(INT="integer"), resources=list())'''
    )


def test_each_operator_keeps_its_own_parameter_environment():
    first = load_user_function(script("7"))
    second = load_user_function(script("9"))
    assert first()[0] == 7
    assert second()[0] == 9
    assert first()[0] == 7
    assert not r.r("exists('UiParameter', envir=.GlobalEnv, inherits=FALSE)")[0]


def test_legacy_scripts_and_windows_line_endings():
    assert load_user_function("function() { 42L }\r\n")()[0] == 42
    assert load_user_function(script("7").replace("\n", "\r\n"))()[0] == 7


def test_missing_parameters_report_the_name():
    with pytest.raises(
        RRuntimeError, match="No UI parameter value found for 'missing'"
    ):
        load_user_function(script("7", name="missing"))


def test_unknown_sdk_versions_are_rejected_explicitly():
    with pytest.raises(ValueError, match="Unsupported Texera UI parameter SDK version"):
        load_user_function("# Texera UI parameters: SDK v2\nfunction() 1")
