# def test_run():
#     """
#     creates a test queue with several different jobs
#     :return: Queues object
#     :rtype: Queues
#     """
#     kind = 'yamldb'
#     q = Queues(filename='~/.cloudmesh/queue/queuetest1')
#     q.create(name='local')
#     q.create(name='rivanna')
#     q.add(name='local', job='job01', command='pwd')
#     q.add(name='local', job='job02', command='ls')
#     q.add(name='local', job='job03', command='hostname')
#     q.add(name='rivanna', job='job04', command='pwd')
#     q.add(name='rivanna', job='job05', command='ls - a')
#     q.add(name='rivanna', job='job06', command='hostname')
#     q.add(name='rivanna', job='job07', command='git status')
#     return q

# # deprecated only here as example/test once working example is implemented, remove
# @app.get("/item/{id}", response_class=HTMLResponse)
# async def read_item(request: Request, id: str):
#     global q
#     jobs = []
#     for queue in q.queues:
#         for job in q.queues[queue]:
#             jobs.append(q.queues[queue][job])
#     order = q.queues[queue][job].keys()
#     order = [word.capitalize() for word in order]
#     Console.error(str(order))
#
#     return templates.TemplateResponse("templates/item.html",
#                                       {"request": request,
#                                        "id": id,
#                                        "jobs": jobs,
#                                        "order": order})
#
# # deprecated only here as example/test once working example is implemented, remove
# @app.get("/items", response_class=HTMLResponse)
# async def item_table(request: Request):
#     return templates.TemplateResponse("templates/table.html",
#                                       {"request": request})
#
# QUEUES
#
# @app.get("/queues/", response_class=HTMLResponse)
# async def list_queues(request: Request):
#     global q
#     return templates.TemplateResponse('templates/queues.html',
#                                       {"request": request,
#                                        "queues": q.queues})
#
#
# #TODO: fix
# @app.post("/queue")
# async def add_queue(name: str):
#     global q
#     q.create(name=name)
#     return {
#         "queues": q.queues
#     }
#
# # TODO this may not be right
# @app.delete("/queue/{name}")
# async def delete_queue(name: str):
#     global q
#     q.remove(name)
#     return {
#         "queues": q.queues
#     }
#
#
# #
# # JOBS
# #
#
# #TODO: fix
# @app.post("/job")
# async def add_job(name: str, job: str, command: str):
#     global q
#     q.add(name=name, job=job, command=command)
#     return {
#         "jobs": q.queues[name]
#     }
#
# # TODO this may not be right
# @app.delete("/job/{queue}/{name}")
# async def delete_job(name: str, queue:str):
#     global q
#     q.remove(name)
#     return {
#         "jobs": q.queues[name]
#     }
#
# @app.get("/jobs/{queue}", response_class=HTMLResponse)
# async def list_jobs(request: Request, queue: str):
#     global q
#     jobs = []
#     for q in q.queues:
#         if q == queue:
#             for job in q.queues[queue]:
#                 jobs.append(q.queues[queue][job])
#     order = q.queues[queue][job][0:1]
#     order = [word.capitalize() for word in order]
#     Console.error(str(order))
#
#     return templates.TemplateResponse("templates/item.html",
#                                       {"request": request,
#                                        "no": no,
#                                        "jobs": jobs,
#                                        "order": order})
#
#
# @app.get("/job/{queue}/{job}", response_class=HTMLResponse)
# async def read_job(queue: str, job: str):
#     global q
#     result = Printer.attribute(q.queues[queue][job], output='html')
#     name = q.queues[queue][job]["name"]
#     d = f"<h1>{name}</h1>"
#     d += "<table>"
#     d += f"<tr> <th> attribute </th><th> value </th> </tr>"
#
#     for attribute in q.queues[queue][job]:
#         value = q.queues[queue][job][attribute]
#         d += f"<tr> <td> {attribute} </td><td> {value} </td> </tr>"
#     d += "</table>"
#     result = d
#     print(Printer.attribute(q.queues[queue][job]))
#     print(result)
#
#     page = f"""
#     <html>
#         <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.21/css/jquery.dataTables.css">
#         <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.10.21/js/jquery.dataTables.js"></script>
#         <head>
#             <title>Some HTML in here</title>
#         </head>
#         <body>
#             {result}
#         </body>
#     </html>
#     """
#     return page
