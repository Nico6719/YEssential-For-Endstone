import setuptools
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 从 constant.py 读取版本号
version = "0.1.0"
constant_path = os.path.join(os.path.dirname(__file__), "src", "endstone_yessential", "constant.py")
if os.path.exists(constant_path):
    with open(constant_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("plugin_version"):
                version = line.split("=")[1].strip().strip('"').strip("'")
                break

setuptools.setup(
    name="endstone-yessential",
    version=version,
    author=["Nico6719", "MengHanLOVE1027"],
    url="https://github.com/Nico6719/YEssential-For-Endstone",
    author_email=["nico6719@qq.com", "2193438288@qq.com"],
    description="基于 Endstone 的 YEssential",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
)
