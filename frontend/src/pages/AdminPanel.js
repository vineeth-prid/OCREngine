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
      const [statsRes, configsRes] = await Promise.all([
        adminAPI.getStats(),
        adminAPI.listConfigs(),
      ]);
      setStats(statsRes.data);
      setConfigs(configsRes.data);
    } catch (error) {
      console.error('Error loading admin data:', error);
    } finally {
      setLoading(false);
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
          </div>
        )}
      </div>
    </div>
  );
}

export default AdminPanel;
