import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="moments",
    version="0.2.1",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Large Language Model-based agent framework with Moment Definition Language (MDL)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/moments",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/moments/issues",
        "Documentation": "https://moments.readthedocs.io",
        "Source Code": "https://github.com/yourusername/moments",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    packages=setuptools.find_packages(),
    install_requires=[],
    python_requires=">=3.7",
)
