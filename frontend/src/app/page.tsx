'use client';

import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { getDocuments, deleteDocument, Document } from '@/lib/api';
import styles from './page.module.css';

export default function Home() {
  const router = useRouter();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const docs = await getDocuments();
      setDocuments(docs);
    } catch (err: any) {
      setError(err.message || 'Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this document?')) return;
    
    try {
      await deleteDocument(id);
      await loadDocuments();
    } catch (err: any) {
      alert('Failed to delete document: ' + err.message);
    }
  };

  const getRiskColor = (score: number) => {
    if (score < 30) return '#10b981'; // green
    if (score < 60) return '#f59e0b'; // yellow
    return '#ef4444'; // red
  };

  const getRiskLabel = (score: number) => {
    if (score < 30) return 'Low Risk';
    if (score < 60) return 'Medium Risk';
    return 'High Risk';
  };

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>Contract Compliance Checker</h1>
        <p>Analyze contracts against standard clause library</p>
      </header>

      <main className={styles.main}>
        <div className={styles.actions}>
          <button 
            className={styles.primaryButton}
            onClick={() => router.push('/upload')}
          >
            Upload Contract
          </button>
          <button 
            className={styles.secondaryButton}
            onClick={() => router.push('/clauses')}
          >
            Manage Clauses
          </button>
        </div>

        <section className={styles.documentsSection}>
          <h2>Uploaded Documents</h2>
          
          {loading && <p>Loading documents...</p>}
          {error && <p className={styles.error}>{error}</p>}
          
          {!loading && !error && documents.length === 0 && (
            <p className={styles.emptyState}>
              No documents uploaded yet. Click &quot;Upload Contract&quot; to get started.
            </p>
          )}

          {!loading && documents.length > 0 && (
            <div className={styles.documentGrid}>
              {documents.map((doc) => (
                <div key={doc.id} className={styles.documentCard}>
                  <div className={styles.documentHeader}>
                    <h3>{doc.original_filename}</h3>
                    <div 
                      className={styles.riskBadge}
                      style={{ backgroundColor: getRiskColor(doc.risk_score) }}
                    >
                      {getRiskLabel(doc.risk_score)}
                    </div>
                  </div>
                  
                  <div className={styles.documentMeta}>
                    <p>Uploaded: {new Date(doc.uploaded_at).toLocaleDateString()}</p>
                    <p>Risk Score: {doc.risk_score.toFixed(1)}/100</p>
                  </div>

                  <div className={styles.documentActions}>
                    <button 
                      className={styles.viewButton}
                      onClick={() => router.push(`/documents/${doc.id}`)}
                    >
                      View Details
                    </button>
                    <button 
                      className={styles.deleteButton}
                      onClick={() => handleDelete(doc.id)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
