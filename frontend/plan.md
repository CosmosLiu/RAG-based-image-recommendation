### Image RAG Demo 前端开发需求说明书

**一、 项目概述**
我们需要为现有的 FastAPI Image RAG 后端开发一个现代化的 Web 前端。该系统主要用于图片的特征向量化入库（拖拽上传）和多模态混合检索（图搜图、文搜图）。

**二、 技术栈要求**

* **构建工具:** Vite
* **前端框架:** React (函数式组件 + Hooks)
* **CSS 框架:** Tailwind CSS (用于快速响应式布局)
* **图标库:** `lucide-react`
* **拖拽组件:** `react-dropzone`
* **请求库:** 原生 `fetch` 或 `axios`

**三、 核心页面与 UI 规划**
采用单页面应用，包含一个顶部导航栏和两个主要的 Tab 页签：

1. **全局导航栏 (Navbar):**
* 左侧：Logo 和系统名称 (Image RAG Engine)。
* 中间：Tab 切换按钮（“图片入库” / “智能检索”）。
* 右侧：全局 UID 模拟输入框（默认值可设为 `user_001`，此 UID 需透传给所有 API）。


2. **图片入库页 (Upload Tab):**
* UI 需求：页面中央实现一个大面积的虚线拖拽区域（使用 `react-dropzone`）。同时支持**点击选择图片**和**拖曳图片到区域**两种方式上传。
* 交互流程：
1. 用户点击选择或拖入本地图片后，UI 显示上传中状态及图片缩略图。
2. 前端将本地 File 对象通过 `FormData` 直接上传到后端 `/api/v1/images/upload` 接口（`uid` + `file` 两个字段）。
3. 后端接收文件后一站式完成：保存图片 → 特征提取 → 向量入库，返回成功结果。
4. 前端收到成功响应后显示完成状态（CheckCircle 图标），并提供”继续上传”按钮。
5. 若上传失败（如重复图片），显示对应的错误提示。




3. **智能检索页 (Discover Tab):**
* UI 需求：顶部为一个宽大的搜索框，支持回车触发搜索。下方为图片结果展示区。
* 结果展示：使用响应式网格布局 (Grid 或 Masonry) 展示返回的图片 URL 列表。鼠标悬浮图片可呈现简单的交互态（如轻微放大、遮罩层等）。
* 数据对接：获取输入框文本，调用 `/api/v1/recommend/text` 接口。



**四、 后端 API 接口契约**
后端运行在 `[http://127.0.0.1:8000](http://127.0.0.1:8000)`。前端需在 `vite.config.js` 中配置 `/api` 代理以解决 CORS 问题。

* **1. 图片文件上传+入库 (POST `/api/v1/images/upload`)**  **[新增接口]**
* **Content-Type:** `multipart/form-data`
* **Fields:** `uid` (string), `file` (binary)
* **Response:** `{ "message": "Success", "image_url": "string" }`
* **说明:** 一步完成文件上传、特征提取和向量入库，替代原有的两步 Mock URL 方案。


* **2. 图片 URL 入库 (POST `/api/v1/images/rag`)**  **[保留，用于 URL 导入]**
* **Payload:** `{ "uid": "string", "image_url": "string" }`
* **Response:** `{ "message": "Success", "image_url": "string" }`


* **3. 文本搜图 (POST `/api/v1/recommend/text`)**
* **Payload:** `{ "uid": "string", "query": "string", "top_k": 6 }`
* **Response:** `{ "results": ["url1", "url2", ...] }`


* *(备用)* **4. 图片搜图 (POST `/api/v1/recommend/image`)**
* **Payload:** `{ "uid": "string", "image_url": "string", "top_k": 6 }`
* **Response:** `{ "results": ["url1", "url2", ...] }`



**五、 给 cc 的执行步骤建议**

1. 初始化 Vite React 项目并安装 Tailwind CSS、`lucide-react`、`react-dropzone`。
2. 配置 `vite.config.js` 的 proxy 代理转发。
3. 编写 `App.jsx` 主体框架，实现状态管理（当前 Tab、全局 UID）。
4. 实现 `UploadSection` 组件，通过 `react-dropzone` 同时支持点击选择和拖曳上传，使用 FormData 将文件直传后端 `/api/v1/images/upload`。
5. 实现 `SearchSection` 组件，完成搜索请求和结果的优雅渲染。
6. 检查所有网络请求的错误处理和 Loading 状态。

---
