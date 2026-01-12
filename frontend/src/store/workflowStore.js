import { create } from 'zustand';

export const useWorkflowStore = create((set, get) => ({
    // Current workflow being edited
    currentWorkflow: null,
    nodes: [],
    edges: [],
    selectedNode: null,

    // Set current workflow
    setWorkflow: (workflow) => set({
        currentWorkflow: workflow,
        nodes: workflow?.nodes || [],
        edges: workflow?.edges || [],
    }),

    // Node operations
    setNodes: (nodes) => set({ nodes }),
    setEdges: (edges) => set({ edges }),
    setSelectedNode: (node) => set({ selectedNode: node }),

    // Add node
    addNode: (node) => set((state) => ({
        nodes: [...state.nodes, node],
    })),

    // Update node data
    updateNodeData: (nodeId, data) => set((state) => ({
        nodes: state.nodes.map((node) =>
            node.id === nodeId ? { ...node, data: { ...node.data, ...data } } : node
        ),
    })),

    // Remove node
    removeNode: (nodeId) => set((state) => ({
        nodes: state.nodes.filter((node) => node.id !== nodeId),
        edges: state.edges.filter((edge) => edge.source !== nodeId && edge.target !== nodeId),
    })),

    // Clear workflow
    clearWorkflow: () => set({
        currentWorkflow: null,
        nodes: [],
        edges: [],
        selectedNode: null,
    }),
}));
