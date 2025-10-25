from keyboard_handler.wx_handler import WXKeyboardHandler
import aiohttp
import asyncio
import os
import requests
import subprocess
import sys
import threading
import time
import wx
import zipfile
import pyprowl
from datetime import datetime
import accessible_output2.outputs.auto, accessible_output2.outputs.sapi5
from sound_lib import stream
from sound_lib import output as o
from easysettings import EasySettings
import socket # Added for TCP/IP error handling

if os.path.exists("unzip.exe"):
    os.remove("unzip.exe")
# Hide the console window for the tasklist check on Windows
startupinfo = None
if sys.platform == "win32":
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

t = subprocess.check_output(["tasklist"], shell=True, startupinfo=startupinfo).decode()
if t.count("UpSiteDown.exe") > 1:
    subprocess.Popen("prockill.exe")

sndout = o.Output()
upsnd = stream.FileStream(file = "snd/Server_Up.wav")
downsnd = stream.FileStream(file = "snd/Server_Down.wav")
errsnd = stream.FileStream(file = "snd/FError.wav")
app = wx.App(redirect=False)
if not os.path.exists("opts.ini"):
    SetFile = EasySettings("opts.ini")
    SetFile.set("get_sites", "win+shift+control+w")
    SetFile.set("toggle_outmode", "win+shift+control+t")
    SetFile.set("toggle_sounds", "win+shift+control+a")
    SetFile.set("up_sites", "win+shift+control+u")
    SetFile.set("down_sites", "win+shift+control+d")
    SetFile.set("view_sites", "win+shift+control+s")
    SetFile.set("view_opts", "win+shift+control+o")
    SetFile.set("upcheck", "win+shift+control+p")
    SetFile.set("view_outs", "win+shift+control+v")
    SetFile.set("clear_outs", "win+shift+control+e")
    SetFile.set("restart", "win+shift+control+y")
    SetFile.set("exit", "win+shift+control+x")
    SetFile.set("toggle_prowl", "win+shift+alt+l")
    SetFile.set("set_prowl_key", "win+shift+alt+k")
    SetFile.set("toggle_ntfy", "win+shift+alt+n")
    SetFile.set("set_ntfy_topic", "win+shift+alt+m")
    SetFile.set("ntfy_url", "https://ntfy.sh")
    SetFile.set("outmode", "1")
    SetFile.set("sleep", "60")
    SetFile.set("timeout", "15")
    SetFile.set("sounds", "on")
    SetFile.set("prowl", "off")
    SetFile.set("prowl_key", "")
    SetFile.set("ntfy", "off")
    SetFile.set("ntfy_topic", "")
    SetFile.save()
else:
    SetFile = EasySettings("opts.ini")
    if SetFile.get("outmode") not in ["1", "2", "3", "4"]:
        SetFile.setsave("outmode", "1")
    if SetFile.has_option("upconf"):
        SetFile.remove("upconf")
        SetFile.save()
    if not SetFile.has_option("view_outs"):
        SetFile.setsave("view_outs", "win+shift+control+v")
    if not SetFile.has_option("timeout"):
        SetFile.setsave("timeout", "15")
    if not SetFile.has_option("clear_outs"):
        SetFile.setsave("clear_outs", "win+shift+control+e")
    if not SetFile.has_option("toggle_sounds"):
        SetFile.setsave("toggle_sounds", "win+shift+control+a")
    if not SetFile.has_option("sounds"):
        SetFile.setsave("sounds", "on")
    if not SetFile.has_option("toggle_prowl"):
        SetFile.setsave("toggle_prowl", "win+shift+alt+l")
    if not SetFile.has_option("set_prowl_key"):
        SetFile.setsave("set_prowl_key", "win+shift+alt+k")
    if not SetFile.has_option("toggle_ntfy"):
        SetFile.setsave("toggle_ntfy", "win+shift+alt+n")
    if not SetFile.has_option("set_ntfy_topic"):
        SetFile.setsave("set_ntfy_topic", "win+shift+alt+m")
    if not SetFile.has_option("prowl"):
        SetFile.setsave("prowl", "off")
    if not SetFile.has_option("prowl_key"):
        SetFile.setsave("prowl_key", "")
    if not SetFile.has_option("ntfy"):
        SetFile.setsave("ntfy", "off")
    if not SetFile.has_option("ntfy_topic"):
        SetFile.setsave("ntfy_topic", "")
if SetFile.get("outmode") == "1":
    out = accessible_output2.outputs.sapi5.SAPI5()
elif SetFile.get("outmode") == "2" or SetFile.get("outmode") == "3" or SetFile.get("outmode") == "4":
    out = accessible_output2.outputs.auto.Auto()
