'use client'

import { useState } from 'react'
import { reportsApi, PipelineResponse } from '../lib/api'
import ReactMarkdown from 'react-markdown'

// Agent progress tracker component
function AgentProgress({ currentStep }: { currentStep: number }) {
    const agents = [
        { name: 'Research Agent', description: 'Gathering information...' },
        { name: 'Analysis Agent', description: 'Extracting insights...' },
        { name: 'Writing Agent', description: 'Writing report...' },
        { name: 'Validator Agent', description: 'Reviewing quality...' },
    ]

    return (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold text-gray-700 mb-3">Agent Progress</h3>
            {agents.map((agent, index) => (
                <div key={index} className="flex items-center gap-3 mb-2">
                    <span className="text-xl">
                        {index < currentStep ? '✅' : index === currentStep ? '⏳' : '⬜'}
                    </span>
                    <div>
                        <p className="font-medium text-sm">{agent.name}</p>
                        {index === currentStep && (
                            <p className="text-xs text-gray-500">{agent.description}</p>
                        )}
                    </div>
                </div>
            ))}
        </div>
    )
}

// Report display component
function ReportDisplay({ report }: { report: PipelineResponse }) {
    return (
        <div className="mt-6 p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
            <div className="flex justify-between items-start mb-4">
                <h2 className="text-xl font-bold text-gray-800">{report.title}</h2>
                <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                    {report.status}
                </span>
            </div>
            <div className="flex gap-4 text-sm text-gray-500 mb-4">
                <span>ID: #{report.id}</span>
                <span>Iterations: {report.iterations}</span>
                <span>Approved: {report.approved ? 'Yes' : 'No'}</span>
                <span>Created: {new Date(report.created_at).toLocaleString()}</span>
            </div>
            <div className="prose max-w-none">
               <div className="prose max-w-none text-gray-700 text-sm">
    <ReactMarkdown>{report.content}</ReactMarkdown>
</div>
            </div>
        </div>
    )
}

// Main page component
export default function Home() {
    const [title, setTitle] = useState('')
    const [topic, setTopic] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [currentStep, setCurrentStep] = useState(-1)
    const [report, setReport] = useState<PipelineResponse | null>(null)
    const [error, setError] = useState<string | null>(null)

    const handleGenerate = async () => {
        // Validate inputs
        if (!title.trim() || !topic.trim()) {
            setError('Please enter both title and topic')
            return
        }

        setIsLoading(true)
        setError(null)
        setReport(null)

        // Simulate agent progress steps
        // In Phase 6 we'll make this real-time using SSE
        setCurrentStep(0)
        
        try {
            // Simulate progress updates while waiting
            const progressInterval = setInterval(() => {
                setCurrentStep(prev => {
                    if (prev < 3) return prev + 1
                    clearInterval(progressInterval)
                    return prev
                })
            }, 8000) // advance every 8 seconds

            const result = await reportsApi.generatePipelineReport({
                title,
                topic,
                user_id: 1
            })

            clearInterval(progressInterval)
            setCurrentStep(4) // all done
            setReport(result)

        } catch (err: unknown) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to generate report'
            setError(errorMessage)
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-gray-100">
            {/* Navbar */}
            <nav className="bg-white shadow-sm border-b">
                <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
                    <h1 className="text-xl font-bold text-blue-600">
                        🤖 AI Report Platform
                    </h1>
                    <span className="text-sm text-gray-500">
                        Powered by GPT-4o + LangGraph
                    </span>
                </div>
            </nav>

            {/* Main content */}
            <div className="max-w-4xl mx-auto px-4 py-8">
                
                {/* Input section */}
                <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
                    <h2 className="text-lg font-semibold text-gray-800 mb-4">
                        Generate Research Report
                    </h2>
                    
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Report Title
                            </label>
                            <input
                                type="text"
                                value={title}
                                onChange={(e) => setTitle(e.target.value)}
                                placeholder="e.g. AI Trends in Healthcare 2025"
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                disabled={isLoading}
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Research Topic
                            </label>
                            <textarea
                                value={topic}
                                onChange={(e) => setTopic(e.target.value)}
                                placeholder="e.g. Impact of artificial intelligence on medical diagnostics and patient outcomes"
                                rows={3}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                disabled={isLoading}
                            />
                        </div>

                        {error && (
                            <div className="p-3 bg-red-50 border border-red-200 rounded-md text-red-600 text-sm">
                                {error}
                            </div>
                        )}

                        <button
                            onClick={handleGenerate}
                            disabled={isLoading}
                            className="w-full py-3 bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            {isLoading ? 'Running Multi-Agent Pipeline...' : 'Generate Report'}
                        </button>
                    </div>

                    {/* Agent progress */}
                    {isLoading && <AgentProgress currentStep={currentStep} />}
                </div>

                {/* Report display */}
                {report && <ReportDisplay report={report} />}
            </div>
        </div>
    )
}