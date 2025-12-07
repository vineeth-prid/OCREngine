import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import { documentAPI, schemaAPI } from '../services/api';

function Documents({ user, onLogout }) {
  const [documents, setDocuments] = useState([]);
  const [schemas, setSchemas] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [extractedFields, setExtractedFields] = useState([]);
  const [processingLogs, setProcessingLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedSchema, setSelectedSchema] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [editedFields, setEditedFields] = useState({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [docsRes, schemasRes] = await Promise.all([
        documentAPI.list(),
        schemaAPI.list(),
      ]);
      setDocuments(docsRes.data);
      setSchemas(schemasRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);
    if (selectedSchema) {
      formData.append('form_schema_id', selectedSchema);
    }

    try {
      const response = await documentAPI.upload(formData);
      await documentAPI.process(response.data.id);
      setSelectedFile(null);
      setSelectedSchema('');
      loadData();
      alert('Document uploaded and processing started!');
    } catch (error) {
      console.error('Error uploading document:', error);
      alert('Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const handleViewDocument = async (doc) => {
    try {
      const [detailRes, fieldsRes, logsRes] = await Promise.all([
        documentAPI.get(doc.id),
        documentAPI.getFields(doc.id),
        documentAPI.getLogs(doc.id),
      ]);
      setSelectedDocument(detailRes.data);
      setExtractedFields(fieldsRes.data || []);
      setProcessingLogs(logsRes.data || []);
    } catch (error) {
      console.error('Error loading document details:', error);
      alert('Failed to load document details');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'processing': return 'bg-blue-100 text-blue-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getProcessingTime = (doc) => {
    if (doc.processing_started_at && doc.processing_completed_at) {
      const start = new Date(doc.processing_started_at);
      const end = new Date(doc.processing_completed_at);
      const seconds = Math.round((end - start) / 1000);
      return seconds > 0 ? `${seconds}s` : 'N/A';
    }
    return 'N/A';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar user={user} onLogout={onLogout} />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Documents</h1>
          <p className="mt-2 text-gray-600">Upload and process your documents</p>
        </div>

        {/* Upload Form */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Upload Document</h2>
          <form onSubmit={handleUpload} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Document
              </label>
              <input
                type="file"
                onChange={handleFileChange}
                accept=".pdf,.jpg,.jpeg,.png"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                data-testid="file-input"
              />
              <p className="mt-1 text-sm text-gray-500">Accepted: PDF, JPG, PNG</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Form Template (Optional)
              </label>
              <select
                value={selectedSchema}
                onChange={(e) => setSelectedSchema(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                data-testid="schema-select"
              >
                <option value="">No template (Extract text only)</option>
                {schemas.map((schema) => (
                  <option key={schema.id} value={schema.id}>
                    {schema.name}
                  </option>
                ))}
              </select>
            </div>
            <button
              type="submit"
              disabled={!selectedFile || uploading}
              className="w-full bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
              data-testid="upload-btn"
            >
              {uploading ? 'Uploading...' : 'Upload & Process'}
            </button>
          </form>
        </div>

        {/* Documents List */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          </div>
        ) : documents.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <p className="text-gray-500">No documents uploaded yet</p>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Filename
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Confidence
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Processing Time
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Uploaded
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {doc.original_filename}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(doc.status)}`}>
                        {doc.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {doc.overall_confidence ? (doc.overall_confidence * 100).toFixed(1) + '%' : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {getProcessingTime(doc)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <button
                        onClick={() => handleViewDocument(doc)}
                        className="text-primary-600 hover:text-primary-900 font-medium"
                        data-testid={`view-doc-${doc.id}`}
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Document Detail Modal */}
        {selectedDocument && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={() => setSelectedDocument(null)}>
            <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
              <div className="p-6">
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">{selectedDocument.original_filename}</h2>
                    <p className="text-sm text-gray-500 mt-1">Document ID: {selectedDocument.id}</p>
                  </div>
                  <button
                    onClick={() => setSelectedDocument(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                {/* Document Info */}
                <div className="grid grid-cols-2 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
                  <div>
                    <p className="text-sm text-gray-600">Status</p>
                    <p className="text-lg font-semibold text-gray-900">{selectedDocument.status}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Confidence</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {selectedDocument.overall_confidence ? (selectedDocument.overall_confidence * 100).toFixed(1) + '%' : 'N/A'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Processing Time</p>
                    <p className="text-lg font-semibold text-gray-900">{getProcessingTime(selectedDocument)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Pages</p>
                    <p className="text-lg font-semibold text-gray-900">{selectedDocument.num_pages}</p>
                  </div>
                </div>

                {/* Extracted Data */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Extracted Data</h3>
                  {extractedFields.length > 0 ? (
                    <div className="space-y-3">
                      {extractedFields.map((field) => (
                        <div key={field.field_id} className="border border-gray-200 rounded-lg p-4">
                          <div className="flex justify-between items-start mb-2">
                            <div className="flex-1">
                              <p className="text-sm font-medium text-gray-700">{field.field_label}</p>
                              <p className="text-lg text-gray-900 mt-1">
                                {field.final_value || field.normalized_value || field.extracted_value || 'N/A'}
                              </p>
                            </div>
                            <div className="text-right ml-4">
                              <p className="text-xs text-gray-500">Confidence</p>
                              <p className={`text-sm font-semibold ${
                                field.confidence_score >= 0.8 ? 'text-green-600' :
                                field.confidence_score >= 0.5 ? 'text-yellow-600' : 'text-red-600'
                              }`}>
                                {(field.confidence_score * 100).toFixed(1)}%
                              </p>
                              {field.needs_review && (
                                <span className="inline-block mt-1 px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded">
                                  Needs Review
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-600">
                        {selectedDocument.status === 'completed' ? 
                          'No structured data extracted. Document was processed without a form template.' :
                          selectedDocument.status === 'processing' ?
                          'Document is currently being processed...' :
                          selectedDocument.status === 'failed' ?
                          'Processing failed. Check logs for details.' :
                          'Document processing has not been completed yet.'
                        }
                      </p>
                    </div>
                  )}
                </div>

                {/* Processing Logs */}
                {processingLogs.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Processing Logs</h3>
                    <div className="bg-gray-50 rounded-lg p-4 max-h-60 overflow-y-auto">
                      <div className="space-y-2">
                        {processingLogs.map((log) => (
                          <div key={log.id} className="text-sm">
                            <span className={`inline-block w-16 font-medium ${
                              log.level === 'ERROR' ? 'text-red-600' :
                              log.level === 'WARNING' ? 'text-yellow-600' : 'text-blue-600'
                            }`}>
                              [{log.level}]
                            </span>
                            <span className="text-gray-600 ml-2">{log.stage}:</span>
                            <span className="text-gray-900 ml-2">{log.message}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                <button
                  onClick={() => setSelectedDocument(null)}
                  className="w-full bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 transition"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Documents;
