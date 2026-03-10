'use client';

import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { getStandardClauses, createStandardClause, deleteStandardClause, StandardClause } from '@/lib/api';
import styles from './clauses.module.css';

export default function ClausesPage() {
  const router = useRouter();
  const [clauses, setClauses] = useState<StandardClause[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    category: '',
    title: '',
    text: '',
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadClauses();
  }, []);

  const loadClauses = async () => {
    try {
      setLoading(true);
      const data = await getStandardClauses();
      setClauses(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load clauses');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.category || !formData.title || !formData.text) {
      alert('Please fill in all fields');
      return;
    }

    try {
      setSubmitting(true);
      await createStandardClause(formData);
      setFormData({ category: '', title: '', text: '' });
      setShowForm(false);
      await loadClauses();
    } catch (err: any) {
      alert('Failed to create clause: ' + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this clause?')) return;

    try {
      await deleteStandardClause(id);
      await loadClauses();
    } catch (err: any) {
      alert('Failed to delete clause: ' + err.message);
    }
  };

  const groupedClauses = clauses.reduce((acc, clause) => {
    if (!acc[clause.category]) {
      acc[clause.category] = [];
    }
    acc[clause.category].push(clause);
    return acc;
  }, {} as Record<string, StandardClause[]>);

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div>
          <h1>Standard Clause Library</h1>
          <p>Manage your standard contract clauses</p>
        </div>
        <button 
          className={styles.backButton}
          onClick={() => router.push('/')}
        >
          ← Back to Home
        </button>
      </header>

      <main className={styles.main}>
        <div className={styles.actions}>
          <button 
            className={styles.addButton}
            onClick={() => setShowForm(!showForm)}
          >
            {showForm ? 'Cancel' : '+ Add New Clause'}
          </button>
        </div>

        {showForm && (
          <div className={styles.formCard}>
            <h2>Add New Standard Clause</h2>
            <form onSubmit={handleSubmit}>
              <div className={styles.formGroup}>
                <label>Category</label>
                <input
                  type="text"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  placeholder="e.g., Confidentiality, Payment, etc."
                  required
                />
              </div>
              <div className={styles.formGroup}>
                <label>Title</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="e.g., Non-Disclosure Obligation"
                  required
                />
              </div>
              <div className={styles.formGroup}>
                <label>Clause Text</label>
                <textarea
                  value={formData.text}
                  onChange={(e) => setFormData({ ...formData, text: e.target.value })}
                  placeholder="Enter the full text of the standard clause..."
                  rows={6}
                  required
                />
              </div>
              <button type="submit" disabled={submitting} className={styles.submitButton}>
                {submitting ? 'Creating...' : 'Create Clause'}
              </button>
            </form>
          </div>
        )}

        {loading && <p className={styles.loading}>Loading clauses...</p>}
        {error && <p className={styles.error}>{error}</p>}

        {!loading && !error && clauses.length === 0 && (
          <div className={styles.emptyState}>
            <p>No standard clauses yet. Add your first clause to get started!</p>
          </div>
        )}

        {!loading && clauses.length > 0 && (
          <div className={styles.clausesGrid}>
            {Object.entries(groupedClauses).map(([category, categoryClaus]) => (
              <div key={category} className={styles.categorySection}>
                <h2>{category} <span>({categoryClaus.length})</span></h2>
                <div className={styles.clausesList}>
                  {categoryClaus.map((clause) => (
                    <div key={clause.id} className={styles.clauseCard}>
                      <div className={styles.clauseHeader}>
                        <h3>{clause.title}</h3>
                        <button
                          className={styles.deleteButton}
                          onClick={() => handleDelete(clause.id)}
                          title="Delete clause"
                        >
                          ×
                        </button>
                      </div>
                      <p className={styles.clauseText}>{clause.text}</p>
                      <div className={styles.clauseMeta}>
                        Added {new Date(clause.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