p = pyprowl.Prowl(SetFile.get("prowl_key"))
def send_ntfy(title, message):
    if SetFile.get("ntfy") == "on":
        topic = SetFile.get("ntfy_topic").strip()
        if topic:
            try:
                url = SetFile.get("ntfy_url").strip().rstrip("/")
                requests.post(f"{url}/{topic}", data=message.encode("utf-8"), headers={"Title": title})
            except Exception:
                pass
if not os.path.exists("sites.txt"):
    setsite = wx.GetTextFromUser("Enter a website URL for your sites.txt file, such as www.mysite.com, and press Enter. You can add more sites to this file at any time by pressing " + SetFile.get("view_sites") + ". Leave blank to exit the program.", "First time setup")
    if setsite == "":
        sys.exit()
    with open("sites.txt", "w") as emp:
        emp.write(setsite)
s = requests.session()
running = True
checked = False
# Globals to hold the loop and shutdown event for cross-thread communication
loop = None
shutdown_event = None

def get_friendly_url(url):
    """Removes protocol for user-friendly display."""
    return url.split('://', 1)[-1] if '://' in url else url

def tout(t):
    if SetFile.get("outmode") == "1" or SetFile.get("outmode") == "2":
        out.speak(t)
    elif SetFile.get("outmode") == "3":
        out.output(t)
    elif SetFile.get("outmode") == "4":
        out.braille(t)
