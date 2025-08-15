# dns_manager_win.py
# -*- coding: utf-8 -*-
"""
DNS manager for Windows with interactive menu:
1) View DNS status
2) Turn ON DNS (set default DNS)
3) Turn OFF DNS (set to DHCP)
4) Change DNS IP (custom)
5) About me  (shows binary image in console)
6) Exit
"""

import subprocess
import sys
import ctypes
import re
import os
from typing import List

# ----------- Defaults -----------
DEFAULT_DNS_PRIMARY = "185.51.200.2"
DEFAULT_DNS_SECONDARY = "178.22.122.100"

# Small binary image to render in console (0/1). '1' = filled pixel; '0' = empty pixel.
BINARY_ART = [
"00000001000000000000000000000000000000000000000000000000000000000000000010000000",
"00000011000000000000000000000000000000000000000000000000000000000000000011000000",
"00000011000000000000000000000000000000000000000000000000000000000000000011000000",
"00000111000000000000000000000000000000000000000000000000000000000000000011100000",
"00001111000000000000000000000000000000000000000000000000000000000000000011110000",
"00001111000000000000000000000000000000000000000000000000000000000000000011110000",
"00011111000000000000000000000000000000000000000000000000000000000000000011111000",
"00011111100000000000000000000000000000000000000000000000000000000000000111111000",
"00011111000000000000000000000000000000000000000000000000000000000000000011111000",
"00001111000000000000000000000000000000000000000000000000000000000000000011110000",
"00001111000000000000000000000000000000000000000000000000000000000000000011110000",
"00001111000000000000000000000000000000000000000000000000000000000000000011110000",
"00001111000000000000000000000000000000000000000000000000000000000000000011110000",
"00001111100000000000000000000000000000000000000000000000000000000000000111110000",
"00001111100000000000000000000000000000000000000000000000000000000000000111110000",
"00001111100000001100000000000000000000000000000000000000000000110000000111110000",
"00001111100000001100000000000000000000000000000000000000000000110000000111110000",
"00001111100000011100000000000000000000000000000000000000000000111000000111110000",
"00000111110000111100000000000000000000000000000000000000000000111100001111100000",
"00000111111000111100000000000000000000000000000000000000000000111100011111100000",
"00000011111110111100000000000000000000000000000000000000000000111101111111000000",
"00000001111111111100000000000000000000000000000000000000000000111111111110000000",
"00000000111111111100000000000001100000000000000110000000000000111111111100000000",
"11000000011111111110000000000001100000000000000110000000000001111111111000000011",
"11100000001111111111000000000011100000000000000111000000000011111111110000000111",
"11100000000111111111000000000111000000000000000011100000000011111111100000000111",
"11110000111111111111111000000111000000000000000011100000011111111111111100001111",
"11111111111111111111111111000111000000000000000011100011111111111111111111111111",
"11111111111111111111111111100111000000000000000011100111111111111111111111111111",
"01111111111111000001111111111111000000000000000011111111111110000011111111111110",
"00011111111000000000000111111111000000000000000011111111100000000000011111111000",
"00001111000000000000000000111111000000000000000011111100000000000000000011110000",
"00000000000000000000000000011111000000000000000011111000000000000000000000000000",
"00000000000000000010000000001111100000011000000111110000000001000000000000000000",
"00000000000000000011110000000111111111111111111111100000001111000000000000000000",
"00000000000000000011111111000011110011100111001111000011111111000000000000000000",
"00000000000000000010110011110111100011000011000111101111001101000000000000000000",
"00000000000000000010011000011110000010000001000001111000011001000000000000000000",
"00000000000000000011001100001100000000000000000000110000110011000000000000000000",
"00000000000000000001000110000100000000000000000000100001100010000000000000000000",
"00000000000000000000100011000000000000000000000000000011000100000000000000000000",
"00000000000000000000110001110000000010000001000000001110001100000000000000000000",
"00000000000000000000010000011001000011000011000010011000001000000000000000000000",
"00000000000000000000000000001001100011000011000110010000000000000000000000000000",
"00000000000000000000000011101001100011000011000110010111000000000000000000000000",
"00000000000000000000000001111111110111000011101111111110000000000000000000000000",
"00000000000000000000000000000110011101000010111001100000000000000000000000000000",
"00000000000000000000000000000101001101100110110010100000000000000000000000000000",
"00000000000000000000000000000000111001111110011100000000000000000000000000000000",
"00000000000000000000000000000000001001100110010000000000000000000000000000000000",
"00000000000000000000000000000000000001000010000000000000000000000000000000000000",
"00000000000000000000000000000000000101000010100000000000000000000000000000000000",
"00000000000000000000000000000010000111000011100001000000000000000000000000000000",
"00000000000000000000000000000011000011000011000011000000000000000000000000000000",
"00000000000000000000000000000011000011000011000011000000000000000000000000000000",
"00000000000000000000000000000011000010000001000011000000000000000000000000000000",
"00000000000000000000000000000010000010000001000001000000000000000000000000000000",
"00000000000000000000000000000010100110000001100101000000000000000000000000000000",
"00000000000000000000000000000110110100011000101101100000000000000000000000000000",
"00000000000000000000000000000100111100111100111100100000000000000000000000000000",
"00000000000000000000000000001101101000111100010110110000000000000000000000000000",
"00000000000000000000000000001001100000011000000110010000000000000000000000000000",
"00000000000000000000000000011011000000000000000011011000000000000000000000000000",
"00000000000000000000000000010010000111100111100001001000000000000000000000000000",
"00000000000000000000000000110110000111000011100001101100000000000000000000000000",
"00000000000000000000000000101100000111000011100000110100000000000000000000000000",
"00000000000000000000000000111000000101100110100000011100000000000000000000000000",
"00000000000000000000000000011000001100000000110000011000000000000000000000000000",
"00000000000000000000000000110000001000000000010000001100000000000000000000000000",
"00000000000000000000000000100000001000000000010000000100000000000000000000000000",
"00000000000000000000000001100000011000000000011000000110000000000000000000000000",
"00000000000000000000000001000000011000000000011000000010000000000000000000000000",
"00000000000000000000000001100000011000000000011000000110000000000000000000000000",
"00000000000000000000000000100000111100000000111100000100000000000000000000000000",
"00000000000000000000000000100000101100000000110100000100000000000000000000000000",
"00000000000000000000000000110001100100000000100110001100000000000000000000000000",
"00000000000000000000000000010001100110000001100110001000000000000000000000000000",
"00000000000000000000000000000001000110000001100010000000000000000000000000000000",
"00000000000000000000000000010011000010000001000011001000000000000000000000000000",
"00000000000000000000000000011010000011000011000001011000000000000000000000000000",
"00000000000000000000000000001010000011000011000001010000000000000000000000000000",
"00000000000000000000000000001110000001000010000001110000000000000000000000000000",
"00000000000000000000000000001100000001100110000000110000000000000000000000000000",
"00000000000000000000000000000100000001100110000000100000000000000000000000000000",
"00000000000000000000000000000110000000100100000001100000000000000000000000000000",
"00000000000000000000000000000011000000111100000011000000000000000000000000000000",
"00000000000000000000000000000000000000111100000000000000000000000000000000000000",
"00000000000000000000000000000000011000011000011000000000000000000000000000000000",
"00000000000000000000000000000000001100011000110000000000000000000000000000000000",
"00000000000000000000000000000000000110011001100000000000000000000000000000000000",
"00000000000000000000000000000000000011000011000000000000000000000000000000000000",
"00000000000000000000000000000000000001100110000000000000000000000000000000000000",
"00000000000000000000000000000000000000011000000000000000000000000000000000000000",
"00000000000000000000000000000000000000000000000000000000000000000000000000000000",
"00000000000000000000000000000000000000000000000000000000000000000000000000000000",
]

