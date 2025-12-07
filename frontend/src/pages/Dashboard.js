import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import { tenantAPI, documentAPI, schemaAPI } from '../services/api';

function Dashboard({ user, onLogout }) {
  const [usage, setUsage] = useState(null);
  const [stats, setStats] = useState({
    totalDocuments: 0,
    totalSchemas: 0,
    processingDocuments: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [usageRes, docsRes, schemasRes] = await Promise.all([
        tenantAPI.getUsage(),
        documentAPI.list(),
        schemaAPI.list(),
      ]);

      setUsage(usageRes.data);
      setStats({
        totalDocuments: docsRes.data.length,
        totalSchemas: schemasRes.data.length,
        processingDocuments: docsRes.data.filter(d => d.status === 'processing').length,
      });
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar user={user} onLogout={onLogout} />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-gray-600">Welcome back, {user?.full_name || 'User'}!</p>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Usage Stats */}
            {usage && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Usage This Month</h2>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Pages Processed</span>
                    <span className="font-semibold text-gray-900">
                      {usage.current_month_usage} / {usage.max_pages_per_month}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div
                      className="bg-primary-600 h-2.5 rounded-full"
                      style={{ width: `${Math.min(usage.percentage_used, 100)}%` }}
                    ></div>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-500">Tier: {usage.tier}</span>
                    <span className="text-gray-500">{usage.remaining_pages} remaining</span>
                  </div>
                </div>
              </div>
            )}

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-500 mb-2">Total Documents</h3>
                <p className="text-3xl font-bold text-gray-900">{stats.totalDocuments}</p>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-500 mb-2">Form Schemas</h3>
                <p className="text-3xl font-bold text-gray-900">{stats.totalSchemas}</p>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-500 mb-2">Processing</h3>
                <p className="text-3xl font-bold text-gray-900">{stats.processingDocuments}</p>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <a
                  href="/documents"
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition"
                >
                  <div>
                    <h3 className="font-medium text-gray-900">Upload Document</h3>
                    <p className="text-sm text-gray-500">Process a new document</p>
                  </div>
                  <span className="text-primary-600">→</span>
                </a>
                <a
                  href="/schemas"
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition"
                >
                  <div>
                    <h3 className="font-medium text-gray-900">Create Schema</h3>
                    <p className="text-sm text-gray-500">Design a new form</p>
                  </div>
                  <span className="text-primary-600">→</span>
                </a>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
