from setuptools import setup, find_packages

setup(
    name="easynmap",
    version="1.0.0",
    description="Beginner-friendly interactive nmap TUI with AI-powered explanations",
    author="easynmap contributors",
    license="MIT",
    packages=find_packages(exclude=["tests*", "config*"]),
    install_requires=[
        "prompt_toolkit>=3.0",
        "rich>=13.0",
        "httpx>=0.27",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "easynmap=easynmap.app:main",
        ],
    },
)
