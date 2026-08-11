cd ~\Desktop\Plugins-Dev\EndStone\Projects\YEssential-For-Endstone\

Write-Host "=== 清理旧产物 ===" -ForegroundColor Cyan
Remove-Item '.\dist\*' -Recurse -ErrorAction SilentlyContinue

Write-Host "=== 构建 wheel ===" -ForegroundColor Cyan
python -m build --wheel

Write-Host "=== 部署到服务器 ===" -ForegroundColor Cyan
Remove-Item 'C:\Users\HeYuHan\Desktop\Plugins-Dev\EndStone\bedrock_server\plugins\endstone_yessential*.whl' -ErrorAction SilentlyContinue
Copy-Item -Path 'C:\Users\HeYuHan\Desktop\Plugins-Dev\EndStone\Projects\YEssential-For-Endstone\dist\end*.whl' -Destination 'C:\Users\HeYuHan\Desktop\Plugins-Dev\EndStone\bedrock_server\plugins'

Write-Host "=== 完成 ===" -ForegroundColor Green
Get-ChildItem 'C:\Users\HeYuHan\Desktop\Plugins-Dev\EndStone\bedrock_server\plugins\endstone_yessential*.whl'
