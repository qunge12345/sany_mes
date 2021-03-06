

# 光隔离设备通信协议

## 光隔离设备 -> 仙知机器人

```json
{
	"info" : "1:0:0:0",
	"machine_code" : "JC-8000A-89",
	"machine_ip" : "192.168.0.222",
	"machine_status" : "4",
	"event_source" : "1",
	"time" : "20180404095212",
	"version" : "1.0",
    "token":"only for hangxin"
}
```

注：以上字段的值类型均为 string。

| 字段名         | 值含义                                                       |
| :------------- | ------------------------------------------------------------ |
| info           | 事件信息<br/>雄帝满料："X:X"，X是1或0，1表示满料<br/>雄帝缺料："X:X"，X 为 0 ~ 3，表示加料份儿数<br/>航信满料："X:X:X:X"，X是1或0，1表示满料<br/>航信缺料："X"，X是正整数，是需要上料的卡数量 |
| machine_code   | 设备名                                                       |
| machine_ip     | 设备IP                                                       |
| machine_status | 设备状态，当前仙知仅响应"4"和"5"。"0"：暂停，"1"：运行，"**4**"：**缺料**，"**5**"：**满料**，"6"：将满（暂不使用该值），"7"：自动，"8"：手动，"9"：故障 |
| event_source   | 事件源。"0"：雄帝，"1"：航信                                 |
| time           | 报文发出时间                                                 |
| version        | 协议版本                                                     |

**变动内容**：

删除 event_status 字段。

## 仙知机器人 -> 光隔离设备

```json
{
	"id" : "",
	"type" : "1",
	"data" : 
    "{ 
		"event_id" : "iEvent_id",
        "event_info" : "",
		"event_status" : "1",
        "machine_code" : "SHZN001",
        "machine_ip" : "192.168.1.1",
    	"token":"only for hangxin"
     }" 
}
```

注：以上字段的值类型均为 string。

| 字段名 | 值含义                             |
| ------ | ---------------------------------- |
| id     | 保留                               |
| type   | 数据的接收方。"0"：雄帝，"1"：航信 |
| data   | 数据内容，参见下表                 |

data 字段的内容如下所述：

| 字段名       | 值含义                                                       |
| ------------ | ------------------------------------------------------------ |
| event_id     | 本次通信所针对的事件类型。"4"：设备缺料（对应机器人上料），"5"：设备满料（对应机器人下料） |
| event_info   | 本次通信所针对的事件的信息                                   |
| event_status | "0"：仙知已收到该任务，但还未开始处理（暂不启用），"1"：任务成功，"2"：任务失败，"3"：开始处理任务，"4"：开始任务中的抓取操作 |
| machine_code | 设备名                                                       |
| machine_ip   | 设备IP                                                       |

**变动内容**：

变动 event_id 和 event_status 字段的内容。

## 通信逻辑

1. 设备出现 ”缺料“ 或者 ”满料“ 情况时，通过 ”光隔离设备前置程序“ 向仙知发送信息，成功发送一次即可。如果因网络问题而发送失败（没有收到 httpserver 的响应），前置程序需要重发一次。
2. 仙知对某事件（例如 ”满料“）开始进行处理时，将针对该设备回复信息，信息包含 event_id == "5"（制证设备满料，需要下料），且 event_status == "3"（仙知开始处理该任务）。在此之后，该设备不应向仙知发送更新的 ”满料“ 信息，直到仙知发送给该设备的信息，包含 event_status == "1"（任务成功），或者 event_status == "2"（任务失败）。
3. 当 ”上料“ 或者 ”下料“ 的任务进行到机械臂抓取的时刻，仙知将发送 event_status == "4"（开始任务中的抓取操作）。设备可据此决定是否要暂停生产。