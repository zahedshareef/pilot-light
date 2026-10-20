"""Exercise the actual launch-agent shell without modifying any Mac settings."""
import os
import plistlib
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = plistlib.loads((ROOT / 'nz.sudolabs.pilotlight.watchdog.plist').read_bytes())['ProgramArguments'][2]

class WatchdogTests(unittest.TestCase):
    def simulate(self, *, disabled=True, running=True, stamp=990, restore_ok=True):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            log = root / 'calls'
            commands = {
                '/usr/bin/pmset': '''printf 'SleepDisabled %s\\n' "$DISABLED"''',
                '/usr/bin/pgrep': 'exit "$RUNNING_STATUS"',
                '/usr/bin/stat': 'echo "$STAMP"',
                '/bin/date': 'echo 1000',
                '/usr/bin/id': 'echo 501',
                '/usr/bin/sudo': 'printf "%s\\n" "$*" >> "$CALL_LOG"; exit "$RESTORE_STATUS"',
            }
            # Substitution only changes executable locations; control flow is the bundled script.
            script = SCRIPT
            for index, (original, body) in enumerate(commands.items()):
                fake = root / str(index)
                fake.write_text('#!/bin/sh\n' + body + '\n')
                fake.chmod(0o700)
                script = script.replace(original, str(fake))
            env = dict(os.environ, DISABLED=str(int(disabled)), RUNNING_STATUS='0' if running else '1',
                       STAMP=str(stamp), CALL_LOG=str(log), RESTORE_STATUS='0' if restore_ok else '1')
            subprocess.run(['/bin/sh', '-c', script], env=env, check=False)
            return log.read_text().splitlines() if log.exists() else []

    def test_healthy_app_is_left_alone(self):
        self.assertEqual(self.simulate(), [])

    def test_normal_sleep_is_left_alone(self):
        self.assertEqual(self.simulate(disabled=False, running=False), [])

    def test_crash_explicitly_restores_and_sleeps(self):
        calls = self.simulate(running=False)
        self.assertEqual(len(calls), 2)
        self.assertTrue(calls[0].endswith('-a disablesleep 0'))
        self.assertTrue(calls[1].endswith('sleepnow'))

    def test_hung_app_explicitly_sleeps(self):
        self.assertEqual(len(self.simulate(stamp=979)), 2)

    def test_missing_heartbeat_fails_closed(self):
        self.assertEqual(len(self.simulate(stamp=0)), 2)

    def test_future_heartbeat_fails_closed(self):
        self.assertEqual(len(self.simulate(stamp=1001)), 2)

    def test_failed_restore_does_not_issue_sleep(self):
        self.assertEqual(len(self.simulate(running=False, restore_ok=False)), 1)

if __name__ == '__main__':
    unittest.main()
