import json
import sys

import pytest

from ftqec.execution import tasks


@pytest.mark.parametrize('limits,reason', [
    ({'cpu_seconds': None, 'wall_seconds': None}, None),
    ({'cpu_seconds': 0, 'wall_seconds': None}, 'CPU_LIMIT'),
    ({'cpu_seconds': None, 'wall_seconds': 0}, 'ACTION_WALL_LIMIT'),
    ({'cpu_seconds': None, 'wall_seconds': None, 'memory_mb': 0}, 'MEMORY_LIMIT'),
    ({'cpu_seconds': None, 'wall_seconds': None, 'cancel': True}, 'CANCELLED'),
])
def test_guarded_worker_optional_time_limits(tmp_path, monkeypatch, limits, reason):
    limits = dict(limits)
    if limits.pop('cancel', False):
        marker = tmp_path / 'cancel.json'
        marker.write_text('{}')
        limits['cancel_file'] = str(marker)
    script = tmp_path / 'worker.py'
    script.write_text('''import json,os,sys,time
t=json.load(open(sys.argv[1]))
start=time.process_time()
while time.process_time()-start<0.3: pass
json.dump(dict(task='test',result={'status':'DONE'},cpu=0.3,wall=0.3,rss=1,pid=os.getpid()),open(sys.argv[2],'w'))
''')
    monkeypatch.setattr(tasks, 'worker_command', lambda inp, out: [
        getattr(sys, '_base_executable', sys.executable), str(script), str(inp), str(out)])
    task = tasks.Task({}, 'screen', 'code', {}, 'auto', 0, 'source', limits)
    result = tasks.guarded(task)
    if reason:
        assert result['result']['status'] == 'UNKNOWN'
        assert result['result']['reason'] == reason
    else:
        assert result['result']['status'] == 'DONE'
        assert result['supervised_pid'] == result['pid']


@pytest.mark.parametrize('unlimited', [False, True])
def test_cli_time_limit_configuration(tmp_path, monkeypatch, unlimited):
    from ftqec.cli import main
    code = tmp_path / 'code.json'
    code.write_text(json.dumps({'generators': ['ZZ']}))
    captured = []
    def optimize(data, output, config):
        captured.append(config)
        return {'status': 'TEST', 'rows': []}
    monkeypatch.setattr(main, 'optimize', optimize)
    monkeypatch.setattr(sys, 'argv', ['ftqec', 'optimize', str(code)] + (
        ['--no-time-limits'] if unlimited else []))
    main.main()
    assert captured[0].task_cpu_seconds == (None if unlimited else 300)
    assert captured[0].task_wall_seconds == (None if unlimited else 600)
    assert captured[0].memory_mb == 512
