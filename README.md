Reverse Shell Generator

This program makes it easy to generate the different types of reverse shells you'll need for Linux and Windows.
Usage
python3 revshell_gen.py

Pick OS → pick shell type → enter IP and port → get your payload.
If it's a bash or PowerShell payload, you'll also be asked whether to encode it (URL encode for bash, Base64 for PowerShell).

Note:Just a payload generator — it only prints known reverse shell one-liners with your IP/port filled in.
Doesn't connect or execute anything. Use only on systems you're authorized to test.