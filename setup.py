from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="git-copilot",
    version="1.0.0",
    description="Smart conventional commit message generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="zhirenhun-stack",
    packages=find_packages(),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "git-copilot=git_copilot.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Version Control :: Git",
        "Topic :: Utilities",
    ],
)
