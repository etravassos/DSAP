from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.decorators import detail_route

from src.core import dsap
from src.core.utils import constants as const
from src.core.exception.DsapException import DsapException, DsapEppException
from src.logging.Logger import Logger
from src.epp import eppclient
from src.logging.ResponseHandler import ResponseLogDict
import logging

logger = Logger().LOG
def handle_operation(self, request, domain_name, operation_func, preview_only):
    logger.mul_wr('{} request for {}'.format(request.method, domain_name))
    epp_data = None
    
    try:
        #Execute operation function to validate and generate proper epp payload content
        epp_data = operation_func(domain_name)

        if preview_only:
            logger.mul_wr('Preview only.')
            stat_code = status.HTTP_201_CREATED if operation_func is dsap.bootstrap else status.HTTP_200_OK
        else:
            logger.mul_wr('Non-preview queries have been disabled in this release.')
            stat_code = status.HTTP_201_CREATED if operation_func is dsap.bootstrap else status.HTTP_200_OK
            # logger.multilog(("info", "resp"),'Making EPP call with data: %s', str(epp_data))
            # epp_data = eppclient.send(domain_name, epp_data)
            # stat_code = status.HTTP_201_CREATED if operation_func is dsap.bootstrap else status.HTTP_200_OK
            
            # for response in epp_data:
            #     if "result" in response:
            #         rcode = int(response["result"]["@code"])
            #         if rcode in const.EPP.CMD_FAILURE_CODES:
            #             raise DsapEppException("EPP call failed (code: {})".format(rcode))
            #         elif rcode in const.EPP.CMD_SUCCESS_CODES:
            #             continue
            #         else:
            #             raise DsapEppException("Unknown EPP response code {}".format(rcode))

        success_msg = "Domain operation finished successfully."
        resp_data = {'domain': domain_name, 'epp': epp_data, 'debug': self.rld.get_resp(True), 'description':success_msg}
        return Response(resp_data, status=stat_code)
        
    except DsapEppException as exp:
        error_msg = "EPP failure: {}".format(exp)
        logger.warn(error_msg)
        return Response(
                    { 'domain': domain_name,
                      'error': error_msg,
                      'debug': self.rld.get_resp(True),
                      'epp': epp_data
                    },
                    status=exp.status_code )
    except DsapException as exp:
        error_msg = "Validation failure: {}".format(exp)
        logger.warn(error_msg)
        return Response(
                    { 'domain': domain_name,
                      'error': error_msg,
                      'debug': self.rld.get_resp(True),
                    },
                    status=exp.status_code )
    except Exception as exp:
        logger.error(exp)
        logging.exception(exp)
        try:
            self.rld.clear()
        except Exception as exp:
            logger.error(exp)
            logging.exception(exp)
            pass
        return Response(
                    { 'domain': domain_name,
                      'error': "Unexpected failure. Please contact CIRA.",
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)