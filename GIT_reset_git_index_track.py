import subprocess


def run_git_command(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output, error = process.communicate()

    if error:
        print(f"Error: {error.decode()}")
    else:
        print(output.decode())


# Untrack all files
# Forcefully untrack all files
run_git_command(["git", "rm", "-r", "-f", "--cached", "."])

# Re-add everything to the repository
run_git_command(["git", "add", "."])

# Commit the changes
run_git_command(["git", "commit", "-m", "Untracked files in .gitignore"])

print("end")
