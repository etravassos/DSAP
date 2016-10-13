#!/usr/bin/python
import binascii
import dns
import getdns
import base64

from src.core.Operations import Operations
from src.core.utils.constants import (FLAGS, DIGEST_TYPES, PROTOCOL)
from src.core.exception.DsapException import (DsapException, InvalidCdsException)
from src.logging.Logger import Logger
from src.core.utils.utils import ( 
        domain_to_zone, 
        make_ds_from_dnskey_rdata, 
        extract_validate,
        cds_is_empty, validate_ds, get_ds_remove_add_lists, validate_cds_digest,
        print_break, extract_n_print_dnskey, print_ds, print_parents_sync)
from src.core.queries.DNSQueryTypes import SecureDNSQuery

logger = Logger().LOG

def secure_load_operations(domain_name):
    op = Operations(extract_validate(domain_name))
    pquery = SecureDNSQuery(op.get_cur_zone()[0])
    
    op.load_parent_zone_ds(pquery) # verifies parent zone is secure
    op.load_parent_rec_ns_in_query(pquery)

    return op, op.get_cur_domain()

def bootstrap(domain_name): # POST
    logger.info("Bootstrapping zone {}".format(domain_to_zone(domain_name)))
    
    op, domain_name = secure_load_operations(domain_name)
    print_parents_sync()

    query, cds = op.get_query_cds_record()

    for cur_cds in cds[:]:
        try:
            print_ds(cur_cds)
            if(cds_is_empty(cur_cds)):
                raise InvalidCdsException('    {}: Null CDS found.  Unable to add secure delegation with null CDS.'.format(domain_name))

            validate_cds_digest(cur_cds)

        except InvalidCdsException as ex:
            cds.remove(cur_cds)
            logger.mul_dr(ex.message)

    if(len(cds) == 0):
        raise DsapException('No valid CDS found for secure domain operation.')

    print_break()

    result = []
    try:
        #queries DNSKEY for DS generation.
        logger.mul_dr("Recursive quering DNSKEY for {} ".format(domain_name))
        dnskeys = query.run(query=getdns.RRTYPE_DNSKEY)
        logger.mul_dr("{} DNSKEYs resource records found:".format(len(dnskeys)))

        for k in dnskeys:
            print_break()
            extract_n_print_dnskey(k)
            if k['protocol'] != PROTOCOL.VALID:
                logger.mul_dr("        Warning: The Protocol Field MUST have value {}.".format(PROTOCOL.VALID))
                continue
            elif k['flags'] == FLAGS.KSK:
                digest_type_label = DIGEST_TYPES.get_obj(cds[0]['digest_type'])._label
                ds = make_ds_from_dnskey_rdata(domain_name, k, digest_type_label)
                logger.mul_dr("    Generated DS:    ")
                print_ds(ds)
                if validate_ds(ds, cds):
                    logger.mul_dr("        {} DS has been successfully validated and will be added to EPP call.".format(ds['key_tag']))
                    result.append(ds)
                else:
                    logger.mul_dr("         Failed validation: DS generated digest does not match CDS digest.")

            else:
                continue # ignore non KSK keys
        print_break()

    except Exception as ex:
        logger.mul_dr("Error while trying to generate DS records. %s", str(ex))

    if len(result) > 0:
        logger.mul_dr("{} Total DS generated for EPP call.".format(len(result)))
    else:
        raise DsapException('No Valid DS was generated for bootstrap. '
                            'Supported Algorithms:  {}'.format(DIGEST_TYPES.pretty_supported()))

    return {"add": result}

def maintenance(domain_name): # PUT

    logger.info("Maintenance on zone {}".format(domain_to_zone(domain_name)))

    op, domain_name = secure_load_operations(domain_name)
    print_parents_sync()
    op.create_squery_for_current()
    query, cds = op.get_query_cds_record()

    for cur_cds in cds[:]:
        try:
            print_ds(cur_cds)
            if(cds_is_empty(cur_cds)):
                raise InvalidCdsException('    {}: Null CDS found.  Unable to perform secure delegation maintenance with null CDS.'.format(domain_name))
            validate_cds_digest(cur_cds)
        except InvalidCdsException as ex:
            cds.remove(cur_cds)
            logger.mul_dr(ex.message)

    if(len(cds) == 0):
        raise DsapException('{}: No valid CDS found for secure domain maintenance operation.'.format(domain_name))

    print_break()

    # zone needs to already have a DS in order to maintain it
    query, ds = op.get_query_ds_record()
    if len(ds) == 0: 
        raise DsapException('{}: No DS records to maintain in zone.'.format(domain_name))
    logger.mul_dr("Including existent DS digest for removal: ")
    new_ds, new_cds = [], []
    for dsrecord in ds:
        print_ds(dsrecord)
        logger.mul_dr("{} DS will be included to EPP call for Removal.".format(dsrecord["key_tag"]))
        new_ds.append({
            'key_tag': dsrecord["key_tag"],
            'algorithm': dsrecord["algorithm"],
            'digest_type': dsrecord["digest_type"],
            'digest': binascii.hexlify( dsrecord["digest"] ).decode('utf-8'),
        })

    print_break()
    logger.mul_dr("Including new CDS digest for addition: ")
    for cdsrecord in cds:
        print_ds(cdsrecord)
        logger.mul_dr("{} DS will be included to EPP call for Addition.".format(cdsrecord["key_tag"]))
        new_cds.append({
            'key_tag': cdsrecord["key_tag"],
            'algorithm': cdsrecord["algorithm"],
            'digest_type': cdsrecord["digest_type"],
            'digest': binascii.hexlify( cdsrecord["digest"] ).decode('utf-8'), # hexlify?
        })

    to_add, to_rem = get_ds_remove_add_lists(new_ds, new_cds)
    
    return {"add": to_add, "rem": to_rem}

def unsign(domain_name): # DELETE

    logger.info("Unsigning zone {}".format(domain_to_zone(domain_name)))
    
    op, domain_name = secure_load_operations(domain_name)

    print_parents_sync()

    op.create_squery_for_current()
    query, cds = op.get_query_cds_record()


    for cur_cds in cds:
        print_ds(cur_cds)

    if (not cds_is_empty(cds[0])):
        # can check for [0] only since we already except when getting cds
        # if there are both empty and non-empty cds records
        raise DsapException('{}: Null CDS not found.  Unable to remove secure delegation.'.format(domain_name))
    else:
        logger.mul_dr("Null CDS successfully loaded.")


    print_break()
    
    # zone needs to already have a DS in order to unsign it
    query, ds = op.get_query_ds_record()

    if len(ds) == 0:
        raise DsapException('{}: No DS records to delete in zone.'.format(domain_name))

    logger.mul_dr("Chain of trust successfully validated for {}".format(domain_name))
    print_break()

    result = []
    for dsrecord in ds:
        print_ds(dsrecord)
        logger.mul_dr("{} DS will be included into EPP call for removal.".format(dsrecord["key_tag"]))
        result.append({
            'key_tag': dsrecord["key_tag"],
            'algorithm': dsrecord["algorithm"],
            'digest_type': dsrecord["digest_type"],
            'digest': dsrecord["digest"],
        })
    for ds in result:
        ds["digest"] = binascii.hexlify( ds["digest"] ).decode('utf-8')
        ds.pop('rdata_raw', None) # remove c buffer data

    return {"rem": result}
