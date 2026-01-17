from apscheduler.schedulers.background import BackgroundScheduler
import yaml
import subprocess
import sys
from pathlib import Path


class TaskScheduler:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.annotes_path = self.base_dir / "annotes.py"
        self.config_path = self.base_dir / "config.yaml"
        self.scheduler = BackgroundScheduler()
        self.config = self.load_config()

    def load_config(self):
        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)

    def get_interval(self):
        # Looks for interval_minutes inside scheduler_settings, defaults to 60
        return self.config.get("scheduler_settings", {}).get("interval_minutes", 60)

    def reload_config(self):
        print("\n🔄 Reloading configuration...")
        self.config = self.load_config()
        if self.scheduler.get_job("annotes_task"):
            self.scheduler.remove_job("annotes_task")
            print("   Removed old schedule")
        new_interval = self.get_interval()
        self.scheduler.add_job(
            self.run_task_now, "interval", minutes=new_interval, id="annotes_task"
        )
        print(f"✓ Configuration reloaded!")
        print(f"✓ New schedule: running every {new_interval} minutes\n")

    def run_task_now(self):
        try:
            print(f"\n▶️  Executing {self.annotes_path.name}...")
            result = subprocess.run(
                [sys.executable, str(self.annotes_path)],
                cwd=str(self.base_dir),
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode == 0:
                print("✓ Execution completed successfully")
                if result.stdout:
                    print(result.stdout)
            else:
                print(f"✗ Execution failed with code {result.returncode}")
                if result.stderr:
                    print(result.stderr)
        except subprocess.TimeoutExpired:
            print("✗ Execution timed out (5 minutes)")
        except Exception as e:
            print(f"✗ Error executing annotes.py: {e}")

    def schedule_task(self):
        interval_minutes = self.get_interval()
        self.scheduler.add_job(
            self.run_task_now, "interval", minutes=interval_minutes, id="annotes_task"
        )
        print(f"📅 Task scheduled: every {interval_minutes} minutes")

    def start(self):
        print("🚀 Running initial task on startup...")
        self.run_task_now()
        self.schedule_task()
        self.scheduler.start()
        print("✓ Scheduler started\n")

    def stop(self):
        self.scheduler.shutdown()
        print("🛑 Scheduler stopped")
