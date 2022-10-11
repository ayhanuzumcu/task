import pymongo

myclient = pymongo.MongoClient('mongodb+srv://ayhanuzumcu:MinaDila0106@taskmanager.wttoldp.mongodb.net/?retryWrites=true&w=majority')


mydb = myclient['task_manager']

mycol = mydb["tasks"]

x = mycol.find_one()

print(x)