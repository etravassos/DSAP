from eppy.client import EppClient
from eppy.exceptions import EppLoginError
from eppy.doc import EppUpdateDomainCommand, EppResponse
from django.conf import settings
from src.logging.Logger import Logger

logger = Logger().LOG
# rename ds attributes to match EPP
def remap_ds_keys(ds):
    ds['keyTag'] = ds.pop('key_tag')
    ds['alg'] = ds.pop('algorithm')
    ds['digestType'] = ds.pop('digest_type')

    return { 'type': 'ds', 'data': ds }

'''
eppclient.send({'add': [], 'rem': []})

'''

def send(domain_name, data):
    try:
        return _send(domain_name, data)
    except EppLoginError as e:
        resp = e.resp
        return { 'error': {'code': resp.code, 'message': resp.msg} }
    except Exception as e:
        raise 
        return { 'error': {'message': e.message} }
  
def _send(domain_name, data):
    client = EppClient( host = settings.EPP_CFG['Host'], 
                        port = int(settings.EPP_CFG['Port']),
                        ssl_enable = settings.EPP_CFG.getboolean('SSLEnable') )
    client.login( settings.EPP_CFG['User'], settings.EPP_CFG['Password'] )
  
    cmds = []

    for action, ds in data.items():
        ds = map(remap_ds_keys, ds)

        for ds_data in ds:
            secdns_data = {}
            secdns_data[action] = [ds_data]

            cmd = EppUpdateDomainCommand()
            cmd.name = domain_name
            cmd.add_secdns_data(secdns_data)
            cmd.add_clTRID()
      
            cmds.append(cmd)

    results = client.batchsend(cmds)

    responses = []

    for cmd in cmds:
        r = { 'request': cmd['epp']['command']['extension'] }

        clTRID = cmd['epp']['command']['clTRID']
        result = list(
                    filter(
                        lambda r: r and r['epp']['response']['trID']['clTRID'] 
                        == clTRID, results))

        if len(result) > 0:
            r.update( {'result': result[0].first_result} )

        responses.append( r )    
    # logger.debug(responses)
    return responses