import schedule
import time
import subprocess
from datetime import datetime

def job():
    print(f"Running the job at {datetime.now()}")

    # Replace 'script1.py' and 'script2.py' with the paths to your Python scripts
    scripts = ['C:\\Users\\DWBRASUELL\\slackbotsdb\\starterbot\\mean_reversion.py', 'C:\\Users\\DWBRASUELL\\slackbotsdb\\starterbot\\mlb_wins.py']

    for script in scripts:
        try:
            subprocess.check_call(['python', script])
            print(f"Successfully executed {script}")
        except subprocess.CalledProcessError as e:
            print(f"Error executing {script}: {e}")

def main():
    # Schedule the job to run every day at 7 AM
    schedule.every().day.at("07:00").do(job)

    # Keep the program running and execute scheduled jobs
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
