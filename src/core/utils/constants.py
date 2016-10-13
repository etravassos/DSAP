
supported_tlds = set(['ca', 'com'])


class EPP:
    CMD_SUCCESS                 = 1000
    CMD_SUCCESS_ACTION_PENDING  = 1001
    CMD_SUCCESS_NO_MSG          = 1300
    CMD_SUCCESS_ACK_DEQUEUE     = 1301
    CMD_SUCCESS_ENDING_SESSION  = 1500
    
    
    CMD_ERR_UNKNOWN_CMD             = 2000
    CMD_ERR_SYNTAX                  = 2001
    CMD_ERR_USE                     = 2002
    CMD_ERR_MISSING_PARAMETER       = 2003
    CMD_ERR_PARAMETER_VALUE_RANGE   = 2004
    CMD_ERR_PARAMETER_SYNTAX        = 2005
    
    CMD_ERR_UNIMPLEMENTED_PROTOCOL_VERSION  = 2100
    CMD_ERR_UNIMPLEMENTED_CMD               = 2101
    CMD_ERR_UNIMPLEMENTED_OPTION            = 2102
    CMD_ERR_UNIMPLEMENTED_EXTENSION         = 2103
    CMD_ERR_BILLING_FAILURE                 = 2104
    CMD_ERR_OBJECT_NOT_ELIGIBLE_RENEWAL     = 2105
    CMD_ERR_OBJECT_NOT_ELIGIBLE_TRANSFER    = 2106
    
    CMD_ERR_AUTHENTICATION              = 2200
    CMD_ERR_AUTHORIZATION               = 2201
    CMD_ERR_INVALID_AUTHORIZATION_INFO  = 2202
    
    CMD_ERR_OBJECT_PENDING_TRANSFER             = 2300
    CMD_ERR_OBJECT_NOT_PENDING_TRANSFER         = 2301
    CMD_ERR_OBJECT_EXISTS                       = 2302
    CMD_ERR_OBJECT_DOES_NOT_EXIST               = 2303
    CMD_ERR_OBJECT_STATUS_PROHIBITS_OP          = 2304
    CMD_ERR_OBJECT_ASSOCATION_PROHIBITS_OP      = 2305
    CMD_ERR_PARAMETER_VALUE_POLICY              = 2306
    CMD_ERR_UNIMPLEMENTED_OBJECT_SERVICE        = 2307
    CMD_ERR_DATA_MANAGEMENT_POLICY_VIOLATION    = 2308
    
    CMD_ERR_FAILED                              = 2400
    CMD_ERR_FAILED_CLOSING_CONNECTION           = 2500
    CMD_ERR_AUTHENTICATION_CLOSING_CONNECTION   = 2501
    CMD_ERR_SESSION_LIMIT_CLOSING_CONNECTION    = 2502
    
    CMD_SUCCESS_CODES = ( 
            CMD_SUCCESS, CMD_SUCCESS_ACTION_PENDING, 
            CMD_SUCCESS_NO_MSG, CMD_SUCCESS_ACK_DEQUEUE,
            CMD_SUCCESS_ENDING_SESSION
            )
    CMD_FAILURE_CODES = (
            CMD_ERR_UNKNOWN_CMD, CMD_ERR_SYNTAX, CMD_ERR_USE,
            CMD_ERR_MISSING_PARAMETER, CMD_ERR_PARAMETER_VALUE_RANGE,
            CMD_ERR_PARAMETER_SYNTAX, CMD_ERR_UNIMPLEMENTED_PROTOCOL_VERSION,
            CMD_ERR_UNIMPLEMENTED_CMD, CMD_ERR_UNIMPLEMENTED_OPTION,
            CMD_ERR_UNIMPLEMENTED_EXTENSION, CMD_ERR_BILLING_FAILURE,
            CMD_ERR_OBJECT_NOT_ELIGIBLE_RENEWAL, CMD_ERR_OBJECT_NOT_ELIGIBLE_TRANSFER,
            CMD_ERR_AUTHENTICATION, CMD_ERR_AUTHORIZATION,
            CMD_ERR_INVALID_AUTHORIZATION_INFO, CMD_ERR_OBJECT_PENDING_TRANSFER,
            CMD_ERR_OBJECT_NOT_PENDING_TRANSFER, CMD_ERR_OBJECT_EXISTS,
            CMD_ERR_OBJECT_DOES_NOT_EXIST, CMD_ERR_OBJECT_STATUS_PROHIBITS_OP,
            CMD_ERR_OBJECT_ASSOCATION_PROHIBITS_OP, CMD_ERR_PARAMETER_VALUE_POLICY,
            CMD_ERR_UNIMPLEMENTED_OBJECT_SERVICE, CMD_ERR_DATA_MANAGEMENT_POLICY_VIOLATION,
            CMD_ERR_FAILED, CMD_ERR_FAILED_CLOSING_CONNECTION,
            CMD_ERR_AUTHENTICATION_CLOSING_CONNECTION, CMD_ERR_SESSION_LIMIT_CLOSING_CONNECTION,
            )
    

