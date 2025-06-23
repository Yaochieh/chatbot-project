# chatbot_backend.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import openai
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import os
from datetime import datetime

app = FastAPI(title="Interface Helper Chatbot API")

# 設定OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

class ChatMessage(BaseModel):
    content: str
    role: str  # 'user' or 'assistant'
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    message: str
    user_id: str
    session_id: str

class ChatResponse(BaseModel):
    response: str
    intent: Optional[str] = None
    confidence: Optional[float] = None

class InterfaceKnowledgeBase:
    """界面操作知識庫"""
    
    def __init__(self):
        self.knowledge = {
            "data_upload": {
                "keywords": ["upload", "import", "data", "file", "csv", "excel", "上傳", "導入", "檔案"],
                "content": """
                數據上傳步驟：
                1. 點擊導航欄中的「數據管理」→「導入數據」
                2. 選擇文件格式（支援CSV、Excel、JSON、Parquet）
                3. 可以拖拽文件或點擊「選擇文件」按鈕
                4. 在預覽界面確認數據格式正確
                5. 設定欄位映射和數據類型
                6. 點擊「確認導入」完成上傳
                
                注意事項：
                - 文件大小限制：最大500MB
                - 支援的編碼：UTF-8, GBK
                - Excel文件請確保工作表名稱為英文
                """,
                "related_actions": ["data_preview", "data_validation"]
            },
            "chart_creation": {
                "keywords": ["chart", "graph", "visualization", "plot", "圖表", "視覺化", "繪圖", "分析"],
                "content": """
                創建圖表的完整流程：
                1. 在左側面板選擇已導入的數據集
                2. 點擊「創建圖表」按鈕
                3. 選擇圖表類型：
                   - 折線圖：適用於時間序列分析
                   - 柱狀圖：適用於類別比較
                   - 散點圖：適用於相關性分析
                   - 熱力圖：適用於矩陣數據
                4. 設定座標軸：
                   - 拖拽欄位到X軸區域
                   - 拖拽欄位到Y軸區域
                   - 可設定分組和顏色映射
                5. 調整樣式和標題
                6. 點擊「生成圖表」
                
                進階功能：
                - 可添加趨勢線和迴歸分析
                - 支援多軸顯示
                - 可導出為PNG、PDF或SVG格式
                """,
                "related_actions": ["data_filtering", "export_chart"]
            },
            "data_filtering": {
                "keywords": ["filter", "search", "query", "condition", "where", "篩選", "搜尋", "查詢", "條件"],
                "content": """
                數據篩選和查詢功能：
                1. 簡單篩選：
                   - 點擊欄位標題的篩選圖標
                   - 選擇篩選條件（等於、不等於、大於、小於、包含、不包含）
                   - 輸入篩選值
                   - 點擊「套用」
                
                2. 進階查詢：
                   - 使用「進階篩選器」功能
                   - 支援SQL-like語法
                   - 可組合多個條件（AND、OR邏輯）
                   - 支援正則表達式匹配
                
                3. 快速搜尋：
                   - 使用全文搜索功能
                   - 支援模糊匹配
                   - 可搜尋特定欄位或全表
                
                篩選結果會即時顯示，並可保存為篩選器模板供重複使用。
                """,
                "related_actions": ["data_export", "chart_creation"]
            },
            "export_functions": {
                "keywords": ["export", "download", "save", "output", "匯出", "下載", "儲存", "輸出"],
                "content": """
                數據和結果匯出功能：
                1. 數據匯出：
                   - 選擇要匯出的數據範圍
                   - 點擊「匯出數據」按鈕
                   - 選擇格式：CSV、Excel、JSON、Parquet
                   - 設定匯出選項（包含標題、編碼格式）
                
                2. 圖表匯出：
                   - 在圖表右上角點擊「匯出」圖標
                   - 選擇格式：PNG、PDF、SVG、HTML
                   - 設定解析度和尺寸
                
                3. 報告匯出：
                   - 創建包含多個圖表的報告
                   - 支援PDF和PowerPoint格式
                   - 可自定義模板和樣式
                
                4. API匯出：
                   - 提供RESTful API接口
                   - 支援即時數據查詢
                   - 可整合到其他系統
                """,
                "related_actions": ["data_upload", "chart_creation"]
            }
        }
        
        # 建立TF-IDF向量化器用於語義搜索
        self._build_search_index()
    
    def _build_search_index(self):
        """建立搜索索引"""
        texts = []
        self.intent_map = []
        
        for intent, data in self.knowledge.items():
            # 組合關鍵詞和內容用於索引
            text = " ".join(data["keywords"]) + " " + data["content"]
            texts.append(text)
            self.intent_map.append(intent)
        
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)
    
    def search_knowledge(self, query: str, threshold: float = 0.1):
        """根據查詢搜索相關知識"""
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]
        
        best_match_idx = np.argmax(similarities)
        best_score = similarities[best_match_idx]
        
        if best_score > threshold:
            intent = self.intent_map[best_match_idx]
            return {
                "intent": intent,
                "confidence": float(best_score),
                "content": self.knowledge[intent]["content"],
                "related_actions": self.knowledge[intent]["related_actions"]
            }
        
        return None