# ============ Helpers ============

def clear_screen():
    # Clear the console screen (Windows)
    os.system("cls")

# ============ Admin check ============

def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False

def relaunch_as_admin():
    params = subprocess.list2cmdline(sys.argv)
    rc = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    if rc <= 32:
        print("Could not relaunch as admin. Please run manually as administrator.")
    sys.exit(0)

# ============ System utils ============

def run_cmd(cmd_args):
    completed = subprocess.run(["cmd", "/c"] + cmd_args, capture_output=True, text=True)
    out = (completed.stdout or "").strip()
    err = (completed.stderr or "").strip()
    if completed.returncode != 0:
        msg = err if err else out
        raise RuntimeError(msg)
    return out

# ============ Interfaces ============

def parse_interfaces_from_ipv4_show_interfaces(text: str):
    interfaces = []
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    header_seen = False
    for line in lines:
        if re.search(r"\bIdx\b", line) and re.search(r"\bName\b", line):
            header_seen = True
            continue
        if not header_seen or line.startswith("---"):
            continue
        parts = line.split()
        if len(parts) < 5:
            continue
        idx = parts[0]
        state = parts[3].lower()
        name = " ".join(parts[4:])
        interfaces.append({"idx": idx, "state": state, "name": name})
    return interfaces

def list_interfaces():
    try:
        out = run_cmd(["netsh", "interface", "ipv4", "show", "interfaces"])
        ifaces = parse_interfaces_from_ipv4_show_interfaces(out)
        if ifaces:
            return ifaces
    except Exception:
        pass

    try:
        out = run_cmd(["netsh", "interface", "show", "interface"])
        lines = [l.strip() for l in out.splitlines() if l.strip()]
        ifaces = []
        header_seen = False
        for line in lines:
            if ("Admin State" in line and "Interface Name" in line):
                header_seen = True
                continue
            if not header_seen or line.startswith("---"):
                continue
            parts = line.split()
            if len(parts) < 4:
                continue
            name = " ".join(parts[3:])
            state = parts[1].lower()
            ifaces.append({"idx": None, "state": state, "name": name})
        return ifaces
    except Exception:
        return []

