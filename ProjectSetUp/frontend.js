import React, { useState, useEffect, useRef } from 'react';
import { Send, User, Bot, Menu, X, BarChart3, Users, MessageSquare, TrendingUp, Clock, CheckCircle, AlertCircle } from 'lucide-react';

// Mock student data (simulating Snowflake unified data layer)
const mockStudentData = {
  id: "STU2024001",
  name: "Sarah Johnson",
  email: "sarah.johnson@techedu.edu",
  program: "Computer Science",
  year: 3,
  gpa: 3.7,
  financialAid: {
    status: "Active",
    amount: 15000,
    disbursementDate: "2025-01-15"
  },
  courses: [
    { code: "CS301", name: "Data Structures", credits: 4, grade: "A" },
    { code: "CS302", name: "Algorithms", credits: 4, grade: "A-" },
    { code: "MATH301", name: "Linear Algebra", credits: 3, grade: "B+" }
  ],
  housing: {
    building: "West Hall",
    room: "204B",
    moveInDate: "2024-08-15"
  }
};

// Knowledge base (simulating vector database)
const knowledgeBase = [
  {
    category: "admissions",
    keywords: ["admission", "apply", "application", "deadline", "requirements"],
    responses: [
      "Application deadlines are: Fall - March 1, Spring - October 1, Summer - March 1.",
      "Required documents: High school transcript, SAT/ACT scores, two recommendation letters, and personal essay.",
      "The average GPA for admitted students is 3.5. We use holistic review considering academics, extracurriculars, and essays."
    ]
  },
  {
    category: "financial_aid",
    keywords: ["financial aid", "scholarship", "loan", "fafsa", "tuition", "payment", "cost"],
    responses: [
      "Your current financial aid package includes ${amount} in grants and scholarships.",
      "The next disbursement is scheduled for {date}. Funds are directly applied to your student account.",
      "To apply for additional aid, complete the FAFSA by March 1. Visit financialaid.techedu.edu for more information."
    ]
  },
  {
    category: "registration",
    keywords: ["register", "enroll", "course", "class", "schedule", "drop", "add"],
    responses: [
      "Course registration opens: Seniors - Nov 1, Juniors - Nov 8, Sophomores - Nov 15, Freshmen - Nov 22.",
      "To add or drop courses, log into the Student Portal > Academic Records > Registration.",
      "You can drop courses without penalty until the end of week 2 of the semester."
    ]
  },
  {
    category: "grades",
    keywords: ["grade", "gpa", "transcript", "academic record"],
    responses: [
      "Your current GPA is {gpa}. You're enrolled in {courseCount} courses this semester.",
      "Official transcripts can be requested through the Registrar's Office. Online requests take 3-5 business days.",
      "Grades are posted within 72 hours after final exams. Check the Student Portal for updates."
    ]
  },
  {
    category: "housing",
    keywords: ["housing", "dorm", "residence", "room", "roommate"],
    responses: [
      "You're currently assigned to {building}, Room {room}.",
      "Housing applications for next year open February 1. Priority is given to returning students.",
      "For maintenance issues, submit a work order at housing.techedu.edu or call (555) 123-4567."
    ]
  }
];

// Simulated AI response generator (in production, this would call GPT-4 API)
const generateAIResponse = (message, studentData) => {
  const lowerMessage = message.toLowerCase();
  
  // Intent classification
  for (const kb of knowledgeBase) {
    if (kb.keywords.some(keyword => lowerMessage.includes(keyword))) {
      let response = kb.responses[Math.floor(Math.random() * kb.responses.length)];
      
      // Personalize response with student data
      response = response
        .replace('{amount}', studentData.financialAid.amount.toLocaleString())
        .replace('{date}', studentData.financialAid.disbursementDate)
        .replace('{gpa}', studentData.gpa)
        .replace('{courseCount}', studentData.courses.length)
        .replace('{building}', studentData.housing.building)
        .replace('{room}', studentData.housing.room);
      
      return {
        text: response,
        confidence: 0.92,
        category: kb.category,
        automated: true
      };
    }
  }
  
  // Default response for unmatched queries
  return {
    text: "I understand you're asking about something specific. Let me connect you with a support specialist who can help you better. In the meantime, you can also check our comprehensive FAQ at support.techedu.edu or call our support line at (555) 123-4567.",
    confidence: 0.45,
    category: "escalation",
    automated: false
  };
};

