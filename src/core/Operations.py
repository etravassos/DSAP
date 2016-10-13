#!/usr/bin/python

import getdns

from src.core.exception.DsapException import DsapException, DsapNoAnswerException
from src.core.queries.DNSQueryTypes import SecureDNSQuery, StubDNSQuery
from src.core.utils.utils import get_ns_ips
from src.logging.Logger import Logger
#
logger = Logger().LOG

class Operations:
    cur_zone = None
    cur_domain_name = None
    cur_query = None
    cur_squery = None
    
    def __init__(self, zone_data):
        self.cur_domain_name, self.cur_zone = zone_data


    def get_query_cds_record(self):
        logger.multilog(("debug", "resp"), "Quering CDS for {} ".format(self.cur_domain_name))
        # CDNSKEY usage currently not supported by DSAP
        # thus a CDS key is mandatory for bootstrapping
        try:
            cds = self.cur_query.run(query=getdns.RRTYPE_CDS)
        except DsapNoAnswerException as e:
            logger.debug(e)
            raise DsapException(e)
    
        logger.mul_dr("{} CDS resource record found".format(len(cds)))

        return self.cur_query, cds
    
    def get_query_ds_record(self):
        logger.multilog(("debug", "resp"), "Quering DS for {} ".format(self.cur_domain_name))
        
        try:
            ds = self.cur_squery.run(query=getdns.RRTYPE_DS)
        except DsapNoAnswerException as e:
            logger.debug(e)
            raise DsapException(e)
        
        logger.mul_dr("{} DS resource record found.".format(len(ds)))

        return self.cur_squery, ds
        
    def load_parent_zone_ds(self, q):
        # load parent zone ds, securely or fail
        logger.mul_dr("Loading DS for: {}".format(self.cur_zone[0]))
        result = q.run(getdns.RRTYPE_DS)
        logger.mul_dr("Securely loaded zone ds for: {}".format(self.cur_zone[0]))
        
        return result

    def load_parent_rec_ns_in_query(self, pquery):
        # load parent zone ns ips
        ns_ips = self._get_parent_zone_ns_ips(pquery)

        logger.mul_dr("Querying NS recursively @ parent ns ips.")
        # use parent ns ips as recursive nameservers
        self.cur_query = self._set_child_zone_as_recursive(
                    StubDNSQuery(self.cur_domain_name)
                    .upstream_servers(ns_ips)
                    )
    
    def create_squery_for_current(self):
        self.cur_squery = SecureDNSQuery(self.get_cur_domain())
        
    def _get_parent_zone_ns_ips(self, q):
        # load parent zone ns
        logger.multilog(("debug", "resp"), "Loading NameServers for: {}".format(self.cur_zone[0]))
        nameservers = q.run(getdns.RRTYPE_NS)
        logger.mul_dr("Parent NS for {} (total: {}): {}".format(self.cur_zone[0],
                        len(nameservers),
                        ', '.join(val['nsdname'] for val in nameservers))
                        )
        return get_ns_ips(nameservers)
        
        
    def _set_child_zone_as_recursive(self, query):

        ns_from_parent = query.run(query=getdns.RRTYPE_NS, section="authority")
        nsdname_from_parent = [val['nsdname'] for val in ns_from_parent]
        logger.mul_dr("NS for {}: {}".format(self.cur_domain_name, ', '.join(nsdname_from_parent)))
    
        #Resolve child zone ns ips
        ns_ips_from_parent = get_ns_ips(ns_from_parent)

        # use child zone ns ips as recursive nameservers
        query.upstream_servers(ns_ips_from_parent)
        logger.mul_dr("Querying NS recursively @ child ns ips.")
        ns_from_child = StubDNSQuery(query.zone).upstream_servers(ns_ips_from_parent).run(query=getdns.RRTYPE_NS)
        nsdname_from_child = [val['nsdname'] for val in ns_from_child]
        logger.mul_dr("Child NS for {}: {}".format(self.cur_domain_name, ', '.join(nsdname_from_child)))

        self.validate_delegation(nsdname_from_parent, nsdname_from_child)

        return query

    def validate_delegation(self, ns_from_parent, ns_from_child):
        for ns in ns_from_parent:
            if ns not in ns_from_child:
                raise DsapException('Invalid delegation in parent NS servers: {} '.format(ns))

        for ns in ns_from_child:
            if ns not in ns_from_parent:
                raise DsapException('Invalid delegation in child NS servers: {} '.format(ns))

    def get_cur_domain(self):
        return self.cur_domain_name
    
    def get_cur_zone(self):
        return self.cur_zone