def choose_interface():
    ifaces = list_interfaces()
    if not ifaces:
        print("No network interface found.")
        sys.exit(1)
    print("\n--- Select network interface ---")
    for i, itf in enumerate(ifaces, 1):
        s = itf.get("state", "")
        nm = itf.get("name", "")
        print(f"{i}. {nm} (state: {s})")
    while True:
        idx = input("Enter number: ").strip()
        if idx.isdigit() and 1 <= int(idx) <= len(ifaces):
            return ifaces[int(idx) - 1]["name"]
        print("Invalid choice. Try again.")

# ============ DNS ops ============

def is_valid_ipv4(ip: str) -> bool:
    pattern = r"^(25[0-5]|2[0-4]\d|[01]?\d?\d)\." \
              r"(25[0-5]|2[0-4]\d|[01]?\d?\d)\." \
              r"(25[0-5]|2[0-4]\d|[01]?\d?\d)\." \
              r"(25[0-5]|2[0-4]\d|[01]?\d?\d)$"
    return re.match(pattern, ip) is not None

def set_dns_static(interface_name: str, primary: str, secondary: str | None = None):
    if not is_valid_ipv4(primary):
        raise ValueError(f"Invalid IP: {primary}")
    if secondary and not is_valid_ipv4(secondary):
        raise ValueError(f"Invalid IP: {secondary}")
    run_cmd(["netsh", "interface", "ipv4", "set", "dnsservers",
             f'name={interface_name}', "static", primary, "primary"])
    if secondary:
        run_cmd(["netsh", "interface", "ipv4", "add", "dnsservers",
                 f'name={interface_name}', secondary, "index=2"])

def set_dns_dhcp(interface_name: str):
    run_cmd(["netsh", "interface", "ipv4", "set", "dnsservers",
             f'name={interface_name}', "dhcp"])

def get_dns_status(interface_name: str):
    try:
        out = run_cmd(["netsh", "interface", "ipv4", "show", "dnsservers",
                       f'name={interface_name}'])
    except RuntimeError as e:
        return {"source": "error", "servers": [], "message": str(e)}

    lines = [l.strip() for l in out.splitlines() if l.strip()]
    src = "unknown"
    servers = []
    for ln in lines:
        low = ln.lower()
        if "configured through dhcp" in low:
            src = "dhcp"
        elif "statically configured dns servers" in low or "configured through static" in low:
            src = "static"
        servers.extend(re.findall(r"\b(?:25[0-5]|2[0-4]\d|[01]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[01]?\d?\d)){3}\b", ln))
    # dedup preserve order
    seen, unique_servers = set(), []
    for s in servers:
        if s not in seen:
            seen.add(s); unique_servers.append(s)
    return {"source": src, "servers": unique_servers}

# ============ Status printing ============

