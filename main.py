""" Main file of the webchat server. """
import logging

import aiohttp_jinja2
import aiohttp_session
import aioredis
import jinja2

from aiohttp import web
from aiohttp_session import redis_storage
from views import index

async def shutdown(app):
    for ws in app['websockets'].values():
        await ws.close()
    app['websockets'].clear()

async def init():
    app = web.Application()
    app.router.add_get('/', index)
    app['websockets'] = {}
    app.on_shutdown.append(shutdown)
    aiohttp_jinja2.setup(
    app, loader=jinja2.PackageLoader('webserver', 'templates'))
    redis = await aioredis.create_pool(('localhost', 6379))
    storage = redis_storage.RedisStorage(redis)
    aiohttp_session.setup(app, storage)
    return app

def main():
    logging.basicConfig(level=logging.INFO)
    app = init()
    web.run_app(app)

if __name__ == '__main__':
    main()
