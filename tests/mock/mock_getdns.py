import getdns

# mock getdns results to take dynamic attributes
class MockGetdnsResult:
    def __init__(self, attrs):
        self.attrs = attrs

    def __getattr__(self, name):
        try:
            return self.attrs[name]
        except KeyError:
            msg = "'{0}' object has no attribute '{1}'"
            raise AttributeError(msg.format(type(self).__name__, name))

def mock_getdns_result(status, result = {}):
    result.update({'status': status})
    return MockGetdnsResult(result)