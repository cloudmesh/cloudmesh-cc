
from fastapi import FastAPI
import logging

#app = FastAPI()

#items = [{"name": "Foo"}, {"name": "Bar"}, {"name": "Baz"}]

#@app.get("/")
#async def read_main():
  #  return {"msg": "Hello World"}

#@app.get("/items/")
#async def read_items():
    #return {"msg": "Hello World"}

#@app.get("/search/")
#async def search_item(name:str):
   # result = None
  #  for item in items:
      #  if item['name'] == name:
            #result = name
   # return result


import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}