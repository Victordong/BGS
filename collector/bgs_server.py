import asyncio
import aiohttp
from datetime import date, time, datetime

loop = asyncio.get_event_loop()
token = ""


host = 'http://localhost:8080'
async def send_data(data):
    global token

    async with aiohttp.ClientSession(headers={"Authorization":token}) as session:
        async with session.post(host+'/datas/auto',json=data) as response:
            if response.status != 200:
                print("Failed")

async def post_auth(info):
    global token
    async with aiohttp.ClientSession() as session:
        async with session.post(host+'/login',json=info) as response:
            json = await response.json()
            token = json.get("token",None)
            if token is not None:
                print("认证成功")
            else:
                print("认证失败")
                exit(0)


class BgsServer(asyncio.Protocol):

    def __init__(self, loop,connections=None):
        if connections is None:
            self.connections = dict()
        self.loop = loop
        self.transport = None

    def connection_made(self, transport):
        self.connections[self] = True
        self.transport = transport

    def connection_lost(self, exc):
        del self.connections[self]

    def data_received(self, data):
        s = str(data, encoding="gb2312")
        print("RECEIVE DATA : {}".format(s))
        # timestamp = datetime.strptime(s[15:19] + s[20:24],
        #                                "%y%m%H%M")
        timestamp = datetime.now()
        d = {'sn': s[4:12],
             'date': str(datetime.now().year)+'-'+(timestamp.date()).strftime("%m-%d"),
             'time': timestamp.time().strftime("%H:%M:%S"),
             'glucose': s[25:29]}
        print("PROCESS DATA :{}".format(data))
        if d['glucose'] == 'LOW ':
            d['glucose'] = 1.0
        if d['glucose'] == 'HIGH':
            d['glucose'] = 34
        d['glucose'] = float(d['glucose'])
        print("SEND DATA : {}".format(d))
        loop.create_task(send_data(data=d))


def server(host, port):

    global loop


    server_coroutine = loop.create_server(lambda: BgsServer(loop=loop),
                                          host=host, port=port)
    print("Server Start at {} ".format(str(host)+":"+str(port)))
    t = loop.create_task(post_auth({"operator_name":"郑湛东", "password":"wshwoaini"}))
    bgs_server = loop.run_until_complete(asyncio.gather(t, server_coroutine))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
        bgs_server.close()
    loop.run_until_complete(bgs_server.wait_closed())
    loop.close()

if __name__ == '__main__':
    server('0.0.0.0', 36751)



"""

'\xcc\xc7"1=ABCD1234=a=0104=0434=03.0mmol/Le\n2'

"""