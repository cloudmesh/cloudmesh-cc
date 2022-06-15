from fastapi import FastAPI

queue_app = FastAPI()

items = [{"name": "Foo"}, {"name": "Bar"}, {"name": "Baz"}]


@queue_app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return items[skip : skip + limit]

@queue_app.get("/search/")
async def search_item(name:str):
    result = None
    for item in items:
        if item['name'] == name:
            result = name
    return result

