import aiohttp
import asyncio
import numpy as np
import pandas as pd

async def get_proxy_list(num):
	global __session
	if '__session' not in globals():
		__session = aiohttp.ClientSession()
	response = await __session.get('http://webapi.http.zhimacangku.com/getip?num={num}&type=1&pro=&city=0&yys=0&port=1&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions=')
	text = await response.text()
	proxy_list = text.split('\r\n')
	proxy_list.pop()
	return proxy_list

async def main():
	proxy_list = await get_proxy_list(10)
	data = {'data': proxy_list}
	df = pd.DataFrame(data)
	df.to_csv('proxy.csv', header=0, index=0)
	global __session
	if '__session' in globals():
		await __session.close()

asyncio.run(main())