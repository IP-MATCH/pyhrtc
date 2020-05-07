import setuptools

setuptools.setup(
    packages=setuptools.find_packages(include=['pyhrtc']),
    install_requires=["networkx", "pulp", "openpyxl"]
)
