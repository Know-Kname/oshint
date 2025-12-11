#!/usr/bin/env python3
"""
Quick API Key Setup Script
Helps users easily configure their API keys for Hughes Clues
"""

import os
import yaml
from pathlib import Path

def setup_api_keys():
    """Interactive API key setup"""

    print("""
╔═══════════════════════════════════════════════════════════╗
║   HUGHES CLUES - API KEY SETUP                           ║
╚═══════════════════════════════════════════════════════════╝

This script will help you configure API keys for Hughes Clues.

API keys enhance functionality but are OPTIONAL. The app works without them,
but some features will be limited.

""")

    config_file = 'config.yaml'

    # Load existing config or create new
    if os.path.exists(config_file):
        with open(config_file) as f:
            config = yaml.safe_load(f)
        print(f"✓ Loaded existing config from: {config_file}\n")
    else:
        print(f"✗ Config file not found. Creating new config...\n")
        config = {
            'mongodb_uri': 'mongodb://localhost:27017',
            'redis_host': 'localhost',
            'redis_port': 6379,
            'max_workers': 4,
            'cache_ttl': 3600,
            'api_keys': {}
        }

    if 'api_keys' not in config:
        config['api_keys'] = {}

    # API key options
    api_services = {
        '1': {
            'name': 'shodan_key',
            'desc': 'Shodan - Internet-connected device search',
            'url': 'https://account.shodan.io/',
            'free': 'Yes (limited)',
            'priority': 'HIGH'
        },
        '2': {
            'name': 'virustotal_key',
            'desc': 'VirusTotal - File/URL malware scanning',
            'url': 'https://www.virustotal.com/gui/my-apikey',
            'free': 'Yes',
            'priority': 'HIGH'
        },
        '3': {
            'name': 'censys_id',
            'desc': 'Censys ID - Internet intelligence platform',
            'url': 'https://censys.io/account/api',
            'free': 'Yes (limited)',
            'priority': 'MEDIUM'
        },
        '4': {
            'name': 'censys_secret',
            'desc': 'Censys Secret - (Pair with Censys ID)',
            'url': 'https://censys.io/account/api',
            'free': 'Yes (limited)',
            'priority': 'MEDIUM'
        },
        '5': {
            'name': 'securitytrails_key',
            'desc': 'SecurityTrails - DNS/Domain intelligence',
            'url': 'https://securitytrails.com/app/account/credentials',
            'free': 'Yes (limited)',
            'priority': 'MEDIUM'
        },
        '6': {
            'name': 'urlscan_key',
            'desc': 'URLScan - Website scanner',
            'url': 'https://urlscan.io/user/profile/',
            'free': 'Yes',
            'priority': 'LOW'
        },
        '7': {
            'name': 'hibp_key',
            'desc': 'HaveIBeenPwned - Data breach database',
            'url': 'https://haveibeenpwned.com/API/Key',
            'free': 'No ($3.50/month)',
            'priority': 'HIGH'
        },
        '8': {
            'name': 'numverify_key',
            'desc': 'NumVerify - Phone number validation',
            'url': 'https://numverify.com/',
            'free': 'Yes (limited)',
            'priority': 'LOW'
        },
        '9': {
            'name': 'truecaller_key',
            'desc': 'TrueCaller - Phone number lookup',
            'url': 'https://www.truecaller.com/',
            'free': 'Requires business account',
            'priority': 'LOW'
        }
    }

    print("Current API Key Status:")
    print("-" * 70)

    for num, service in sorted(api_services.items()):
        key_name = service['name']
        is_set = bool(config['api_keys'].get(key_name))
        status = "✓ Configured" if is_set else "✗ Not set"
        priority = service['priority']

        print(f"[{num}] {service['desc'][:40]:<40} {status:15} {priority}")

    print("-" * 70)
    print("\nOptions:")
    print("[1-9] Configure specific API key")
    print("[A]   Configure all (step-by-step)")
    print("[S]   Skip and save current configuration")
    print("[Q]   Quit without saving")
    print()

    while True:
        choice = input("Select option: ").strip().upper()

        if choice == 'Q':
            print("Exiting without saving...")
            return

        elif choice == 'S':
            break

        elif choice == 'A':
            # Configure all
            for num, service in sorted(api_services.items()):
                key_name = service['name']
                current = config['api_keys'].get(key_name, '')

                print(f"\n{'='*70}")
                print(f"{service['desc']}")
                print(f"Get API key: {service['url']}")
                print(f"Free tier: {service['free']}")
                print(f"Priority: {service['priority']}")

                if current:
                    masked = current[:4] + "*" * (len(current) - 8) + current[-4:] if len(current) > 8 else "***"
                    print(f"Current value: {masked}")

                action = input(f"Enter new API key (or press Enter to skip): ").strip()

                if action:
                    config['api_keys'][key_name] = action
                    print(f"✓ {key_name} updated")

        elif choice in api_services:
            # Configure specific key
            service = api_services[choice]
            key_name = service['name']
            current = config['api_keys'].get(key_name, '')

            print(f"\n{'='*70}")
            print(f"{service['desc']}")
            print(f"Get API key: {service['url']}")
            print(f"Free tier: {service['free']}")

            if current:
                masked = current[:4] + "*" * (len(current) - 8) + current[-4:] if len(current) > 8 else "***"
                print(f"Current value: {masked}")

            action = input(f"Enter new API key (or press Enter to cancel): ").strip()

            if action:
                config['api_keys'][key_name] = action
                print(f"✓ {key_name} updated")

            # Ask if more keys
            more = input("\nConfigure another key? (y/n): ").strip().lower()
            if more != 'y':
                break

        else:
            print("Invalid option. Try again.")

    # Save configuration
    print(f"\nSaving configuration to: {config_file}")

    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    print("✓ Configuration saved successfully!")

    # Summary
    configured = sum(1 for k in config['api_keys'].values() if k)
    total = len(api_services)

    print(f"\n{'='*70}")
    print(f"API Keys Configured: {configured}/{total}")
    print(f"{'='*70}")

    if configured == 0:
        print("\n⚠ No API keys configured. Basic functionality only.")
        print("You can add keys later via: CLI → Settings → API Key Management")
    elif configured < 5:
        print("\n✓ Some API keys configured. Most features available.")
        print("Consider adding more keys for full functionality.")
    else:
        print("\n✓ Good coverage! Most features will work.")
        print("You can always add more keys later.")

    print("\nNext steps:")
    print("1. Run: python3 cli_interface.py")
    print("2. Select your desired intelligence operation")
    print("3. Enjoy comprehensive OSINT gathering!")
    print()


if __name__ == "__main__":
    try:
        setup_api_keys()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("Please report this issue if it persists.")
