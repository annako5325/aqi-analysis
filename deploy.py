#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub 部署腳本
自動化 Git 初始化和 GitHub 倉庫創建
"""

import os
import subprocess
import sys

def run_command(command, description):
    """執行命令並處理結果"""
    print(f"執行: {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print(f"成功: {description}")
            if result.stdout.strip():
                print(f"   輸出: {result.stdout.strip()}")
            return True
        else:
            print(f"失敗: {description}")
            if result.stderr.strip():
                print(f"   錯誤: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"異常: {description} - {e}")
        return False

def check_git_installed():
    """檢查 Git 是否已安裝"""
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def check_gh_installed():
    """檢查 GitHub CLI 是否已安裝"""
    try:
        result = subprocess.run(['gh', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def main():
    """主程式"""
    print("=" * 60)
    print("GitHub 部署腳本 - AQI Analysis 專案")
    print("=" * 60)
    
    # 檢查必要工具
    print("\n檢查必要工具...")
    
    if not check_git_installed():
        print("錯誤: Git 未安裝，請先安裝 Git")
        print("   下載地址: https://git-scm.com/download/win")
        return False
    
    if not check_gh_installed():
        print("錯誤: GitHub CLI 未安裝，請先安裝 GitHub CLI")
        print("   下載地址: https://cli.github.com/")
        return False
    
    print("成功: Git 和 GitHub CLI 已安裝")
    
    # 檢查登入狀態
    print("\n檢查 GitHub 登入狀態...")
    if not run_command("gh auth status", "檢查 GitHub 登入"):
        print("錯誤: 請先登入 GitHub:")
        print("   執行: gh auth login")
        print("   選擇: GitHub.com")
        print("   選擇: HTTPS")
        print("   選擇: 使用 web browser 登入")
        return False
    
    # Git 初始化
    print("\n初始化 Git 倉庫...")
    git_commands = [
        ("git init", "初始化 Git 倉庫"),
        ("git add .", "添加所有檔案"),
        ("git commit -m 'Initial commit: AQI Analysis Project'", "建立初始提交"),
        ("git branch -M main", "設定主分支為 main")
    ]
    
    for cmd, desc in git_commands:
        if not run_command(cmd, desc):
            print(f"錯誤: Git 操作失敗: {desc}")
            return False
    
    # 創建 GitHub 倉庫
    print("\n創建 GitHub 倉庫...")
    if not run_command("gh repo create aqi-analysis --public --source=. --remote=origin --push", "創建 GitHub 倉庫"):
        print("錯誤: 創建 GitHub 倉庫失敗")
        return False
    
    # 顯示結果
    print("\n" + "=" * 60)
    print("部署完成！")
    print("=" * 60)
    print("GitHub 倉庫: https://github.com/YOUR_USERNAME/aqi-analysis")
    print("專案檔案:")
    print("   - aqi_map.py (主程式)")
    print("   - requirements.txt (依賴套件)")
    print("   - README.md (說明文件)")
    print("   - outputs/ (輸出目錄)")
    print("     - aqi_map.html (互動式地圖)")
    print("     - aqi_analysis.csv (數據分析)")
    print("\n後續操作:")
    print("   1. 訪問 GitHub 倉庫查看程式碼")
    print("   2. 分享倉庫連結給其他人")
    print("   3. 繼續開發新功能")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n部署失敗，請檢查錯誤訊息並重試")
        sys.exit(1)
    else:
        print("\n部署成功！")
