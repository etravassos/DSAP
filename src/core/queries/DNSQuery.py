#!/usr/bin/python
import dns
import getdns

from src.core.exception.DsapException import DsapException, DsapNoAnswerException
from src.logging.Logger import Logger
from src.core.utils.constants import QUERY_TYPES
#
logger = Logger().LOG

class DNSQuery(object):
    def __init__(self, zone, extensions = {}):
        self.ctx = getdns.Context()
        self.ext = {"return_both_v4_and_v6" : getdns.EXTENSION_TRUE}
        self.ext.update(extensions)
        self.zone = zone
        
    def run(self, query, section="answer", upstream_recursive_server=None):

        logger.multilog(("debug", "resp"), "    Domain: {}, QType: {}, section: {}, @srv: {}".format(self.zone,
            QUERY_TYPES.get_obj(query), section, None if upstream_recursive_server == None else upstream_recursive_server['address_data']))
        try:
            if upstream_recursive_server:
                self.ctx.upstream_recursive_servers = [upstream_recursive_server]
            results = self.ctx.general(name=self.zone, request_type=query, extensions=self.ext)
            query_text = dns.rdatatype.to_text(query)
        except getdns.error as e:
            raise DsapException("{}: getdns error for '{}' query - '{}'".format(self.zone, dns.rdatatype.to_text(query), e))

        if results.status == getdns.RESPSTATUS_NO_SECURE_ANSWERS:
            raise DsapException("{}: Secure delegation not established. No secure answers found for '{}' query".format(self.zone, query_text))

        if results.status == getdns.RESPSTATUS_NO_NAME:
            raise DsapException("{}: zone not found for '{}' query".format(self.zone, query_text))

        if results.status == getdns.RESPSTATUS_ALL_TIMEOUT:
            raise DsapException("{}: DNS timeout for '{}' query".format(self.zone, query_text))
            
        if results.status != getdns.RESPSTATUS_GOOD:
            raise DsapException("{}: bad DNS response '{}' query - '{}'".format(self.zone, query_text, results.status))
        try:
            reply = results.replies_tree[0][section] 

        except AttributeError: 
            raise DsapNoAnswerException("{}: no answers for '{}' query".format(self.zone, query_text)) 

        # filter out records that don't match query
        records = [ x["rdata"] for x in reply if x["type"] is query ]

        if len(records) == 0:
            raise DsapNoAnswerException("{}: no answers for '{}' query".format(self.zone, query_text))
        #logger.debug("\tQResp {}".format(records))
        return records