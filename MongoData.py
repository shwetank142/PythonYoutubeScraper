import pymongo
import time



def insert_front_page(data1):
    client=pymongo.MongoClient("mongodb+srv://shwetank:shwetank123@cluster0.rjsvn.mongodb.net/?retryWrites=true&w=majority")
    database=client['YTScraper']
    collection=database['Frontpage']
    print("\nInserting new 1st page data...")
    time.sleep(2)
    collection.insert_one(data1)
    print("Data inserted")
    client.close()

def drop_front_page():
    try:
        client=pymongo.MongoClient("mongodb+srv://shwetank:shwetank123@cluster0.rjsvn.mongodb.net/?retryWrites=true&w=majority")
        database=client['YTScraper']
        collection=database['Frontpage']
        print("\nDropping Previous 1st page data...")
        time.sleep(4)
        collection.drop()
        print("Old Data Dropped")
    except Exception as e:
        print(e)
    finally:
        client.close()


def fetch_front_page():
    try:
        client = pymongo.MongoClient("mongodb+srv://shwetank:shwetank123@cluster0.rjsvn.mongodb.net/?retryWrites=true&w=majority")

        database = client['YTScraper']
        collection = database["Frontpage"]
        record = collection.find_one()

        table=[keys for keys in record]
        return table
    except Exception as e:
        print(e)
    finally:
        client.close()

# will only use for video_info function in ytScrapper
def fetch_info():
    try:
        client = pymongo.MongoClient("mongodb+srv://shwetank:shwetank123@cluster0.rjsvn.mongodb.net/?retryWrites=true&w=majority")

        database = client['YTScraper']
        collection = database["Frontpage"]
        records = collection.find_one()

        return records
    except Exception as e:
        print(e)
    finally:
        client.close()

def fetch_page2_info():
    try:
        client = pymongo.MongoClient("mongodb+srv://shwetank:shwetank123@cluster0.rjsvn.mongodb.net/?retryWrites=true&w=majority")

        database = client['YTScraper']
        collection = database["secondpage"]
        records = collection.find_one()

        return records
    except Exception as e:
        print(e)
    finally:
        client.close()

def insert_second_page(data2):
    client=pymongo.MongoClient("mongodb+srv://shwetank:shwetank123@cluster0.rjsvn.mongodb.net/?retryWrites=true&w=majority")
    database=client['YTScraper']
    collection=database['secondpage']
    print("\nInserting new 2nd page data...")
    time.sleep(2)
    collection.insert_one(data2)
    print("Data inserted")
    client.close()

def drop_second_page():
    try:
        client=pymongo.MongoClient("mongodb+srv://shwetank:shwetank123@cluster0.rjsvn.mongodb.net/?retryWrites=true&w=majority")
        database=client['YTScraper']
        collection=database['secondpage']
        print("\nDropping previous 2nd page data...")
        time.sleep(4)
        collection.drop()
        print("Old Data Dropped")
    except Exception as e:
        print(e)
    finally:
        client.close()


def fetch_second_page():
    try:
        client = pymongo.MongoClient("mongodb+srv://shwetank:shwetank123@cluster0.rjsvn.mongodb.net/?retryWrites=true&w=majority")

        database = client['YTScraper']
        collection = database["secondpage"]
        record = collection.find_one()
        table2=[keys for keys in record]
        return table2
    except Exception as e:
        print(e)
    finally:
        client.close()

def mongo_dropphotosvideos():
    try:
        client = pymongo.MongoClient("mongodb+srv://shwetank:shwetank123@cluster0.rjsvn.mongodb.net/?retryWrites=true&w=majority")
        database = client['YTScraper']
        collection = database["fs.chunks"]
        collection.drop()
        collection = database['fs.files']
        collection.drop()
        print('Old data deleted')
    except Exception as e:
        print(e)
    finally:
        client.close()