class UpSiteDown(wx.Frame):
    def __init__(self):
        super().__init__(None, title="UpSiteDown", size=(800, 600))
        self.hndlr = WXKeyboardHandler(self)
        self.hndlr.register_key(SetFile.get("toggle_prowl"), self.tglprl)
        self.hndlr.register_key(SetFile.get("set_prowl_key"), self.setprl)
        self.hndlr.register_key(SetFile.get("toggle_ntfy"), self.tglntfy)
        self.hndlr.register_key(SetFile.get("set_ntfy_topic"), self.setntfy)
        self.hndlr.register_key(SetFile.get("get_sites"), self.getsites)
        self.hndlr.register_key(SetFile.get("toggle_outmode"), self.tglbrl)
        self.hndlr.register_key(SetFile.get("toggle_sounds"), self.tglsnd)
        self.hndlr.register_key(SetFile.get("up_sites"), self.upsites)
        self.hndlr.register_key(SetFile.get("down_sites"), self.downsites)
        self.hndlr.register_key(SetFile.get("view_sites"), self.viewsites)
        self.hndlr.register_key(SetFile.get("view_opts"), self.viewopts)
        self.hndlr.register_key(SetFile.get("upcheck"), self.upcheck)
        self.hndlr.register_key(SetFile.get("view_outs"), self.viewouts)
        self.hndlr.register_key(SetFile.get("clear_outs"), self.clearouts)
        self.hndlr.register_key(SetFile.get("restart"), self.restart)
        self.hndlr.register_key(SetFile.get("exit"), self.shutdown)

    def tglbrl(self):
        global out
        if SetFile.get("outmode") == "1":
            SetFile.setsave("outmode", "2")
            out = accessible_output2.outputs.auto.Auto()
            out.speak("Screen reader speech")
        elif SetFile.get("outmode") == "2":
            SetFile.setsave("outmode", "3")
            out.output("Screen reader speech and braille")
        elif SetFile.get("outmode") == "3":
            SetFile.setsave("outmode", "4")
            out.braille("Screen reader braille only")
        elif SetFile.get("outmode") == "4":
            SetFile.setsave("outmode", "1")
            out = accessible_output2.outputs.sapi5.SAPI5()
            out.speak("SAPI 5")
    def tglsnd(self):
        if SetFile.get("sounds") == "on":
            SetFile.setsave("sounds", "off")
            tout("Sounds off.")
        elif SetFile.get("sounds") == "off":
            SetFile.setsave("sounds", "on")
            tout("Sounds on.")
    def getsites(self):
        with open("sites.txt", "r") as sitefile:
            sites = sitefile.readlines()
        if len(	sites) == 1:
            noun = "site"
            be = "is"
        else:
            noun = "sites"
            be = "are"
        tout(f"{len(sites)} {noun} {be} being monitored.")
        [tout(site) for site in sites]

    def upsites(self):
        global ups
        ups = set(ups)
        if len(ups) == 1:
            noun = "site"
            be = "is"
        else:
            noun = "sites"
            be = "are"
        tout(f"{len(ups)} {noun} {be} up.")
        [tout(get_friendly_url(up)) for up in ups]

    def downsites(self):
        if len(downs) == 1:
            noun = "site"
            be = "is"
        else:
            noun = "sites"
            be = "are"
        if len(downs) == 0:
            tout(f"No {noun} {be} down.")
        else:
            tout(f"{len(downs)} {noun} {be} down.")
            [tout(get_friendly_url(down)) for down in downs]

    def shutdown(self):
        global running
        tout("Exiting")
        running = False
        # THIS IS THE FIX: This thread-safe call sets the event, which will
        # immediately interrupt the `await shutdown_event.wait()` in the other thread.
        if loop and shutdown_event:
            loop.call_soon_threadsafe(shutdown_event.set)
        # Give the message time to be spoken before the app closes
        time.sleep(1.5)
        # Use the proper wxPython way to close the application
        self.Close()

    def restart(self):
        try:
            p = os.path.join(os.getcwd(), "UpSiteDown.exe")
            os.execl(p, p, *sys.argv)
        except FileNotFoundError:
            p = sys.executable
            os.execl(p, p, *sys.argv)

    def viewsites(self):
        os.system("sites.txt")

    def viewopts(self):
        os.system("opts.ini")

    def upcheck(self):
        global checked
        global NV
        CV = "2.1"
        tout("Checking for updates...")
        try:
            response = requests.get("https://api.github.com/repos/seediffusion/UpSiteDown/releases/latest")
            if response.status_code != 200:
                if SetFile.get("sounds") == "on":
                    errsnd.play()
                tout(f"Error! The server returned HTTP error {response.status_code}.")
            else:
                NV = response.json().get("tag_name")
                checked = True
                if NV != CV:
                    self.updown()
                else:
                    tout("There are no updates available.")
                    if os.path.exists("UpSiteDown.zip"):
                        os.remove("UpSiteDown.zip")
        except requests.exceptions.ConnectionError:
            if SetFile.get("sounds") == "on":
                errsnd.play()
            tout("Error! The connection to the update server was refused.")
        except requests.exceptions.SSLError:
            if SetFile.get("sounds") == "on":
                errsnd.play()
            tout("Error! Misconfigured or expired SSL certificate detected.")
        except requests.exceptions.Timeout:
            if SetFile.get("sounds") == "on":
                errsnd.play()
            tout("The connection to the update server has timed out.")

    def updown(self):
        global checked
        global running
        global NV
        if checked:
            tout("Connecting to update server...")
            try:
                downlink_r = requests.get("https://github.com/seediffusion/UpSiteDown/releases/latest/download/UpSiteDown.zip")
                if downlink_r.status_code == 200:
                    downlink = "https://github.com/seediffusion/UpSiteDown/releases/latest/download/UpSiteDown.zip"
                    tout(f"Downloading version {NV}.")
                    with open("UpSiteDown.zip", "wb") as downfile:
                        downfile.write(requests.get(downlink).content)
                    tout("Applying update...")
                    with zipfile.ZipFile("UpSiteDown.zip", "r") as zfile:
                        zfile.extractall(".")
                    subprocess.Popen("updater.exe")
                    running = False
                    # Signal shutdown to the asyncio loop as well
                    if loop and shutdown_event:
                        loop.call_soon_threadsafe(shutdown_event.set)
                    self.Close()
                else:
                    if SetFile.get("sounds") == "on":
                        errsnd.play()
                    tout("Error! Update download failed. HTTP error " + str(downlink_r.status_code) + ". press " + SetFile.get("upcheck") + " to try again.")
            except requests.exceptions.ConnectionError:
                if SetFile.get("sounds") == "on":
                    errsnd.play()
                tout("Error! Update download failed. Connection refused! press " + SetFile.get("upcheck") + " to try again.")
            except requests.exceptions.SSLError:
                if SetFile.get("sounds") == "on":
                    errsnd.play()
                tout("Error! Update download failed. Misconfigured or expired SSL certificate. Press " + SetFile.get("upcheck") + " to try again.")
            except requests.exceptions.Timeout:
                if SetFile.get("sounds") == "on":
                    errsnd.play()
                tout("Error! Download failed. Connection timed out! Press " + SetFile.get("upcheck") + " to try again.")
            except requests.exceptions.ChunkedEncodingError:
                if SetFile.get("sounds") == "on":
                    errsnd.play()
                tout("Error! Update download failed. Connection died while downloading. Press " + SetFile.get("upconf") + " to try again.")
    def viewouts(self):
        if os.path.exists("outage.txt"):
            os.system("outage.txt")
        else:
            tout("No outages to view.")

    def clearouts(self):
        if os.path.exists("outage.txt"):
            os.remove("outage.txt")
            tout("Outage report deleted")
        else:
            tout("Can't delete outage report file because it doesn't exist.")
    def tglprl(self):
        if SetFile.get("prowl") == "off":
            tout("Verifying Prowl key...")
            try:
                p.verify_key()
                SetFile.setsave("prowl", "on")
                tout("Prowl on")
            except Exception:
                tout("Prowl was not enabled because your Prowl key could not be verified.")
        elif SetFile.get("prowl") == "on":
            SetFile.setsave("prowl", "off")
            tout("Prowl off")
    def setprl(self):
        global p
        prlkey = wx.GetTextFromUser("Enter your Prowl API key", "Enter Prowl key")
        SetFile.setsave("prowl_key", prlkey)
        p = pyprowl.Prowl(SetFile.get("prowl_key"))
        tout("Prowl key set")
        if SetFile.get("prowl") == "on":
            SetFile.setsave("prowl", "off")
            self.tglprl()
    def tglntfy(self):
        if SetFile.get("ntfy") == "off":
            if SetFile.get("ntfy_topic").strip() == "":
                tout("Set an ntfy topic first.")
                return
            SetFile.setsave("ntfy", "on")
            tout("ntfy on")
        else:
            SetFile.setsave("ntfy", "off")
            tout("ntfy off")
    def setntfy(self):
        topic = wx.GetTextFromUser("Enter ntfy topic", "ntfy Topic")
        SetFile.setsave("ntfy_topic", topic)
        url = wx.GetTextFromUser("Enter ntfy server URL (default: https://ntfy.sh)", "ntfy Server URL")
        if url.strip() == "":
            url = "https://ntfy.sh"
            SetFile.setsave("ntfy_url", url)
            tout("ntfy settings saved.")
