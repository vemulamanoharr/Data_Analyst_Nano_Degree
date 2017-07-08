'''
                                           ##################
                                           # Auditing Flow: #
                                           ##################
        
        1) Auditing:
            1.1) Loading the OSM file.
            1.2) Study of the file structure(Different tags,attributes etc...)
            1.3) Defining different regular expression
            1.4) Defining audit_osm function
            1.5) Analysis of audited fields by printing them
            1.6) Comments on the audit results and cleaning tasks
            
'''
import os
import xml.etree.ElementTree as ET
from collections import defaultdict
import pprint
import re
import phonenumbers
import codecs
import json
import pprint



'''houston_sample.osm file is downloaded from Mapzen metro extracts.
   The downloaded file is in compressed format (.osm.bz2). 
   '''

# 1.1) Loading the OSM file.
print ("Size of houston_sample.osm file in bytes:")
print (os.path.getsize("houston_sample.osm"))


osm_file = open("houston_sample.osm", "r")

'''The data in OSM file is organized in XML format. 
   It has a root node and many child nodes. Python provides us many
   ways to parse an XML file. Since the file is huge there is a need
   parse the file iteratively. By parsing iteratively we load one node
   into memory for each iteration. To identify the elements that are to
   be audited and cleaned we should be aware of different types of tags in 
   the file.'''

   
# 1.2) Study of the file structure(Different tags,attributes etc...)
all_tags = {}

for _,element in ET.iterparse(osm_file):
    if element.tag in all_tags:
        all_tags[element.tag] += 1
    else:
        all_tags[element.tag] = 1


'''All the tags of OSM file are displayed below. OSM has three main data structures [3]
    1) Node
    2) Way
    3) Relation
    
    Each tag describes a geographic attribute of the feature being shown by that specific node, 
    way or relation.
    
    A node is one of the core elements in the OpenStreetMap data model. It consists of a single point in 
    space defined by its latitude, longitude and node id.
    
    A way is an ordered list of nodes which normally also has at least one tag or is included within a 
    Relation. 
    
    A relation consists of one or more tags and also an ordered list of one or more nodes, ways and/or 
    relations as members which is used to define logical or geographic relationships between other 
    elements.
    
    '''

print ("The tags and their count:")
pprint.pprint (all_tags)



print "The Houston metro extract has: %d nodes and %d ways" %(all_tags["node"],all_tags["way"])

# 1.3) Defining different regular expression

street = re.compile(r'^(addr:street$)')
city = re.compile(r'^(addr:city$)')
postcode = re.compile(r'^(addr:postcode$)')

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
#The above regular expression captures the last part of the street name
#For example: street_type_re.search(Hillcroft Rd.) => Rd.

city_re = re.compile(r'TX$', re.IGNORECASE)
zero_one_colon = re.compile(r'^(\w+:?\w*$)')
zip_code1_re = re.compile(r'(-\d*$)')
zip_code2_re = re.compile(r'(^TX)',re.IGNORECASE)
phone_start_re = re.compile(r'^(\(|\+1|[2-9])')


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


'''
The approved list is provided by Houston city council. It is avalible in appendix III of [4]
'''

Houston_approved_st_types = ["Avenue","Boulevard","Bridge","Bypass","Circle","Court","Crossing",
                             "Crossroad","Drive","Expressway","Fork","Freeway","Freeway","Highway",
                             "Lane","Loop","Motorway","Oval","Parkway","Passage","Path","Place",
                             "Road","Street","Throughway","Trail","Tunnel","Way"]




'Auditing the necessary attributes:'
street_types = defaultdict(set)
post_code_set = set()
city_set = set()
phone_set = set()

# 1.4) Defining audit_osm function    

