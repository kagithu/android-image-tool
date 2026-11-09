# Android Image Tool — 使い方

![アプリアイコン](../assets/logo.png)

## 何ができるソフトか

Windows・Linux・macOSでAndroidのpartition imageを解析・展開・編集する、カスタムROM開発向けツールです。端末への自動flashは行わず、元イメージを直接変更しません。

## 基本的な流れ

1. Stock imageを開いて形式を確認
2. プロジェクト用コピーを作りSHA-256を記録
3. ext4またはboot ramdiskを展開
4. `init`、`fstab`、vendor logoなどを編集
5. 新しい出力イメージを再構築
6. `validate`と差分比較を実行
7. AVB署名と端末互換性を確認してから、信頼できる手順でflash

## 外部ツール

不足ツールがある場合、GUIは取得前に確認します。Google Platform-Toolsは確認後にGoogle公式URLから取得します。`avbtool`、`mkbootimg`、`lpunpack`、`mkfs.erofs`、payload関連ツールは、勝手に実行ファイルを取得せず上流の手順を案内します。

## ローカライズ

`locales/ja.json`または`locales/en.json`を編集して再起動してください。画面文言はJSONファイルから読み込みます。