def human_readable_downtime(start_time, end_time):
    delta = end_time - start_time
    seconds = delta.total_seconds()
    if seconds < 1:
        return "less than a second"
    
    time_dict = {
        'days': int(seconds // (24*3600)),
        'hours': int((seconds % (24*3600)) // 3600),
        'minutes': int((seconds % 3600) // 60),
        'seconds': int(seconds % 60)
    }
    
    parts = []
    for unit, value in time_dict.items():
        if value > 0:
            parts.append(f"{value} {unit if value > 1 else unit[:-1]}")
            
    return ', '.join(parts)


ups = set()
downs = set()
status_dict = {}

async def check_websites(file_path, shutdown_event):
    with open(file_path, 'r') as file:
        sites = [url.strip() for url in file.readlines() if url.strip()]
    
    global ups, downs, status_dict
    status_dict = {url: {'status': True, 'down_since': None, 'reason': None} for url in sites}
    ups = set(sites)
    downs = set()
    global running

    async def fetch_status(session, url):
        timeout_sec = int(SetFile.get("timeout"))

        # Feature 1: ICMP Ping
        if url.startswith("icmp://"):
            host = url[7:]
            
            subprocess_kwargs = {
                "stdout": asyncio.subprocess.PIPE,
                "stderr": asyncio.subprocess.PIPE
            }
            if sys.platform == 'win32':
                timeout_ms = str(timeout_sec * 1000)
                command = ['ping', '-n', '1', '-w', timeout_ms, host]
                subprocess_kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            else:
                command = ['ping', '-c', '1', '-W', str(timeout_sec), host]
            try:
                proc = await asyncio.create_subprocess_exec(*command, **subprocess_kwargs)
                await proc.communicate()
                return (url, True) if proc.returncode == 0 else (url, False, "Ping failed (Host unreachable or timed out)")
            except FileNotFoundError:
                return url, False, "Ping command not found"
            except Exception as e:
                return url, False, f"Ping error: {e}"

        # Feature 2: TCP Connection
        elif url.startswith("tcp://"):
            target = url[6:]
            try:
                if ':' not in target:
                    raise ValueError
                host, port_str = target.rsplit(':', 1)
                port = int(port_str)
            except ValueError:
                return url, False, "Invalid TCP format. Use tcp://host:port"
            
            try:
                fut = asyncio.open_connection(host, port)
                reader, writer = await asyncio.wait_for(fut, timeout=timeout_sec)
                writer.close()
                await writer.wait_closed()
                return url, True
            except asyncio.TimeoutError:
                return url, False, "TCP connection timed out"
            except (ConnectionRefusedError, OSError) as e:
                return url, False, f"TCP connection failed: {e.__class__.__name__}"
            except Exception as e:
                return url, False, f"TCP error: {e}"

        # Default: HTTP/HTTPS
        else:
            http_url = url
            if not http_url.startswith(('http://', 'https://')):
                http_url = "http://" + http_url
            
            try:
                async with session.get(http_url, timeout=timeout_sec, allow_redirects=True) as response:
                    return (url, True) if response.status < 400 else (url, False, f"HTTP error {response.status}")
            except aiohttp.ClientConnectorError as e:
                return url, False, "Connection refused or DNS lookup failed"
            except aiohttp.ClientSSLError:
                return url, False, "SSL certificate is misconfigured or expired"
            except asyncio.TimeoutError:
                return url, False, "Connection to the site timed out"
            except aiohttp.ClientError as e:
                return url, False, f"Client error: {type(e).__name__}"


    async def check_sites():
        async with aiohttp.ClientSession() as session:
            while running:
                tasks = [fetch_status(session, url) for url in sites]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                up_status_change = False
                down_status_change = False

                for result in results:
                    if isinstance(result, Exception):
                        tout(f"An unexpected error occurred during a check: {result}")
                        continue

                    url, status = result[0], result[1]
                    friendly_url = get_friendly_url(url)

                    if status: # Site is UP
                        if url in downs:
                            up_status_change = True
                            start_time = status_dict[url]['down_since']
                            end_time = datetime.now()
                            downtime = human_readable_downtime(start_time, end_time)
                            
                            tout(f"{friendly_url} is back up after being down for {downtime}.")
                            if SetFile.get("prowl") == "on":
                                try:
                                    p.notify(event = "Site back up", description = f"{friendly_url} is back up after being down for {downtime}.", priority = 0, appName = "UpSiteDown")
                                except Exception:
                                    pass
                            if SetFile.get("ntfy") == "on":
                                try:
                                    send_ntfy("Site back up", f"{friendly_url} is back up after being down for {downtime}.")
                                except Exception:
                                    pass
                            with open("outage.txt", "a") as report:
                                report.write(f"Service Restored: {end_time.strftime('%A, %d %B, %Y at %I:%M %p')}\n")
                                report.write(f"Affected site: {url}\n")
                                report.write(f"Reason for original outage: {status_dict[url].get('reason', 'Unknown')}\n")
                                report.write(f"Outage duration: {downtime}\n\n")

                            ups.add(url)
                            downs.remove(url)
                            status_dict[url] = {'status': True, 'down_since': None, 'reason': None}
                    else: # Site is DOWN
                        e = result[2]
                        if url in ups:
                            down_status_change = True
                            tout(f"{friendly_url} is down! {e}")
                            if SetFile.get("prowl") == "on":
                                try:
                                    p.notify(event = "Site down", description = f"{friendly_url} is down! {e}", priority = 2, appName = "UpSiteDown")
                                except Exception:
                                    pass
                            if SetFile.get("ntfy") == "on":
                                try:
                                    send_ntfy("Site down", f"{friendly_url} is down! {e}")
                                except Exception:
                                    pass
                            downs.add(url)
                            ups.remove(url)
                            
                            down_time = datetime.now()
                            status_dict[url] = {'status': False, 'down_since': down_time, 'reason': e}

                            with open("outage.txt", "a") as report:
                                dtime_str = down_time.strftime("%A, %d %B, %Y at %I:%M %p")
                                report.write(f"Outage Detected: {dtime_str}\n")
                                report.write(f"Affected site: {url}\n")
                                report.write(f"Reason: {e}\n\n")

                if up_status_change and SetFile.get("sounds") == "on":
                    upsnd.play()
                if down_status_change and SetFile.get("sounds") == "on":
                    downsnd.play()
                
                # THIS IS THE FIX: Instead of a blocking sleep, we wait on an event with a timeout.
                try:
                    # This will wait for the sleep duration OR until shutdown_event.set() is called.
                    await asyncio.wait_for(shutdown_event.wait(), timeout=int(SetFile.get("sleep")))
                except asyncio.TimeoutError:
                    # This is the normal path. The timeout was reached, so we continue to the next check cycle.
                    pass

    await check_sites()

def run_asyncio(loop, shutdown_event):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(check_websites('sites.txt', shutdown_event))

if __name__ == '__main__':
    program = UpSiteDown()
    tout("Site monitoring is ready")
    loop = asyncio.new_event_loop()
    shutdown_event = asyncio.Event()
    
    t = threading.Thread(target=run_asyncio, args=(loop, shutdown_event))
    t.start()
    app.MainLoop()
    
    # After the app closes, ensure the background thread is also finished.
    running = False
    if not shutdown_event.is_set():
        loop.call_soon_threadsafe(shutdown_event.set)
    t.join()