class LOGGING:
    RESP_STREAM_LEVEL = 162
    
class FLAGS:
    ZSK         = 256
    KSK         = 257

class PROTOCOL:
    VALID                  = 3

class CODED_LABEL(object):
        def __init__(self, code, label):
            self._code = code
            self._label = label
        def __str__(self):
            return "{}({})".format(self._label, self._code)

class TYPED(object):
    supported   = []
    unsupported = []

    @classmethod
    def get_obj(cls, code):
        for e in cls.supported + cls.unsupported:
            if code == e._code: return e
        return

    @classmethod
    def supports(cls, digest_type):
        for e in cls.supported:
            if digest_type == e._code: return True
        return False

    @classmethod
    def pretty_supported(cls):
        return ", ".join([str(i) for i in cls.supported])

class DS_ALGS(TYPED):
    class DS_ALG(CODED_LABEL):
        pass

    RESERVED                = [0]

    RSAMD5                  = DS_ALG(1, 'RSAMD5')
    DH                      = DS_ALG(2, 'DH')
    DSA                     = DS_ALG(3, 'DSA')

    RESERVED               += [4]

    RSASHA1                 = DS_ALG(5, 'RSASHA1')
    DSA_NSEC3_SHA1          = DS_ALG(6, 'DSA_NSEC3_SHA1')
    RSASHA1_NSEC3_SHA1      = DS_ALG(7, 'RSASHA1_NSEC3_SHA1')

    RSASHA256               = DS_ALG(8, 'RSASHA256')

    RESERVED               += [9]

    RSASHA512               = DS_ALG(10, 'RSASHA512')

    RESERVED               += [11]

    ECC_GOST                = DS_ALG(12, 'ECC_GOST')

    ECDSAP256SHA256         = DS_ALG(13, 'ECDSAP256SHA256')
    ECDSAP384SHA384         = DS_ALG(14, 'ECDSAP384SHA384')

    UNASSIGNED              = list(range(15, 122+1))
    RESERVED               += list(range(123, 251+1))

    INDIRECT                = 252
    PRIVATEDNS              = 253
    PRIVATEOID              = 254

    RESERVED               += [255]

    supported = [RSAMD5, DH, DSA, RSASHA1, DSA_NSEC3_SHA1, RSASHA1_NSEC3_SHA1,
                 RSASHA256, RSASHA512, RSASHA512, ECC_GOST, ECDSAP256SHA256, ECDSAP384SHA384]

class DIGEST_TYPES(TYPED):
    class DIGEST_TYPE(CODED_LABEL):
        pass

    SHA_1                   = DIGEST_TYPE(1, 'SHA1')
    SHA_256                 = DIGEST_TYPE(2, 'SHA256')
    ECC_GOST                = DIGEST_TYPE(3, 'ECCGOST')
    SHA_384                 = DIGEST_TYPE(4, 'SHA_384')

    RESERVED                = [0]
    UNASSIGNED              = list(range(5, 255+1))

    supported    = [SHA_1, SHA_256]
    unsupported  = [ECC_GOST, SHA_384]

class QUERY_TYPES(TYPED):
    class QUERY_TYPE(CODED_LABEL):
        pass
    A           = QUERY_TYPE(1, 'A')
    NS          = QUERY_TYPE(2, 'NS')
    AAAA        = QUERY_TYPE(28, 'AAAA')
    DS          = QUERY_TYPE(43, 'DS')
    CDS         = QUERY_TYPE(59, 'CDS')
    DNSKEY      = QUERY_TYPE(48, 'DNSKEY')

    CDNSKEY     = QUERY_TYPE(60, 'CDNSKEY')
    DNSKEY      = QUERY_TYPE(48, 'DNSKEY')
    RRSIG       = QUERY_TYPE(46, 'RRSIG')
    SOA         = QUERY_TYPE(6, 'SOA')
    TSIG        = QUERY_TYPE(250, 'TSIG')
    AXFR        = QUERY_TYPE(252, 'AXFR')
    IXFR        = QUERY_TYPE(251, 'IXFR')

    supported = [A, NS, AAAA, CDNSKEY, CDS,
                 DNSKEY, DS, RRSIG, SOA, TSIG,
                 AXFR, IXFR,]
