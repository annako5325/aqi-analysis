#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows 環境 GitHub 部署腳本
專為 Windows PowerShell 設計
"""

import os
import subprocess
import sys
import platform

def run_powershell_command(command, description):
    """執行 PowerShell 命令"""
    print(f"執行: {description}...")
    try:
        # 使用 PowerShell 執行命令
        ps_command = f'powershell -Command "{command}"'
        result = subprocess.run(ps_command, shell=True, capture_output=True, text=True, encoding='utf-8')
        
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

def check_system_info():
    """檢查系統資訊"""
    print("=" * 60)
    print("系統資訊檢查")
    print("=" * 60)
    print(f"作業系統: {platform.system()} {platform.release()}")
    print(f"Python 版本: {sys.version}")
    print(f"當前目錄: {os.getcwd()}")
    print()

def check_git_installation():
    """檢查 Git 安裝狀態"""
    print("檢查 Git 安裝狀態...")
    
    # 檢查 Git 是否在 PATH 中
    git_commands = [
        ("git --version", "檢查 Git 版本"),
        ("where git", "查找 Git 安裝路徑")
    ]
    
    for cmd, desc in git_commands:
        if not run_powershell_command(cmd, desc):
            return False
    
    return True

def check_github_cli():
    """檢查 GitHub CLI 安裝狀態"""
    print("檢查 GitHub CLI 安裝狀態...")
    
    gh_commands = [
        ("gh --version", "檢查 GitHub CLI 版本"),
        ("gh auth status", "檢查 GitHub 登入狀態")
    ]
    
    for cmd, desc in gh_commands:
        if not run_powershell_command(cmd, desc):
            if "auth status" in desc:
                print("錯誤: GitHub CLI 未登入")
                print("   請執行: gh auth login")
                return False
            else:
                print("錯誤: GitHub CLI 未安裝")
                print("   請下載安裝: https://cli.github.com/")
                return False
    
    return True

def initialize_git_repo():
    """初始化 Git 倉庫"""
    print("初始化 Git 倉庫...")
    
    git_commands = [
        ("git init", "初始化 Git 倉庫"),
        ("git add .", "添加所有檔案"),
        ("git commit -m 'Initial commit: AQI Analysis Project with TWD97'", "建立初始提交"),
        ("git branch -M main", "設定主分支為 main")
    ]
    
    for cmd, desc in git_commands:
        if not run_powershell_command(cmd, desc):
            print(f"錯誤: Git 操作失敗: {desc}")
            return False
    
    return True

def create_github_repo():
    """創建 GitHub 倉庫"""
    print("創建 GitHub 倉庫...")
    
    repo_commands = [
        ("gh repo create aqi-analysis --public --source=. --remote=origin --push", "創建並推送 GitHub 倉庫")
    ]
    
    for cmd, desc in repo_commands:
        if not run_powershell_command(cmd, desc):
            print(f"錯誤: GitHub 操作失敗: {desc}")
            return False
    
    return True

def show_project_info():
    """顯示專案資訊"""
    print("\n" + "=" * 60)
    print("AQI Analysis 專案部署完成！")
    print("=" * 60)
    
    print("\n專案檔案:")
    files = [
        "aqi_map.py - 主程式（TWD97 距離計算）",
        "aqi_twd97_results.csv - TWD97 計算結果",
        "outputs/aqi_map.html - 互動式地圖",
        "outputs/aqi_analysis.csv - 數據分析",
        "README.md - 專案說明",
        "MANUAL_DEPLOY.md - 手動部署指南"
    ]
    
    for file_info in files:
        print(f"   - {file_info}")
    
    print("\n專案特色:")
    features = [
        "TWD97 精確距離計算",
        "85 個測站即時數據",
        "互動式地圖視覺化",
        "CSV 數據導出",
        "統計分析功能"
    ]
    
    for feature in features:
        print(f"   - {feature}")
    
    print("\nGitHub 倉庫: https://github.com/YOUR_USERNAME/aqi-analysis")
    print("\n後續操作:")
    print("   1. 訪問 GitHub 倉庫查看程式碼")
    print("   2. 下載 CSV 檔案查看分析結果")
    print("   3. 開啟 HTML 檔案查看互動地圖")
    print("   4. 繼續開發新功能並推送更新")

def main():
    """主程式"""
    print("=" * 60)
    print("Windows GitHub 部署腳本")
    print("AQI Analysis Project with TWD97")
    print("=" * 60)
    
    # 檢查系統資訊
    check_system_info()
    
    # 檢查 Git 安裝
    if not check_git_installation():
        print("\n錯誤: Git 未正確安裝")
        print("請先安裝 Git: https://git-scm.com/download/win")
        return False
    
    # 檢查 GitHub CLI
    if not check_github_cli():
        print("\n錯誤: GitHub CLI 未正確設定")
        print("請先安裝並登入 GitHub CLI")
        return False
    
    # 初始化 Git 倉庫
    if not initialize_git_repo():
        print("\n錯誤: Git 倉庫初始化失敗")
        return False
    
    # 創建 GitHub 倉庫
    if not create_github_repo():
        print("\n錯誤: GitHub 倉庫創建失敗")
        return False
    
    # 顯示專案資訊
    show_project_info()
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n部署失敗，請檢查錯誤訊息並重試")
        print("如需手動部署，請參考 MANUAL_DEPLOY.md")
        sys.exit(1)
    else:
        print("\n部署成功！")