def show_dns_status(all_interfaces=False):
    if all_interfaces:
        ifaces = list_interfaces()
        if not ifaces:
            print("No interfaces found.")
            return
        print("\n{:<25} {:<10} {}".format("Interface", "Source", "DNS Servers"))
        print("-" * 60)
        for itf in ifaces:
            iface_name = itf.get("name", "")
            info = get_dns_status(iface_name)
            if info.get("source") == "error":
                print("{:<25} {:<10} {}".format(iface_name, "ERROR", info.get("message")))
            else:
                src = info.get("source").upper()
                servers = ", ".join(info.get("servers", [])) if info.get("servers") else "-"
                print("{:<25} {:<10} {}".format(iface_name, src, servers))
    else:
        iface = choose_interface()
        info = get_dns_status(iface)
        print("\n{:<25} {:<10} {}".format("Interface", "Source", "DNS Servers"))
        print("-" * 60)
        if info.get("source") == "error":
            print("{:<25} {:<10} {}".format(iface, "ERROR", info.get("message")))
        else:
            src = info.get("source").upper()
            servers = ", ".join(info.get("servers", [])) if info.get("servers") else "-"
            print("{:<25} {:<10} {}".format(iface, src, servers))

# ============ About + Binary image ============

def render_binary_image(binary_rows: List[str], on="#", off=" "):
    for row in binary_rows:
        line = "".join(on if ch == "1" else off for ch in row)
        print(line)

def about_me():
    print("\n=== About me ===")
    print("DNS Manager helper script for Windows.")
    print("Features: view status, set static DNS, revert to DHCP, custom DNS, and About page.")
    print("Author: Mehdi :)")
    render_binary_image(BINARY_ART, on="░", off=" ")

# ============ Menu ============

def show_menu():
    print("\n===== DNS Manager (Windows) =====")
    print("1) View DNS status")
    print("2) Turn ON DNS (set default DNS)")
    print("3) Turn OFF DNS (set to DHCP)")
    print("4) Change DNS IP (custom)")
    print("5) About me")
    print("6) Exit")

def menu():
    while True:
        clear_screen()
        show_menu()
        choice = input("Choose: ").strip()

        # Clear screen before showing result of the choice
        clear_screen()

        if choice == "1":
            mode = input("View (A)ll interfaces or (S)ingle interface? [A/S]: ").strip().lower()
            clear_screen()
            show_dns_status(all_interfaces=(mode == "a"))
            input("\nPress Enter to return to menu...")

        elif choice == "2":
            iface = choose_interface()
            clear_screen()
            try:
                set_dns_static(iface, DEFAULT_DNS_PRIMARY, DEFAULT_DNS_SECONDARY)
                print(f"DNS set to {DEFAULT_DNS_PRIMARY} and {DEFAULT_DNS_SECONDARY} for '{iface}'.")
            except Exception as e:
                print(f"Error: {e}")
            input("\nPress Enter to return to menu...")

        elif choice == "3":
            iface = choose_interface()
            clear_screen()
            try:
                set_dns_dhcp(iface)
                print(f"DNS for '{iface}' set to DHCP.")
            except Exception as e:
                print(f"Error: {e}")
            input("\nPress Enter to return to menu...")

        elif choice == "4":
            iface = choose_interface()
            clear_screen()
            primary = input("Primary DNS IP (e.g., 8.8.4.4): ").strip()
            secondary = input("Secondary DNS IP (optional): ").strip()
            clear_screen()
            secondary = secondary if secondary else None
            try:
                set_dns_static(iface, primary, secondary)
                if secondary:
                    print(f"DNS for '{iface}' set to {primary} and {secondary}.")
                else:
                    print(f"DNS for '{iface}' set to {primary}.")
            except Exception as e:
                print(f"Error: {e}")
            input("\nPress Enter to return to menu...")

        elif choice == "5":
            about_me()
            input("\nPress Enter to return to menu...")

        elif choice == "6":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Try again.")
            input("\nPress Enter to return to menu...")

# ============ Entry point ============

if __name__ == "__main__":
    if not is_admin():
        print("Need admin rights. Relaunching with UAC...")
        relaunch_as_admin()
    try:
        menu()
    finally:
        try:
            input("\nPress Enter to close...")
        except EOFError:
            pass
