from django.test import TestCase
from src.core.utils.utils import (
    extract_validate,
    validate_ns_for_results,
    domain_to_zone,
    validate_ds,
    check_if_cds_empty,
    cds_is_empty,
    get_dnskey_for_rdata,
    make_ds_from_dnskey_rdata,
    get_ds_remove_add_lists,
    extract_key_id,
)
from src.core.exception.DsapException import DsapException
from src.core.utils import constants as const 
from tests.mock.mock_getdns import mock_getdns_result
import getdns
import binascii
import base64

const.supported_tlds |= {"ca", "com"}

class UtilsTestCase(TestCase):
    
    def test_extract_validate_success_withroot(self):
        domain_name = 'cira.ca.'
        zone = ['ca', 'cira']
        self.cur_domain_name, self.cur_zone = extract_validate(domain_name)
        self.assertEqual(self.cur_domain_name, domain_name)
        self.assertEqual(self.cur_zone, zone)
        
    def test_extract_validate_success_withoutroot(self):
        domain_name = 'google.com'
        zone = ['com', 'google']
        self.cur_domain_name, self.cur_zone = extract_validate(domain_name)
        self.assertEqual(self.cur_domain_name, domain_name + '.')
        self.assertEqual(self.cur_zone, zone)
                
    def test_extract_validate_error_tld(self):
        invalid_dn = 'code.org'
        self.assertRaises(DsapException, extract_validate, invalid_dn)
        
    def test_extract_validate_error_onelevel(self):
        invalid_dn = 'hello'
        self.assertRaises(DsapException, extract_validate, invalid_dn)
        
    def test_extract_validate_error_blankinzone(self):
        invalid_dn = 'roots.'
        self.assertRaises(DsapException, extract_validate, invalid_dn)
    
    def test_extract_validate_error_space(self):
        invalid_dn = ' '
        self.assertRaises(DsapException, extract_validate, invalid_dn)
    
    def test_validate_ns_for_results_success(self):
        query = 2
        #mock_getdns_context.return_value.general.return_value = mock_getdns_result(status=-1)
        results = [{'nsdname': 'ns2.www2.ca.', 'rdata_raw': 0x1}, {'nsdname': 'ns.www2.ca.', 'rdata_raw': 0x1}]
        previous_results = None
        zone = 'test.ca'
        new_results = validate_ns_for_results(query, results, previous_results, zone)
        self.assertEqual(new_results, {'ns.www2.ca.','ns2.www2.ca.'})
        
    def test_validate_ns_for_results_unsynced(self):
        query = 2
        results = [{'nsdname': 'ns2.www2.ca.', 'rdata_raw': 0x1}, {'nsdname': 'ns.www2.ca.', 'rdata_raw': 0x1}]
        previous_results = {'ns2.www.ca','ns.www2.ca'}
        zone = 'test.ca'
        self.assertRaises(DsapException, validate_ns_for_results, query, results, previous_results, zone)

    def test_validate_ds_success(self):
        ds = {  'algorithm': 13, 'key_tag': 2371, 'digest_type': 2,
                'digest': 'da1c0633fd26bdb3c4133028ece678d7502504f0a1885d778ec37cf89cc7f5a6' }
        cds = [
            {  'algorithm': 13, 'key_tag': 1234, 'digest_type': 2,
                'digest': b'baec121cabec11bc13b13cb1331ae76ea671e67167a76921be12313bc2123123' },
            {  'algorithm': 13, 'key_tag': 2371, 'digest_type': 2,
                'digest': b'da1c0633fd26bdb3c4133028ece678d7502504f0a1885d778ec37cf89cc7f5a6' },
        ]
        result = validate_ds(ds, cds)
        self.assertEqual(result, True)
    
    def test_validate_ds_failure(self):
        ds = {  'algorithm': 13, 'key_tag': 2371, 'digest_type': 2,
                'digest': 'da1c0633fd26bdb3c4133028ece678d7502504f0a1885d778ec37cf89cc7f5a6' }
        cds = [
            {  'algorithm': 13, 'key_tag': 1234, 'digest_type': 2,
                'digest': b'baec121cabec11bc13b13cb1331ae76ea671e67167a76921be12313bc2123123' },
        ]
        result = validate_ds(ds, cds)
        self.assertEqual(result, False)

    def test_check_if_cds_empty_pass(self):
        cds1 = [
            {  'algorithm': 0, 'key_tag': 0, 'digest_type': 0 },
            {  'algorithm': 0, 'key_tag': 0, 'digest_type': 0 },
        ]
        cds2 = [
            {  'algorithm': 13, 'key_tag': 2371, 'digest_type': 2,
                'digest': b'da1c0633fd26bdb3c4133028ece678d7502504f0a1885d778ec37cf89cc7f5a6' },
            {  'algorithm': 13, 'key_tag': 1234, 'digest_type': 2,
                'digest': b'baec121cabec11bc13b13cb1331ae76ea671e67167a76921be12313bc2123123' },
        ]

        with self.assertRaises(Exception):
            try:
                check_if_cds_empty(getdns.RRTYPE_CDS, cds1)
                check_if_cds_empty(getdns.RRTYPE_CDS, cds2)
            except:
                pass
            else:
                raise Exception

    def test_check_if_cds_empty_fail(self):
        cds1 = [
            {  'algorithm': 0, 'key_tag': 0, 'digest_type': 0 },
            {  'algorithm': 0, 'key_tag': 0, 'digest_type': 0 },
        ]
        cds2 = [
            {  'algorithm': 13, 'key_tag': 2371, 'digest_type': 2,
                'digest': b'da1c0633fd26bdb3c4133028ece678d7502504f0a1885d778ec37cf89cc7f5a6' },
            {  'algorithm': 13, 'key_tag': 1234, 'digest_type': 2,
                'digest': b'baec121cabec11bc13b13cb1331ae76ea671e67167a76921be12313bc2123123' },
        ]
        cds3 = cds1 + cds2
        
        self.assertRaises(DsapException, check_if_cds_empty, getdns.RRTYPE_CDS, cds3)

    def test_check_if_cds_empty_appends_empty_digest(self):
        pre_cds = [
            {  'algorithm': 0, 'key_tag': 0, 'digest_type': 0 },
            {  'algorithm': 0, 'key_tag': 0, 'digest_type': 0 },
        ]
        post_cds = [
            {  'algorithm': 0, 'key_tag': 0, 'digest_type': 0, 'digest': b''},
            {  'algorithm': 0, 'key_tag': 0, 'digest_type': 0, 'digest': b''},
        ]

        with self.assertRaises(Exception):
            try:
                check_if_cds_empty(getdns.RRTYPE_CDS, pre_cds)
            except:
                pass
            else:
                raise Exception
        
        self.assertEqual(str(pre_cds[0]), str(post_cds[0]))
        self.assertEqual(str(pre_cds[1]), str(post_cds[1]))
    
    def test_cds_is_empty_true(self):
        cds = {  'algorithm': 0, 'key_tag': 0, 'digest_type': 0 }

        self.assertEqual(cds_is_empty(cds), True)

    def test_cds_is_empty_false(self):
        cds = { 'algorithm': 13, 'key_tag': 2371, 'digest_type': 2,
                'digest': b'da1c0633fd26bdb3c4133028ece678d7502504f0a1885d778ec37cf89cc7f5a6' }

        self.assertEqual(cds_is_empty(cds), False)

    def test_get_dnskey_for_rdata(self):
        pkey = b"\x99\xdb,\xc1L\xab\xdc3\xd6\xd7}\xa6:/\x15\xf7\x11\x12XO#N\x8d\x1d\xc4(\xe3\x9e\x8aJ\x97\xe1\xaa'\x1aU]\xc9\x07\x01\xe1~*LKo\x12\x0b|2\xd4OJ\xc0+\xd8\x94\xcf-K\xe7w\x8a\x19"
        rdata = {'protocol': 3, 'flags': 257, 'algorithm': 13, 'rdata_raw': b'', 'public_key': pkey}

        dnskey_dict = {'flags': 257, 'public_key': 'mdsswUyr3DPW132mOi8V9xESWE8jTo0d xCjjnopKl+GqJxpVXckHAeF+KkxLbxIL fDLUT0rAK9iUzy1L53eKGQ==', 'protocol': 3, 'algorithm': 13}
        self.assertEqual(get_dnskey_for_rdata(rdata), dnskey_dict)

    def test_make_ds_from_dnskey_rdata(self):
        pkey = b"\x99\xdb,\xc1L\xab\xdc3\xd6\xd7}\xa6:/\x15\xf7\x11\x12XO#N\x8d\x1d\xc4(\xe3\x9e\x8aJ\x97\xe1\xaa'\x1aU]\xc9\x07\x01\xe1~*LKo\x12\x0b|2\xd4OJ\xc0+\xd8\x94\xcf-K\xe7w\x8a\x19"
        rdata = {'protocol': 3, 'flags': 257, 'algorithm': 13, 'rdata_raw': b'', 'public_key': pkey}

        good_ds = {'key_tag': 2371, 'algorithm': 13, 'digest': 'da1c0633fd26bdb3c4133028ece678d7502504f0a1885d778ec37cf89cc7f5a6', 'digest_type': 2}
        gen_ds = make_ds_from_dnskey_rdata("dnsse.ca.", rdata, "SHA256")
        
        self.assertEqual(good_ds, gen_ds)

    def test_get_ds_remove_add_lists_bytestrings_success(self):
        good_add = [
            {'key_tag': 123, 'digest_type': 2, 'algorithm': 7, 'digest': b'abcd12218127373abef112217363193973822ee222be232c3c23c121313c4123'},
            {'key_tag': 124, 'digest_type': 2, 'algorithm': 7, 'digest': b'1735793218313efacf313761376137e1f221c21131313c13c13c13f131223ffc'},
        ]
        good_rem = [
            {'digest_type': 2, 'key_tag': 65100, 'algorithm': 7, 'digest': b'fbcf6bdfb0bd9ec0eb748643d1b080f3f30eb15aa49a9e8b0ab447a3f42e7e59'},
        ]

        cds = [
            {'key_tag': 123, 'digest_type': 2, 'algorithm': 7, 'digest': b'abcd12218127373abef112217363193973822ee222be232c3c23c121313c4123'},
            {'key_tag': 124, 'digest_type': 2, 'algorithm': 7, 'digest': b'1735793218313efacf313761376137e1f221c21131313c13c13c13f131223ffc'},
        ]
        ds = [
            {'digest_type': 2, 'key_tag': 65100, 'algorithm': 7, 'digest': b'fbcf6bdfb0bd9ec0eb748643d1b080f3f30eb15aa49a9e8b0ab447a3f42e7e59'},
        ]

        result_add, result_rem = get_ds_remove_add_lists(ds, cds)

        self.assertEqual(result_add, good_add)
        self.assertEqual(result_rem, good_rem)

    def test_get_ds_remove_add_lists_strings_success(self):
        good_add = [
            {'key_tag': 123, 'digest_type': 2, 'algorithm': 7, 'digest': 'abcd12218127373abef112217363193973822ee222be232c3c23c121313c4123'},
            {'key_tag': 124, 'digest_type': 2, 'algorithm': 7, 'digest': '1735793218313efacf313761376137e1f221c21131313c13c13c13f131223ffc'},
        ]
        good_rem = [
            {'digest_type': 2, 'key_tag': 65100, 'algorithm': 7, 'digest': 'fbcf6bdfb0bd9ec0eb748643d1b080f3f30eb15aa49a9e8b0ab447a3f42e7e59'},
        ]

        cds = [
            {'key_tag': 123, 'digest_type': 2, 'algorithm': 7, 'digest': 'abcd12218127373abef112217363193973822ee222be232c3c23c121313c4123'},
            {'key_tag': 124, 'digest_type': 2, 'algorithm': 7, 'digest': '1735793218313efacf313761376137e1f221c21131313c13c13c13f131223ffc'},
        ]
        ds = [
            {'digest_type': 2, 'key_tag': 65100, 'algorithm': 7, 'digest': 'fbcf6bdfb0bd9ec0eb748643d1b080f3f30eb15aa49a9e8b0ab447a3f42e7e59'},
        ]

        result_add, result_rem = get_ds_remove_add_lists(ds, cds)

        self.assertEqual(result_add, good_add)
        self.assertEqual(result_rem, good_rem)
    
    def test_get_ds_remove_add_lists_byteshex_success(self):
        good_add = [
            {'key_tag': 123, 'digest_type': 2, 'algorithm': 7, 'digest': binascii.unhexlify(b'abcd12218127373abef112217363193973822ee222be232c3c23c121313c4123')},
            {'key_tag': 124, 'digest_type': 2, 'algorithm': 7, 'digest': binascii.unhexlify(b'1735793218313efacf313761376137e1f221c21131313c13c13c13f131223ffc')},
        ]
        good_rem = [
            {'digest_type': 2, 'key_tag': 65100, 'algorithm': 7, 'digest': binascii.unhexlify(b'fbcf6bdfb0bd9ec0eb748643d1b080f3f30eb15aa49a9e8b0ab447a3f42e7e59')},
        ]

        cds = [
            {'key_tag': 123, 'digest_type': 2, 'algorithm': 7, 'digest': binascii.unhexlify(b'abcd12218127373abef112217363193973822ee222be232c3c23c121313c4123')},
            {'key_tag': 124, 'digest_type': 2, 'algorithm': 7, 'digest': binascii.unhexlify(b'1735793218313efacf313761376137e1f221c21131313c13c13c13f131223ffc')},
        ]
        ds = [
            {'digest_type': 2, 'key_tag': 65100, 'algorithm': 7, 'digest': binascii.unhexlify(b'fbcf6bdfb0bd9ec0eb748643d1b080f3f30eb15aa49a9e8b0ab447a3f42e7e59')},
        ]

        result_add, result_rem = get_ds_remove_add_lists(ds, cds)

        self.assertEqual(result_add, good_add)
        self.assertEqual(result_rem, good_rem)

    def test_get_ds_remove_add_lists_strings_success_no_changes(self):
        good_add, good_rem = [], []

        cds = [
            {'algorithm': 7, 'digest': 'fbcf6bdfb0bd9ec0eb748643d1b080f3f30eb15aa49a9e8b0ab447a3f42e7e59', 'digest_type': 2, 'key_tag': 65100},
        ]
        ds = [
            {'digest_type': 2, 'key_tag': 65100, 'algorithm': 7, 'digest': 'fbcf6bdfb0bd9ec0eb748643d1b080f3f30eb15aa49a9e8b0ab447a3f42e7e59'},
        ]

        result_add, result_rem = get_ds_remove_add_lists(ds, cds)

        self.assertEqual(result_add, good_add)
        self.assertEqual(result_rem, good_rem)


    def test_get_ds_remove_add_lists_failure(self):
        cds = []
        ds = [
            {'digest_type': 2, 'key_tag': 65100, 'algorithm': 7, 'digest': 'fbcf6bdfb0bd9ec0eb748643d1b080f3f30eb15aa49a9e8b0ab447a3f42e7e59'},
        ]

        self.assertRaises(DsapException, get_ds_remove_add_lists, ds, cds)

    def test_extract_key_id_ksk(self):
        key = "AwEAAasIUeyekz2PU9+tvKh9Hnos1IFAeLwzhmf/rEeZb9ZsZH+62Do8 LeDpP5bzJISW/FLAie8uAOnCeqWwfqmlmpnHKNDCLG2q3mEPAt5gqrvz 2rv+66N24ew5J61MkiJ9GVaqmHRrSp0p7t93kzPRSwB8jSGtqsBLwxl2 T/          SUMYPg4HkQTNO7KNmXPUKEG3ZNj7Brda8qbyr+aVbHdPkAYAJ1JeqD 9afJzT7LHmYz4spJxLv3O6nHvVm2AaVFizHmW+5MTWLiQ8GJ8/hUk5rV 0CbxSbsP3a07IIkdsyPoG776EKPMTcyH92UudoKdajcmlm8GL5jITdUj ylMo17VtOCs="
        key = base64.b64decode(key)
        gen_key_tag = extract_key_id(const.FLAGS.KSK, const.DIGEST_TYPES.ECC_GOST._code, 8, key)
        expected_key_tag = 49342
        self.assertEqual(expected_key_tag, gen_key_tag)

    def test_extract_key_id_zsk(self):
        key = "AwEAAZeBismDvUHhCxrnoBEX6ERDwMqrAvp7d2xdUGjiJ5qV8rtaB1Hp TsNcINz6RI542vMi/TfdGAEOtifKZRzkKV2JiRCuIiL8BbtRJjy2AB7B B25vjY0FLgD5ZGfjnHO5MbuWTKutvgvwY4ZBy+Y1jTukhNVbLj4gXLlE /3eMIWRV"
        key = base64.b64decode(key)
        gen_key_tag = extract_key_id(const.FLAGS.ZSK, const.DIGEST_TYPES.ECC_GOST._code, 8, key)
        expected_key_tag = 48816
        self.assertEqual(expected_key_tag, gen_key_tag)
