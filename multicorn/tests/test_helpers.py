from attest import Tests, assert_hook
import attest

from multicorn.requests import CONTEXT as c
from multicorn.requests.requests import as_request, WithRealAttributes
from multicorn.requests.requests import as_chain, cut_request
from multicorn.python_executor import PythonExecutor


suite = Tests()


@suite.test
def test_simple_helpers():
    root = as_request([1, 2, 3, 4, 5])
    filter = root.filter(c > 2)
    request = filter.map(c)
    chain = as_chain(request)
    assert len(chain) == 3
    left, right = cut_request(request, filter)
    assert len(as_chain(left)) == 2
    # The right part as a len of totallen - len(left) + 1,
    # because we append a dummy context
    right_chain = as_chain(right)
    assert isinstance(right_chain[0], c.__class__)
    assert isinstance(WithRealAttributes(right_chain[1]).subject, c.__class__)
    assert len(right_chain) == 2
    left_chain = as_chain(left)
    assert left_chain[-1] == filter
    full_result = list(PythonExecutor.from_request(request).execute(()))
    first_part_result = list(PythonExecutor.from_request(request).execute(()))
    second_part_result = list(
        PythonExecutor.from_request(request).execute((first_part_result,)))
    assert full_result == second_part_result
