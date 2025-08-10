import { useState, useEffect } from 'react'
import { Search, Users, Database, MessageSquare, Loader2, Network } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import './App.css'

interface QueryResult {
  results: any[]
  cypher_used: string
  execution_time: number
}

interface GraphStats {
  total_nodes: number
  total_relationships: number
  person_count: number
  organization_count: number
}

function App() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<QueryResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [stats, setStats] = useState<GraphStats | null>(null)

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_URL}/graph/stats`)
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (err) {
      console.error('Failed to fetch stats:', err)
    }
  }

  const handleQuery = async () => {
    if (!query.trim()) return

    setLoading(true)
    setError('')
    setResults(null)

    try {
      const response = await fetch(`${API_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query.trim(),
          user_name: 'CurrentUser'
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setResults(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const exampleQueries = [
    "Find friends who live in San Francisco",
    "Who would want to join a book club?",
    "Who in my network has fintech experience?",
    "What are Will's interests?",
    "Find Cornell friends in their 3rd year",
    "Who are my rock climbing buddies?",
    "Show me people interested in startups",
    "Find venture capitalists in my network"
  ]

  const handleExampleQuery = (exampleQuery: string) => {
    setQuery(exampleQuery)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleQuery()
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Network className="h-8 w-8 text-blue-600" />
            <h1 className="text-4xl font-bold text-gray-900">Network Query Platform</h1>
          </div>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Ask questions about your network in natural language. Discover connections, interests, and opportunities within your social graph.
          </p>
        </div>

        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <Card>
              <CardContent className="p-4 text-center">
                <Users className="h-6 w-6 text-blue-600 mx-auto mb-2" />
                <div className="text-2xl font-bold">{stats.person_count}</div>
                <div className="text-sm text-gray-600">People</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <Database className="h-6 w-6 text-green-600 mx-auto mb-2" />
                <div className="text-2xl font-bold">{stats.organization_count}</div>
                <div className="text-sm text-gray-600">Organizations</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <Network className="h-6 w-6 text-purple-600 mx-auto mb-2" />
                <div className="text-2xl font-bold">{stats.total_nodes}</div>
                <div className="text-sm text-gray-600">Total Nodes</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <MessageSquare className="h-6 w-6 text-orange-600 mx-auto mb-2" />
                <div className="text-2xl font-bold">{stats.total_relationships}</div>
                <div className="text-sm text-gray-600">Relationships</div>
              </CardContent>
            </Card>
          </div>
        )}

        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Search className="h-5 w-5" />
              Ask Your Network
            </CardTitle>
            <CardDescription>
              Type your question in natural language and discover insights about your network
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-2 mb-4">
              <Input
                placeholder="e.g., Find friends who live in San Francisco"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                className="flex-1"
              />
              <Button onClick={handleQuery} disabled={loading || !query.trim()}>
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                {loading ? 'Searching...' : 'Search'}
              </Button>
            </div>

            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-2">Try these example queries:</p>
              <div className="flex flex-wrap gap-2">
                {exampleQueries.map((example, index) => (
                  <Badge
                    key={index}
                    variant="secondary"
                    className="cursor-pointer hover:bg-blue-100 hover:text-blue-800 transition-colors"
                    onClick={() => handleExampleQuery(example)}
                  >
                    {example}
                  </Badge>
                ))}
              </div>
            </div>

            {error && (
              <Alert className="mb-4 border-red-200 bg-red-50">
                <AlertDescription className="text-red-800">
                  Error: {error}
                </AlertDescription>
              </Alert>
            )}

            {results && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">Results</h3>
                  <Badge variant="outline">
                    {results.results.length} result{results.results.length !== 1 ? 's' : ''} in {typeof results.execution_time === 'number' ? results.execution_time.toFixed(2) : parseFloat(results.execution_time).toFixed(2)}ms
                  </Badge>
                </div>

                {results.results.length === 0 ? (
                  <Alert>
                    <AlertDescription>
                      No results found for your query. Try rephrasing or using one of the example queries.
                    </AlertDescription>
                  </Alert>
                ) : (
                  <div className="grid gap-4">
                    {results.results.map((result, index) => (
                      <Card key={index} className="border-l-4 border-l-blue-500">
                        <CardContent className="p-4">
                          <div className="space-y-2">
                            {Object.entries(result).map(([key, value]) => (
                              <div key={key} className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-4">
                                <span className="font-medium text-gray-700 min-w-24 capitalize">
                                  {key.replace(/[._]/g, ' ')}:
                                </span>
                                <span className="text-gray-900 break-words">
                                  {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                                </span>
                              </div>
                            ))}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}

                <Card className="bg-gray-50">
                  <CardHeader>
                    <CardTitle className="text-sm">Generated Cypher Query</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <code className="text-xs bg-white p-2 rounded border block overflow-x-auto">
                      {results.cypher_used}
                    </code>
                  </CardContent>
                </Card>
              </div>
            )}
          </CardContent>
        </Card>

        <div className="text-center text-sm text-gray-500">
          <p>Powered by FastAPI, Neo4j, and OpenAI • Built for Applied AI Hackathon 2025</p>
        </div>
      </div>
    </div>
  )
}

export default App
