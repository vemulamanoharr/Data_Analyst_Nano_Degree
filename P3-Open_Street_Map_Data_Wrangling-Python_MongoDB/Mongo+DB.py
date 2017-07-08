
'''
                                           ##################
                                           # Program Flow: #
                                           ##################
        
        1) Mongo DB:
            1.1) Connecting to Mongo DB local host.
            1.2) Printing the stats of the OSM collection.
            1.3) Printing the counts of the document.
            1.4) Different queries on OSM collection.
            
'''
from pymongo import MongoClient
import pprint
client = MongoClient("mongodb://localhost:27017")
db = client.openstreetmap




# Statistics of OSM collection:
print("Stats of Houston collection")
pprint.pprint(db.command("dbstats"))




'''
    Some fun with the counts:
'''
num_docs = db.houston.find().count()
print "Number of documents inserted:", num_docs

node_query = {"type":"node"}
num_nodes = db.houston.find(node_query).count()
print "Number of nodes inserted:", num_nodes

way_query = {"type":"way"}
num_ways = db.houston.find(way_query).count()
print "Number of ways inserted:", num_ways




'''
    There is a count mismatch. We have document types other than node and way inserted into mongo DB. 
    We have 15 such documents
'''
type_pipeline = [
            {"$match":{"type":{"$ne":"node"}}},
            {"$match":{"type":{"$ne":"way"}}}      
]




'''
    Print all the inconsistent types:
'''
print ("Invalid tag types:")
for doc in db.houston.aggregate(type_pipeline):
    print doc["type"]


# After researching those specific documets, I noticed that they are actually node or way types but they are having extra 
# attribute called "type". So the exisiting type value (node or way) in the dictionary is repalced. As there are only 15 such 
# documents I decided to leave as them as such without deleting or updating.



'''
    Number of unique users:
'''
users = db.houston.distinct('created.user')
print "Number of users who contributed to OSM-Houston area:", len(users)




def aggregate(pipeline):
    return [doc for doc in db.houston.aggregate(pipeline,allowDiskUse=True)]




# Few basic stats (Ones suggested in project requirements)
'''
    Top ten creators
'''
user_pipeline = [{"$group":{"_id": "$created.user",
                          "count":{"$sum":1}}},
                 {"$sort":{"count":-1}},
                 {"$limit":10}
                ]
users = aggregate(user_pipeline)
print("Top 10 contributors:")
pprint.pprint(users)




'''
    Top ten sources
'''
source_pipeline = [{"$match":{"source":{"$exists":1}}},
                   {"$group":{"_id":"$source",
                             "count":{"$sum":1}}},
                   {"$sort":{"count":-1}},
                   {"$limit":10}
                  ]
sources = aggregate(source_pipeline)
print("Top 10 sources:")
pprint.pprint(sources)




'''
    Ameneties in The WoodLands city(My locality). I learnt how to use logical operator within 
    match operator [5].
'''
woodlands_pipeline = [{"$match":{
                           "$or":[
                                   {"address.city":{"$eq":"The Woodlands"}},
                                   {"address.city":{"$eq":"woodlands"}} 
                                 ]}},
                       {"$match":{"amenity":{"$exists":1}}},
                       {"$project":{"amenity":"$amenity",
                                  "name":"$name",
                                   "_id":0}}
                     ]
woodlands_amenity = aggregate(woodlands_pipeline)
print("Amenities in The Woodlands:")
pprint.pprint(woodlands_amenity)




'''
    Top five areas in Houston with more number of amenities:
'''
city_amenities_pipeline = [{"$match":{"amenity":{"$exists":1}}},
                           {"$match":{"address.city":{"$exists":1}}},
                           {"$group":{"_id":"$address.city",
                             "count":{"$sum":1}}},
                           {"$sort":{"count":-1}},
                           {"$limit":5}
                          ]
city_amenities = aggregate(city_amenities_pipeline)
print("Top five areas with more number of amenities:")
pprint.pprint(city_amenities)




'''
    Eataries with Chinese Cuisine:
'''
chinese_cuisine_pipeline = [{"$match":{
                            "$or":[
                                   {"amenity":{"$eq":"restaurant"}},
                                   {"amenity":{"$eq":"fast_food"}} 
                                 ]}},
                            {"$match":{"cuisine":{"$eq":"chinese"}}},
                            {"$project":{
                                  "name":"$name",
                                   "_id":0}}
                           ]
chinese_cuisine = aggregate(chinese_cuisine_pipeline)
print("Eataries with Chinise cuisine:")
pprint.pprint(chinese_cuisine)




'''
    What is the most referred node in Houston city? Bar? Place_of_Worship? Lets check it out!
'''
node_ref_pipeline = [{"$match":{"type":{"$eq":"way"}}},
                     {"$unwind":"$node_refs"},
                     {"$group":{"_id":"$node_refs",
                             "count":{"$sum":1}}},
                     {"$sort":{"count":-1}},
                     {"$limit":1}
                    ]
node_ref = aggregate(node_ref_pipeline)
print("Most referenced node in Houston:")
pprint.pprint(node_ref)

# Initially the group statemnt exceded 100MB of data and the query failed. Upon further researching I learnt about
# allowDiskUse=True option in aggrgation framework [6]. I updated the aggregate funnction.




'''
    Extracting the most referenced node details:
'''
ref = [{"$match":{"id":{"$eq":node_ref[0]["_id"]}}}
      ]
n = aggregate(ref)
pprint.pprint(n)

# Unfortunately we do not have any deatils of the most referenced node except the position



'''
    Time to validate our update_zipcode function:
'''
zipcode_pipeline = [{"$match":{"address.postcode":{"$exists":1}}},
                    {"$group":{"_id":"$address.postcode"}}
                   ]
zipcode = aggregate(zipcode_pipeline)

'''
    The update_zipcode function cleans only two types of inconsistencies(TX 77086 and 77340-7856). 
    The below result shows that the two inconsistencies are cleaned very well. But, we do have other 
    invalid formats like street name in zipcode or a 9 digit zipcode without '-' or a zipcode with 
    less than 5 digits. If the zipcode auditing is very critical then we have to clean those kind 
    of inconsistencies by revisiting the cleaning process (Data Wrangling is an iterative proccess). 
'''

print("Zip codes in Houston:")
pprint.pprint(zipcode)

