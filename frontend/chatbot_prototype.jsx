import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, FileText, Settings, HelpCircle } from 'lucide-react';

const ChatbotPrototype = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: '您好！我是界面操作助手。我可以幫助您了解如何使用這個複雜的數據分析平台。請問有什麼我可以協助您的嗎？',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  // 模擬知識庫 - 這在實際應用中會是向量資料庫
  const knowledgeBase = {
    'data upload': {
      keywords: ['upload', 'import', 'data', 'file', '上傳', '導入', '檔案'],
      response: '要上傳數據，請按照以下步驟：\n1. 點擊左上角的「數據導入」按鈕\n2. 選擇文件格式（CSV, Excel, JSON）\n3. 拖拽文件或點擊瀏覽\n4. 確認數據預覽後點擊「確認導入」\n\n支援的文件大小最大為100MB。'
    },
    'create chart': {
      keywords: ['chart', 'graph', 'visualization', 'plot', '圖表', '視覺化', '繪圖'],
      response: '創建圖表的步驟：\n1. 在右側面板選擇「圖表工具」\n2. 選擇圖表類型（折線圖、柱狀圖、散點圖等）\n3. 拖拽字段到X軸和Y軸區域\n4. 調整顏色和樣式設定\n5. 點擊「生成圖表」\n\n提示：建議先清理數據以獲得更好的視覺效果。'
    },
    'filter data': {
      keywords: ['filter', 'search', 'query', 'condition', '篩選', '搜尋', '查詢', '條件'],
      response: '數據篩選功能：\n1. 在數據表格上方找到「篩選器」圖標\n2. 點擊要篩選的欄位標題\n3. 設定篩選條件（等於、大於、包含等）\n4. 輸入篩選值\n5. 點擊「應用篩選」\n\n您也可以組合多個篩選條件進行複雜查詢。'
    },
    'export results': {
      keywords: ['export', 'download', 'save', 'output', '匯出', '下載', '儲存', '輸出'],
      response: '匯出結果的方法：\n1. 選擇要匯出的內容（表格、圖表或報告）\n2. 點擊右上角的「匯出」按鈕\n3. 選擇格式（PDF、Excel、PNG、CSV）\n4. 設定匯出選項（包含原始數據、圖表樣式等）\n5. 點擊「開始匯出」\n\n匯出的文件會自動下載到您的下載資料夾。'
    }
  };

  // 模擬LLM API調用
  const simulateLLMResponse = async (userMessage) => {
    setIsTyping(true);
    
    // 模擬API延遲
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    const lowerMessage = userMessage.toLowerCase();
    
    // 簡單的意圖識別邏輯
    let bestMatch = null;
    let maxScore = 0;
    
    Object.entries(knowledgeBase).forEach(([intent, data]) => {
      const score = data.keywords.reduce((acc, keyword) => {
        return acc + (lowerMessage.includes(keyword.toLowerCase()) ? 1 : 0);
      }, 0);
      
      if (score > maxScore) {
        maxScore = score;
        bestMatch = data;
      }
    });
    
    let response;
    if (bestMatch && maxScore > 0) {
      response = bestMatch.response;
    } else {
      // 通用回應
      response = `我理解您的問題："${userMessage}"。\n\n目前我可以協助您處理以下操作：\n• 數據上傳和導入\n• 創建圖表和視覺化\n• 數據篩選和查詢\n• 結果匯出和下載\n\n請告訴我您想了解哪個功能的詳細操作步驟？`;
    }
    
    setIsTyping(false);
    return response;
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;
    
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    
    // 獲取bot回應
    const botResponse = await simulateLLMResponse(inputMessage);
    
    const botMessage = {
      id: Date.now() + 1,
      type: 'bot',
      content: botResponse,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, botMessage]);
  };

  const quickActions = [
    { label: '如何上傳數據？', icon: FileText },
    { label: '怎麼創建圖表？', icon: Settings },
    { label: '數據篩選方法', icon: HelpCircle }
  ];

  const handleQuickAction = (action) => {
    setInputMessage(action);
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto bg-gray-50">
      {/* Header */}
      <div className="bg-blue-600 text-white p-4 shadow-lg">
        <div className="flex items-center space-x-3">
          <Bot className="w-8 h-8" />
          <div>
            <h1 className="text-xl font-bold">數據平台操作助手</h1>
            <p className="text-blue-100 text-sm">協助您快速掌握複雜界面操作</p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="p-4 bg-white border-b">
        <p className="text-sm text-gray-600 mb-2">常見問題：</p>
        <div className="flex flex-wrap gap-2">
          {quickActions.map((action, index) => (
            <button
              key={index}
              onClick={() => handleQuickAction(action.label)}
              className="flex items-center space-x-1 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm hover:bg-blue-200 transition-colors"
            >
              <action.icon className="w-3 h-3" />
              <span>{action.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`flex max-w-3xl ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'} space-x-3`}>
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                message.type === 'user' ? 'bg-blue-500' : 'bg-gray-500'
              }`}>
                {message.type === 'user' ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-white" />}
              </div>
              <div className={`px-4 py-2 rounded-lg ${
                message.type === 'user' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-white shadow-md'
              }`}>
                <div className="whitespace-pre-line">{message.content}</div>
                <div className={`text-xs mt-1 ${
                  message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                }`}>
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {isTyping && (
          <div className="flex justify-start">
            <div className="flex max-w-3xl flex-row space-x-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-gray-500">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div className="px-4 py-2 rounded-lg bg-white shadow-md">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 bg-white border-t">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="輸入您的問題..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatbotPrototype;