import aiohttp_jinja2
import jinja2
import logging

from aiohttp import web
from views import index


async def shutdown(app):
	for ws in app['websockets'].values():
		await ws.close()
	app['websockets'].clear()

async def init():
	app = web.Application()
	app['websockets'] = {}
	app.on_shutdown.append(shutdown)
	app.router.add_get('/', index)
	aiohttp_jinja2.setup(
		app, loader=jinja2.PackageLoader('webserver', 'templates'))
	return app

def main():
	logging.basicConfig(level=logging.INFO)
	app = init()
	web.run_app(app)

if __name__ == '__main__':
	main()
