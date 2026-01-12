import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate, useParams } from 'react-router-dom';
import { QueryClient, QueryClientProvider, useQuery, useMutation } from '@tanstack/react-query';
import { workflowAPI, documentAPI, chatAPI } from './services/api';
import { useWorkflowStore } from './store/workflowStore';
import { Plus, Save, Play, MessageCircle, Upload, FileText, Sparkles, Database, Eye, Settings } from 'lucide-react';
import ReactFlow, { Background, Controls, MiniMap, useNodesState, useEdgesState, addEdge } from 'reactflow';
import 'reactflow/dist/style.css';
import './index.css';

const queryClient = new QueryClient();

// My Stacks Page
function MyStacksPage() {
  const navigate = useNavigate();
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({ name: '', description: '' });

  const { data: workflowsData, refetch } = useQuery({
    queryKey: ['workflows'],
    queryFn: async () => {
      const res = await workflowAPI.list();
      return res.data.workflows;
    },
  });

  const createMutation = useMutation({
    mutationFn: (data) => workflowAPI.create(data),
    onSuccess: (response) => {
      refetch();
      setShowModal(false);
      navigate(`/workflow/${response.data.id}`);
    },
  });

  const handleCreate = () => {
    createMutation.mutate({ ...formData, nodes: [], edges: [] });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-xl font-bold">GenAI Stack</h1>
        </div>
        <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center text-purple-600 font-semibold">
          U
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-8 py-12">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-3xl font-bold">My Stacks</h2>
          <button onClick={() => setShowModal(true)} className="btn-primary flex items-center gap-2">
            <Plus className="w-5 h-5" />
            New Stack
          </button>
        </div>

        {!workflowsData || workflowsData.length === 0 ? (
          <div className="flex items-center justify-center py-20">
            <div className="card max-w-md text-center">
              <h3 className="text-xl font-semibold mb-2">Create New Stack</h3>
              <p className="text-gray-600 mb-6">
                Start building your generative AI apps with our essential tools and frameworks
              </p>
              <button onClick={() => setShowModal(true)} className="btn-primary mx-auto flex items-center gap-2">
                <Plus className="w-5 h-5" />
                New Stack
              </button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {workflowsData.map((workflow) => (
              <div key={workflow.id} className="card cursor-pointer" onClick={() => navigate(`/workflow/${workflow.id}`)}>
                <h3 className="text-lg font-semibold mb-2">{workflow.name}</h3>
                <p className="text-gray-600 text-sm mb-4">{workflow.description || 'No description'}</p>
                <button className="btn-outline w-full text-sm flex items-center justify-center gap-2">
                  Edit Stack
                  <Settings className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </main>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={() => setShowModal(false)}>
          <div className="bg-white rounded-xl p-6 w-full max-w-md" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-xl font-semibold mb-4">Create New Stack</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Name</label>
                <input
                  type="text"
                  className="input-field"
                  placeholder="Chat With PDF"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Description</label>
                <textarea
                  className="textarea-field"
                  placeholder="Chat with your pdf docs"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button onClick={() => setShowModal(false)} className="btn-outline flex-1">Cancel</button>
              <button onClick={handleCreate} className="btn-primary flex-1">Create</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Workflow Builder Page
function WorkflowBuilderPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: workflow } = useQuery({
    queryKey: ['workflow', id],
    queryFn: async () => {
      const res = await workflowAPI.get(id);
      return res.data;
    },
  });

  const [nodes, setNodes, onNodesChange] = useNodesState(workflow?.nodes || []);
  const [edges, setEdges, onEdgesChange] = useEdgesState(workflow?.edges || []);
  const [selectedNode, setSelectedNode] = useState(null);
  const [chatOpen, setChatOpen] = useState(false);

  React.useEffect(() => {
    if (workflow) {
      setNodes(workflow.nodes || []);
      setEdges(workflow.edges || []);
    }
  }, [workflow]);

  const updateMutation = useMutation({
    mutationFn: (data) => workflowAPI.update(id, data),
  });

  const handleSave = () => {
    updateMutation.mutate({ nodes, edges });
  };

  const onConnect = (params) => setEdges((eds) => addEdge(params, eds));

  const componentTypes = [
    { type: 'userQuery', label: 'User Query', icon: Eye },
    { type: 'llmEngine', label: 'LLM (OpenAI)', icon: Sparkles },
    { type: 'knowledgeBase', label: 'Knowledge Base', icon: Database },
    { type: 'output', label: 'Output', icon: FileText },
  ];

  const onDragStart = (event, nodeType) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  const onDrop = (event) => {
    event.preventDefault();
    const type = event.dataTransfer.getData('application/reactflow');
    const position = { x: event.clientX - 300, y: event.clientY - 100 };
    const newNode = {
      id: `${type}-${Date.now()}`,
      type: 'default',
      data: { label: type, type },
      position,
    };
    setNodes((nds) => nds.concat(newNode));
  };

  const onDragOver = (event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  };

  return (
    <div className="h-screen flex flex-col">
      <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/')} className="text-gray-600 hover:text-gray-900">
            <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
          </button>
          <h1 className="text-lg font-semibold">{workflow?.name || 'Loading...'}</h1>
        </div>
        <div className="flex gap-2">
          <button onClick={handleSave} className="btn-outline flex items-center gap-2 text-sm">
            <Save className="w-4 h-4" />
            Save
          </button>
          <button onClick={() => setChatOpen(true)} className="btn-secondary flex items-center gap-2 text-sm">
            <MessageCircle className="w-4 h-4" />
            Chat with Stack
          </button>
        </div>
      </header>

      <div className="flex-1 flex">
        <div className="w-60 bg-white border-r border-gray-200 p-4">
          <h3 className="text-sm font-semibold text-gray-600 mb-3">Components</h3>
          <div className="space-y-2">
            {componentTypes.map(({ type, label, icon: Icon }) => (
              <div
                key={type}
                draggable
                onDragStart={(e) => onDragStart(e, type)}
                className="flex items-center gap-2 p-3 border border-gray-200 rounded-lg cursor-move hover:bg-gray-50"
              >
                <Icon className="w-5 h-5 text-gray-600" />
                <span className="text-sm font-medium">{label}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="flex-1 bg-gray-50" onDrop={onDrop} onDragOver={onDragOver}>
          {nodes.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center text-gray-500">
                <div className="w-16 h-16 bg-primary bg-opacity-10 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Plus className="w-8 h-8 text-primary" />
                </div>
                <p className="font-medium">Drag & drop to get started</p>
              </div>
            </div>
          ) : (
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              onNodeClick={(_, node) => setSelectedNode(node)}
              fitView
            >
              <Background />
              <Controls />
            </ReactFlow>
          )}
        </div>

        {selectedNode && (
          <div className="w-80 bg-white border-l border-gray-200 p-4">
            <h3 className="font-semibold mb-4">Configure: {selectedNode.data.label}</h3>
            <p className="text-sm text-gray-500">Configuration panel for {selectedNode.data.type}</p>
          </div>
        )}
      </div>

      {chatOpen && <ChatModal workflowId={id} onClose={() => setChatOpen(false)} />}
    </div>
  );
}

// Chat Modal Component
function ChatModal({ workflowId, onClose }) {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!query.trim()) return;

    const userMsg = { role: 'user', content: query };
    setMessages([...messages, userMsg]);
    setQuery('');
    setLoading(true);

    try {
      const res = await chatAPI.execute({ workflow_id: workflowId, query, session_id: sessionId });
      setSessionId(res.data.session_id);
      setMessages((msgs) => [...msgs, { role: 'assistant', content: res.data.assistant_message.content }]);
    } catch (error) {
      setMessages((msgs) => [...msgs, { role: 'assistant', content: 'Error: ' + error.message }]);
    }
    setLoading(false);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-white rounded-xl w-full max-w-3xl h-[600px] flex flex-col" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between p-4 border-b">
          <h3 className="font-semibold flex items-center gap-2">
            <div className="w-6 h-6 bg-primary rounded-full flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            GenAI Stack Chat
          </h3>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">×</button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-gray-500">
              <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center mb-3">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <p>Start a conversation to test your stack</p>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={idx} className={`flex gap-3 ${msg.role === 'user' ? '' : ''}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${msg.role === 'user' ? 'bg-blue-100 text-blue-600' : 'bg-green-100 text-green-600'
                  }`}>
                  {msg.role === 'user' ? 'U' : <Sparkles className="w-4 h-4" />}
                </div>
                <div className={`flex-1 p-3 rounded-lg ${msg.role === 'user' ? 'bg-blue-50' : 'bg-white border border-gray-200'
                  }`}>
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            ))
          )}
          {loading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-green-600" />
              </div>
              <div className="bg-gray-100 p-3 rounded-lg">
                <p className="text-sm text-gray-500">Thinking...</p>
              </div>
            </div>
          )}
        </div>

        <div className="p-4 border-t">
          <div className="flex gap-2">
            <input
              type="text"
              className="input-field flex-1"
              placeholder="Send a message"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            />
            <button onClick={handleSend} className="btn-primary px-4">→</button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Main App
function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/" element={<MyStacksPage />} />
          <Route path="/workflow/:id" element={<WorkflowBuilderPage />} />
        </Routes>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
