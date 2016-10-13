import dns
import getdns
import base64
import binascii
import struct
from dns import rdataclass
from dns import rdatatype
from dns.rdtypes.ANY.DNSKEY import DNSKEY
from src.logging.Logger import Logger
from src.core.exception.DsapException import (DsapException, InvalidCdsException)
from src.core.utils.constants import (supported_tlds,FLAGS, DIGEST_TYPES, DS_ALGS)

logger = Logger().LOG

def get_validation_attr(query, results):
    __fn_ds_cds = (lambda r: [ "{} {} {} {}".format( x["key_tag"], x["algorithm"], 
                    x["digest_type"], base64.b64encode(x["digest"]) )
                    for x in r ])
    __fn_dnskey = (lambda r: [ "{} {} {} {}".format( x["flags"], x["protocol"], 
                    x["algorithm"], base64.b64encode(x["public_key"]) )
                    for x in r ])

    truth = { getdns.RRTYPE_NS:     (lambda r: [ x["nsdname"] for x in r ]),
              getdns.RRTYPE_CDS:    __fn_ds_cds,
              getdns.RRTYPE_DS:     __fn_ds_cds,
              getdns.RRTYPE_DNSKEY: __fn_dnskey,
              "default":            (lambda r: [ x["rdata_raw"] for x in r ])
              }
    # logger.critical(results)
    check_if_cds_empty(query, results)
    
    _fn = truth.get(query, truth.get("default", (lambda *args, **kwargs: None)))
    return _fn(results)

def check_if_cds_empty(query, results):
    if query == getdns.RRTYPE_CDS:
        cdsnonempty = 0
        cdsempty = 0
        for result in results:
            if cds_is_empty(result):
                cdsempty += 1
                result['digest'] = b''
            else:
                cdsnonempty += 1
        if cdsnonempty != 0 and cdsempty != 0:
            raise DsapException("Cannot have empty CDS and non-empty CDS record")

def cds_is_empty(record):
    return (record['key_tag'] == 0 and record['algorithm'] == 0 
                and record['digest_type'] == 0)

def domain_to_zone(domain_name):
    zone = domain_name.split(".")
    zone.reverse()
    return zone

def validate_ds(ds, cds_list):
    _ds, _cds_list = {}, []
    _ds = { "key_tag": ds["key_tag"], 
            "algorithm": ds["algorithm"],
            "digest_type": ds["digest_type"],
            "digest": ds["digest"],
            }
    
    for cds in cds_list:
        digest = binascii.hexlify(cds["digest"]) if type(cds["digest"]) is memoryview else cds["digest"]
        _cds_list.append({  "key_tag": cds["key_tag"],
                            "algorithm": cds["algorithm"],
                            "digest_type": cds["digest_type"],
                            "digest": digest.decode('utf-8')
                            })
    
    for cds in _cds_list:
        if (_ds["key_tag"] == cds["key_tag"] 
            and _ds["algorithm"] == cds["algorithm"]
            and _ds["digest_type"] == cds["digest_type"]
            and _ds["digest"] == cds["digest"]):
                return True
    return False

def extract_validate(domain_name):
    #add . to domain_name
    if domain_name[-1] != '.':
        domain_name += '.'
    
    #for zone split should not use .
    zone = domain_to_zone(domain_name[:-1])
    
    #check the length of characters
    if zone.__len__() <= 1 or '' in zone:
        raise DsapException("The usage of the {} TLD is not allowed.".format(domain_name))
        
    #check for supported tlds
    if not zone[0] in supported_tlds:
        raise DsapException("{} is not a supported TLD. Currently supported by DSAP: {}".format(zone[0], supported_tlds))

    return domain_name, zone

def get_ns_ips(nameservers):
    from src.core.queries.DNSQueryTypes import InsecureDNSQuery
    ns_ips = []
    for ns in nameservers:
        try:
            # get nameserver ip
            ip = InsecureDNSQuery(ns['nsdname']).address('IPv4')
        except Exception as e:
            logger.debug("No ips found for {} ".format(ns))
            raise e

        ns_ips.extend( ip )

    if len(ns_ips) == 0:
        raise DsapException("Zone ns missing ip")

    return ns_ips
    
def validate_ns_for_results(query, results, previous_results, zone):

    new_results = set(get_validation_attr(query, results))

    if previous_results:
        diff = previous_results ^ new_results
        if len(diff) > 0:
            raise DsapException("{}: nameservers not in sync for '{}' data"
                    .format(zone, dns.rdatatype.to_text(query)))
        
    return new_results
    
