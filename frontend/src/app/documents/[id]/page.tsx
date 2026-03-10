'use client';

import { useRouter } from 'next/navigation';
import { useState, useEffect, useCallback } from 'react';
import { getDocument, DocumentDetail } from '@/lib/api';
import styles from './document.module.css';

export default function DocumentPage({ params }: { params: any }) {
  const router = useRouter();
  const [document, setDocument] = useState<DocumentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('ALL');

  const loadDocument = useCallback(async () => {
    try {
      setLoading(true);
      const doc = await getDocument(parseInt(params.id));
      setDocument(doc);
    } catch (err: any) {
      setError(err.message || 'Failed to load document');
    } finally {
      setLoading(false);
    }
  }, [params.id]);

  useEffect(() => {
    loadDocument();
  }, [loadDocument]);

  const getRiskColor = (score: number) => {
    if (score < 30) return '#10b981';
    if (score < 60) return '#f59e0b';
    return '#ef4444';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'OK': return '#10b981';
      case 'MISSING': return '#ef4444';
      case 'REVIEW': return '#f59e0b';
      default: return '#6b7280';
    }
  };

  const filteredAnalyses = document?.analyses.filter(
    analysis => filterStatus === 'ALL' || analysis.status === filterStatus
  ) || [];

  const summary = document ? {
    total: document.analyses.length,
    ok: document.analyses.filter(a => a.status === 'OK').length,
    missing: document.analyses.filter(a => a.status === 'MISSING').length,
    review: document.analyses.filter(a => a.status === 'REVIEW').length,
  } : null;

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>Loading document...</div>
      </div>
    );
  }

  if (error || !document) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>{error || 'Document not found'}</div>
        <button onClick={() => router.push('/')}>← Back to Home</button>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div>
          <button 
            className={styles.backButton}
            onClick={() => router.push('/')}
          >
            ← Back
          </button>
          <h1>{document.original_filename}</h1>
          <p>Uploaded {new Date(document.uploaded_at).toLocaleString()}</p>
        </div>
      </header>

      <main className={styles.main}>
        <div className={styles.summaryCard}>
          <h2>Compliance Summary</h2>
          <div className={styles.riskScore}>
            <div>
              <div 
                className={styles.riskCircle}
                style={{ 
                  background: `conic-gradient(${getRiskColor(document.risk_score)} ${document.risk_score * 3.6}deg, #e5e7eb 0deg)`
                }}
              >
                <div className={styles.riskInner}>
                  <span className={styles.riskValue}>{document.risk_score.toFixed(0)}</span>
                  <span className={styles.riskLabel}>Risk Score</span>
                </div>
              </div>
            </div>
            <div className={styles.summaryStats}>
              {summary && (
                <>
                  <div className={styles.stat}>
                    <span className={styles.statValue}>{summary.total}</span>
                    <span className={styles.statLabel}>Total Checks</span>
                  </div>
                  <div className={styles.stat}>
                    <span className={styles.statValue} style={{ color: '#10b981' }}>{summary.ok}</span>
                    <span className={styles.statLabel}>Passed</span>
                  </div>
                  <div className={styles.stat}>
                    <span className={styles.statValue} style={{ color: '#f59e0b' }}>{summary.review}</span>
                    <span className={styles.statLabel}>Need Review</span>
                  </div>
                  <div className={styles.stat}>
                    <span className={styles.statValue} style={{ color: '#ef4444' }}>{summary.missing}</span>
                    <span className={styles.statLabel}>Missing</span>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>

        <div className={styles.analysisSection}>
          <div className={styles.sectionHeader}>
            <h2>Clause Analysis</h2>
            <div className={styles.filters}>
              <button 
                className={filterStatus === 'ALL' ? styles.filterActive : styles.filterButton}
                onClick={() => setFilterStatus('ALL')}
              >
                All ({document.analyses.length})
              </button>
              <button 
                className={filterStatus === 'OK' ? styles.filterActive : styles.filterButton}
                onClick={() => setFilterStatus('OK')}
              >
                OK ({summary?.ok})
              </button>
              <button 
                className={filterStatus === 'REVIEW' ? styles.filterActive : styles.filterButton}
                onClick={() => setFilterStatus('REVIEW')}
              >
                Review ({summary?.review})
              </button>
              <button 
                className={filterStatus === 'MISSING' ? styles.filterActive : styles.filterButton}
                onClick={() => setFilterStatus('MISSING')}
              >
                Missing ({summary?.missing})
              </button>
            </div>
          </div>

          <div className={styles.analysisTable}>
            {filteredAnalyses.map((analysis) => (
              <div key={analysis.id} className={styles.analysisRow}>
                <div className={styles.analysisHeader}>
                  <div>
                    <span className={styles.category}>{analysis.standard_clause.category}</span>
                    <h3>{analysis.standard_clause.title}</h3>
                  </div>
                  <div className={styles.analysisStatus}>
                    <span 
                      className={styles.statusBadge}
                      style={{ backgroundColor: getStatusColor(analysis.status) }}
                    >
                      {analysis.status}
                    </span>
                    <span className={styles.similarity}>
                      {(analysis.similarity_score * 100).toFixed(1)}% match
                    </span>
                  </div>
                </div>

                <div className={styles.clauseComparison}>
                  <div className={styles.clauseBox}>
                    <h4>Standard Clause</h4>
                    <p>{analysis.standard_clause.text}</p>
                  </div>
                  <div className={styles.clauseBox}>
                    <h4>Found in Contract</h4>
                    {analysis.extracted_clause ? (
                      <>
                        {analysis.extracted_clause.clause_number && (
                          <span className={styles.clauseNum}>
                            {analysis.extracted_clause.clause_number}
                          </span>
                        )}
                        <p>{analysis.extracted_clause.text}</p>
                      </>
                    ) : (
                      <p className={styles.notFound}>No matching clause found</p>
                    )}
                  </div>
                </div>

                {analysis.notes && (
                  <div className={styles.notes}>
                    <strong>Note:</strong> {analysis.notes}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
