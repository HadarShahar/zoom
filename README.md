# zoom

So far I have made the following features, all of them work between multiple users in multiple meetings:
- Sign in with google / with your name.

- Video streaming (UDP).
- Audio streaming (UDP).
- Screen sharing  (UDP).

- Chat: broadcast messages and direct messages to specific users.
- Painting on a smart board, which also detects lines and rectangles.
- Writing in a "remote" window (currently notepad, reflects the text that each user writes to all the others).

![alt text](screenshots/opening_window.jpg?raw=true)

![alt text](screenshots/join_meeting_frame.jpg?raw=true)

![alt text](screenshots/4users.png?raw=true)

## Setup
Run the file [setup/setup.bat](setup/setup.bat) which installs all the requirements and 
imports the registry constants (the server's ip and ports).

If pyaudio installation fails, check [this link](https://stackoverflow.com/a/55630212).

## Run
Use the batch files in the [run directory](run) or run these commands: 
- Server: python -m server.main_server
- Client: python -m GUI.opening_window