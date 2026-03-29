import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="endstone-yessential",
    version="0.1.0",
    author=["Nico6719", "MengHanLOVE1027"],
    url='https://github.com/MengHanLOVE1027',
    author_email=["nico6719@qq.com", "2193438288@qq.com"],
    description="基于 Endstone 的 YEssential",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
)
