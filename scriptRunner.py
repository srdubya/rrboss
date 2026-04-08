import subprocess
import sys

class SmsSender:
    max_phone_nums : int = 10
    script_template ='''
tell application "Messages"
	activate
	try
		set svc to first account whose service type = iMessage
	on error
		set svc to first account whose service type = SMS
	end try
	set recipient to participant "%s" of svc
	send "%s" to recipient
end tell
'''

    @staticmethod
    def run_cmd(cmd, timeout=30):
        # cmd can be a list (preferred) or string (if shell=True)
        try:
            completed = subprocess.run(
                ['osascript', '-e', cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,       # don't raise automatically; handle returncode
                timeout=timeout,
            )
            if completed.returncode != 0:
                print(f"Error executing: {cmd}", file=sys.stderr)
                print(f"Error(s): {completed.stderr.decode(errors="replace")}", file=sys.stderr)
        except subprocess.TimeoutExpired:
            print(f"timeout after {timeout}s", file=sys.stderr)

    @staticmethod
    def send_sms(num :str, message :str) -> None:
        text_escaped = message.replace('"', '\\"')
        cmd = SmsSender.script_template % (num, text_escaped)
        SmsSender.run_cmd(cmd.strip())
