'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { uploadDocument } from '@/lib/api';
import styles from './upload.module.css';

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState('');
  const [error, setError] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    try {
      setUploading(true);
      setProgress('Uploading document...');
      setError('');

      const result = await uploadDocument(file);
      
      setProgress('Analysis complete!');
      
      // Redirect to document detail page after 1 second
      setTimeout(() => {
        router.push(`/documents/${result.document.id}`);
      }, 1000);
      
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Upload failed');
      setUploading(false);
    }
  };

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>Upload Contract</h1>
        <button 
          className={styles.backButton}
          onClick={() => router.push('/')}
        >
          ← Back to Home
        </button>
      </header>

      <main className={styles.main}>
        <div className={styles.uploadCard}>
          <h2>Select PDF Contract</h2>
          <p className={styles.subtitle}>
            Upload a contract PDF to analyze compliance against standard clauses
          </p>

          <div className={styles.uploadArea}>
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              disabled={uploading}
              className={styles.fileInput}
              id="file-upload"
            />
            <label htmlFor="file-upload" className={styles.fileLabel}>
              {file ? file.name : 'Choose PDF file'}
            </label>
          </div>

          {file && (
            <div className={styles.fileInfo}>
              <p>Selected: {file.name}</p>
              <p>Size: {(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          )}

          {progress && (
            <div className={styles.progress}>
              {progress}
            </div>
          )}

          {error && (
            <div className={styles.error}>
              {error}
            </div>
          )}

          <button
            className={styles.uploadButton}
            onClick={handleUpload}
            disabled={!file || uploading}
          >
            {uploading ? 'Processing...' : 'Upload and Analyze'}
          </button>
        </div>

        <div className={styles.infoCard}>
          <h3>What happens next?</h3>
          <ol>
            <li>Your PDF will be uploaded to the server</li>
            <li>Text will be extracted from the document</li>
            <li>Clauses will be identified and analyzed</li>
            <li>Each clause will be compared against our standard clause library</li>
            <li>You&apos;ll receive a compliance report with risk assessment</li>
          </ol>
        </div>
      </main>
    </div>
  );
}
