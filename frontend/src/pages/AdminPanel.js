import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import { adminAPI, llmAPI } from '../services/api';

function AdminPanel({ user, onLogout }) {
  const [stats, setStats] = useState(null);
  const [configs, setConfigs] = useState([]);
  const [llmStatus, setLlmStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [testingConnection, setTestingConnection] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [statsRes, configsRes, llmStatusRes] = await Promise.all([
        adminAPI.getStats().catch(e => ({ data: null })),
        adminAPI.listConfigs().catch(e => ({ data: [] })),
        llmAPI.getStatus().catch(e => ({ data: null })),
      ]);
      setStats(statsRes.data);
      setConfigs(configsRes.data);
      setLlmStatus(llmStatusRes.data);
    } catch (error) {
      console.error('Error loading admin data:', error);
      alert('Failed to load admin data: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTestConnection = async (modelType) => {
    setTestingConnection(true);
    try {
      const response = await llmAPI.testConnection(modelType);
      if (response.data.success) {
        alert('✅ Connection successful!\n\n' + response.data.message);
      } else {
        alert('❌ Connection failed:\n\n' + response.data.message);
      }
    } catch (error) {
      alert('❌ Connection test failed:\n\n' + error.message);
    } finally {
      setTestingConnection(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar user={user} onLogout={onLogout} />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Admin Panel</h1>
          <p className="mt-2 text-gray-600">System configuration and monitoring</p>
        </div>

        {/* Tabs */}
        <div className="mb-6 border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('overview')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'overview'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('config')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'config'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Configuration
            </button>
            <button
              onClick={() => setActiveTab('llm')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'llm'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              LLM Management
            </button>
          </nav>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          </div>
        ) : (
          <div>
            {activeTab === 'overview' && stats && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-sm font-medium text-gray-500 mb-2">Total Tenants</h3>
                    <p className="text-3xl font-bold text-gray-900">{stats.tenants.total}</p>
                  </div>
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-sm font-medium text-gray-500 mb-2">Total Users</h3>
                    <p className="text-3xl font-bold text-gray-900">{stats.users.total}</p>
                  </div>
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-sm font-medium text-gray-500 mb-2">Total Documents</h3>
                    <p className="text-3xl font-bold text-gray-900">{stats.documents.total}</p>
                  </div>
                </div>

                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">Subscriptions</h2>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">Free Tier</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.subscriptions.free}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Standard Tier</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.subscriptions.standard}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Professional Tier</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.subscriptions.professional}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">Document Status</h2>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">Uploaded</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.documents.uploaded}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Processing</p>
                      <p className="text-2xl font-bold text-blue-600">{stats.documents.processing}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Completed</p>
                      <p className="text-2xl font-bold text-green-600">{stats.documents.completed}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Failed</p>
                      <p className="text-2xl font-bold text-red-600">{stats.documents.failed}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'config' && (
              <div className="space-y-6">
                {/* OCR Engine Configuration */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">OCR Engine Configuration</h2>
                  <div className="space-y-4">
                    <div className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-medium text-gray-900">Tesseract OCR</h3>
                        <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Active</span>
                      </div>
                      <p className="text-sm text-gray-500">Traditional OCR engine for high-quality images</p>
                    </div>
                    <div className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-medium text-gray-900">RapidOCR</h3>
                        <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Active</span>
                      </div>
                      <p className="text-sm text-gray-500">Fast ONNX-based OCR for quick processing</p>
                    </div>
                    <div className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-medium text-gray-900">PaddleOCR</h3>
                        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">Mock Mode</span>
                      </div>
                      <p className="text-sm text-gray-500">Deep learning OCR (currently mocked to save resources)</p>
                    </div>
                  </div>
                </div>

                {/* LLM Configuration */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">LLM Configuration</h2>
                  <div className="space-y-4">
                    <div className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-medium text-gray-900">DeepSeek</h3>
                        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">Mock Mode</span>
                      </div>
                      <p className="text-sm text-gray-500">Configure API key for DeepSeek LLM</p>
                    </div>
                    <div className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-medium text-gray-900">Qwen</h3>
                        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">Mock Mode</span>
                      </div>
                      <p className="text-sm text-gray-500">Configure API key for Qwen LLM</p>
                    </div>
                    <div className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-medium text-gray-900">Mistral</h3>
                        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">Mock Mode</span>
                      </div>
                      <p className="text-sm text-gray-500">Configure API key for Mistral LLM</p>
                    </div>
                    <div className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-medium text-gray-900">Qwen-VL</h3>
                        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">Mock Mode</span>
                      </div>
                      <p className="text-sm text-gray-500">Configure API key for Qwen Vision LLM</p>
                    </div>
                  </div>
                </div>

                {/* Cloud OCR Configuration */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">Cloud OCR Configuration</h2>
                  <div className="space-y-4">
                    <div className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-medium text-gray-900">Google Cloud Vision API</h3>
                        <span className="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded">Not Configured</span>
                      </div>
                      <p className="text-sm text-gray-500">Configure API key for Google Vision (Professional tier)</p>
                    </div>
                    <div className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-medium text-gray-900">AWS Textract</h3>
                        <span className="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded">Not Configured</span>
                      </div>
                      <p className="text-sm text-gray-500">Configure AWS credentials for Textract (Professional tier)</p>
                    </div>
                    <div className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-medium text-gray-900">Azure Document Intelligence</h3>
                        <span className="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded">Not Configured</span>
                      </div>
                      <p className="text-sm text-gray-500">Configure Azure credentials (Professional tier)</p>
                    </div>
                  </div>
                </div>

                {/* Payment Gateway */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">Payment Gateway - Razorpay</h2>
                  <div className="space-y-4">
                    <div className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-medium text-gray-900">Test Mode</h3>
                        <span className="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded">Not Configured</span>
                      </div>
                      <p className="text-sm text-gray-500">Test Key ID & Secret not configured</p>
                    </div>
                    <div className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-medium text-gray-900">Live Mode</h3>
                        <span className="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded">Not Configured</span>
                      </div>
                      <p className="text-sm text-gray-500">Live Key ID & Secret not configured</p>
                    </div>
                  </div>
                </div>

                {/* Existing Configs */}
                {configs.length > 0 && (
                  <div className="bg-white rounded-lg shadow p-6">
                    <h2 className="text-lg font-semibold text-gray-900 mb-4">Custom Configurations</h2>
                    <div className="space-y-4">
                      {configs.map((config) => (
                        <div key={config.id} className="border border-gray-200 rounded-lg p-4">
                          <div className="flex justify-between items-start">
                            <div>
                              <h3 className="font-medium text-gray-900">{config.config_key}</h3>
                              <p className="text-sm text-gray-500 mt-1">{config.description}</p>
                            </div>
                            {config.is_secret && (
                              <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">Secret</span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'llm' && llmStatus && (
              <div className="space-y-6">
                {/* System Resources */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">System Resources</h2>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="border border-gray-200 rounded-lg p-4">
                      <p className="text-sm text-gray-600">Total Memory</p>
                      <p className="text-2xl font-bold text-gray-900">{llmStatus.system_resources.total_memory_gb}GB</p>
                    </div>
                    <div className="border border-gray-200 rounded-lg p-4">
                      <p className="text-sm text-gray-600">Available Memory</p>
                      <p className="text-2xl font-bold text-green-600">{llmStatus.system_resources.available_memory_gb}GB</p>
                    </div>
                    <div className="border border-gray-200 rounded-lg p-4">
                      <p className="text-sm text-gray-600">Free Disk Space</p>
                      <p className="text-2xl font-bold text-blue-600">{llmStatus.system_resources.disk_free_gb}GB</p>
                    </div>
                    <div className="border border-gray-200 rounded-lg p-4">
                      <p className="text-sm text-gray-600">CPU Cores</p>
                      <p className="text-2xl font-bold text-gray-900">{llmStatus.system_resources.cpu_count}</p>
                    </div>
                  </div>
                </div>

                {/* Cloud LLM Status */}
                <div className="bg-white rounded-lg shadow p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-semibold text-gray-900">Cloud LLM (OpenAI)</h2>
                    {llmStatus.cloud_llm.status === 'connected' && (
                      <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                        ✓ Connected
                      </span>
                    )}
                  </div>
                  <div className="space-y-4">
                    <div className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <h3 className="font-medium text-gray-900">GPT-4o (Complex Documents)</h3>
                          <p className="text-sm text-gray-500 mt-1">High accuracy for complex extraction</p>
                        </div>
                        <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Active</span>
                      </div>
                      <div className="mt-3 flex gap-2">
                        <button
                          onClick={() => handleTestConnection('cloud')}
                          disabled={testingConnection}
                          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 text-sm"
                        >
                          {testingConnection ? 'Testing...' : 'Test Connection'}
                        </button>
                      </div>
                    </div>
                    <div className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <h3 className="font-medium text-gray-900">GPT-4o-mini (Simple Documents)</h3>
                          <p className="text-sm text-gray-500 mt-1">Fast and cost-effective for simple docs</p>
                        </div>
                        <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Active</span>
                      </div>
                      <p className="text-sm text-gray-600 mt-2">
                        💰 Cost: ~$0.001/doc | ⚡ Speed: 2-3 seconds
                      </p>
                    </div>
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <p className="text-sm text-blue-900">
                        <strong>Smart Routing Enabled:</strong> System automatically uses GPT-4o-mini for simple documents (confidence &gt;85%) and GPT-4o for complex documents, optimizing cost and accuracy.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Local LLM Status */}
                <div className="bg-white rounded-lg shadow p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-semibold text-gray-900">Local LLM (Ollama)</h2>
                    {llmStatus.local_llm.status === 'insufficient_memory' || llmStatus.local_llm.status === 'installed_but_insufficient_memory' ? (
                      <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">
                        ⚠ Memory Limit
                      </span>
                    ) : (
                      <span className="px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm font-medium">
                        Not Available
                      </span>
                    )}
                  </div>
                  
                  {llmStatus.local_llm.installed_models.length > 0 ? (
                    <div className="space-y-4">
                      <p className="text-sm text-gray-600 mb-3">
                        Downloaded models ({llmStatus.local_llm.installed_models.length}):
                      </p>
                      {llmStatus.local_llm.installed_models.map((model, idx) => (
                        <div key={idx} className="border border-gray-200 rounded-lg p-4">
                          <div className="flex items-center justify-between">
                            <div>
                              <h3 className="font-medium text-gray-900">{model.name}</h3>
                              <p className="text-sm text-gray-500 mt-1">Size: {model.size_gb}GB</p>
                            </div>
                            <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                              Needs 6GB+ Memory
                            </span>
                          </div>
                        </div>
                      ))}
                      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                        <p className="text-sm text-yellow-900">
                          <strong>Container Memory Limit:</strong> {llmStatus.system_resources.total_memory_gb}GB detected. Local models require 6-8GB container memory limit to run. Models are downloaded but cannot load due to insufficient memory.
                        </p>
                        <p className="text-sm text-yellow-900 mt-2">
                          <strong>Recommendation:</strong> Increase Kubernetes container memory limit to 8GB, or continue using cloud LLMs with smart routing (70% cost savings).
                        </p>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                        <p className="text-sm text-gray-600 mb-3">
                          <strong>Status:</strong> {llmStatus.local_llm.reason}
                        </p>
                        <p className="text-sm text-gray-600">
                          Local models like Qwen2.5-7B and DeepSeek-R1 are available for download, but require 6-8GB container memory to run efficiently.
                        </p>
                      </div>
                      
                      <div className="border border-gray-200 rounded-lg p-4">
                        <h3 className="font-medium text-gray-900 mb-2">Available Models (When Memory Increased)</h3>
                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-700">• Qwen2.5-7B (Recommended)</span>
                            <span className="text-gray-500">4.7GB, 85-90% accuracy</span>
                          </div>
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-700">• DeepSeek-R1-Distill-7B</span>
                            <span className="text-gray-500">4.7GB, 87-92% accuracy</span>
                          </div>
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-700">• Qwen2.5-3B (Lightweight)</span>
                            <span className="text-gray-500">1.9GB, 82-88% accuracy</span>
                          </div>
                        </div>
                      </div>

                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <p className="text-sm text-blue-900">
                          <strong>Current Solution:</strong> System is using cloud LLMs with smart routing. This provides excellent accuracy (92-97%) with 70% cost savings compared to always using GPT-4o. You can switch to local models later when memory limits are increased.
                        </p>
                      </div>
                    </div>
                  )}
                </div>

                {/* Cost Comparison */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">Cost Comparison</h2>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead>
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Solution</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cost/Doc</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Speed</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Accuracy</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        <tr className="bg-green-50">
                          <td className="px-4 py-3 text-sm font-medium text-gray-900">Smart Routing (Current) ✓</td>
                          <td className="px-4 py-3 text-sm text-gray-900">$0.002-0.005</td>
                          <td className="px-4 py-3 text-sm text-gray-900">2-5 sec</td>
                          <td className="px-4 py-3 text-sm text-gray-900">92-97%</td>
                        </tr>
                        <tr>
                          <td className="px-4 py-3 text-sm text-gray-700">GPT-4o Only</td>
                          <td className="px-4 py-3 text-sm text-gray-700">$0.01</td>
                          <td className="px-4 py-3 text-sm text-gray-700">2-3 sec</td>
                          <td className="px-4 py-3 text-sm text-gray-700">95-97%</td>
                        </tr>
                        <tr>
                          <td className="px-4 py-3 text-sm text-gray-700">Local Model (When Available)</td>
                          <td className="px-4 py-3 text-sm text-green-600 font-medium">$0</td>
                          <td className="px-4 py-3 text-sm text-gray-700">10-20 sec</td>
                          <td className="px-4 py-3 text-sm text-gray-700">85-90%</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default AdminPanel;
