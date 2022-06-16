from cloudmesh.cc.db.shelve.database import Database
from cloudmesh.cc.db.yamldb.database import Database as DatabaseY

s = Database("filename01")
s.__setitem__("key1","data1")
#print(s.__getitem__("key1"))
#print(s.get("key1"))
s.__setitem__("key2",123)

s.save()

print(s.__str__())
print(s.load())

s.clear()
print("after clearing:")
print(s.__str__())

s.remove()

s = DatabaseY("filename02.yaml")
s.__setitem__("key3", 0.001)
s.__setitem__("key4", "helloworld")
s.save()
print(s.__str__())

# There are issues with running this script twice; looks like I have to remove the yamldb file
s.remove()