class ChatbotService:
    """聊天機器人服務類"""
    
    def __init__(self):
        self.knowledge_base = InterfaceKnowledgeBase()
        self.conversation_history = {}
    
    def get_conversation_history(self, session_id: str) -> List[ChatMessage]:
        """獲取對話歷史"""
        return self.conversation_history.get(session_id, [])
    
    def add_to_history(self, session_id: str, message: ChatMessage):
        """添加消息到對話歷史"""
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        self.conversation_history[session_id].append(message)
        
        # 限制歷史長度（最多保留20條消息）
        if len(self.conversation_history[session_id]) > 20:
            self.conversation_history[session_id] = self.conversation_history[session_id][-20:]
    
    def create_system_prompt(self) -> str:
        """創建系統提示"""
        return """
        你是一個專業的數據分析平台操作助手。你的任務是幫助用戶理解和操作複雜的數據分析界面。

        你應該：
        1. 提供清晰、具體的操作步驟
        2. 使用友善、專業的語調
        3. 根據用戶的問題提供最相關的信息
        4. 在必要時詢問澄清問題
        5. 提供相關功能的建議

        如果用戶的問題不在你的知識範圍內，請誠實說明並建議聯繫技術支援。
        
        請用繁體中文回答，除非用戶使用其他語言。
        """
    
    async def process_message(self, user_message: str, session_id: str) -> ChatResponse:
        """處理用戶消息並生成回應"""
        
        # 搜索知識庫
        knowledge_result = self.knowledge_base.search_knowledge(user_message)
        
        # 獲取對話歷史
        history = self.get_conversation_history(session_id)
        
        # 準備消息列表給OpenAI
        messages = [{"role": "system", "content": self.create_system_prompt()}]
        
        # 添加歷史對話（最近5輪）
        for msg in history[-10:]:  # 限制上下文長度
            messages.append({"role": msg.role, "content": msg.content})
        
        # 如果找到相關知識，添加到提示中
        if knowledge_result:
            context_prompt = f"""
            根據以下相關信息回答用戶問題：
            
            {knowledge_result['content']}
            
            用戶問題：{user_message}
            
            請提供具體、實用的回答，並在適當時提及相關功能。
            """
            messages.append({"role": "user", "content": context_prompt})
        else:
            messages.append({"role": "user", "content": user_message})
        
        try:
            # 調用OpenAI API
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            bot_response = response.choices[0].message.content
            
            # 保存對話歷史
            user_msg = ChatMessage(content=user_message, role="user", timestamp=datetime.now())
            bot_msg = ChatMessage(content=bot_response, role="assistant", timestamp=datetime.now())
            
            self.add_to_history(session_id, user_msg)
            self.add_to_history(session_id, bot_msg)
            
            return ChatResponse(
                response=bot_response,
                intent=knowledge_result["intent"] if knowledge_result else None,
                confidence=knowledge_result["confidence"] if knowledge_result else None
            )
            
        except Exception as e:
            # 如果API調用失敗，使用備用回應
            fallback_response = self._generate_fallback_response(user_message, knowledge_result)
            return ChatResponse(response=fallback_response)
    
    def _generate_fallback_response(self, user_message: str, knowledge_result):
        """生成備用回應（當API不可用時）"""
        if knowledge_result:
            return f"根據您的問題，我找到了相關信息：\n\n{knowledge_result['content']}"
        else:
            return f"我理解您的問題：「{user_message}」。目前我可以協助您處理數據上傳、圖表創建、數據篩選和結果匯出等功能。請告訴我您需要哪方面的具體幫助？"

# 初始化服務
chatbot_service = ChatbotService()

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """聊天接口"""
    try:
        response = await chatbot_service.process_message(
            request.message, 
            request.session_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """健康檢查接口"""
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/knowledge/{intent}")
async def get_knowledge(intent: str):
    """獲取特定意圖的知識"""
    if intent in chatbot_service.knowledge_base.knowledge:
        return chatbot_service.knowledge_base.knowledge[intent]
    else:
        raise HTTPException(status_code=404, detail="Intent not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)