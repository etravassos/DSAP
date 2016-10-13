from django.test import TestCase
from django.conf import settings

from eppy.doc import EppResponse
from eppy.exceptions import EppLoginError
from mock import patch
from src.epp import eppclient
from src.core.utils import constants as const
from tests.core.utils import constants as tconst


class RemapKeysTestCase(TestCase):
    def setUp(self):
        self.ds = { 'algorithm': 8, 'digest_type': 2, 'key_tag': 1, 'digest': '0xAB'}
    
    def test_pass(self): 
        ds = eppclient.remap_ds_keys(self.ds)
        self.assertEquals(ds, {'type': 'ds', 'data': {'alg': 8, 'digestType': 2, 'keyTag': 1, 'digest': '0xAB'}})
  
    # def test_remove_later(self):
    #   print eppclient.add_ds('domain.tld', [self.ds])


class EppSendTestCase(TestCase):

    def setUp(self):
        patcher = patch(tconst.TEST.EPPCLIENT_MODULE_REMAP_DS_KEYS, autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_remap_ds = patcher.start()
        self.mock_remap_ds.return_value = 'x'
        
        patcher = patch(tconst.TEST.EPPCLIENT_MODULE_EPP_UPDATE_CMD, autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_update_cmd = patcher.start().return_value
    
        patcher = patch(tconst.TEST.EPPCLIENT_MODULE_EPPCLIENT_CLASS, autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_epp_client = patcher.start().return_value
    
        self.args = ('domain.tld', {'add': [{'digest': '0xAB'}]})
    
    def test_send_pass(self):
        eppclient.send(*self.args)
        
        self.mock_remap_ds.assert_called_with({'digest': '0xAB'})
        
        self.mock_update_cmd.add_secdns_data.assert_called_with({'add': ['x']})
        self.assertEquals(self.mock_update_cmd.name, 'domain.tld')
    
        self.mock_epp_client.login.assert_called_with(settings.EPP_CFG['User'], settings.EPP_CFG['Password'])
        self.mock_epp_client.batchsend.assert_called_with([self.mock_update_cmd])
  
    @patch(tconst.TEST.EPPCLIENT_MODULE_SEND, autospec=True)
    def test_send_generic_error(self, mock_internal_send):
        mock_internal_send.side_effect = Exception('aa')
    
        result = eppclient.send(*self.args)
    
        self.assertEquals({'error': {'message': 'aa'}}, result)
    
        self.mock_epp_client.send.assert_not_called
        self.mock_epp_client.batchsend.assert_not_called
  
    @patch(tconst.TEST.EPPCLIENT_MODULE_SEND, autospec=True)
    def test_send_generic_error(self, mock_internal_send):
        mock_internal_send.side_effect = EppLoginError(EppResponse({
            'epp': {
              'response': {
                'result': [{
                  '@code': 2000,
                  'msg': 'authentication error'
                }]
            }}}))
        result = eppclient.send(*self.args)
    
        self.assertEquals({'error': { 'code': 2000, 'message': 'authentication error'}}, result)
    
        self.mock_epp_client.send.assert_not_called
        self.mock_epp_client.batchsend.assert_not_called