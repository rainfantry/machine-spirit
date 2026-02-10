@echo off
REM TalkyTalk Windows Launcher
REM Usage: talkytalk "your message here"
REM        talkytalk --test
REM        talkytalk --windows "force offline mode"

python "%~dp0talkytalk.py" %*
