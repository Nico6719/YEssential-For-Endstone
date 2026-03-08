cd ~\Desktop\Plugins-Dev\EndStone\Projects\YEssential-For-Endstone\
Remove-Item '.\dist\*' -Recurse
Remove-Item '.\build\*' -Recurse
Remove-Item '.\src\endstone_yessential.egg-info' -Recurse
python .\setup.py sdist build
pipx run build --wheel
cd ~\Desktop\Plugins-Dev\Endstone\
Remove-Item 'C:\Users\HeYuHan\Desktop\Plugins-Dev\Endstone\bedrock_server\plugins\endstone_yessential*.whl'
Copy-Item -Path 'C:\Users\HeYuHan\Desktop\Plugins-Dev\EndStone\Projects\YEssential-For-Endstone\dist\end*.whl' -Destination 'C:\Users\HeYuHan\Desktop\Plugins-Dev\Endstone\bedrock_server\plugins'
# cls
start .\start.cmd