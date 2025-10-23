# UpSiteDown, by Seediffusion!

## Introduction

Welcome to UpSiteDown, the simple, accessible website monitoring solution without limits.

If you're a webmaster, you want to ensure that your website(s) are always running at peak performance. Website outages can be very frustrating and stressful, and for business websites, devastating to both company finances and customer reputation!

Website monitors are a great way to keep track of the status of your website(s) in real time. However, most of them require you to create an account on some online service, they can cost a lot of money if you don't want feature limits, and they can potentially be somewhat confusing or completely inaccessible to blind people; yes, blind people can run websites too!

What if there was a solution that didn't require any personal data, was completely free, could monitor an unlimited number of sites, could give status alerts in either speech or braille, and could be controlled from any program on your computer? Introducing... UpSiteDown!

UpSiteDown is a powerful, customisable, accessible, limitless website monitoring tool for Windows that can provide status alerts for any number of websites. All you need to use UpSiteDown is a Windows PC, a sound card, an optional braille display, and a text file containing a list of the sites you want to monitor.

## System requirements

UpSiteDown requires at least Windows 7 or higher in order to run. Both 32-bit and 64-bit Windows editions are supported. You must have a compatible screen reader and braille display for braille output mode to work. See your screen reader's documentation for compatible braille displays and setup instructions.

## Download and installation

### From source

Here are the instructions for running UpSiteDown from its source code on Windows.

1. The highest recommended Python version is 3.13; you can [download it here](https://github.com/adang1345/PythonVista/raw/refs/heads/master/3.13.9/python-3.13.9-full.exe). This installer is for a modified version of Python 3.13 that keeps Windows 7 support alive.
2. Download and install [Git for Windows](github.com/git-for-windows/git/releases/latest/download/Git-2.51.1-64-bit.exe)
3. Install Python by following the on-screen prompts. Python installation is not covered in this readme, however, please note that having Python added to your environment variables is highly recommended.
4. Press Windows + R, type cmd, and hit Enter to open a command prompt.
5. Clone this repository with git.
```
git clone https://github.com/seediffusion/UpSiteDown.git
```
6. Create a virtual environment. This creates a separate workspace for the project's dependencies, isolated from your main Python install.
```
cd UpSiteDown
python -m venv venv
```
7. Activate the virtual environment.
```
venv\scripts\activate
```
8. To avoid library installation errors, ensure you have the highest versions of pip, setuptools and wheel.
```
python -m pip install --upgrade pip setuptools wheel
```
9. Install the required libraries.
```
pip install -r requirements.txt
```
10. Finally, you should now be able to run the program.
```
python UpSiteDown.py
```

### Compiled

The highest version of UpSiteDown is V 1.8, compiled on Monday, November 4th, 2024.
The below link will allow you to download the latest pre-compiled release.
[UpSiteDownload](https://github.com/seediffusion/UpSiteDown/releases/latest/download/UpSiteDown.zip)

UpSiteDown is a portable program, meaning everything the program needs to run is stored inside a single folder. all you have to do is extract the UpSiteDown.zip file to a location of your choice using a zip archiver like [7-Zip](https://7-zip.org).
To start the program, simply launch the UpSiteDown.exe file. If Windows isn't set up to show file extensions, you won't see the .exe part.

## Usage

When you launch UpSiteDown for the first time, a dialog will appear asking you to enter a website URL. This URL will be stored inside a file called sites.txt, housed in the UpSiteDown program folder. You can add more URLs to this file at any time, either by using the hotkey, Windows+Shift+Control+S by default, or by manually locating and opening the sites.txt file. You don't have to specify the protocol, such as http:// or https://, you can just put in the site's hostname. If no protocol is supplied, the program will assume HTTP and redirect accordingly.

When the program starts, you will hear 'Site monitoring is ready'. It will then sit quietly in the background, monitoring your chosen websites for any status changes. The program won't hog your system tray or task bar; you may even forget that it's running at all! That is, until one or more of your sites dies.

## Changing settings

All your program settings are stored inside a file called opts.ini, which is generated automatically upon first launch. This file can be opened in any text editor, or by using the hotkey, Windows+Shift+Control+O by default.

### Hotkeys

There are 12 hotkeys you can use in UpSiteDown. Of course, with every Seediffusion program that uses hotkeys, you have the power to modify these hotkeys at any time. These hotkeys are global, meaning they can be used from anywhere within the Windows OS.

*   Windows+Shift+Control+W: get all the websites being monitored.
*   Windows+Shift+Control+U: get the sites that are up.
*   Windows+Shift+Control+D: get the sites that are down.
*   Windows+Shift+Control+T: toggle between 4 output modes. SAPI 5 speech, screen reader speech, screen reader speech and braille, and braille only. SAPI 5 speech is the default setting.
*   Windows+Shift+Control+A: toggle on and off the program's site up, site down and error sound events.
*   Windows+Shift+Control+S: open sites.txt in your default text editor.
*   Windows+Shift+Control+O: open opts.ini, the program's configuration file, in your default text editor.
*   Windows+Shift+Control+P: Check for updates.
*   Windows+Shift+Control+V: View outage report file.
*   Windows+Shift+Control+E: delete outage report file.
*   Windows+Shift+Control+Y: restart the program. Useful if your sites or settings files have been modified.
*   Windows+Shift+Control+X. Kill the program completely.

### Program settings

#### outmode

This controls how the program outputs information. Valid values for this setting are:

1.  SAPI 5 speech. The program pipes through SAPI 5, the text to speech synthesizer built into Windows XP and higher, using the currently selected system voice.
2.  Screen reader speech. The program speaks through a screen reader, such as NVDA or JAWS.
3.  Screen reader speech and braille. The program provides both speech and braille output through the screen reader.
4.  Braille only. The program only outputs to a braille display.

The default setting is 1. Note: modes 3 and 4 require a compatible screen reader and braille display for braille output to work. See your screen reader's documentation for compatible braille displays and setup instructions. Don't worry, if you use mode 3 and you don't have a braille display, you will still get speech output through the screen reader.

#### sleep

This is the time to wait between website checks. Set this to 0 for true realtime monitoring. Note, however, that doing this can cause heightened CPU usage. The default setting is 60 seconds.

#### timeout

This controls how long the program waits for a reply from a website before calling it down. The default is 15 seconds.

#### sounds

On by default, this setting controls whether the program plays sounds for site status changes and program errors.

When you're done modifying settings, save the file and close your text editor. If UpSiteDown is running, restart it using the restart hotkey so your new settings are applied properly.

## Outage reports

When a site comes back up, UpSiteDown will generate a report of the outage. These reports are written to a file called outage.txt, housed within the UpSiteDown program folder. You can access this file at any time with the Windows+Shift+Control+V hotkey by default, and delete it with Windows+Shift+Control+E.

Outage reports contain the following information:

*   Date and time: the exact date and time the site went down.
*   Affected site: the site that went down.
*   Reason: why the site was declared down.
*   Outage duration: how long the site was down for.

## Supporting Seediffusion

Although UpSiteDown and all other Seediffusion programs are free of charge, donations and contributions are appreciated, as they help keep Seediffusion alive and support the development of present and future Seediffusion projects. Here are the ways you can give your support:

*   [Ko-Fi](https://ko-fi.com/seediffusion)
*   [Patreon](https://patreon.com/seediffusion)

If you can't give financial support, sharing around also helps. :)

*   [Visit the Seediffusion website](https://seediffusion.cc)
*   [Follow Seediffusion on Mastodon](https://vee.seedy.cc/@seediffusion)
*   [Email Seediffusion](mailto:"seedy@thecubed.cc")