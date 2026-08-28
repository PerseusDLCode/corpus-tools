from __future__ import annotations

import pytest

from schmidt_cit_unwrap import UnbalancedCitWrapperError, unwrap_doubled_cit

WRAPPED = (
    "present. <mentioned>An</mentioned> for <mentioned>a</mentioned>: <cit>\n"
    "              <cit>\n"
    "                <quote>an hair,</quote>\n"
    '                <ref target="urn:cts:engLit:shakespeare.tmp.globe:1.2">Tp. I, 2, 30</ref>\n'
    "              </cit>\n"
    "\n"
    "            </cit>. <cit>\n"
    "              <cit>\n"
    "                <quote>an happy end,</quote>\n"
    '                <ref target="urn:cts:engLit:shakespeare.jn.globe:3.2">John III, 2, 10</ref>\n'
    "              </cit>\n"
    "\n"
    "            </cit>. "
)

UNWRAPPED = (
    "present. <mentioned>An</mentioned> for <mentioned>a</mentioned>: <cit>\n"
    "                <quote>an hair,</quote>\n"
    '                <ref target="urn:cts:engLit:shakespeare.tmp.globe:1.2">Tp. I, 2, 30</ref>\n'
    "              </cit>. <cit>\n"
    "                <quote>an happy end,</quote>\n"
    '                <ref target="urn:cts:engLit:shakespeare.jn.globe:3.2">John III, 2, 10</ref>\n'
    "              </cit>. "
)


def test_unwrap_doubled_cit_removes_outer_wrapper():
    result, count = unwrap_doubled_cit(WRAPPED)
    assert result == UNWRAPPED
    assert count == 2


def test_unwrap_doubled_cit_leaves_unwrapped_text_alone():
    result, count = unwrap_doubled_cit(UNWRAPPED)
    assert result == UNWRAPPED
    assert count == 0


def test_unwrap_doubled_cit_raises_on_unbalanced_patterns():
    truncated = WRAPPED.replace(
        "              </cit>\n\n            </cit>. ", "              </cit>. ", 1
    )
    with pytest.raises(UnbalancedCitWrapperError):
        unwrap_doubled_cit(truncated)
