import aiohttp
import asyncio
from lxml import etree
import json
import orm
from models import Video
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import time
import logging
from functools import reduce
from random import choice
import pandas

class Log(object):
	logger = logging.getLogger()
	logger.setLevel(logging.INFO)
	if logger.handlers:
		logger.handlers.pop()
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	sh = logging.StreamHandler()
	sh.setLevel(logging.INFO)
	sh.setFormatter(formatter)
	logger.addHandler(sh)

	def __init__(self):
		pass

	@classmethod
	def log(cls, level, msg):
		cls.logger.log(level, msg)

async def get_test(url):
	global __proxyes
	proxy = choice(__proxyes)
	global __session
	if '__session' not in globals():
		__session = aiohttp.ClientSession(headers={"Connection": "close"})
	try:
		response = await __session.get(url, proxy=proxy)
	except Exception:
		result = await get_test(url)
		return result
	if response.status==200:
		result = await response.text()
	else:
		result = await get_test(url)
	return result

async def get(url):
	try:
		result = await asyncio.wait_for(get_test(url), timeout=5)
		return result
	except asyncio.TimeoutError:
		raise asyncio.TimeoutError('time out 10s')

async def get_video_page_num(mid):
	driver = webdriver.Chrome()
	driver.get(f'https://space.bilibili.com/{mid}/video')
	wait = WebDriverWait(driver,10)
	wait.until(lambda driver: driver.find_element_by_xpath("//span[@class='be-pager-total']"))
	page_num = driver.find_element_by_xpath("//span[@class='be-pager-total']")
	page_num = int(page_num.text[2])
	driver.quit()
	return page_num

async def get_onepage_aid_list(mid, page):
	url = f'https://space.bilibili.com/ajax/member/getSubmitVideos?mid={mid}&pagesize=30&tid=0&page={page}&keyword=&order=pubdate'
	data = await get(url)
	djson = json.loads(data)
	aids = []
	for i in range(30):
		try:
			aid = str(djson['data']['vlist'][i]['aid'])
			aids.append(aid)
		except IndexError as err:
			break
	return aids

async def get_aid_list(mid):
	page_num = await get_video_page_num(mid)
	tasks = map(get_onepage_aid_list,[mid for _ in range(page_num)],range(1,page_num+1))
	tasks = list(tasks)
	result = await asyncio.gather(*tasks)
	aid_list = reduce(list.__add__,result)
	Log.log(logging.INFO, f'get {len(aid_list)} video id from uper {mid}')
	return aid_list

async def get_video_msg(aid):
	try:
		url = 'https://api.bilibili.com/x/web-interface/view?aid=' + aid
		data = await get(url)
		djson = json.loads(data)
		aid = str(djson['data']['stat']['aid'])
		view = str(djson['data']['stat']['view'])
		danmaku = str(djson['data']['stat']['danmaku'])
		reply = str(djson['data']['stat']['reply'])
		favorite = str(djson['data']['stat']['favorite'])
		coin = str(djson['data']['stat']['coin'])
		share = str(djson['data']['stat']['share'])
		like = str(djson['data']['stat']['like'])
		video_num = str(djson['data']['videos'])
		ctime = str(djson['data']['ctime'])
		duration = str(djson['data']['duration'])
		mid = str(djson['data']['owner']['mid'])
		title = djson['data']['title']
		cid_list = []
		for i in range(djson['data']['videos']):
			cid_list.append(str(djson['data']['pages'][i]['cid']))
		cid = ','.join(cid_list)
		video = Video(
				aid = aid,
				mid = mid,
				cid = cid,
				ctime = ctime,
				duration = duration,
				coin = coin,
				danmaku = danmaku,
				favorite = favorite,
				like = like,
				reply = reply,
				share = share,
				view = view,
				video_num = video_num,
				title = title
			)
		await video.save()
		Log.log(logging.INFO, f'save massage of video {aid} successfully')
	except Exception as err:
		Log.log(logging.ERROR, f'from video aid={aid}: ' + str(err))

async def get_danmaku():
	url = 'https://api.bilibili.com/x/v1/dm/list.so?oid=63071683'
	data = await get(url)
	tree = etree.fromstring(data.encode('utf-8'))
	result = tree.xpath('//i/d[1]/@p')[0]
	hashid = result.split(',')[6]
	getuid_url = 'http://biliquery.typcn.com/api/user/hash/'+hashid
	uid = await get(getuid_url)
	print(uid)

def load_proxyes():
	with open('proxy.csv') as file:
		proxyes = ['http://'+line.strip('\n') for line in file]
		Log.log(logging.INFO, f'load {len(proxyes)} proxyes successfully')
	return proxyes

async def test_proxy(proxy):
	global __session
	if '__session' not in globals():
		__session = aiohttp.ClientSession(headers={"Connection": "close"})
	response = await __session.get('https://www.bilibili.com/', proxy=proxy)
	return response.status

async def filter_proxy(proxy):
	try:
		result = await asyncio.wait_for(test_proxy(proxy), timeout=5)
		return True if result==200 else False
	except Exception:
		return False

async def get_all_videos(mid):
	global __pool
	if '__pool' not in globals():
		await orm.create_pool(loop=loop, user='root', password='962452648', database='bilidata')
	global __proxyes
	if '__proxyes' not in globals():
		proxyes = load_proxyes()
		__proxyes = [proxy for proxy in proxyes if await filter_proxy(proxy)]
		Log.log(logging.INFO, f'{len(__proxyes)} proxyes are available')

	aid_list = await get_aid_list(mid)
	tasks = map(get_video_msg, aid_list)
	tasks = list(tasks)
	await asyncio.gather(*tasks)

	global __session
	if '__session' in globals():
		await __session.close()
	if '__pool' in globals():
		await __pool.close()


async def main(loop):
	
	global __pool
	if '__pool' not in globals():
		await orm.create_pool(loop=loop, user='root', password='962452648', database='bilidata')

	df = pandas.read_csv('videos.csv')
	aids = [aid for aid in df['aid']]
	print(aids)
	
	global __session
	if '__session' in globals():
		await __session.close()
	if '__pool' in globals():
		await __pool.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))