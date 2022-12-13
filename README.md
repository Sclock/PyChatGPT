## 简介

这是一个 GPT 的替代方案，直接调用 GPT3 去进行对话(调教)

## 需要使用的库

- Python3.7+(开发环境为 Python3.10.5)
- openai
- pydantic
  ```bash
  pip install openai
  pip install pydantic
  ```

### 使用方法

- ~~0.给本库点 Star~~
- 1.获取你的 OpenAI 的 Key 并填写到 `main.py` 里的 openai.api_key 后面的双引号里面，形如"sk-MXXXXXX"。
- 2.运行，如果没有开发环境，可以使用 win + r 运行 CMD，然后 CD 到当前目录，输入 python main.py 运行。
- 3.结束运行可以输入 `exit` 或者直接 ctrl + c

### 问题答疑汇总

#### pip 安装过慢

```bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

#### Key 去哪里获得？

https://beta.openai.com/account/api-keys

#### Python 去哪里获得？

https://www.runoob.com/python3/python3-install.html