def get_dnskey_for_rdata(rdata):
    flags = rdata["flags"]
    protocol = rdata["protocol"]
    algorithm = rdata["algorithm"]
    pubkey = dns.rdata._base64ify(rdata["public_key"])
    dnskey_dict =  { 'flags': flags, 'protocol': protocol,
                    'algorithm': algorithm, 'public_key': pubkey
                    }
                
    return dnskey_dict
    
def make_ds_from_dnskey_rdata(domain_name, rdata, digest_alg):
    tokd =  get_dnskey_for_rdata(rdata)
    tok = dns.tokenizer.Tokenizer('%d %d %d %s' % (tokd["flags"], tokd["protocol"], 
                tokd["algorithm"] , tokd["public_key"]))

    dnskey = DNSKEY.from_text(rdatatype.DNSKEY, rdataclass.IN, tok)

    ds = dns.dnssec.make_ds(domain_name, dnskey, digest_alg)
    
    return { 'key_tag': ds.key_tag,
             'algorithm': ds.algorithm,
             'digest_type': ds.digest_type,
             'digest': binascii.hexlify(ds.digest).decode('utf-8'),
        }

def get_ds_remove_add_lists(ds, cds):
    to_add, to_rem = [], []
    for dsrecord in ds:
        if not dsrecord in cds:
            to_rem.append(dsrecord)

    for cdsrecord in cds:
        if not cdsrecord in ds:
            to_add.append(cdsrecord)
    
    plusminus = len(to_add) - len(to_rem)
    if len(ds) + plusminus < 1:
        raise DsapException('Cannot delete entire DS RRset!')

    return to_add, to_rem

def extract_key_id(flags, protocol, algorithm, key):
    key_pack = struct.pack('!HBB', int(flags), int(protocol), int(algorithm)) + key

    bbytes = [key_pack[i:i + 1] for i in range(len(key_pack))]

    cnt, idx = 0, 0
    for cur_byte in bbytes:
        s = struct.unpack('B', cur_byte)[0]
        if (idx % 2) == 0:
            cnt += s << 8
        else:
            cnt += s
        idx += 1

    ret = ((cnt & 0xFFFF) + (cnt >> 16)) & 0xFFFF

    return (ret)

def print_break():
    logger.mul_dr('-'*130)

def print_ds(ds):
        digest = binascii.hexlify(ds["digest"]).decode('utf8') if type(ds["digest"]) is memoryview else ds["digest"]
        logger.mul_dr("    Key Tag: {}, Digest Type: {}, Algorithm: {} "
                      .format(ds['key_tag'], DIGEST_TYPES.get_obj(ds['digest_type']), DS_ALGS.get_obj(ds['algorithm'])))
        logger.mul_dr("    Digest: {} ".format(digest))

def extract_n_print_dnskey(dnskey):
    if dnskey['flags'] == FLAGS.KSK:
        logger.mul_dr("    KSK - KeySigning Key found - flag: {}  ".format(dnskey['flags']))
    else:
        logger.mul_dr("    ZSK - Zone Siging Key found (will be ignored) - flag: {}:".format(dnskey['flags']))
    pk_mem = dnskey["public_key"]
    logger.mul_dr("        Key Tag: {}, Protocol: {}, Algorithm: {}"
                  .format(extract_key_id(dnskey['flags'], dnskey['protocol'], dnskey['algorithm'], pk_mem),
                  dnskey['protocol'], DS_ALGS.get_obj(dnskey['algorithm'])))
    logger.mul_dr("        Public Key: {} ".format(dns.rdata._base64ify(pk_mem)))#base64.b64encode(pk_mem).decode('utf8'))

def print_parents_sync():
    logger.mul_dr("Parents Name Servers are in sync.")
    print_break()

def validate_cds_digest(cds):
    if(not DIGEST_TYPES.supports(cds['digest_type'])):
        raise InvalidCdsException('        - CDS {} has unsupported algorithm: {}. Supported Algorithms:  {}'
                            .format(cds['key_tag'], DIGEST_TYPES.get_obj(cds['digest_type']), DIGEST_TYPES.pretty_supported()))
    logger.mul_dr('        - CDS {} has been successfully validated.'.format(cds['key_tag']))