# BubbleBlob
> [點這裡將機器人加入伺服器](https://t.co/uJqjtSgcfG)

以Discord機器人(BubbleBlob#2986)實作的仿泡泡服務。
## 使用方式
### 藝人端
- 使用!init指令開通藝人帳號
- 私訊機器人使用!bbl指令發布泡泡訊息
- 機器人會用私訊將訂閱者的回覆匿名轉傳給藝人
### 訂閱者端
- 使用!get_all_artists指令取得藝人名單
- 在您想用於收取泡泡訊息的頻道使用!subscribe指令訂閱藝人
- 機器人會將藝人發布的泡泡訊息轉傳至該頻道
- 在該頻道使用!reply指令向藝人傳送匿名回覆
## 指令語法
> 中括號都不用打
### !init [artist_name]
開通藝人帳號
### !subscribe [artist_name] [nickname]
在當前頻道訂閱藝人
### !subscribe [artist_name] 
在當前頻道取消訂閱藝人
### !change_nickname [artist_name] [nickname]
將暱稱更新為nickname
### !bbl [content]
輸入y/n在訂閱者端會自動替換為該頻道之暱稱
### !reply [artist_name] [content]
向指定藝人傳送匿名回覆
### !get_all_artists
取得目前已註冊的artists名單
## 推薦設定
### 藝人
透過私訊開通泡泡、發布訊息及接收回覆即可。
### 只想訂閱一名藝人的訂閱者
在私訊頻道訂閱泡泡、接收訊息及傳送匿名回覆即可。
### 訂閱多名藝人的用戶
新建一個接收泡泡的專用伺服器，為每個想訂閱的藝人新建文字頻道並在其中使用!subscribe指令，之後就可以在各頻道和不同藝人互動了。