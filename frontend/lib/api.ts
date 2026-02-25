import axios from 'axios'

// Base URL of your FastAPI backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json'
    }
})

// Types — TypeScript forces you to define data shapes
export interface Report {
    id: number
    title: string
    topic: string
    status: string
    content: string | null
    created_at: string
}

export interface CreateReportRequest {
    title: string
    topic: string
    user_id: number
}

export interface PipelineResponse {
    id: number
    title: string
    topic: string
    status: string
    content: string
    iterations: number
    approved: boolean
    created_at: string
}

// API functions — one function per endpoint
export const reportsApi = {
    
    // Get a single report
    getReport: async (id: number): Promise<Report> => {
        const response = await api.get(`/reports/${id}`)
        return response.data
    },
    
    // Generate report using multi-agent pipeline
    generatePipelineReport: async (data: CreateReportRequest): Promise<PipelineResponse> => {
        const response = await api.post('/reports/pipeline', data)
        return response.data
    },
    
    // Health check
    healthCheck: async () => {
        const response = await api.get('/health')
        return response.data
    }
}