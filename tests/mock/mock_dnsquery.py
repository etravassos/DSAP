import base64
import copy
import struct
from binascii import unhexlify

import getdns
from src.core.utils import constants as const

results = {
    'tld': {
        getdns.RRTYPE_DS: [],
        getdns.RRTYPE_NS: [
            {'nsdname': "1.tld-servers.tld."},
        ]
    },
    'zone.tld.': {
        getdns.RRTYPE_NS: [
            {'nsdname': "ns0.zone.tld."},
        ],
        getdns.RRTYPE_CDS: [
            {   'algorithm': const.DS_ALGS.ECDSAP256SHA256._code,
                'digest_type': const.DIGEST_TYPES.SHA_256._code,
                'key_tag': 43801,
                'digest': b'fe36c7ec1a7de661a2741e78e289cf19aa14cfd3fb519d0dcd249efbca0b4aac'
                }
        ],
        getdns.RRTYPE_DNSKEY: [
            # {'flags': const.FLAGS.KSK, 'rdata_raw': struct.pack('!HBB', const.FLAGS.KSK, 3, 12) + base64.b64decode(
            #     'BDtDa2UxLe7cdDs9bX/X1Y/UXuhJnDrGDRuVQW0BBo8QF1Pr959WBI5QylNxyKp9Rm4yslb1hj4BQUEUWpOLWw==')}
            {   "flags": const.FLAGS.KSK, 
                "protocol": const.PROTOCOL.VALID,
                "algorithm": const.DS_ALGS.ECDSAP256SHA256._code,
                "public_key": base64.b64decode('UWtSMFJHRXlWWGhNWlRkalpFUnpPV0pZ TDFneFdTOVZXSFZvU201RWNrZEVVblZX VVZjd1FrSnZPRkZHTVZCeU9UVTVWMEpK TlZGNWJFNTRlVXR3T1ZKdE5IbHpiR0l4 YUdvMFFsRlZSVlZYY0U5TVYzYzlQUT09')
                }
        ]
    }
}

addresses = {
    '1.tld-servers.tld.': [
        {'address_type': 'IPv4', 'address_data': '1.1.1.1'},
    ],
    'ns0.zone.tld.': [
        {'address_type': 'IPv4', 'address_data': '2.2.2.2'},
    ]
}


def mock_dnsquery_run(name="", result=None):
    mock_results = copy.deepcopy(results)
    if result:
        mock_results[name].update(result)

    def run(self, query, section="answer"):
        result = mock_results[self.zone][query]
        # print "%s: run(%s, %s) = %s" % (self.zone, query, section, results)
        return answer(result)

    return run  # mocked method


def mock_dnsquery_address(name="", result={}):
    def address(self, family="IPv4"):
        if self.zone == name:
            return answer(result)  # mocked result
        return addresses[self.zone]

    return address  # mocked method


def answer(result):
    if type(result) is Exception:
        raise result
    return result
