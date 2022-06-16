from cloudmesh.cc.db.shelve.database import Database
import shelve


filename = "filename01"
key = "key1"
value = "data1"

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