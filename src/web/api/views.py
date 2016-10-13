from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.decorators import detail_route

from src.core import dsap
from src.core.exception.DsapException import DsapException
from src.logging.Logger import Logger
from src.epp import eppclient
from src.logging.ResponseHandler import ResponseLogDict
from src.web.api.dsap_handler import handle_operation
from src.core import dsap


logger = Logger().LOG
class DomainAPIView(ViewSet):
    lookup_value_regex = '.+\.*'
    lookup_field = 'name'

class CDSRecordAPIView(ViewSet):
    #lookup_field = 'token'
    rld = ResponseLogDict() 
    ops = { 'bootstrap':   dsap.bootstrap, 
            'maintenance': dsap.maintenance,
            'unsign':      dsap.unsign,
            }

    logger.info('DSAP Started listening.')

    def create(self, request, domain_name=None):
        return handle_operation(self, request, domain_name, self.ops['bootstrap'], False)

    def delete(self, request, domain_name=None):
        return handle_operation(self, request, domain_name, self.ops['unsign'], False)

    def put(self, request, domain_name=None):
        return handle_operation(self, request, domain_name, self.ops['maintenance'], False)


class PreviewCDSRecordAPIView(ViewSet):
    rld = CDSRecordAPIView.rld
    ops = CDSRecordAPIView.ops
    lookup_field='oper'
    def retrieve(self, request, domain_name=None, oper=None):
        return handle_operation(self, request, domain_name, self.ops[oper], True)
