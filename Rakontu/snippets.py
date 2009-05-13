The simplest way to get a list of Author instances from a
db.ListProperty(db.Key) is:
authors = [db.get(key) for key in book.authors] 

# change property of Model
p.properties()[s].get_value_for_datastore(p) 
