# BubbleBlob
| [點這裡加入官方伺服器](https://t.co/GpORqHYbEo) | [點這裡將機器人加入你的伺服器](https://t.co/uJqjtSgcfG) |

以Discord機器人(BubbleBlob#2986)實作的仿泡泡服務。

## 使用方式
### 訂閱者
- 私訊機器人!get_all_artists
- 新建訂閱專用伺服器
- 為每個想訂閱的藝人創建頻道並在其中使用!subscribe訂閱
- 使用!reply回覆藝人
- (選用) 使用!change_artist_nickname設定藝人暱稱
### 藝人
- 私訊機器人!init
- 使用!bbl發送泡泡訊息
- (選用) 創建頻道訂閱自己以檢查發送情形
- (選用) 使用!change_artist_color自定義對話框顏色

## 指令語法
> 中括號都不用打！

### 開通藝人帳號
> !init [artist_name]

將使用指令的DC帳號註冊為藝人。**一個DC帳號只能開通一個藝人帳號。**

### 刪除藝人帳號
> !close [artist_name]

只有該藝人帳號擁有者可以刪除帳號，所有訂閱者都會收到刪除通知。**此功能不可回逆**，刪除帳號後所有訂閱者資訊都會遺失，但該DC帳號可以重新註冊為藝人。

### 歡迎訊息設置
> !set_welcome [msg] 

藝人用戶可以使用此指令將訂閱歡迎訊息設置為[msg]。

### 藝人名稱更新
> !change_artist_name [new_name]

只有該藝人帳號擁有者可以更新名稱。

### 藝人對話框顏色更新
> !change_artist_color [hex_code]

只有該藝人帳號擁有者可以更新顏色。

### 發送文字泡泡訊息
> !bbl [msg]

藝人用戶可以使用這個指令向所有訂閱者發送文字泡泡訊息[msg]。

### 發送圖片泡泡訊息
> !img

藝人用戶可以使用這個指令並將圖片加入附加檔案，向所有訂閱者發送圖片泡泡訊息。

### 訂閱藝人
> !subscribe [artist_name] [nickname]

使用此指令會在當前頻道訂閱藝人，之後就能在該頻道收取泡泡訊息，其中y/n會被替換為[nickname]。

### 取消訂閱
> !unsubscribe

在當前頻道取消訂閱藝人。

### 訂閱者暱稱更新
> !change_nickname [nickname]

在已訂閱藝人的頻道使用，將該藝人泡泡訊息中對自己的暱稱更新為[nickname]。

### 藝人暱稱更新
> !change_artist_nickname [artist_nickname]

訂閱者用戶可以使用這個指令將藝人在訂閱頻道中顯示的暱稱更新為[artist_nickname]。

### 傳送匿名回覆
> !reply [content]

在已訂閱藝人的頻道使用，向該藝人傳送匿名回覆。

### 取得藝人名單
> !get_all_artists

取得所有目前已註冊的藝人名稱。

### 匿名投稿功能
> !submit [msg] 

私訊使用指令，機器人會在匿名區發布「投稿: [msg]」。
