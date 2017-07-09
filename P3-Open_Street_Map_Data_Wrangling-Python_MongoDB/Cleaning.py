'''
                                           ##################
                                           # Cleaning Flow: #
                                           ##################
        
        1) Cleaning:
            1.1) Defining update_street function to clean the street names.
            1.2) Defining update_city function to clean the city names.
            1.3) Defining update_zipcode function to clean the zip codes.
            1.4) Defining update_phone function to clean the phone numbers.
            1.5) Defining shape_element function to create a mongo DB document 
                 by using all the cleaning functions.
            1.6) Defining process_map function to write the document to JSON file
            
            
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



# Regular expression: 

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



def update_street(street,mapping):
    ''' 
    The update_street function updates the inconsistent street types to the consistent types. 
    It uses the mapping dictionary which is created after audting the street names. 
    '''
    m = re.search(street_type_re,street)
    if m.group() in mapping.keys():
        p = street.split(m.group())
        return p[0] + mapping[m.group()]
    else:
        return street


def update_city(city):
    ''' 
    The update_city function updates the inconsistent city names. If the city has 'TX' at 
    the end, it removes 'TX' and returns just the city name.
    
    '''
    m = re.search(city_re,city)
    if m:
        p = city.split(',')
        return p[0]
    else:
        return city




def update_zipcode(zipcode):
    ''' 
    The update_zipcode function updates the inconsistent zipcodes. It cleans two types of inconsistent 
    zip codes.

    1) The zip code which has a '-' is made consistent by removing the '-' and digits after that. It 
       retuns a five digit number.
    2) The zip code which starts with TX is made consistent by removing 'TX'. Returns a five digit number.
    '''
    m1 = re.search(zip_code1_re,zipcode)
    m2 = re.search(zip_code2_re,zipcode)
    if m1:
        p = zipcode.split('-')
        return p[0]
    elif m2:
        p = zipcode.split(' ')
        return p[1]
    else:
        return zipcode


def update_phone(phone):
    ''' The update_phone function returns the phone number in a standard format {(XXX) XXX-XXXX}. It makes use of 
    Phonenumbers module [8] to format number. This function is called only for the phone numbers which start 
    with '+1' or '(' or any digit from [2-9].
    '''
    return phonenumbers.format_number(phonenumbers.parse(phone, 'US'), phonenumbers.PhoneNumberFormat.NATIONAL)



def shape_element(element,mapping):
    ''' 
    The shape_element function accepts the XML tag (Nodes and Ways) as an argument and returns a 
    dictionary. The cleaning functions of specific attributes are called here and cleansed values 
    are written to the dictionary.  
    '''
    node = {}
    if element.tag == "node":
        l = element.attrib.keys()
        node["id"] = element.attrib["id"]
        node["type"] = "node"
        if "visible" in l:
            node["visible"] = element.attrib["visible"]
        created = {}
        created["version"] = element.attrib["version"]
        created["changeset"] = element.attrib["changeset" ]
        created["timestamp"] =element.attrib["timestamp"]
        created["user"] = element.attrib["user"]
        created["uid"] = element.attrib["uid"]
        node["created"] = created
        pos = []
        pos.append(float(element.attrib["lat"]))
        pos.append(float(element.attrib["lon"]))
        node["pos"] = pos
        address = {}
        for tag in element.iter("tag"):
            if ((not re.search(problemchars,tag.attrib["k"])) and re.search(zero_one_colon,tag.attrib["k"])):
                if(tag.attrib["k"][0:4]=="addr"):
                    if(tag.attrib["k"]=="addr:street"):
                        address["street"] = update_street(tag.attrib["v"],mapping)
                    elif(tag.attrib["k"]=="addr:city"):
                        address["city"] = update_city(tag.attrib["v"])
                    elif(tag.attrib["k"]=="addr:postcode"):
                        address["postcode"] = update_zipcode(tag.attrib["v"])
                    else:
                        l = tag.attrib["k"].split(':')
                        address[l[1]] = tag.attrib["v"]
                elif(':' in tag.attrib["k"]):
                    s = tag.attrib["k"].replace(':','_')
                    node[s] = tag.attrib["v"]
                elif(tag.attrib["k"]=="phone"):
                    if re.search(phone_start_re,tag.attrib["v"]):
                        node["phone"] = update_phone(tag.attrib["v"])
                else:
                    node[tag.attrib["k"]] = tag.attrib["v"]
                
        if(address):
            node["address"] = address                    
        return node
    elif element.tag == "way":
        l = element.attrib.keys()
        node["id"] = element.attrib["id"]
        node["type"] = "way"
        if "visible" in l:
            node["visible"] = element.attrib["visible"]
        created = {}
        created["version"] = element.attrib["version"]
        created["changeset"] = element.attrib["changeset" ]
        created["timestamp"] =element.attrib["timestamp"]
        created["user"] = element.attrib["user"]
        created["uid"] = element.attrib["uid"]
        node["created"] = created
        ref = []
        for r in element.iter("nd"):
            ref.append(r.attrib["ref"])
        node["node_refs"] = ref
        address = {}
        for tag in element.iter("tag"):
            if ((not re.search(problemchars,tag.attrib["k"])) and re.search(zero_one_colon,tag.attrib["k"])):
                if(tag.attrib["k"][0:4]=="addr"):
                    if(tag.attrib["k"]=="addr:street"):
                        address["street"] = update_street(tag.attrib["v"],mapping)
                    elif(tag.attrib["k"]=="addr:city"):
                        address["city"] = update_city(tag.attrib["v"])
                    elif(tag.attrib["k"]=="addr:postcode"):
                        address["postcode"] = update_zipcode(tag.attrib["v"])
                    elif(tag.attrib["k"]=="phone"):
                        if re.search(phone_start_re,tag.attrib["v"]):
                            node["phone"] = update_phone(tag.attrib["v"])
                    else:
                        l = tag.attrib["k"].split(':')
                        address[l[1]] = tag.attrib["v"]
                elif(':' in tag.attrib["k"]):
                    s = tag.attrib["k"].replace(':','_')
                    node[s] = tag.attrib["v"]
                else:
                    node[tag.attrib["k"]] = tag.attrib["v"]
                
        if(address):
            node["address"] = address                    
        return node
    else:
        return None


def process_map(file_in, pretty):
    ''' The process map function creates a new JSON file. It calls the shape_element function for each tag and 
    writes the dictionary to json to a new line.
    '''
    
    '''
        After auditing the street names, the above street types are found to be inconsistent. Few of the above types can be
        made consistent by updating the street types using the below mapping dictionary
        For example: 'Louetta Rd' => 'Louetta Road'
    '''
    mapping = {
           "Rd":"Road",
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
    file_out = "{0}.json".format(file_in)
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element,mapping)
            if el:
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")



def test():
	file_in = "houston_sample.osm"
	process_map(file_in, False)
	print ("The JSON document has been created")

if __name__ == "__main__":
    test()

