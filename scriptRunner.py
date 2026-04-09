import sys
import subprocess, json, tempfile, os
from typing import Any

class SmsSender:
    max_phone_nums : int = 20

    @staticmethod
    def run_cmd(payload :dict, timeout=30) -> None:
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            json.dump(payload, f)
            path = f.name
        try:
            ret = subprocess.run(
                ["shortcuts", "run", "SendBatchSMS", "--input-path", path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=timeout,
            )
        finally:
            os.remove(path)
        try:
            if ret.returncode != 0:
                print(f"Error executing: {json.dumps(payload, indent=2)}", file=sys.stderr)
                print(f"Error(s): {ret.stderr.decode(errors="replace")}", file=sys.stderr)
        except subprocess.TimeoutExpired:
            print(f"Timeout after {timeout}s", file=sys.stderr)

    @staticmethod
    def send_sms(nums :list[str], msg :str) -> None:
        payload = SmsSender.new_payload(msg)
        for i in range(len(nums)):
            payload["numbers"].append(str(nums[i]))
            if (i + 1) % SmsSender.max_phone_nums == 0:
                SmsSender.run_cmd(payload)
                payload["numbers"].clear()
        if len(payload["numbers"]) > 0:
            SmsSender.run_cmd(payload)

    @staticmethod
    def new_payload(msg :str) -> dict[str, Any]:
        return {
            "numbers": [],
            "message": msg.replace('"', '\\"')
        }
