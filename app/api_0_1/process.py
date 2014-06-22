from flask import jsonify
from . import api
import psutil

@api.route('/process/')
def show_process():
	response = []
	try:
		for pid in psutil.pids():
			response.append(_makeProcessResponse(pid))
		return jsonify({
			'_status': 'ok',
			'_count': len(response),
			'_data': response
		}), 200
	except Exception, e:
		return jsonify({
			'_status': 'fail',
			'_reason': 'Cannot retrieve info from processes.',
		}), 404


@api.route('/process/kill/<int:pid>', methods=['GET', 'DELETE'])
def kill_process(pid):
	try:
		p = psutil.Process(pid)
		p.kill()
		return jsonify({
			'_status': 'ok'
		}), 200

	except Exception, e:
		return jsonify({
			'_status': 'fail',
			'_reason': str(e)
		}), 404

def _makeProcessResponse(pid):
	p = psutil.Process(pid)
	return {
		'pid': pid,
		'name': p.name(),
		'user': p.username(),
		'cpu_in_percent': p.cpu_percent(),
		'mem_in_percent': p.memory_percent(),
		'vsz': p.memory_info()[1],
		'rss': p.memory_info()[0],
		'tty': p.terminal(),
		'status': p.status()
	}