import struct
import getdns

from src.core.utils import constants as const
from tests.core.utils import constants as tconst

from src.core.exception.DsapException import DsapNoAnswerException
from src.core.queries.DNSQuery import DNSQuery
from src.core.queries.DNSQueryTypes import SecureDNSQuery, InsecureDNSQuery, StubDNSQuery

from tests.mock.mock_getdns import mock_getdns_result
from django.test import TestCase
from mock import patch, call

const.supported_tlds |= {"tld"} # patch constant to have ".tld" tld for tests


class DNSQueryTestCase(TestCase):

    def setUp(self):
        self.extensions = {"return_both_v4_and_v6" : getdns.EXTENSION_TRUE}
        self.zone = 'zone.tld'
        self.q = DNSQuery(self.zone, self.extensions)

    def test_context_set(self):
        self.assertIsInstance(self.q.ctx, getdns.Context)

    def test_extensions_set(self):
        self.assertIsNotNone(self.q.ext)
        self.assertEquals(self.q.ext, self.extensions)

    def test_zone_set(self):
        self.assertEquals(self.q.zone, self.zone)
        

@patch(tconst.TEST.CORE_MODULE_GETDNS_CONTEXT, autospec=True)
class DNSQueryMockTestCase(TestCase):

    def test_run_generic_error(self, mock_getdns_context):
        mock_getdns_context.return_value.general.side_effect = getdns.error
        self.assertRaisesMessage(Exception, "domain.tld: getdns error for 'A' query - ''", DNSQuery('domain.tld').run, getdns.RRTYPE_A)

    def test_run_RESPSTATUS_NO_SECURE_ANSWERS(self, mock_getdns_context):
        mock_getdns_context.return_value.general.return_value = mock_getdns_result(status=getdns.RESPSTATUS_NO_SECURE_ANSWERS)
        self.assertRaisesMessage(Exception, "domain.tld: Secure delegation not established. No secure answers found for 'A' query", DNSQuery('domain.tld').run, getdns.RRTYPE_A)

    def test_run_RESPSTATUS_NO_NAME(self, mock_getdns_context):
        mock_getdns_context.return_value.general.return_value = mock_getdns_result(status=getdns.RESPSTATUS_NO_NAME)
        self.assertRaisesMessage(Exception, "domain.tld: zone not found for 'A' query", DNSQuery('domain.tld').run, getdns.RRTYPE_A)

    def test_run_RESPSTATUS_RESPSTATUS_ALL_TIMEOUT(self, mock_getdns_context):
        mock_getdns_context.return_value.general.return_value = mock_getdns_result(status=getdns.RESPSTATUS_ALL_TIMEOUT)
        self.assertRaisesMessage(Exception, "domain.tld: DNS timeout for 'A' query", DNSQuery('domain.tld').run, getdns.RRTYPE_A)

    def test_run_go_good_response(self, mock_getdns_context):
        mock_getdns_context.return_value.general.return_value = mock_getdns_result(status=-1)
        self.assertRaisesMessage(Exception, "domain.tld: bad DNS response 'A' query - '-1'", DNSQuery('domain.tld').run, getdns.RRTYPE_A)

    def test_run_no_replies(self, mock_getdns_context):
        mock_getdns_context.return_value.general.return_value = mock_getdns_result(status=getdns.RESPSTATUS_GOOD)
        self.assertRaisesMessage(DsapNoAnswerException, "domain.tld: no answers for", DNSQuery('domain.tld').run, getdns.RRTYPE_A)

    def test_run_no_replies_with_correct_type(self, mock_getdns_context):
        mock_getdns_context.return_value.general.return_value = mock_getdns_result(status=getdns.RESPSTATUS_GOOD, result={
            'replies_tree': [{
                "answer": [
                    {
                        'type': getdns.RRTYPE_NS,
                        'rdata': {}
                    }                    
                ]
            }]})
        self.assertRaisesMessage(DsapNoAnswerException, "domain.tld: no answers for 'A' query", DNSQuery('domain.tld').run, getdns.RRTYPE_A)

    def test_run_no_replies_in_specific_section(self, mock_getdns_context):
        mock_getdns_context.return_value.general.return_value = mock_getdns_result(status=getdns.RESPSTATUS_GOOD, result={
            'replies_tree': [{
                "answer": [
                    {
                        'type': getdns.RRTYPE_NS,
                        'rdata': {}
                    }                    
                ]
            }]})
        self.assertRaisesMessage(KeyError, "authority", DNSQuery('domain.tld').run, getdns.RRTYPE_NS, "authority")

    def test_run_replies_with_correct_type_in_specific_section_passes(self, mock_getdns_context):
        mock_getdns_context.return_value.general.return_value = mock_getdns_result(status=getdns.RESPSTATUS_GOOD, result={
            'replies_tree': [{
                "authority": [
                    {
                        'type': getdns.RRTYPE_NS,
                        'rdata': { "nsdname": "abc" }
                    }                    
                ]
            }]})
        records = DNSQuery('domain.tld').run(query=getdns.RRTYPE_NS, section="authority")
        self.assertEquals(records, [{ "nsdname": "abc" }])

    def test_address_generic_error(self, mock_getdns_context):
        mock_getdns_context.return_value.address.side_effect = getdns.error
        self.assertRaisesMessage(Exception, "domain.tld: getdns error for address - ''", InsecureDNSQuery('domain.tld').address)

    def test_address_no_good_response(self, mock_getdns_context):
        mock_getdns_context.return_value.address.return_value = mock_getdns_result(status=-1)
        self.assertRaisesMessage(Exception, "domain.tld: Unable to resolve address - '-1'", InsecureDNSQuery('domain.tld').address)

    def test_address_passes(self, mock_getdns_context):
        mock_getdns_context.return_value.address.return_value = mock_getdns_result(status=getdns.RESPSTATUS_GOOD, result={
            'just_address_answers': [
                {
                    'address_type': 'IPv6',
                    'address_data': '::'
                }
            ]})
        address = InsecureDNSQuery('domain.tld').address()
        self.assertEquals(address, [{'address_type': 'IPv6', 'address_data': '::'}])

    def test_address_ipv4_only(self, mock_getdns_context):
        mock_getdns_context.return_value.address.return_value = mock_getdns_result(status=getdns.RESPSTATUS_GOOD, result={
            'just_address_answers': [
                {
                    'address_type': 'IPv6',
                    'address_data': '::'
                },
                {
                    'address_type': 'IPv4',
                    'address_data': '1.1.1.1'
                }
            ]})
        address = InsecureDNSQuery('domain.tld').address(family='IPv4')
        self.assertEquals(address, [{'address_type': 'IPv4', 'address_data': '1.1.1.1'}])    