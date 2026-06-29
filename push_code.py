import subprocess
import os

def run_git():
    repo_path = r"E:\Flutter\Carrer_Lens\career_lens_backend"
    try:
        print(f"Current directory: {os.getcwd()}")
        
        # Add all files
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
        print("✅ Git Add completed")
        
        # Commit
        subprocess.run(["git", "commit", "-m", "feat: add admin role support and SaaS features"], cwd=repo_path, check=False)
        print("✅ Git Commit completed")
        
        # Push
        result = subprocess.run(["git", "push", "origin", "main"], cwd=repo_path, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git Push successful! Render is deploying now.")
        else:
            print(f"❌ Git Push failed:\n{result.stderr}")
            
    except Exception as e:
        print(f"Error executing git commands: {e}")

if __name__ == "__main__":
    run_git()
