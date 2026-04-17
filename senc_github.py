import os
import shutil
import subprocess

def fix_my_system():
    print("🚀 AarogyamScanAI ko smooth karne ka process shuru ho raha hai...")
    
    # 1. Purani files ka kachra saaf karna
    print("⏳ Purani configuration reset kar rahe hain...")
    try:
        # Git ko force reset karna takki local changes hat jayein
        subprocess.run(["git", "fetch", "--all"], check=True)
        subprocess.run(["git", "reset", "--hard", "origin/main"], check=True)
        subprocess.run(["git", "clean", "-fd"], check=True)
        
        print("✅ GitHub ka fresh code load ho chuka hai.")
    except Exception as e:
        print(f"❌ Git reset fail hua: {e}")
        return

    # 2. Essential Folders check karna
    folders = ['static/uploads', 'reports', 'models']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"📁 Folder banaya gaya: {folder}")

    # 3. Environment verify karna
    print("\n🔍 System check:")
    print(f"📂 Current Directory: {os.getcwd()}")
    
    if os.path.exists('app.py'):
        print("✅ app.py mil gayi hai.")
    else:
        print("❌ app.py nahi mili! Check karein aap sahi folder mein hain.")

    print("\n✨ Ab aapka system GitHub se fully match kar raha hai.")
    print("👉 Ab terminal mein likhein: python app.py")

if __name__ == "__main__":
    fix_my_system()