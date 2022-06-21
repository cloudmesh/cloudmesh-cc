import socket

from fastapi import FastAPI
import wmi
app = FastAPI()

@app.get("/temperature")
async def temperature():
    host_name = socket.gethostname()
    w_temp = wmi.WMI(namespace=r'root\wmi', privileges=["Security"])
    temp = ""
    temp = (w_temp.MSAcpi_ThermalZoneTemperature()[0].CurrentTemperature / 10) - 273.2
    temp = f"{str(temp)}C"
    temp_dictionary = '{HostName:',host_name, 'Temperature:',temp,'}'
    print(temp_dictionary)
    return temp_dictionary