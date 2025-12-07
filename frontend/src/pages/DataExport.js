import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import { documentAPI, schemaAPI } from '../services/api';

function DataExport({ user, onLogout }) {
  const [schemas, setSchemas] = useState([]);
  const [selectedSchema, setSelectedSchema] = useState(null);
  const [tableData, setTableData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    loadSchemas();
  }, []);

  const loadSchemas = async () => {
    try {
      const response = await schemaAPI.list();
      setSchemas(response.data);
    } catch (error) {
      console.error('Error loading schemas:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSchemaSelect = async (schemaId) => {
    setSelectedSchema(schemaId);
    setLoading(true);
    try {
      const response = await documentAPI.getDataBySchema(schemaId);
      setTableData(response.data);
    } catch (error) {
      console.error('Error loading table data:', error);
      alert('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleExportCSV = async () => {
    if (!selectedSchema) return;
    
    setExporting(true);
    try {
      const response = await documentAPI.exportCSV(selectedSchema);
      
      // Create blob and download
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${tableData.schema_name}_export_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exporting CSV:', error);
      alert('Failed to export CSV');
    } finally {
      setExporting(false);
    }
  };

  const handleExportExcel = () => {
    if (!tableData) return;
    
    // Convert table data to Excel format (simple CSV for now)
    const csvContent = convertToCSV(tableData);
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${tableData.schema_name}_export_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  const convertToCSV = (data) => {
    const headers = data.columns.join(',');
    const rows = data.rows.map(row => {
      return data.columns.map(col => {
        const value = row[col] || '';
        // Escape commas and quotes
        return `"${String(value).replace(/"/g, '""')}"`;
      }).join(',');
    });
    return [headers, ...rows].join('\n');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar user={user} onLogout={onLogout} />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Data Export</h1>
          <p className="mt-2 text-gray-600">View and export extracted data by template</p>
        </div>

        {/* Schema Selection */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Select Template</h2>
          <select
            value={selectedSchema || ''}
            onChange={(e) => handleSchemaSelect(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          >
            <option value="">Choose a template...</option>
            {schemas.map((schema) => (
              <option key={schema.id} value={schema.id}>
                {schema.name} ({schema.fields?.length || 0} fields)
              </option>
            ))}
          </select>
        </div>

        {/* Table View */}
        {loading && selectedSchema ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          </div>
        ) : tableData ? (
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">{tableData.schema_name}</h2>
                  <p className="text-sm text-gray-600 mt-1">
                    {tableData.total_documents} document{tableData.total_documents !== 1 ? 's' : ''} processed
                  </p>
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={handleExportExcel}
                    disabled={exporting}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 font-medium"
                  >
                    📊 Export Excel
                  </button>
                  <button
                    onClick={handleExportCSV}
                    disabled={exporting}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
                  >
                    📄 Export CSV
                  </button>
                </div>
              </div>
            </div>

            {tableData.rows.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      {tableData.columns.map((col, idx) => (
                        <th
                          key={idx}
                          className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap"
                        >
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {tableData.rows.map((row, rowIdx) => (
                      <tr key={rowIdx} className="hover:bg-gray-50">
                        {tableData.columns.map((col, colIdx) => {
                          const value = row[col];
                          return (
                            <td key={colIdx} className="px-6 py-4 text-sm text-gray-900 whitespace-nowrap">
                              {value !== null && value !== undefined && value !== '' ? value : '-'}
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="p-12 text-center">
                <p className="text-gray-500">No completed documents found for this template</p>
              </div>
            )}
          </div>
        ) : selectedSchema ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <p className="text-gray-500">No data available</p>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <p className="text-gray-500">Select a template to view extracted data</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default DataExport;
