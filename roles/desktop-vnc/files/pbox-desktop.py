#!/usr/bin/python3
"""Recipe launcher protocol: ensure a persistent session; return its VNC port as JSON."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import pwd
import re
import signal
import socket
import subprocess
import sys
import time


def probe(port):
    try:
        with socket.create_connection(('127.0.0.1', port), timeout=1) as sock:
            return sock.recv(12).startswith(b'RFB ')
    except OSError:
        return False


def supervise(state, session, config, display):
    env = dict(os.environ, DISPLAY=f':{display}', XDG_RUNTIME_DIR=str(state / 'runtime'),
               XDG_SESSION_TYPE='x11')
    env.pop('WAYLAND_DISPLAY', None)
    env.pop('DBUS_SESSION_BUS_ADDRESS', None)
    env.pop('SESSION_MANAGER', None)
    (state / 'runtime').mkdir(mode=0o700, exist_ok=True)
    x = desktop = None
    def stop(*_):
        raise SystemExit(0)
    signal.signal(signal.SIGTERM, stop)
    try:
        x = subprocess.Popen(['Xtigervnc', f':{display}', '-localhost', '-interface', '127.0.0.1',
                              '-SecurityTypes', 'None', '-geometry', '1600x900', '-depth', '24',
                              '-nolisten', 'tcp', '-AlwaysShared', '-desktop', session])
        for _ in range(100):
            if x.poll() is not None:
                raise RuntimeError('VNC server exited; inspect desktop.log')
            if subprocess.run(['xdpyinfo'], env=env, stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL).returncode == 0:
                break
            time.sleep(.1)
        else:
            raise RuntimeError('X display did not become ready')
        desktop = subprocess.Popen(['dbus-run-session', '--'] + config['argv'], env=env,
                                   start_new_session=True)
        time.sleep(3)
        if desktop.poll() is not None:
            raise RuntimeError('Desktop exited during startup; inspect desktop.log')
        (state / 'ready').write_text(str(os.getpid()))
        while x.poll() is None and desktop.poll() is None:
            time.sleep(.5)
    finally:
        (state / 'ready').unlink(missing_ok=True)
        if desktop is not None:
            try:
                os.killpg(desktop.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        if x is not None and x.poll() is None:
            x.terminate()
            x.wait(timeout=5)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--session')
    parser.add_argument('--supervise', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    sessions = sorted(p.stem for p in Path('/etc/pbox/desktops').glob('*.json'))
    session = args.session or (sessions[0] if len(sessions) == 1 else None)
    if session not in sessions or not re.fullmatch(r'[a-z0-9-]+', session or ''):
        raise RuntimeError('Choose --session from: ' + ', '.join(sessions))
    account = pwd.getpwnam('pbox')
    if os.getuid() == 0:
        os.initgroups(account.pw_name, account.pw_gid)
        os.setgid(account.pw_gid)
        os.setuid(account.pw_uid)
    if os.getuid() != account.pw_uid:
        raise RuntimeError('Desktop must run as the pbox development account')
    os.environ.update(HOME=account.pw_dir, USER='pbox', LOGNAME='pbox')
    os.chdir(account.pw_dir)
    state = Path(account.pw_dir) / '.local/state/pbox-desktop' / session
    state.mkdir(parents=True, mode=0o700, exist_ok=True)
    # Stable per-session display assignment persists when further recipes are installed.
    allocation = state.parent / 'displays.json'
    with (state.parent / 'allocation.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        displays = json.loads(allocation.read_text()) if allocation.exists() else {}
        if session not in displays:
            displays[session] = next(n for n in range(10, 100) if n not in displays.values())
            allocation.write_text(json.dumps(displays))
        display = displays[session]
    port = 5900 + display
    config = json.loads((Path('/etc/pbox/desktops') / (session + '.json')).read_text())
    if args.supervise:
        with (state / 'supervisor.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            supervise(state, session, config, display)
        return
    with (state / 'start.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        alive = False
        if (state / 'ready').exists():
            try:
                pid = int((state / 'ready').read_text())
                alive = b'--supervise' in Path(f'/proc/{pid}/cmdline').read_bytes() and probe(port)
            except (OSError, ValueError):
                pass
        if not alive:
            (state / 'ready').unlink(missing_ok=True)
            with (state / 'desktop.log').open('ab') as log:
                child = subprocess.Popen([sys.executable, __file__, '--session', session, '--supervise'],
                                         stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                                         start_new_session=True)
            for _ in range(150):
                if child.poll() is not None:
                    raise RuntimeError(f'Desktop startup failed; inspect {state}/desktop.log')
                if (state / 'ready').exists() and probe(port):
                    break
                time.sleep(.1)
            else:
                child.terminate()
                raise RuntimeError(f'Desktop startup timed out; inspect {state}/desktop.log')
    print(json.dumps({'session': session, 'port': port}))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
