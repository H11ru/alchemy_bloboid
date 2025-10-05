import sys
message = sys.argv[1]
import os
os.system("git add .")
os.system(f'git commit -m "{message}"')
os.system("git push origin main")