import subprocess
import sys


def get_installed_packages():
    """Returns a set of installed packages with versions."""
    result = subprocess.run([sys.executable, '-m', 'pip', 'freeze'], capture_output=True, text=True)
    return set(result.stdout.splitlines())


def find_new_dependencies(before, after):
    """Finds new dependencies by comparing before and after snapshots."""
    return after - before


def main():
    if len(sys.argv) < 2:
        print("Usage: python track_dependencies.py <package-name>")
        sys.exit(1)

    package = sys.argv[1]
    print(f"Tracking dependencies for: {package}\n")

    print("Taking snapshot before installation...")
    before_install = get_installed_packages()

    print(f"Installing {package}...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)

    print("Taking snapshot after installation...")
    after_install = get_installed_packages()

    new_dependencies = find_new_dependencies(before_install, after_install)

    if not new_dependencies:
        print("No new dependencies were installed.")
        return

    print("New dependencies installed:")
    for dep in sorted(new_dependencies):
        print(dep)


if __name__ == "__main__":
    main()
