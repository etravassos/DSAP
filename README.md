#DSAP
##Welcome to the DS Automated Provisioning (DSAP) prototype. 
DSAP was developed to enable DNS Operator for perform automated DNSSEC provisioning activities such as creating the initial secure delegation for a properly signed domain, to perform automated DNSSEC maintenance activities and ultimately to remove the secure delegation of a domain.

DSAP is an implementation of the protocol defined in [https://tools.ietf.org/html/draft-ietf-regext-dnsoperator-to-rrr-protocol-01](https://tools.ietf.org/html/draft-ietf-regext-dnsoperator-to-rrr-protocol-01)
  
CIRA created 5 test domains with various configuration to test the API.  
  
- CIRA-DSAP-1.CA – SECURE DOMAIN – create initial secure delegation – add DS
  
- CIRA-DSAP-2.CA – SECURE DOMAIN – validation failure due to lame delegation
  
- CIRA-DSAP-3.CA – REMOVE SECURE DELEGATION – remove DS
  
- CIRA-DSAP-4.CA – SECURE DOMAIN MAINTENANCE – remove a DS record
  
- CIRA-DSAP-5.CA – SECURE DOMAIN MAINTENANCE – add a DS record  
  
We developed a web based interface to enable individual DNS Operator to perform DNSSEC maintenance activities ([http://dsap.ciralabs.ca](http://dsap.ciralabs.ca))  
  
The RESTful API is available under [http://dsap.ciralabs.ca/api](http://dsap.ciralabs.ca/api)  
  
At this time, dsap.ciralabs.ca functions only in test mode, no EPP commands are sent to the .CA registry.  The prototype allows for
.CA and .COM testing.  DSAP has a preview mode that provides a verbose output. The prototype is also by default in high verbose mode.  
  
Feedback is more than welcome ([dsap@cira.ca](mailto:dsap@cira.ca)).
  
Below is the expected DSAP behaviour for each test domain.

###CIRA-DSAP-1.CA – SECURE DOMAIN:

POST [http://dsap.ciralabs.ca/api/domains/cira-dsap-1.ca/cds/](http://dsap.ciralabs.ca/api/domains/cira-dsap-1.ca/cds/)

·        
Zone properly signed

·        
Good DNS Hygiene

·        
Valid CDS records (3 records) for same key

·        
No DS present
 
Output:

·        
Status 201 

Action: (behind the scene)

DSAP would execute the following EPP command to create a DS record for the given domain name.

{

  "epp": {

   
"add": [

      {

       
"digest_type": 2,

       
"algorithm": 8,

       
"key_tag": 27022,

       
"digest": "6abc389804c23ceb9046ec9a35a3b254f1b8ba6a430d604aac1ed1b610a1d226"

      }

    ]

  }


###CIRA-DSAP-2.CA – SECURE DOMAIN:

POST [http://dsap.ciralabs.ca/api/domains/cira-dsap-2.ca/cds/](http://dsap.ciralabs.ca/api/domains/cira-dsap-2.ca/cds/)

·        
Zone properly signed

·        
Valid CDS record (1 record)

·        
Lame Delegation

·        
No DS present

 

Output:

·        
Status 400

·        
(Validation failure; lame delegation)

### CIRA-DSAP-3.CA – REMOVE SECURE DELEGATION:

DELETE [http://dsap.ciralabs.ca/api/domains/cira-dsap-3.ca/cds/](http://dsap.ciralabs.ca/api/domains/cira-dsap-3.ca/cds/)

·        
Zone properly signed

·        
Secure delegation valid with DS (2 records) for
same key.

·        
Valid NULL CDS record (1 record)

 

Output:

·        
Status 200

 

Action: (behind the scene)

·        
DSAP would execute the following EPP command to
remove two (2) DS records for the given domain name. 

{

  "epp": {

   
"rem": [

      {

       
"digest_type": 1,

       
"algorithm": 8,

       
"key_tag": 11869,

       
"digest":
"950bd7dd077b8de1d2bd180a3ffc8ca29aa4c0f0"

      },

      {

       
"digest_type": 2,

       
"algorithm": 8,

        "key_tag":
11869,

       
"digest":
"6610f35be88666d2dd82f45fec1d4c8e18f479476e6359f980204ac6f48140c5"

      }

    ]

  },

**

 **

**

 **

**

### CIRA-DSAP-4.CA – SECURE DOMAIN MAINTENANCE:

PUT [http://dsap.ciralabs.ca/api/domains/cira-dsap-4.ca/cds/](http://dsap.ciralabs.ca/api/domains/cira-dsap-4.ca/cds/)

·        
Zone properly signed

·        
Secure delegation valid with DS (2 records)

·        
Valid CDS record (1 records)

 

Output:

·        
Status 200

 

Action: (behind the scene)

·        
DSAP would execute the following EPP command to remove one (1) DS records for the given domain name. 

{

  "epp": {

   
"rem": [

      {

       
"digest_type": 2,

       
"algorithm": 8,

       
"key_tag": 12334,

       
"digest": "8d3f024cf63bb536dd3fff59bbe2cd9c0a17ba6c467a17955adf9e29197d5422"

      }

    ],

   
"add": []

  },

### CIRA-DSAP-5.CA – SECURE DOMAIN MAINTENANCE:

PUT [http://dsap.ciralabs.ca/api/domains/cira-dsap-5.ca/cds/](http://dsap.ciralabs.ca/api/domains/cira-dsap-5.ca/cds/)

·        
Zone properly signed

·        
Secure delegation valid with DS (1 records)

·        
Valid CDS record (2 records)

Output:

·        
Status 200

 

Action: (behind the scene)

·        
DSAP would execute the following EPP command to
add (1) DS records for the given domain name. 

{

  "epp": {

   
"rem": [],

   
"add": [

      {

       
"digest_type": 2,

       
"algorithm": 8,

       
"key_tag": 61939,

       
"digest":
"95b5879ece5418cfbd1dc354dc684c3f8ac33d21a48ceed0c5eef1a969c37e9d"

      }

    ]

  },

 
