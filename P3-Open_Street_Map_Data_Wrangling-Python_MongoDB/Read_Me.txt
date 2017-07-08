Project: OpenStreetMap Data Wrangling
By: Vemula Manohar Reddy

Data Wrangling is one of the most important phases in Data Sceince. Sources say that data wrangling constitute to 70 percent of Data analysis work. It is 
a process of gathering, extracting, cleaning and storing our data. Most of the data avaliable today is in complex formats. Those formats include data 
from social networking sites, video streaming sites etc.. in XML,JSON or many standard formats. Data wrangling begins with gathering of data from any of 
the sources. In this project, the data is being gathered from OpenStreetMap. OpenStreetMap distributes free geographic data of the world. It provides 
the map data in many different formats. This project uses different data wrangling techniques to check the quality of OSM data.

I have downloaded the metro extract of Houston City. I have chosen Houston city for data wrangling beacuse I have been living there for couple of years and
that is the biggest city I have ever lived in. The Houston city openstreet map data is around 700 MB. 

Download link: https://mapzen.com/data/metro-extracts/metro/houston_texas/

							*****************	
							* Project flow: *
							*****************
		Step 1: Download the metro extract from OpenStreetMap
		Step 2: Create a sample file(houston_sample.osm) from downloaded file using Sample_file.ipynb
		Step 3: Audit the sample file using Auditing.py
		Step 4: Clean the sample file and create a sample JSON file using Cleaning.py
		Step 4: Import the JSON file to Mongo DB
		Step 5: Execute Mongo+DB.py to perform the analysis on smaple JSON file
		Step 6: Step 3 to Step 5 is performed on full file using  Houton_OSM_Data_Wrangling.ipynb

Contents in the folder:

Auditing.py
Cleaning.py
houston_sample.osm
houston_sample.osm.json
Houton_OSM_Data_Wrangling.ipynb
Mongo+DB.py
Sample_file.ipynb

Auditing.py and Cleaning.py are the scripts which are created to test the small sample file(houston_sample.osm.json). The small sample file is created
using the script(Sample_file.ipynb) provdied by Udacity. 

Auditing.py audits the houston_sample.osm file and Cleaning.py cleans the selected attributes and cerates a JSON document(houston_sample.osm.json).

Once the JSON document us created, we have to import it to the local Mongo DB instance using the cmd prompt.

Command used: 
mongoimport -d openstreetmap -c houston --file "C:\Users\vemul\Data_Analyst_Nano_Degree\P3-Open_Street_Map_Data_
Wrangling-Python_MongoDB\houston_sample.osm.json"

Once the JSON document id loaded to Mongo Db instance we can run Mongo+DB.py script to perfrom different queries.

**********************
Note to the Reviewer *:  
**********************	 
If the "houston_sample.osm.json" file is imported to your local Mongo DB instace using the above command then you can run Mongo+DB.py 
script dierctly. 


The full file(700 MB metro extarct) is audited,cleaned and imported to Mongo DB in Houton_OSM_Data_Wrangling.ipynb jupyter notebook. The scripts which are
used on sample file are used for the full file. Jupyter notebook has step by step execution of project as suggested in project rubric.

References:

[1] Data Wrangling course- Udacity
[2] https://wiki.openstreetmap.org/wiki/Using_OpenStreetMap
[3] https://wiki.openstreetmap.org/wiki/Map_Features
[4] http://www.houstontx.gov/council/
[5] https://stackoverflow.com/questions/20469712/using-and-with-match-in-mongodb
[6] https://stackoverflow.com/questions/27272699/cant-get-allowdiskusetrue-to-work-with-pymongo
[7] Udacity discussion forum [Main reference]
[8] https://pypi.python.org/pypi/phonenumbers