def audit_osm(osmfile):
    osm_file = open(osmfile, "r")
    for _, element in ET.iterparse(osm_file):
        if element.tag == "way" or element.tag == "node":
            for tag in element.iter("tag"):
                if re.search(street,tag.attrib["k"]):
                    m = street_type_re.search(tag.attrib["v"])
                    if m:
                        street_type = m.group()
                        if street_type not in Houston_approved_st_types:
                            street_types[street_type].add(tag.attrib["v"])
                elif re.search(city,tag.attrib["k"]):
                    city_set.add(tag.attrib["v"])
                elif re.search(postcode,tag.attrib["k"]):
                    post_code_set.add(tag.attrib["v"])
                elif(tag.attrib["k"]=="phone"):
                    phone_set.add(tag.attrib["v"])
                





osm_file = "houston_sample.osm"
audit_osm(osm_file)


# 1.5) Analysis of audited fields by printing them
print ("Inconsistent street types:")
print(street_types.keys())




''' After auditing the street names, the above street types are found to be inconsistent. Few of the above types can be
made consistent by updating the street types using the below mapping dictionary
For example: 'Louetta Rd' => 'Louetta Road'
'''
mapping = {"Rd":"Road",
           "S.":"South",
           "Stree":"Street",
           "street":"Street",
           "Ave.":"Avenue",
           "Fwy":"Freeway",
           "Es":"East",
           "St.":"Street",
           "Blvd.":"Boulevard",
           "St":"Street",
           "Rd.":"Road",
           "ST":"Street",
           "Frwy":"Freeway",
           "Ave":"Avenue",
           "Ln":"Lane",
           "blvd":"Boulevard",
           "Dr":"Drive",
           "Expy":"Expressway",
           "N":"North",
           "E":"East",
           "W":"West",
           "S":"South"
    
}




'''
   After auditing the city names, there are few inconsistent city names which are appended with ", Tx". 
   Those cities can be updated and made consistent just by having city name alone.
   For example: 'Angleton,TX' => 'Angleton'
   
'''
print('Cities in Hoouston Area:')
print city_set




'''
    After auditing the postal codes, there are few inconsistent codes which begin with 'TX'. 
    Those postal codes can be updated to one consistent format. The second type of cleaning 
    can be done on nine digit postal codes. Nide digits can be converted to a five digit code.

    For example: a) "TX 77086"    => "77086"
                 b) "77025-9998"  => "77025" 
'''

print ("Zip codes of Houston Area:")
print (post_code_set)

print ("Phone numbers:")
print (phone_set)


# 1.6) Comments on the audit results and cleaning tasks

'''
  This project audits and cleans only two types of tags(nodes,ways) and their attributes. With the help 
  of classroom casestudy the following steps are considered for auditing and cleaning:

 - Process only 2 types of top level tags: "node" and "way
 
 - All attributes of "node" and "way" should be turned into regular key/value pairs, except:
     - attributes in the CREATED array should be added under a key "created"
     - attributes for latitude and longitude should be added to a "pos" array,
       for use in geospacial indexing. Make sure the values inside "pos" array are floats
       and not strings.
       
 - If the second level tag "k" value contains problematic characters, it should be ignored.
 
 - If the second level tag "k" value starts with "addr:", it should be added to a dictionary "address"
 
 - The value of addr:street should be audited and the unexpected street types should be cleaned to an
   appropriate ones in the expected list provided by Houston city council[4]. The street name may appear
   in both the node and way tags.
   For example: St.  => Street
                Blvd => Boulevard
   
 - If the second level tag "k" value does not start with "addr:", but contains ":", it can be
   processed any way. 
    
 - If there is a second ":" that separates the type/direction of a street,
   the tag should be ignored.(Only for attributes of type 'addr')
   
 - The value of addr:city should be audited and the unexpected city names should be cleaned to 
   exact city name.
   For example: "Pearland, TX" => "Pearland"
   
 - The value of addr:postcode should be audited and the unexpected post codes should be cleaned to 
   standard format.
   For example: "TX 77009"   => "77009"
                "77340-3124" => "77340"  
            
 - If there is a second ":", it should be replaced with "_" and added as key value pairs

 - The value of phone should be audited and converted to standard format. There are many 
   standard formats for phone number but I would like to store the number as one format in
   my DB. The standard format would be (XXX) XXX-XXXX.
   For example: = +1 281-776-0143 => (281) 776-0143
  '''