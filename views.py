import aiohttp
import aiohttp_jinja2
import logging
import uuid

from aiohttp import web
from aiohttp_session import get_session
from faker import Faker

log = logging.getLogger(__name__)

def generate_name():
	fake = Faker()
	return fake.name()


async def display_online_users(cur_ws, request):
	prompt = ''
	if len(request.app['websockets']) == 0:
		prompt = "You're the first person to join this chat!"
	elif len(request.app['websockets']) == 1:
		prompt = ("Currently {0} is online".format(list(request.app['websockets'].keys())[0]))
	elif len(request.app['websockets']) == 2:
		prompt = ("Currently {0} and {1} are online".format( 
			list(request.app['websockets'].keys())[0],
			list(request.app['websockets'].keys())[1]))
	elif len(request.app['websockets']) == 3:
		prompt = ("Currently {0}, {1}, and {2} are online".format( 
			list(request.app['websockets'].keys())[0],
			list(request.app['websockets'].keys())[1],
			list(request.app['websockets'].keys())[2]))
	else:
		prompt = ("Currently {0} and {1} and {2} more people are online".format( 
			list(request.app['websockets'].keys())[0],
			list(request.app['websockets'].keys())[1],
			len(request.app['websockets'].keys()) - 2))
	await cur_ws.send_json({'action': 'display_online', 'text': prompt})


async def index(request):
	session = await get_session(request)
	print(session)
	print(request.cookies)
	cur_ws = web.WebSocketResponse()
	ws_ready = cur_ws.can_prepare(request)
	if not ws_ready.ok:
		if 'AIOHTTP_SESSION' not in request.cookies:
			response =  aiohttp_jinja2.render_template(
				'index.html', 
				request, 
				{})
			cur_user = generate_name()
			session['username'] = cur_user
			if 'websockets' not in session:
				session['websockets'] = {}
			return response
		else:
			return web.Response(status=204)

	await cur_ws.prepare(request)
	cur_user = session['username']
	log.info('%s joined', cur_user)
	await cur_ws.send_json({'action': 'connect', 'name': cur_user})
	await display_online_users(cur_ws, request)
	for ws in request.app['websockets'].values():
		await ws.send_json({'action': 'join', 'name': cur_user})
	session['websockets'][cur_user] = cur_ws
	request.app['websockets'][cur_user] = cur_ws


	# Sending messages
	while True:
		msg = await cur_ws.receive()
		if msg.type == aiohttp.WSMsgType.text:
			for ws in request.app['websockets'].values():
				if ws is not cur_ws:
					await ws.send_json(
						{'action': 'sent', 
						'text': msg.data, 
						'name': cur_user})
		else:
			break
	
	# Disconnecting
	del session['websockets'][cur_user]
	del request.app['websockets'][cur_user]
	log.info('%s disconnected', cur_user)
	for ws in request.app['websockets'].values():
		await ws.send_json({'action': 'disconnect', 'name': cur_user})
	return cur_ws
