import streamlit as st
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI 
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置页面配置
st.set_page_config(
    page_title="小红书爆款文案生成器",
    page_icon="📝",
    layout="wide"
)

# 设置标题
st.title("✨ 小红书爆款文案生成器 ✨")

# 从prompt_template.py导入模板
from prompt_template import system_template_text, user_template_text

# 创建提示模板
prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_template_text),
    ("human", user_template_text),
])

# 创建侧边栏
with st.sidebar:
    st.header("🔑 API设置")
    api_key = st.text_input("请输入阿里云API密钥：", type="password")
    st.markdown("""
    ### 如何获取阿里云API密钥：
    1. 访问[阿里云控制台](https://dashscope.console.aliyun.com/)
    2. 登录或注册阿里云账号
    3. 在左侧菜单找到"API密钥管理"
    4. 创建或查看您的API密钥
    
    ⚠️ 注意：
    - API密钥不会被保存
    - 每次刷新页面都需要重新输入
    - 请妥善保管您的API密钥
    """)
    
    st.divider()  # 添加分隔线
    
    st.header("使用说明 📖")
    st.write("""
    1. 在下方输入框中输入你想要生成文案的主题
    2. 点击'生成文案'按钮
    3. 等待几秒钟，通义千问AI将为你生成5个标题和1段正文
    """)
    
    st.header("示例主题 💡")
    st.write("""
    - 如何提高工作效率
    - 居家收纳技巧分享
    - 超实用的穿搭技巧
    - 记录生活中的小确幸
    """)

# 主要内容区域
theme = st.text_input("请输入文案主题：", placeholder="例如：如何提高工作效率")

def generate_content(theme, api_key):
    # 初始化 ChatDashScope
    chat = ChatOpenAI(
        model="qwen-max",  # 使用通义千问max模型
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        temperature=0.7,
    )
    
    # 生成回复
    messages = prompt_template.format_messages(
        parser_instructions="""请按照以下格式返回JSON：
        {
            "titles": ["标题1", "标题2", "标题3", "标题4", "标题5"],
            "content": "正文内容",
            "tags": ["标签1", "标签2", "标签3"]
        }
        """,
        theme=theme
    )
    
    response = chat.invoke(messages)
    
    try:
        # 解析JSON响应
        content = json.loads(response.content)
        return content
    except:
        return None

if st.button("生成文案", type="primary"):
    if not api_key:
        st.error("请先在侧边栏输入阿里云API密钥")
    elif not theme:
        st.warning("请输入文案主题")
    else:
        with st.spinner("AI正在努力创作中..."):
            try:
                content = generate_content(theme, api_key)
                
                if content:
                    # 显示标题
                    st.header("📌 标题方案")
                    for i, title in enumerate(content["titles"], 1):
                        st.write(f"{i}. {title}")
                    
                    # 显示正文
                    st.header("📝 正文内容")
                    st.write(content["content"])
                    
                    # 显示标签
                    st.header("🏷️ 推荐标签")
                    st.write(" ".join([f"#{tag}" for tag in content["tags"]]))
                    
                    # 添加复制按钮
                    st.text_area("复制区域", 
                                value=f"{content['titles'][0]}\n\n{content['content']}\n\n" + \
                                      " ".join([f"#{tag}" for tag in content["tags"]]),
                                height=300)
                else:
                    st.error("生成失败，请检查API密钥是否正确")
            except Exception as e:
                st.error(f"发生错误：{str(e)}") 