import getdns

from src.core.utils import constants as const
from tests.core.utils import constants as tconst

from tests.mock.mock_dnsquery import mock_dnsquery_run, mock_dnsquery_address
from django.test import TestCase
from mock import patch

from src.core import dsap

const.supported_tlds |= {"tld"} # patch constant to have ".tld" tld for tests

class BootstrapTestCase(TestCase):

    def t(self):
        return dsap.bootstrap('zone.tld')

    def setUp(self):
        patcher = patch(tconst.TEST.DNS_QUERY_MODULE_RUN, autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_run = patcher.start()
        self.mock_run.side_effect = mock_dnsquery_run()

        patcher = patch(tconst.TEST.STUB_DNS_QUERY_MODULE_RUN, self.mock_run)
        self.addCleanup(patcher.stop)
        patcher.start()

        patcher = patch(tconst.TEST.INSECURE_DNS_QUERY_MODULE_ADDRESS, autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_address = patcher.start()
        self.mock_address.side_effect = mock_dnsquery_address()

        self.ds = { 'algorithm': const.DS_ALGS.ECDSAP256SHA256._code, 'digest_type': const.DIGEST_TYPES.SHA_256._code, 'key_tag': 1, 'digest': '0c05d47049d1145d38be5ed5d1c4b84fc429f2023bb2bf14d504fe1436058d0e' }
        #self.ds_from_key = { 'algorithm': const.DS_ALGS.ECDSAP256SHA256._code, 'digest_type': const.DIGEST_TYPES.SHA_256._code, 'key_tag': 43545, 'digest': '0c05d47049d1145d38be5ed5d1c4b84fc429f2023bb2bf14d504fe1436058d0e' }
        self.ds_from_key = { 'algorithm': const.DS_ALGS.ECDSAP256SHA256._code, 'digest_type': const.DIGEST_TYPES.SHA_256._code, 'key_tag': 43801, 'digest': 'fe36c7ec1a7de661a2741e78e289cf19aa14cfd3fb519d0dcd249efbca0b4aac' }

    def test_pass(self):
        self.assertEquals({'add': [ self.ds_from_key ]}, self.t())

    def test_parent_zone_not_secure_fails(self):
        self.mock_run.side_effect = mock_dnsquery_run('tld', { getdns.RRTYPE_DS: Exception('no ds') })
        self.assertRaisesMessage(Exception, 'no ds', self.t)

    def test_parent_zone_no_secure_nameservers(self):
        self.mock_run.side_effect = mock_dnsquery_run('tld', { getdns.RRTYPE_NS: Exception('no ns') })
        self.assertRaisesMessage(Exception, 'no ns', self.t)

    def test_parent_zone_nameservers_missing_ip(self):
        self.mock_address.side_effect = mock_dnsquery_address(name='1.tld-servers.tld.', result=Exception('Zone ns missing ip'))
        self.assertRaisesMessage(Exception, 'Zone ns missing ip', self.t)

    def test_child_zone_no_nameservers(self):
        self.mock_run.side_effect = mock_dnsquery_run('zone.tld.', { getdns.RRTYPE_NS: Exception('no child ns') })
        self.assertRaisesMessage(Exception, 'no child ns', self.t)

    def test_child_zone_nameservers_missing_ip(self):
        self.mock_address.side_effect = mock_dnsquery_address(name='ns0.zone.tld.', result=Exception('Zone ns missing ip'))
        self.assertRaisesMessage(Exception, 'Zone ns missing ip', self.t)

    def test_child_zone_no_cds_has_zsk(self):
        self.mock_run.side_effect = mock_dnsquery_run('zone.tld.', {getdns.RRTYPE_CDS: Exception('no child cds')})
        self.assertRaisesMessage(Exception, 'no child cds', self.t)

    def test_child_zone_has_cds_no_zsk(self):
        self.mock_run.side_effect = mock_dnsquery_run('zone.tld.', {getdns.RRTYPE_DNSKEY: Exception()})
        self.assertRaisesMessage(Exception, '', self.t)

    def test_child_zone_no_cds_no_zsk(self):
        self.mock_run.side_effect = mock_dnsquery_run('zone.tld.', { 
                                                                    getdns.RRTYPE_CDS: Exception('no child cds'),
                                                                    getdns.RRTYPE_DNSKEY: Exception('no child zsk')
                                                                   } )
        self.assertRaisesMessage(Exception, 'no child', self.t)


# can only be run manually
class DummyTestCase(TestCase):

    def nohats(self):
        print(dsap.bootstrap('nohats.ca'))