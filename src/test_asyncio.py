import asyncio
import time

async def say_after(delay, msg):
	await asyncio.sleep(delay)
	print(msg)

#阻塞
async def tasks():
	task1 = asyncio.create_task(say_after(1, 'hello'))
	task2 = asyncio.create_task(say_after(2, 'world'))
	print(f"started at {time.strftime('%X')}")

	await task1
	await task2

	print(f"finished at {time.strftime('%X')}")

async def factorial(task_name, num):
	f = 1
	for i in range(2, num+1):
		print(f"Task {task_name}: Compute factorial({i})...")
		await asyncio.sleep(1)
		f *= i
	print(f"Task {task_name}: factorial({num})={f}")

	return f"Task {task_name} is done"

#并发
async def main():
	results = await asyncio.gather(
			factorial('A', 2),
			factorial('B', 3),
			factorial('C', 5),
		)
	print(results)

asyncio.run(main())