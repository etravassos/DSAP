import struct
import getdns

from src.core.utils import constants as const
from tests.core.utils import constants as tconst

from src.core.exception.DsapException import DsapNoAnswerException
from src.core.queries.DNSQueryTypes import SecureDNSQuery, InsecureDNSQuery, StubDNSQuery

from tests.core.queries.test_query import DNSQueryTestCase
from tests.mock.mock_getdns import mock_getdns_result
from django.test import TestCase
from mock import patch, call

const.supported_tlds |= {"tld"} # patch constant to have ".tld" tld for tests

class SecureDNSQueryTestCase(DNSQueryTestCase):

    def setUp(self):
        self.extensions = {
            "dnssec_return_only_secure": getdns.EXTENSION_TRUE,
            "return_both_v4_and_v6": getdns.EXTENSION_TRUE
            }

        self.zone = 1
        self.q = SecureDNSQuery(self.zone)

    def test_queries_should_be_over_TCP_only(self):
        # print self.q.ctx.dns_transport_list
        pass


class InsecureDNSQueryTestCase(DNSQueryTestCase):
    
    def setUp(self):
        super(InsecureDNSQueryTestCase, self).setUp()
        self.q = InsecureDNSQuery(self.zone)


class StubDNSQueryTestCase(InsecureDNSQueryTestCase):

    def setUp(self):
        super(StubDNSQueryTestCase, self).setUp()
        self.q = StubDNSQuery(self.zone)
        
    def test_resolution_type_should_be_stub(self):
        self.assertEquals(self.q.ctx.resolution_type, getdns.RESOLUTION_STUB)

    def test_run_fails_without_upstream_servers_set(self):
        self.assertRaisesMessage(Exception, 'No upstream servers set for stub DNS query', self.q.run, getdns.RRTYPE_DNSKEY)

    def test_set_upstream_servers(self):
        upstream_servers = [{'address_type': 'IPv4', 'address_data': '8.8.8.8'}]

        self.q.upstream_servers(upstream_servers)
        self.assertEquals(self.q.upstream_recursive_servers, upstream_servers)

    @patch(tconst.TEST.DNS_QUERY_MODULE_RUN)
    def test_all_upstream_servers_queried(self, mock_getdns_run):
        mock_getdns_run.return_value = [{ 'rdata_raw': 0x1 }]
        
        ip = [{'address_type': 'IPv4', 'address_data': '1.1.1.1'}, {'address_type': 'IPv4', 'address_data': '2.2.2.2'}, {'address_type': 'IPv4', 'address_data': '3.3.3.3'}]
        q = StubDNSQuery('domain.tld').upstream_servers( ip )
        
        records = q.run(getdns.RRTYPE_AAAA)
        self.assertEquals([{'rdata_raw': 0x1}], records)        

        mock_getdns_run.assert_has_calls( [ 
            call(getdns.RRTYPE_AAAA, "answer", upstream_recursive_server=ip[0]), 
            call(getdns.RRTYPE_AAAA, "answer", upstream_recursive_server=ip[1]), 
            call(getdns.RRTYPE_AAAA, "answer", upstream_recursive_server=ip[2])])

    @patch(tconst.TEST.DNS_QUERY_MODULE_RUN)
    def test_upstream_servers_disagree_on_number_of_records(self, mock_getdns_run):

        def run_side_effect(self, query, section="answer", upstream_recursive_server=None):
            if upstream_recursive_server['address_data'] == '1.1.1.1':
                return [{"flags": const.FLAGS.KSK, "protocol":3, "algorithm":12, "public_key": b'1'}]
            else:
                return [{"flags": const.FLAGS.KSK, "protocol":3, "algorithm":12, "public_key": b'1'}, 
                        {"flags": const.FLAGS.ZSK, "protocol":3, "algorithm":12, "public_key": b'1'}]
        mock_getdns_run.side_effect = run_side_effect

        ip = [{'address_type': 'IPv4', 'address_data': '1.1.1.1'}, {'address_type': 'IPv4', 'address_data': '2.2.2.2'}]
        q = StubDNSQuery('domain.tld').upstream_servers( ip )

        self.assertRaisesMessage(Exception, "domain.tld: nameservers not in sync for 'DNSKEY' data", q.run, getdns.RRTYPE_DNSKEY)
    
    @patch(tconst.TEST.DNS_QUERY_MODULE_RUN)
    def test_upstream_servers_disagree_on_record(self, mock_getdns_run):

        def run_side_effect(self, query, section="answer", upstream_recursive_server=None):
            if upstream_recursive_server['address_data'] == '1.1.1.1':
                # return [{'rdata_raw': struct.pack('!HBB', const.FLAGS.KSK, 3, 8) }]
                return [{"flags": const.FLAGS.KSK, "protocol":3, "algorithm":8, "public_key": b'1'}]
            else:
                return [{"flags": const.FLAGS.KSK, "protocol":3, "algorithm":8, "public_key": b'12'}]
                # return [{'rdata_raw': struct.pack('!HBB', const.FLAGS.KSK, 3, 8) + b'1' }]
        mock_getdns_run.side_effect = run_side_effect

        ip = [{'address_type': 'IPv4', 'address_data': '1.1.1.1'}, {'address_type': 'IPv4', 'address_data': '2.2.2.2'}]
        q = StubDNSQuery('domain.tld').upstream_servers( ip )

        self.assertRaisesMessage(Exception, "domain.tld: nameservers not in sync for 'DNSKEY' data", q.run, getdns.RRTYPE_DNSKEY)