// Main App Component
const UniAssistPro = () => {
  const [currentView, setCurrentView] = useState('chat');
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      text: `Hi ${mockStudentData.name}! 👋 I'm UniAssist, your AI-powered student support assistant. I have access to your student profile and can help you with:

• Financial Aid & Tuition
• Course Registration
• Academic Records & Grades
• Housing Information
• Admissions Questions

How can I help you today?`,
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const messagesEndRef = useRef(null);

  // Analytics data (simulated real-time metrics)
  const [analytics, setAnalytics] = useState({
    totalQueries: 1247,
    automatedResolution: 73,
    avgResponseTime: 3.2,
    satisfactionScore: 87,
    activeUsers: 342,
    queriesLast24h: 156,
    topCategories: [
      { name: 'Financial Aid', count: 423, percentage: 34 },
      { name: 'Registration', count: 361, percentage: 29 },
      { name: 'Grades', count: 298, percentage: 24 },
      { name: 'Housing', count: 165, percentage: 13 }
    ]
  });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: messages.length + 1,
      type: 'user',
      text: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    // Simulate AI processing time
    setTimeout(() => {
      const aiResponse = generateAIResponse(inputMessage, mockStudentData);
      
      const botMessage = {
        id: messages.length + 2,
        type: 'bot',
        text: aiResponse.text,
        timestamp: new Date(),
        confidence: aiResponse.confidence,
        category: aiResponse.category,
        automated: aiResponse.automated
      };

      setMessages(prev => [...prev, botMessage]);
      setIsTyping(false);

      // Update analytics
      setAnalytics(prev => ({
        ...prev,
        totalQueries: prev.totalQueries + 1,
        avgResponseTime: 3.2,
        queriesLast24h: prev.queriesLast24h + 1
      }));
    }, 1500);
  };

  const suggestedQuestions = [
    "When is my next financial aid disbursement?",
    "What's my current GPA?",
    "How do I register for next semester?",
    "Where is my dorm room located?",
    "What are the admission requirements?"
  ];

  // Chat View Component
  const ChatView = () => (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-4 shadow-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
              <Bot size={24} />
            </div>
            <div>
              <h1 className="font-bold text-lg">UniAssist Pro</h1>
              <p className="text-xs text-blue-100">AI Student Support • Online 24/7</p>
            </div>
          </div>
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          >
            {menuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {menuOpen && (
        <div className="bg-white border-b shadow-md p-4">
          <div className="flex flex-col gap-2">
            <button
              onClick={() => {
                setCurrentView('chat');
                setMenuOpen(false);
              }}
              className="p-3 text-left hover:bg-gray-100 rounded-lg flex items-center gap-2"
            >
              <MessageSquare size={20} />
              <span>Chat Support</span>
            </button>
            <button
              onClick={() => {
                setCurrentView('dashboard');
                setMenuOpen(false);
              }}
              className="p-3 text-left hover:bg-gray-100 rounded-lg flex items-center gap-2"
            >
              <BarChart3 size={20} />
              <span>Analytics Dashboard</span>
            </button>
            <button
              onClick={() => {
                setCurrentView('profile');
                setMenuOpen(false);
              }}
              className="p-3 text-left hover:bg-gray-100 rounded-lg flex items-center gap-2"
            >
              <User size={20} />
              <span>My Profile</span>
            </button>
          </div>
        </div>
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3 ${msg.type === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
            >
              <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                msg.type === 'user' ? 'bg-blue-600' : 'bg-green-600'
              }`}>
                {msg.type === 'user' ? (
                  <User size={18} className="text-white" />
                ) : (
                  <Bot size={18} className="text-white" />
                )}
              </div>
              <div className={`flex flex-col max-w-[80%] ${msg.type === 'user' ? 'items-end' : 'items-start'}`}>
                <div className={`rounded-2xl px-4 py-3 ${
                  msg.type === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-800 shadow-md border border-gray-200'
                }`}>
                  <p className="text-sm whitespace-pre-line">{msg.text}</p>
                </div>
                <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
                  <span>{msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  {msg.confidence && (
                    <span className="flex items-center gap-1">
                      <CheckCircle size={12} className="text-green-600" />
                      {(msg.confidence * 100).toFixed(0)}% confident
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-green-600 flex items-center justify-center">
                <Bot size={18} className="text-white" />
              </div>
              <div className="bg-white rounded-2xl px-4 py-3 shadow-md border border-gray-200">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Suggested Questions */}
      {messages.length <= 2 && (
        <div className="px-4 py-3 bg-white border-t">
          <p className="text-xs text-gray-600 mb-2 font-medium">Suggested Questions:</p>
          <div className="flex gap-2 overflow-x-auto pb-2">
            {suggestedQuestions.map((question, idx) => (
              <button
                key={idx}
                onClick={() => setInputMessage(question)}
                className="px-3 py-2 bg-blue-50 text-blue-700 rounded-full text-xs whitespace-nowrap hover:bg-blue-100 transition-colors border border-blue-200"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="p-4 bg-white border-t shadow-lg">
        <div className="max-w-4xl mx-auto flex gap-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Type your question here..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim()}
            className="px-6 py-3 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <Send size={18} />
            <span className="hidden sm:inline">Send</span>
          </button>
        </div>
        <p className="text-xs text-gray-500 text-center mt-2">
          Powered by AI • Response time: ~3 seconds • 99.7% uptime
        </p>
      </div>
    </div>
  );

  // Dashboard View Component
  const DashboardView = () => (
    <div className="h-full overflow-y-auto bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-purple-700 text-white p-6 shadow-lg">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-bold">Analytics Dashboard</h1>
            <button
              onClick={() => setCurrentView('chat')}
              className="px-4 py-2 bg-white/20 rounded-lg hover:bg-white/30 transition-colors"
            >
              Back to Chat
            </button>
          </div>
          <p className="text-purple-100">Real-time system performance and metrics</p>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="max-w-7xl mx-auto p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {/* Total Queries */}
          <div className="bg-white rounded-xl p-6 shadow-md border border-gray-200">
            <div className="flex items-center justify-between mb-2">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <MessageSquare className="text-blue-600" size={24} />
              </div>
              <span className="text-green-600 text-sm font-medium">+12%</span>
            </div>
            <h3 className="text-gray-600 text-sm">Total Queries</h3>
            <p className="text-3xl font-bold text-gray-900">{analytics.totalQueries.toLocaleString()}</p>
            <p className="text-xs text-gray-500 mt-1">{analytics.queriesLast24h} in last 24h</p>
          </div>

          {/* Automation Rate */}
          <div className="bg-white rounded-xl p-6 shadow-md border border-gray-200">
            <div className="flex items-center justify-between mb-2">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <CheckCircle className="text-green-600" size={24} />
              </div>
              <span className="text-green-600 text-sm font-medium">Target: 70%</span>
            </div>
            <h3 className="text-gray-600 text-sm">Automated Resolution</h3>
            <p className="text-3xl font-bold text-gray-900">{analytics.automatedResolution}%</p>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div className="bg-green-600 h-2 rounded-full" style={{ width: `${analytics.automatedResolution}%` }}></div>
            </div>
          </div>

          {/* Response Time */}
          <div className="bg-white rounded-xl p-6 shadow-md border border-gray-200">
            <div className="flex items-center justify-between mb-2">
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                <Clock className="text-yellow-600" size={24} />
              </div>
              <span className="text-green-600 text-sm font-medium">-15%</span>
            </div>
            <h3 className="text-gray-600 text-sm">Avg Response Time</h3>
            <p className="text-3xl font-bold text-gray-900">{analytics.avgResponseTime}m</p>
            <p className="text-xs text-gray-500 mt-1">Target: &lt;5 minutes</p>
          </div>

          {/* Satisfaction Score */}
          <div className="bg-white rounded-xl p-6 shadow-md border border-gray-200">
            <div className="flex items-center justify-between mb-2">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <TrendingUp className="text-purple-600" size={24} />
              </div>
              <span className="text-green-600 text-sm font-medium">+25%</span>
            </div>
            <h3 className="text-gray-600 text-sm">Satisfaction Score</h3>
            <p className="text-3xl font-bold text-gray-900">{analytics.satisfactionScore}%</p>
            <p className="text-xs text-gray-500 mt-1">Target: 85%</p>
          </div>
        </div>

        {/* Query Categories */}
        <div className="bg-white rounded-xl p-6 shadow-md border border-gray-200 mb-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Query Categories</h3>
          <div className="space-y-4">
            {analytics.topCategories.map((cat, idx) => (
              <div key={idx}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">{cat.name}</span>
                  <span className="text-sm text-gray-600">{cat.count} queries ({cat.percentage}%)</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all duration-500"
                    style={{ width: `${cat.percentage}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* System Status */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white rounded-xl p-6 shadow-md border border-gray-200">
            <h3 className="text-lg font-bold text-gray-900 mb-4">System Health</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">API Response Time</span>
                <span className="text-sm font-medium text-green-600">124ms</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Database Query Time</span>
                <span className="text-sm font-medium text-green-600">45ms</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">System Uptime</span>
                <span className="text-sm font-medium text-green-600">99.7%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Active Users</span>
                <span className="text-sm font-medium text-blue-600">{analytics.activeUsers}</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-md border border-gray-200">
            <h3 className="text-lg font-bold text-gray-900 mb-4">ROI Metrics</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Cost per Query</span>
                <span className="text-sm font-medium text-green-600">$0.38</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Staff Workload Reduction</span>
                <span className="text-sm font-medium text-green-600">52%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Monthly Savings</span>
                <span className="text-sm font-medium text-green-600">$91,667</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">ROI (Projected Y1)</span>
                <span className="text-sm font-medium text-green-600">85.7%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Profile View Component
  const ProfileView = () => (
    <div className="h-full overflow-y-auto bg-gray-50">
      <div className="bg-gradient-to-r from-green-600 to-green-700 text-white p-6 shadow-lg">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-bold">Student Profile</h1>
            <button
              onClick={() => setCurrentView('chat')}
              className="px-4 py-2 bg-white/20 rounded-lg hover:bg-white/30 transition-colors"
            >
              Back to Chat
            </button>
          </div>
          <p className="text-green-100">Unified student information from all systems</p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto p-6 space-y-6">
        {/* Personal Info */}
        <div className="bg-white rounded-xl p-6 shadow-md border border-gray-200">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Personal Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-gray-600">Student ID</label>
              <p className="font-medium">{mockStudentData.id}</p>
            </div>
            <div>
              <label className="text-sm text-gray-600">Full Name</label>
              <p className="font-medium">{mockStudentData.name}</p>
            </div>
            <div>
              <label className="text-sm text-gray-600">Email</label>
              <p className="font-medium">{mockStudentData.email}</p>
            </div>
            <div>
              <label className="text-sm text-gray-600">Program</label>
              <p className="font-medium">{mockStudentData.program}</p>
            </div>
            <div>
              <label className="text-sm text-gray-600">Year</label>
              <p className="font-medium">Year {mockStudentData.year}</p>
            </div>
            <div>
              <label className="text-sm text-gray-600">GPA</label>
              <p className="font-medium text-green-600">{mockStudentData.gpa}</p>
            </div>
          </div>
        </div>

        {/* Financial Aid */}
        <div className="bg-white rounded-xl p-6 shadow-md border border-gray-200">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Financial Aid</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
              <span className="text-sm text-gray-700">Status</span>
              <span className="px-3 py-1 bg-green-600 text-white text-xs rounded-full font-medium">
                {mockStudentData.financialAid.status}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="text-sm text-gray-700">Total Package</span>
              <span className="font-bold text-gray-900">${mockStudentData.financialAid.amount.toLocaleString()}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="text-sm text-gray-700">Next Disbursement</span>
              <span className="font-medium text-gray-900">{mockStudentData.financialAid.disbursementDate}</span>
            </div>
          </div>
        </div>

        {/* Current Courses */}
        <div className="bg-white rounded-xl p-6 shadow-md border border-gray-200">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Current Courses</h3>
          <div className="space-y-3">
            {mockStudentData.courses.map((course, idx) => (
              <div key={idx} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors">
                <div>
                  <p className="font-medium text-gray-900">{course.code}: {course.name}</p>
                  <p className="text-sm text-gray-600">{course.credits} credits</p>
                </div>
                <div className="px-3 py-1 bg-blue-100 text-blue-700 rounded-lg font-medium">
                  {course.grade}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Housing */}
        <div className="bg-white rounded-xl p-6 shadow-md border border-gray-200">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Housing Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-gray-600">Building</label>
              <p className="font-medium">{mockStudentData.housing.building}</p>
            </div>
            <div>
              <label className="text-sm text-gray-600">Room Number</label>
              <p className="font-medium">{mockStudentData.housing.room}</p>
            </div>
            <div className="md:col-span-2">
              <label className="text-sm text-gray-600">Move-In Date</label>
              <p className="font-medium">{mockStudentData.housing.moveInDate}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="h-screen flex flex-col bg-white">
      {currentView === 'chat' && <ChatView />}
      {currentView === 'dashboard' && <DashboardView />}
      {currentView === 'profile' && <ProfileView />}
    </div>
  );
};

export default UniAssistPro;