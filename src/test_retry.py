from robust_call import call_with_retry, is_transient


class FakeAPIError(Exception):
    def __init__(self, code):
        super().__init__(f"fake error {code}")
        self.code = code


def flaky(fail_times, error):
    state = {"calls": 0}

    def call():
        state["calls"] += 1
        if state["calls"] <= fail_times:
            raise error
        return "answer"

    return call


cases = [
    ("A: two 503 errors, then success", flaky(2, FakeAPIError(503))),
    ("B: 503 every time", flaky(99, FakeAPIError(503))),
    ("C: wrong API key (code 400)", flaky(99, FakeAPIError(400))),
    ("D: broken JSON twice, then success", flaky(2, ValueError("No valid JSON came back"))),
]

for name, make_call in cases:
    print(name)
    outcome = call_with_retry(make_call, is_transient, base_wait=0.1)
    print("  result:", outcome)
    print()