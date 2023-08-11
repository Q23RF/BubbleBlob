# [BubbleBlob](https://t.co/uJqjtSgcfG)
以Discord機器人(BubbleBlob#2986)實作的仿[泡泡](https://ba-store.dear-u.co/dontalkshop/main/aboutDearU)服務。
## 使用方式
### 藝人端
- 使用!init指令開通藝人帳號
- 私訊機器人使用!bbl指令發布泡泡訊息
- 機器人會用私訊將訂閱者的回覆匿名轉傳給藝人
- ### 訂閱者端
- 在您想用於收取泡泡訊息的頻道使用!subscribe指令訂閱藝人
- 機器人會將藝人發布的泡泡訊息轉傳至該頻道
- 在該頻道使用!reply指令向藝人傳送匿名回覆
## 指令語法
> 中括號都不用打
### !init [artist_name]
開通藝人帳號
### !subscribe [artist_name] [nickname]
在當前頻道訂閱藝人
### !bbl [content]
輸入y/n在訂閱者端會自動替換為該頻道之暱稱
### !reply [artist_name] [content]
向指定藝人傳送匿名回覆
### !get_all_artists
取得目前已註冊的artists名單