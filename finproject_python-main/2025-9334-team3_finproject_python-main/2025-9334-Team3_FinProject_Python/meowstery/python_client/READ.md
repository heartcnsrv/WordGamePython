"""
# Meowstery Python Client (Player)

This Python 3.8 application uses omniORB 4.x to connect to the existing Java CORBA Meowstery server.

## Installation & Setup
1. Install Python 3.8 and omniORB:
   ```bash
   sudo apt-get install python3.8 python3-tk omniORB omniORB-python
   ```
2. Install missing Python packages:
   ```bash
   python -m pip install omniORB
   ```
3. Generate Python stubs from IDL:
   ```bash
   omniidl -bpython -I idl idl/GameService.idl
   omniidl -bpython -I idl idl/UserService.idl
   ```
4. Start naming service:
   ```bash
   omniNames &
   ```
5. Run the client:
   ```bash
   python main.py
   ```
