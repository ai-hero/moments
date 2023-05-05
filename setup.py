import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="moments",
    version="0.2.3",
    author="Rahul Parundekar",
    author_email="rahul@aihero.studio",
    description="A Large Language Model-based agent framework with Moment Definition Language (MDL)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ai-hero/moments",
    project_urls={
        "Bug Tracker": "https://github.com/ai-hero/moments/issues",
        "Documentation": "https://moments.readthedocs.io",
        "Source Code": "https://github.com/ai-hero/moments",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    packages=setuptools.find_packages(),
    install_requires=[],
    python_requires=">=3.10",
)
