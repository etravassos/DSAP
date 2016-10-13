import dns
import getdns
from src.core.exception.DsapException import DsapException
from src.core.queries.DNSQuery import DNSQuery
from src.core.utils import utils
from src.logging.Logger import Logger

logger = Logger().LOG

class SecureDNSQuery(DNSQuery):
    def __init__(self, zone):
        super(SecureDNSQuery, self).__init__(zone, {"dnssec_return_only_secure" : getdns.EXTENSION_TRUE})
        # limit the queries to TCP only to avoid simple spoofing
        try:
            logger.debug("Attempting to set acceptable transport to TCP {}".format(getdns.TRANSPORT_TCP))
            self.ctx.dns_transport_list = [ getdns.TRANSPORT_TCP ]
            logger.debug("Set acceptable transport: {}".format(self.ctx.dns_transport_list))
        except:
            raise DsapException("Could not set dns_transport_list to TCP only! getdns bug? [{}]"
                    .format(self.ctx.dns_transport_list))
        # self.ctx.dns_transport_list = [getdns.TRANSPORT_TCP, getdns.TRANSPORT_TLS]

class InsecureDNSQuery(DNSQuery):
    def __init__(self, zone):
        super(InsecureDNSQuery, self).__init__(zone)

    def address(self, family=None):
        try:
            results = self.ctx.address(name=self.zone)
        except getdns.error as e:
            logger.mul_dr("    Resolving {} : X ".format(self.zone))
            raise DsapException("{}: getdns error for address - '{}'".format(self.zone, e))

        if results.status != getdns.RESPSTATUS_GOOD:
            logger.mul_dr("    Resolving {} : X ".format(self.zone))
            raise DsapException("{}: Unable to resolve address - '{}'".format(self.zone, results.status))

        ext_ips = [ip for ip in results.just_address_answers if family is None or ip['address_type'] == family]
        logger.mul_dr("    Resolving {} : {} ".format(self.zone, ', '.join([ip_val['address_data'] for ip_val in ext_ips])))
        return ext_ips
        
class StubDNSQuery(InsecureDNSQuery):
    def __init__(self, zone):
        super(StubDNSQuery, self).__init__(zone)
        self.ctx.resolution_type = getdns.RESOLUTION_STUB
        self.upstream_recursive_servers = []
        
    def upstream_servers(self, upstream_recursive_servers):
        self.upstream_recursive_servers = upstream_recursive_servers 
        return self

    def run(self, query, section="answer"):
        if len(self.upstream_recursive_servers) == 0:
            raise DsapException("No upstream servers set for stub DNS query ")

        previous_results = None
        for ip in self.upstream_recursive_servers:

            results = super(StubDNSQuery, self).run(query, section, upstream_recursive_server=ip)

            previous_results = utils.validate_ns_for_results(query, results, previous_results, self.zone)


        return results