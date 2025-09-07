import shutil

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def run_health_check():
    """Check for required dependencies and print a report."""
    print("\n--- OOS Health Check ---")
    all_ok = True
    dependencies = {
        "python": "python3",
        "git": "git",
        "op (1Password CLI)": "op"
    }

    for name, cmd in dependencies.items():
        if shutil.which(cmd):
            print(f"{Colors.GREEN}[OK]{Colors.END} {name}")
        else:
            print(f"{Colors.RED}[FAIL]{Colors.END} {name}")
            all_ok = False
    
    print("------------------------")
    if all_ok:
        print(f"{Colors.GREEN}✅ All systems operational.{Colors.END}\n")
        return 0
    else:
        print(f"{Colors.YELLOW}⚠️ Some dependencies are missing. Please run the installer.{Colors.END}\n")
        return 1
