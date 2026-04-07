import filecmp
import os
from datetime import datetime

# ✅ Correct paths
SHARED = r"C:\Users\vanwykfa\Vodafone Group\Shaheed Johaadien, Vodacom - PythonScripts"
LOCAL  = r"C:\Users\vanwykfa\OneDrive - Vodafone Group\🛜Network_Intelligence_Engine\Neon_PythonScripts\UIPath_reference"

def analyze():
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("   NETWORK INTELLIGENCE ENGINE - DIFF TOOL")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Checked on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    comparison = filecmp.dircmp(SHARED, LOCAL)

    # ✅ 1. Files new in shared folder
    if comparison.left_only:
        print("✅ New files in shared folder:")
        for f in comparison.left_only:
            print("   ➤", f)
    else:
        print("✅ No new files in shared folder.")

    print("")

    # ✅ 2. Files missing on shared side
    if comparison.right_only:
        print("⚠️ Files only in your local DEV folder:")
        for f in comparison.right_only:
            print("   ➤", f)
    else:
        print("✅ No missing files on local side.")

    print("")

    # ✅ 3. Modified files
    if comparison.diff_files:
        print("⚠️ Files modified (differences detected):")
        for f in comparison.diff_files:
            print("   ➤", f)
    else:
        print("✅ No modified files detected.")

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")


if __name__ == "__main__":
    analyze()