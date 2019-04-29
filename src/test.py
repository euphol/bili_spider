import aiohttp
import asyncio
from lxml import etree

async def get(url):
	session = aiohttp.ClientSession()
	response = await session.get(url)
	result = await response.text()
	await session.close()
	return result

async def main():
	url = 'https://api.bilibili.com/x/v1/dm/list.so?oid=63071683'
	data = await get(url)
	tree = etree.fromstring(data.encode('utf-8'))
	result = tree.xpath('//i/d[1]/@p')[0]
	hashid = result.split(',')[6]
	getuid_url = 'http://biliquery.typcn.com/api/user/hash/'+hashid
	uid = await get(getuid_url)
	print(uid)
	
asyncio.run(main())