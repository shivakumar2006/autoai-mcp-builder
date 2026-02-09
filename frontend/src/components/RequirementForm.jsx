import React, { useState } from 'react';

const RequirementForm = () => {
  const [requirements, setRequirements] = useState("");
  const [generating, setGenerating] = useState(false);
  const [generatedCode, setGeneratedCode] = useState(null);

  const handleGenerate = async () => {
    setGenerating(true);
    
    try {
      // Call backend to generate MCP
      const response = await fetch('/api/generate-mcp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ requirements })
      });
      
      const result = await response.json();
      setGeneratedCode(result);
      
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto bg-black">
      <h1 className="text-4xl font-bold text-white mb-8">
        🚀 Auto-Generate MCP Servers
      </h1>
      
      <div className="grid grid-cols-2 gap-8">
        {/* Input Side */}
        <div>
          <label className="block text-white mb-4">
            Describe your MCP server requirements:
          </label>
          <textarea
            value={requirements}
            onChange={(e) => setRequirements(e.target.value)}
            placeholder="e.g., 'I need an MCP server that analyzes database queries and suggests optimizations'"
            className="w-full h-64 p-4 bg-slate-800 text-white rounded-lg border border-slate-700"
          />
          
          <button
            onClick={handleGenerate}
            disabled={generating || !requirements}
            className="mt-4 w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg disabled:opacity-50"
          >
            {generating ? "🔄 Generating..." : "✨ Generate MCP Server"}
          </button>
        </div>

        {/* Output Side */}
        <div>
          {generatedCode && (
            <div className="space-y-4">
              <div className="bg-green-900 border border-green-700 p-4 rounded-lg">
                <p className="text-green-300">✓ MCP Server Generated Successfully!</p>
              </div>
              
              <div className="bg-slate-800 p-4 rounded-lg">
                <h3 className="text-white font-bold mb-2">Generated Files:</h3>
                <ul className="text-gray-300 text-sm space-y-1">
                  {generatedCode.files?.map((file) => (
                    <li key={file.name}>📄 {file.path}</li>
                  ))}
                </ul>
              </div>
              
              <div className="bg-blue-900 border border-blue-700 p-4 rounded-lg">
                <p className="text-blue-300">
                  🚀 Endpoint: <span className="font-mono">{generatedCode.endpoint}</span>
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RequirementForm;
